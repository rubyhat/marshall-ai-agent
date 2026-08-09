#!/usr/bin/env python3
"""Run Codex spec review and read the authoritative child-session result.

The Codex CLI outer process is only a launcher and diagnostic stream. Review
correctness comes from matched review child JSONL sessions under the active
Codex sessions directory. The implementation intentionally uses only the
Python standard library so installed skills remain portable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Sequence


CAPTURE_CONTRACT_REVISION = 1
RESULT_SCHEMA_VERSION = 1
SESSION_ID_RE = re.compile(
    r"(?im)^\s*session id:\s*"
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\s*$"
)
ALLOWED_EFFORTS = {"low", "medium", "high", "xhigh"}
ALLOWED_TARGET_KINDS = {"uncommitted", "committed"}
DELETED_BLOB_PREFIX = "deleted:"
NATIVE_RESULT_FIELDS = {
    "findings",
    "overall_correctness",
    "overall_explanation",
    "overall_confidence_score",
}
NATIVE_FINDING_FIELDS = {
    "title",
    "body",
    "confidence_score",
    "priority",
    "code_location",
}
TOKEN_USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)
CORRECT_VERDICT = "patch is correct"
INCORRECT_VERDICT = "patch is incorrect"
TERMINAL_OUTER_EVENTS = {"task_complete", "turn_aborted", "turn_complete"}
EXIT_BY_STATUS = {
    "clean": 0,
    "non_clean": 10,
    "terminal_contract_error": 11,
    "target_changed": 12,
    "invocation_binding_error": 13,
    "technical_retry_budget_exhausted": 14,
    "session_settlement_timeout": 15,
    "no_authoritative_terminal_result": 16,
}


class RunnerConfigurationError(ValueError):
    """Raised before a model invocation when the runner contract is invalid."""


@dataclass(frozen=True)
class TargetSnapshot:
    kind: str
    worktree: str
    branch: str
    base_revision: str
    head_revision: str | None
    manifest: tuple[tuple[str, str], ...]
    manifest_fingerprint: str
    state_fingerprint: str

    def as_result(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "worktree": self.worktree,
            "branch": self.branch,
            "base_revision": self.base_revision,
            "head_revision": self.head_revision,
            "manifest_fingerprint": self.manifest_fingerprint,
        }


@dataclass
class Invocation:
    invocation_id: str
    kind: str
    correlation_id: str
    started_at: datetime
    completed_at: datetime
    review_parent_session_id: str | None
    process_exit_code: int
    stdout_bytes: int = 0
    stderr_bytes: int = 0
    stdout_sha256: str | None = None
    stderr_sha256: str | None = None
    binding_error: str | None = None

    def as_result(self) -> dict[str, Any]:
        return {
            "invocation_id": self.invocation_id,
            "kind": self.kind,
            "correlation_id": self.correlation_id,
            "review_parent_session_id": self.review_parent_session_id,
            "started_at": format_time(self.started_at),
            "completed_at": format_time(self.completed_at),
            "process_exit_code": self.process_exit_code,
            "stdout_diagnostic": {
                "bytes": self.stdout_bytes,
                "sha256": self.stdout_sha256,
            },
            "stderr_diagnostic": {
                "bytes": self.stderr_bytes,
                "sha256": self.stderr_sha256,
            },
        }


@dataclass
class SessionDocument:
    path: Path
    size: int
    mtime_ns: int
    meta: dict[str, Any] | None
    records: list[tuple[int, dict[str, Any]]]
    parse_errors: list[str] = field(default_factory=list)

    @property
    def session_id(self) -> str | None:
        if not self.meta:
            return None
        value = self.meta.get("id")
        return value if isinstance(value, str) else None


@dataclass
class BoundSessions:
    outers: dict[str, SessionDocument]
    children: list[tuple[Invocation, SessionDocument]]
    binding_errors: list[dict[str, Any]]
    missing_outer_invocations: list[str]
    outer_sessions_terminal: bool
    matched_child_sessions_terminal: bool
    signature: str


@dataclass
class SettlementResult:
    status: str
    started_at: datetime
    completed_at: datetime
    stable_scans_observed: int
    last_change_observed_at: datetime
    final_rescan_at: datetime
    bound: BoundSessions

    def as_result(self) -> dict[str, Any]:
        return {
            "started_at": format_time(self.started_at),
            "completed_at": format_time(self.completed_at),
            "registered_subprocesses_exited": True,
            "registered_outer_sessions_terminal": self.bound.outer_sessions_terminal,
            "matched_child_sessions_terminal": self.bound.matched_child_sessions_terminal,
            "stable_scans_observed": self.stable_scans_observed,
            "last_change_observed_at": format_time(self.last_change_observed_at),
            "final_rescan_at": format_time(self.final_rescan_at),
        }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def build_review_instructions(target: TargetSnapshot, task_id: str) -> str:
    manifest_paths = json.dumps(
        [path for path, _ in target.manifest],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"""Perform an independent specification-contract review for task {task_id}.

The runner has selected the exact Git review target; do not substitute a different diff. The target kind is {target.kind}, its canonical base is {target.base_revision}, its manifest fingerprint is {target.manifest_fingerprint}, and its complete changed-path manifest is {manifest_paths}.

Treat the changed specification package as the shaped contract. Read its task anchor, outcome, scope, non-goals, dependencies, requirements, acceptance criteria, and test plan. Require the task identity to agree with {task_id}. Read applicable AGENTS.md plus only the architecture, code, policy, tracker references, and tests needed to verify concrete claims.

Report concrete defects in identity, scope boundaries, requirements, permissions, states, errors, recovery, lifecycle behavior, API/data/migration/compatibility/rollout/privacy/security/billing/localization/accessibility/observability/operations where applicable, dependency ordering, cross-repository ownership, acceptance-criteria coverage, actionable verification, invented technical detail, hidden blockers, or task size. Do not request stylistic rewrites, general improvements, speculative edge cases without a credible current-task risk, or work explicitly assigned to another task. Do not use planning discussion history, author reasoning, expected findings, or an intended verdict."""


def run_git(worktree: Path, arguments: Sequence[str], *, input_bytes: bytes | None = None) -> bytes:
    process = subprocess.run(
        ["git", "-C", str(worktree), *arguments],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise RunnerConfigurationError(
            f"git {' '.join(arguments)} failed in {worktree}: {detail}"
        )
    return process.stdout


def parse_porcelain_paths(raw: bytes) -> set[str]:
    entries = raw.split(b"\0")
    paths: set[str] = set()
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        if len(entry) < 4:
            raise RunnerConfigurationError("unexpected git status --porcelain entry")
        status = entry[:2].decode("ascii", errors="replace")
        candidate = entry[3:].decode("utf-8", errors="surrogateescape")
        paths.add(candidate)
        if "R" in status or "C" in status:
            if index >= len(entries) or not entries[index]:
                raise RunnerConfigurationError("rename/copy status is missing its source path")
            source = entries[index].decode("utf-8", errors="surrogateescape")
            index += 1
            if "R" in status:
                paths.add(source)
    return paths


def changed_paths(worktree: Path, base_revision: str) -> tuple[set[str], bytes]:
    committed = run_git(
        worktree,
        ["diff", "--name-only", "-z", f"{base_revision}..HEAD", "--"],
    )
    status = run_git(worktree, ["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    committed_paths = {
        item.decode("utf-8", errors="surrogateescape")
        for item in committed.split(b"\0")
        if item
    }
    return committed_paths | parse_porcelain_paths(status), status


def base_blob_oid_for_path(
    worktree: Path, base_revision: str, relative_path: str
) -> str | None:
    raw = run_git(
        worktree,
        ["ls-tree", "-z", base_revision, "--", relative_path],
    )
    if not raw:
        return None
    entries = [entry for entry in raw.split(b"\0") if entry]
    if len(entries) != 1 or b"\t" not in entries[0]:
        raise RunnerConfigurationError(
            f"unexpected base tree entry for manifest path: {relative_path}"
        )
    metadata, recorded_path = entries[0].split(b"\t", 1)
    fields = metadata.split()
    if len(fields) != 3 or fields[1] != b"blob":
        raise RunnerConfigurationError(
            f"review manifest base path is not a blob: {relative_path}"
        )
    if recorded_path.decode("utf-8", errors="surrogateescape") != relative_path:
        raise RunnerConfigurationError(
            f"review manifest base path mismatch: {relative_path}"
        )
    return fields[2].decode("ascii")


def manifest_blob_state_for_path(
    worktree: Path, base_revision: str, relative_path: str
) -> str | None:
    candidate = (worktree / relative_path).resolve()
    try:
        candidate.relative_to(worktree.resolve())
    except ValueError as error:
        raise RunnerConfigurationError(
            f"manifest path escapes the worktree: {relative_path}"
        ) from error
    base_blob_oid = base_blob_oid_for_path(worktree, base_revision, relative_path)
    if candidate.is_file():
        current_blob_oid = run_git(
            worktree, ["hash-object", "--", relative_path]
        ).decode().strip()
        return None if current_blob_oid == base_blob_oid else current_blob_oid
    if candidate.exists():
        raise RunnerConfigurationError(
            f"review manifest contains a non-file path: {relative_path}"
        )
    if base_blob_oid is not None:
        return f"{DELETED_BLOB_PREFIX}{base_blob_oid}"
    return None


def build_target_snapshot(
    worktree_value: str,
    target_kind: str,
    base_value: str,
    head_value: str | None = None,
) -> TargetSnapshot:
    worktree = Path(worktree_value).resolve()
    if target_kind not in ALLOWED_TARGET_KINDS:
        raise RunnerConfigurationError(f"unsupported target kind: {target_kind}")
    if not worktree.is_dir():
        raise RunnerConfigurationError(f"review worktree does not exist: {worktree}")
    top_level = Path(run_git(worktree, ["rev-parse", "--show-toplevel"]).decode().strip()).resolve()
    if top_level != worktree:
        raise RunnerConfigurationError(
            f"--worktree must be the exact Git worktree root: {worktree} != {top_level}"
        )
    base_revision = run_git(worktree, ["rev-parse", "--verify", f"{base_value}^{{commit}}"])
    base_revision_text = base_revision.decode().strip()
    current_head = run_git(worktree, ["rev-parse", "--verify", "HEAD^{commit}"]).decode().strip()
    if head_value is not None:
        expected_head = run_git(worktree, ["rev-parse", "--verify", f"{head_value}^{{commit}}"]).decode().strip()
        if expected_head != current_head:
            raise RunnerConfigurationError(
                f"configured head {expected_head} does not match worktree HEAD {current_head}"
            )
    branch = run_git(worktree, ["symbolic-ref", "--quiet", "--short", "HEAD"]).decode().strip()
    paths, status = changed_paths(worktree, base_revision_text)
    if target_kind == "committed" and status:
        raise RunnerConfigurationError("committed review target requires a clean worktree")
    manifest_items: list[tuple[str, str]] = []
    for path in paths:
        blob_state = manifest_blob_state_for_path(
            worktree, base_revision_text, path
        )
        if blob_state is not None:
            manifest_items.append((path, blob_state))
    manifest = tuple(sorted(manifest_items))
    if not manifest:
        raise RunnerConfigurationError("review target has an empty diff manifest")
    manifest_payload = [
        {"path": path, "blob_oid": blob_oid} for path, blob_oid in manifest
    ]
    state_payload = {
        "head": current_head,
        "status_sha256": hashlib.sha256(status).hexdigest(),
        "manifest": manifest_payload,
    }
    return TargetSnapshot(
        kind=target_kind,
        worktree=str(worktree),
        branch=branch,
        base_revision=base_revision_text,
        head_revision=current_head if target_kind == "committed" else None,
        manifest=manifest,
        manifest_fingerprint=sha256_json(manifest_payload),
        state_fingerprint=sha256_json(state_payload),
    )


def default_sessions_root() -> Path:
    configured = os.environ.get("CODEX_HOME")
    codex_root = Path(configured).expanduser() if configured else Path.home() / ".codex"
    return codex_root / "sessions"


def read_session_document(path: Path) -> SessionDocument:
    stat = path.stat()
    records: list[tuple[int, dict[str, Any]]] = []
    errors: list[str] = []
    meta: dict[str, Any] | None = None
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                errors.append(f"line {line_number}: {error.msg}")
                continue
            if not isinstance(record, dict):
                errors.append(f"line {line_number}: JSONL record is not an object")
                continue
            records.append((line_number, record))
            if record.get("type") == "session_meta" and isinstance(record.get("payload"), dict):
                if meta is not None:
                    errors.append(f"line {line_number}: duplicate session_meta")
                else:
                    meta = record["payload"]
                    if "timestamp" not in meta and isinstance(record.get("timestamp"), str):
                        meta = {**meta, "timestamp": record["timestamp"]}
    return SessionDocument(
        path=path,
        size=stat.st_size,
        mtime_ns=stat.st_mtime_ns,
        meta=meta,
        records=records,
        parse_errors=errors,
    )


def scan_session_documents(sessions_root: Path, attempt_started_at: datetime) -> list[SessionDocument]:
    if not sessions_root.is_dir():
        return []
    earliest_mtime = attempt_started_at.timestamp() - 5.0
    documents: list[SessionDocument] = []
    for path in sorted(sessions_root.rglob("*.jsonl")):
        try:
            if path.stat().st_mtime < earliest_mtime:
                continue
            documents.append(read_session_document(path))
        except FileNotFoundError:
            continue
    return documents


def source_is_exec(meta: dict[str, Any]) -> bool:
    return meta.get("source") == "exec"


def source_is_review(meta: dict[str, Any]) -> bool:
    source = meta.get("source")
    return isinstance(source, dict) and source.get("subagent") == "review"


def same_worktree(value: Any, expected: str) -> bool:
    if not isinstance(value, str):
        return False
    return Path(value).resolve() == Path(expected).resolve()


def event_type(record: dict[str, Any]) -> str | None:
    if record.get("type") != "event_msg" or not isinstance(record.get("payload"), dict):
        return None
    value = record["payload"].get("type")
    return value if isinstance(value, str) else None


def has_outer_terminal(document: SessionDocument) -> bool:
    return any(event_type(record) in TERMINAL_OUTER_EVENTS for _, record in document.records)


def terminal_records(document: SessionDocument) -> list[tuple[int, dict[str, Any]]]:
    return [
        (line_number, record)
        for line_number, record in document.records
        if event_type(record) == "task_complete"
    ]


def bind_sessions(
    documents: list[SessionDocument],
    invocations: list[Invocation],
    worktree: str,
) -> BoundSessions:
    by_id: dict[str, list[SessionDocument]] = {}
    for document in documents:
        if document.session_id:
            by_id.setdefault(document.session_id, []).append(document)

    outers: dict[str, SessionDocument] = {}
    children: list[tuple[Invocation, SessionDocument]] = []
    errors: list[dict[str, Any]] = []
    missing: list[str] = []
    invocation_by_parent = {
        invocation.review_parent_session_id: invocation
        for invocation in invocations
        if invocation.review_parent_session_id
    }

    for parent_id, invocation in invocation_by_parent.items():
        candidates = by_id.get(parent_id, [])
        exact = [
            document
            for document in candidates
            if document.meta
            and source_is_exec(document.meta)
            and same_worktree(document.meta.get("cwd"), worktree)
        ]
        if len(exact) != 1:
            if not exact:
                missing.append(invocation.invocation_id)
            else:
                errors.append(
                    {
                        "code": "duplicate_outer_session",
                        "invocation_id": invocation.invocation_id,
                        "review_parent_session_id": parent_id,
                        "paths": sorted(str(item.path) for item in exact),
                    }
                )
            continue
        outer = exact[0]
        meta_time = parse_time(outer.meta.get("timestamp")) if outer.meta else None
        if (
            meta_time is None
            or meta_time < invocation.started_at.replace(microsecond=0)
            or meta_time > invocation.completed_at + timedelta(seconds=1)
        ):
            errors.append(
                {
                    "code": "outer_session_boundary_mismatch",
                    "invocation_id": invocation.invocation_id,
                    "review_parent_session_id": parent_id,
                    "path": str(outer.path),
                }
            )
            continue
        if outer.parse_errors:
            errors.append(
                {
                    "code": "outer_session_jsonl_error",
                    "invocation_id": invocation.invocation_id,
                    "review_parent_session_id": parent_id,
                    "path": str(outer.path),
                    "details": outer.parse_errors,
                }
            )
            continue
        outers[invocation.invocation_id] = outer

    parent_ids = set(invocation_by_parent)
    for document in documents:
        meta = document.meta
        if not meta or meta.get("parent_thread_id") not in parent_ids:
            continue
        parent_id = meta["parent_thread_id"]
        invocation = invocation_by_parent[parent_id]
        if not source_is_review(meta):
            continue
        if not same_worktree(meta.get("cwd"), worktree):
            errors.append(
                {
                    "code": "review_child_worktree_mismatch",
                    "invocation_id": invocation.invocation_id,
                    "session_id": document.session_id,
                    "path": str(document.path),
                }
            )
            continue
        if document.parse_errors:
            errors.append(
                {
                    "code": "review_child_jsonl_error",
                    "invocation_id": invocation.invocation_id,
                    "session_id": document.session_id,
                    "path": str(document.path),
                    "details": document.parse_errors,
                }
            )
            continue
        children.append((invocation, document))

    outer_terminal = len(outers) == len(invocation_by_parent) and all(
        has_outer_terminal(document) for document in outers.values()
    )
    child_terminal = all(bool(terminal_records(document)) for _, document in children)
    signature_payload = {
        "outers": [
            [invocation_id, str(document.path), document.size, document.mtime_ns]
            for invocation_id, document in sorted(outers.items())
        ],
        "children": [
            [
                invocation.invocation_id,
                document.session_id,
                str(document.path),
                document.size,
                document.mtime_ns,
                len(terminal_records(document)),
            ]
            for invocation, document in sorted(
                children,
                key=lambda item: (item[0].invocation_id, item[1].session_id or ""),
            )
        ],
        "errors": errors,
        "missing": missing,
    }
    invocation_order = {
        invocation.invocation_id: index for index, invocation in enumerate(invocations)
    }
    children.sort(
        key=lambda item: (
            invocation_order[item[0].invocation_id],
            item[1].session_id or "",
            str(item[1].path),
        )
    )
    errors.sort(key=sha256_json)
    return BoundSessions(
        outers=outers,
        children=children,
        binding_errors=errors,
        missing_outer_invocations=missing,
        outer_sessions_terminal=outer_terminal,
        matched_child_sessions_terminal=child_terminal,
        signature=sha256_json(signature_payload),
    )


def settle_sessions(
    sessions_root: Path,
    attempt_started_at: datetime,
    invocations: list[Invocation],
    worktree: str,
    *,
    minimum_stable_scans: int,
    settle_interval_seconds: float,
    settlement_timeout_seconds: float,
    clock: Callable[[], datetime] = utc_now,
    sleeper: Callable[[float], None] = time.sleep,
) -> SettlementResult:
    started = clock()
    deadline = time.monotonic() + settlement_timeout_seconds
    last_signature: str | None = None
    stable_scans = 0
    last_change = started
    latest = bind_sessions([], invocations, worktree)

    while True:
        documents = scan_session_documents(sessions_root, attempt_started_at)
        latest = bind_sessions(documents, invocations, worktree)
        now = clock()
        ready = (
            not latest.binding_errors
            and not latest.missing_outer_invocations
            and latest.outer_sessions_terminal
            and latest.matched_child_sessions_terminal
        )
        if ready:
            if latest.signature == last_signature:
                stable_scans += 1
            else:
                stable_scans = 1
                last_change = now
            last_signature = latest.signature
            if stable_scans >= minimum_stable_scans:
                final_documents = scan_session_documents(sessions_root, attempt_started_at)
                final_bound = bind_sessions(final_documents, invocations, worktree)
                final_time = clock()
                if (
                    final_bound.signature == latest.signature
                    and not final_bound.binding_errors
                    and not final_bound.missing_outer_invocations
                    and final_bound.outer_sessions_terminal
                    and final_bound.matched_child_sessions_terminal
                ):
                    status = (
                        "settled_with_terminal_result"
                        if final_bound.children
                        else "no_authoritative_terminal_result"
                    )
                    return SettlementResult(
                        status=status,
                        started_at=started,
                        completed_at=final_time,
                        stable_scans_observed=stable_scans,
                        last_change_observed_at=last_change,
                        final_rescan_at=final_time,
                        bound=final_bound,
                    )
                stable_scans = 0
                last_signature = final_bound.signature
                last_change = final_time
                latest = final_bound
        else:
            if latest.signature != last_signature:
                last_change = now
                last_signature = latest.signature
            stable_scans = 0

        if time.monotonic() >= deadline:
            final_documents = scan_session_documents(sessions_root, attempt_started_at)
            final_bound = bind_sessions(final_documents, invocations, worktree)
            final_time = clock()
            status = (
                "invocation_binding_error"
                if final_bound.binding_errors or final_bound.missing_outer_invocations
                else "session_settlement_timeout"
            )
            return SettlementResult(
                status=status,
                started_at=started,
                completed_at=final_time,
                stable_scans_observed=stable_scans,
                last_change_observed_at=last_change,
                final_rescan_at=final_time,
                bound=final_bound,
            )
        sleeper(settle_interval_seconds)


def normalize_whitespace(value: str) -> str:
    return " ".join(value.strip().split())


def is_confidence(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1


def normalize_location(location: Any, worktree: Path, manifest_paths: set[str]) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(location, dict):
        return None, "missing_code_location"
    absolute_value = location.get("absolute_file_path")
    line_range = location.get("line_range")
    if not isinstance(absolute_value, str) or not isinstance(line_range, dict):
        return None, "invalid_code_location"
    absolute_path = Path(absolute_value).resolve()
    try:
        relative = absolute_path.relative_to(worktree.resolve()).as_posix()
    except ValueError:
        return None, "location_outside_review_worktree"
    if relative not in manifest_paths:
        return None, "location_outside_review_manifest"
    start = line_range.get("start")
    end = line_range.get("end")
    if (
        not isinstance(start, int)
        or isinstance(start, bool)
        or not isinstance(end, int)
        or isinstance(end, bool)
        or start < 1
        or end < start
    ):
        return None, "invalid_line_range"
    return {"path": relative, "line_range": {"start": start, "end": end}}, None


def finding_fingerprint(finding: dict[str, Any]) -> str:
    priority = finding.get("priority")
    payload = {
        "title": normalize_whitespace(finding["title"]),
        "body": normalize_whitespace(finding["body"]),
        "confidence_score": finding["confidence_score"],
        "priority": priority if priority is not None else "unspecified",
        "code_location": finding["code_location"],
    }
    return sha256_json(payload)


def validate_terminal_message(
    raw_message: Any,
    worktree: Path,
    manifest_paths: set[str],
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if not isinstance(raw_message, str):
        return None, ["last_agent_message_not_json_string"]
    try:
        parsed = json.loads(raw_message)
    except json.JSONDecodeError:
        return None, ["invalid_terminal_json"]
    if not isinstance(parsed, dict):
        return None, ["terminal_result_not_object"]

    unknown_result_fields = sorted(set(parsed) - NATIVE_RESULT_FIELDS)
    if unknown_result_fields:
        errors.append(
            "unsupported_top_level_fields:" + ",".join(unknown_result_fields)
        )

    findings_value = parsed.get("findings")
    correctness = parsed.get("overall_correctness")
    explanation = parsed.get("overall_explanation")
    overall_confidence = parsed.get("overall_confidence_score")
    if not isinstance(findings_value, list):
        errors.append("findings_not_array")
        findings_value = []
    if correctness not in {CORRECT_VERDICT, INCORRECT_VERDICT}:
        errors.append("unsupported_overall_correctness")
    if not isinstance(explanation, str) or not explanation.strip():
        errors.append("missing_overall_explanation")
    if not is_confidence(overall_confidence):
        errors.append("invalid_overall_confidence_score")

    normalized_findings: list[dict[str, Any]] = []
    for index, finding in enumerate(findings_value):
        prefix = f"finding_{index}"
        if not isinstance(finding, dict):
            errors.append(f"{prefix}_not_object")
            continue
        unknown_finding_fields = sorted(set(finding) - NATIVE_FINDING_FIELDS)
        if unknown_finding_fields:
            errors.append(
                f"{prefix}_unsupported_fields:" + ",".join(unknown_finding_fields)
            )
        title = finding.get("title")
        body = finding.get("body")
        confidence = finding.get("confidence_score")
        priority = finding.get("priority")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{prefix}_missing_title")
        if not isinstance(body, str) or not body.strip():
            errors.append(f"{prefix}_missing_body")
        if not is_confidence(confidence):
            errors.append(f"{prefix}_invalid_confidence_score")
        if priority is not None and (
            not isinstance(priority, int)
            or isinstance(priority, bool)
            or priority not in {0, 1, 2, 3}
        ):
            errors.append(f"{prefix}_invalid_priority")
        normalized_location, location_error = normalize_location(
            finding.get("code_location"), worktree, manifest_paths
        )
        if location_error:
            errors.append(f"{prefix}_{location_error}")
        if any(error.startswith(prefix) for error in errors):
            continue
        normalized = {
            "title": title.strip(),
            "body": body.strip(),
            "confidence_score": confidence,
            "code_location": normalized_location,
        }
        if "priority" in finding:
            normalized["priority"] = priority
        normalized["fingerprint"] = finding_fingerprint(normalized)
        normalized_findings.append(normalized)

    if correctness == INCORRECT_VERDICT and not findings_value:
        errors.append("incorrect_without_findings")
    if errors:
        return None, errors
    return {
        "findings": normalized_findings,
        "overall_correctness": correctness,
        "overall_explanation": explanation.strip(),
        "overall_confidence_score": overall_confidence,
    }, []


def last_token_usage(document: SessionDocument) -> dict[str, int] | None:
    usage: dict[str, int] | None = None
    for _, record in document.records:
        if event_type(record) != "token_count":
            continue
        payload = record.get("payload", {})
        info = payload.get("info") if isinstance(payload, dict) else None
        total = info.get("total_token_usage") if isinstance(info, dict) else None
        if not isinstance(total, dict):
            continue
        fields = {
            "input_tokens": total.get("input_tokens", 0),
            "cached_input_tokens": total.get("cached_input_tokens", 0),
            "output_tokens": total.get("output_tokens", 0),
            "reasoning_output_tokens": total.get("reasoning_output_tokens", 0),
            "total_tokens": total.get("total_tokens", 0),
        }
        if all(isinstance(value, int) and not isinstance(value, bool) and value >= 0 for value in fields.values()):
            usage = fields
    return usage


def cumulative_token_usage(
    matched_sessions: list[dict[str, Any]],
) -> dict[str, int] | None:
    """Sum the final cumulative snapshot once per matched child session."""

    by_session: dict[str, dict[str, int]] = {}
    for matched in matched_sessions:
        session_id = matched.get("session_id")
        usage = matched.get("token_usage")
        if isinstance(session_id, str) and isinstance(usage, dict):
            by_session[session_id] = usage
    if not by_session:
        return None
    totals = {
        field: sum(usage[field] for usage in by_session.values())
        for field in TOKEN_USAGE_FIELDS
    }
    totals["matched_sessions_with_usage"] = len(by_session)
    return totals


def terminal_event_identity(document: SessionDocument, line_number: int, record: dict[str, Any]) -> str:
    payload = record.get("payload")
    if isinstance(payload, dict) and isinstance(payload.get("id"), str):
        return payload["id"]
    return hashlib.sha256(
        f"{document.path}:{line_number}:".encode("utf-8") + canonical_json(record)
    ).hexdigest()


def consolidate_terminal_results(
    bound: BoundSessions,
    target: TargetSnapshot,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    normalized_results: list[dict[str, Any]] = []
    matched_sessions: list[dict[str, Any]] = []
    contract_errors: list[dict[str, Any]] = []
    manifest_paths = {path for path, _ in target.manifest}
    worktree = Path(target.worktree)

    for invocation, document in bound.children:
        for line_number, record in terminal_records(document):
            payload = record.get("payload", {})
            raw_message = payload.get("last_agent_message") if isinstance(payload, dict) else None
            event_id = terminal_event_identity(document, line_number, record)
            message_hash = hashlib.sha256(
                raw_message.encode("utf-8") if isinstance(raw_message, str) else canonical_json(raw_message)
            ).hexdigest()
            normalized, errors = validate_terminal_message(
                raw_message, worktree, manifest_paths
            )
            if errors:
                for code in errors:
                    contract_errors.append(
                        {
                            "code": code,
                            "session_id": document.session_id,
                            "terminal_event_id": event_id,
                        }
                    )
            else:
                normalized_results.append(normalized)
            session_result = {
                "session_id": document.session_id,
                "invocation_id": invocation.invocation_id,
                "parent_thread_id": invocation.review_parent_session_id,
                "terminal_event_id": event_id,
                "terminal_message_sha256": message_hash,
                "token_usage": last_token_usage(document),
            }
            matched_sessions.append(session_result)

    if contract_errors:
        matched_sessions.sort(
            key=lambda item: (
                item["invocation_id"],
                item["session_id"] or "",
                item["terminal_event_id"],
            )
        )
        contract_errors.sort(
            key=lambda item: (
                item["session_id"] or "",
                item["terminal_event_id"],
                item["code"],
            )
        )
        return "terminal_contract_error", [], matched_sessions, contract_errors

    deduplicated: dict[str, dict[str, Any]] = {}
    for result in normalized_results:
        for finding in result["findings"]:
            deduplicated.setdefault(finding["fingerprint"], finding)
    findings = sorted(
        deduplicated.values(),
        key=lambda item: (
            item.get("priority") if item.get("priority") is not None else 4,
            item["code_location"]["path"],
            item["code_location"]["line_range"]["start"],
            item["fingerprint"],
        ),
    )
    status = "non_clean" if findings else "clean"
    matched_sessions.sort(
        key=lambda item: (
            item["invocation_id"],
            item["session_id"] or "",
            item["terminal_event_id"],
        )
    )
    return status, findings, matched_sessions, []


def launch_codex_review(
    *,
    codex_bin: str,
    target: TargetSnapshot,
    task_id: str,
    model: str,
    effort: str,
    invocation_kind: str,
    correlation_id: str,
) -> Invocation:
    started = utc_now()
    review_instructions = build_review_instructions(target, task_id)
    review_target_arguments = (
        ["--uncommitted"]
        if target.kind == "uncommitted"
        else ["--base", target.base_revision]
    )
    command = [
        codex_bin,
        "-C",
        target.worktree,
        "--sandbox",
        "read-only",
        "-c",
        'approval_policy="never"',
        "review",
        "-c",
        f'model="{model}"',
        "-c",
        f'model_reasoning_effort="{effort}"',
        "-c",
        "developer_instructions="
        + json.dumps(review_instructions, ensure_ascii=False),
        *review_target_arguments,
        "--title",
        f"{task_id} specification review ({correlation_id})",
    ]
    with tempfile.TemporaryDirectory(prefix="codex-spec-review-") as temporary:
        stdout_path = Path(temporary) / "stdout"
        stderr_path = Path(temporary) / "stderr"
        with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
            process = subprocess.run(
                command,
                cwd=target.worktree,
                stdin=subprocess.DEVNULL,
                stdout=stdout_handle,
                stderr=stderr_handle,
                check=False,
            )
        stdout_data = stdout_path.read_bytes()
        stderr_data = stderr_path.read_bytes()
        captured = stdout_data.decode("utf-8", errors="replace")
        captured += "\n" + stderr_data.decode("utf-8", errors="replace")
    matches = SESSION_ID_RE.findall(captured)
    parent_id = matches[0] if len(matches) == 1 else None
    binding_error = None
    if not matches:
        binding_error = "missing_startup_session_id"
    elif len(matches) != 1:
        binding_error = "ambiguous_startup_session_id"
    return Invocation(
        invocation_id=str(uuid.uuid4()),
        kind=invocation_kind,
        correlation_id=correlation_id,
        started_at=started,
        completed_at=utc_now(),
        review_parent_session_id=parent_id,
        process_exit_code=process.returncode,
        stdout_bytes=len(stdout_data),
        stderr_bytes=len(stderr_data),
        stdout_sha256=hashlib.sha256(stdout_data).hexdigest(),
        stderr_sha256=hashlib.sha256(stderr_data).hexdigest(),
        binding_error=binding_error,
    )


def validate_runtime_contract(args: argparse.Namespace) -> None:
    if args.effort not in ALLOWED_EFFORTS:
        raise RunnerConfigurationError(f"unsupported reviewer effort: {args.effort}")
    if args.minimum_stable_scans < 2:
        raise RunnerConfigurationError("minimum stable scans must be at least 2")
    if not 0 < args.settle_interval_seconds <= 10:
        raise RunnerConfigurationError(
            "settle interval must satisfy 0 < interval <= 10 seconds"
        )
    if not args.settle_interval_seconds < args.settlement_timeout_seconds <= 120:
        raise RunnerConfigurationError(
            "settlement timeout must satisfy interval < timeout <= 120 seconds"
        )
    if args.technical_retry_limit != 1:
        raise RunnerConfigurationError("technical retry limit must equal 1")


def build_result(
    *,
    status: str,
    task_id: str,
    attempt_id: str,
    caller_thread_id: str | None,
    attempt_started_at: datetime,
    completed_at: datetime,
    target: TargetSnapshot,
    model: str,
    effort: str,
    invocations: list[Invocation],
    settlement: SettlementResult,
    technical_retries_used: int,
    findings: list[dict[str, Any]],
    matched_sessions: list[dict[str, Any]],
    contract_errors: list[dict[str, Any]],
    target_change_error: str | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "review_capture_contract_revision": CAPTURE_CONTRACT_REVISION,
        "status": status,
        "task_id": task_id,
        "publication_attempt_id": attempt_id,
        "caller_thread_id": caller_thread_id,
        "attempt_started_at": format_time(attempt_started_at),
        "completed_at": format_time(completed_at),
        "wall_time_seconds": round((completed_at - attempt_started_at).total_seconds(), 3),
        "technical_retry_limit": 1,
        "technical_retries_used": technical_retries_used,
        "review_target": target.as_result(),
        "reviewer": {"model": model, "effort": effort},
        "invocations": [invocation.as_result() for invocation in invocations],
        "settlement": settlement.as_result(),
        "matched_sessions": matched_sessions,
        "cumulative_token_usage": cumulative_token_usage(matched_sessions),
        "findings": findings,
        "diagnostics": {
            "process_exit_codes": [item.process_exit_code for item in invocations],
            "outer_stdout_truncated_or_unknown": any(
                item.stdout_sha256 is None or item.stderr_sha256 is None
                for item in invocations
            ),
            "binding_errors": settlement.bound.binding_errors,
            "terminal_contract_errors": contract_errors,
            "target_change_error": target_change_error,
        },
    }
    result["normalized_result_sha256"] = sha256_json(result)
    return result


def execute(
    args: argparse.Namespace,
    *,
    launcher: Callable[..., Invocation] = launch_codex_review,
) -> dict[str, Any]:
    validate_runtime_contract(args)
    target_before = build_target_snapshot(
        args.worktree, args.target_kind, args.base, args.head
    )
    sessions_root = Path(args.sessions_root).expanduser().resolve()
    attempt_started = utc_now()
    attempt_id = str(uuid.uuid4())
    invocations: list[Invocation] = []
    technical_retries_used = 0
    settlement: SettlementResult | None = None
    status = "invocation_binding_error"
    findings: list[dict[str, Any]] = []
    matched_sessions: list[dict[str, Any]] = []
    contract_errors: list[dict[str, Any]] = []
    target_change_error: str | None = None

    for invocation_kind in ("initial", "technical_retry"):
        if invocation_kind == "technical_retry":
            technical_retries_used += 1
        correlation_id = str(uuid.uuid4())
        invocation = launcher(
            codex_bin=args.codex_bin,
            target=target_before,
            task_id=args.task_id,
            model=args.model,
            effort=args.effort,
            invocation_kind=invocation_kind,
            correlation_id=correlation_id,
        )
        invocations.append(invocation)
        if invocation.binding_error:
            now = utc_now()
            empty_bound = bind_sessions([], invocations, target_before.worktree)
            empty_bound.binding_errors.append(
                {
                    "code": invocation.binding_error,
                    "invocation_id": invocation.invocation_id,
                }
            )
            settlement = SettlementResult(
                status="invocation_binding_error",
                started_at=now,
                completed_at=now,
                stable_scans_observed=0,
                last_change_observed_at=now,
                final_rescan_at=now,
                bound=empty_bound,
            )
            status = "invocation_binding_error"
            break
        settlement = settle_sessions(
            sessions_root,
            attempt_started,
            invocations,
            target_before.worktree,
            minimum_stable_scans=args.minimum_stable_scans,
            settle_interval_seconds=args.settle_interval_seconds,
            settlement_timeout_seconds=args.settlement_timeout_seconds,
        )
        if settlement.status in {
            "invocation_binding_error",
            "session_settlement_timeout",
        }:
            status = settlement.status
            break
        if settlement.status == "no_authoritative_terminal_result":
            if technical_retries_used < args.technical_retry_limit:
                continue
            status = "technical_retry_budget_exhausted"
            break
        status, findings, matched_sessions, contract_errors = consolidate_terminal_results(
            settlement.bound, target_before
        )
        break

    if settlement is None:
        raise AssertionError("runner exited without settlement evidence")
    try:
        target_after = build_target_snapshot(
            args.worktree, args.target_kind, args.base, args.head
        )
    except RunnerConfigurationError as error:
        status = "target_changed"
        findings = []
        target_change_error = str(error)
    else:
        if target_after.state_fingerprint != target_before.state_fingerprint:
            status = "target_changed"
            findings = []

    completed = utc_now()
    return build_result(
        status=status,
        task_id=args.task_id,
        attempt_id=attempt_id,
        caller_thread_id=args.caller_thread_id,
        attempt_started_at=attempt_started,
        completed_at=completed,
        target=target_before,
        model=args.model,
        effort=args.effort,
        invocations=invocations,
        settlement=settlement,
        technical_retries_used=technical_retries_used,
        findings=findings,
        matched_sessions=matched_sessions,
        contract_errors=contract_errors,
        target_change_error=target_change_error,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Codex spec review and normalize authoritative child-session evidence."
    )
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--target-kind", required=True, choices=sorted(ALLOWED_TARGET_KINDS))
    parser.add_argument("--base", required=True)
    parser.add_argument("--head")
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", required=True, choices=sorted(ALLOWED_EFFORTS))
    parser.add_argument("--caller-thread-id", default=os.environ.get("CODEX_THREAD_ID"))
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--sessions-root", default=str(default_sessions_root()))
    parser.add_argument("--minimum-stable-scans", type=int, default=2)
    parser.add_argument("--settle-interval-seconds", type=float, default=2.0)
    parser.add_argument("--settlement-timeout-seconds", type=float, default=30.0)
    parser.add_argument("--technical-retry-limit", type=int, default=1)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = execute(args)
    except RunnerConfigurationError as error:
        print(f"configuration error: {error}", file=sys.stderr)
        return 64
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return EXIT_BY_STATUS[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
