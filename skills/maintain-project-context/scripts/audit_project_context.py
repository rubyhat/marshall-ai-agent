#!/usr/bin/env python3
"""Read-only project-context inventory and candidate-signal audit."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import unquote


MIN_PYTHON = (3, 9)
DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".next",
    ".turbo",
    ".venv",
    "build",
    "coverage",
    "dist",
    "log",
    "node_modules",
    "tmp",
    "vendor",
}
TEXT_EXTENSIONS = {
    ".md",
    ".markdown",
    ".mdx",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".csv",
    ".tsv",
}
TASK_ID_TOKEN_WRAPPERS = "`*_[](){}<>.,:;!?\"'"
DATED_HEADING_RE = re.compile(r"^\s*#{1,6}\s+.*\b20\d{2}-\d{2}-\d{2}\b", re.I)
MARKDOWN_HEADING_RE = re.compile(r"^\s*(#{1,6})\s+\S")
MARKDOWN_SETEXT_RE = re.compile(r"^[ ]{0,3}(=+|-+)[ \t]*$")
MARKDOWN_FENCE_RE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})")
MARKDOWN_FRONT_MATTER_START_RE = re.compile(r"^\ufeff?---[ \t]*(?:\r?\n)?$")
MARKDOWN_FRONT_MATTER_END_RE = re.compile(r"^(?:---|\.\.\.)[ \t]*(?:\r?\n)?$")
UNRESOLVED_RE = re.compile(
    r"\b(?:TODO|FIXME|BLOCKED|UNRESOLVED|OPEN QUESTION|PENDING)\b|"
    r"\b(?:блокер|заблокирован|нереш[её]н|открыт(?:ый|ые)? вопрос)\w*",
    re.I,
)
SUPERSEDED_RE = re.compile(
    r"\b(?:superseded|deprecated|obsolete|replaced by)\b|"
    r"\b(?:устарел\w*|замен[её]н\w*|больше не актуал\w*)",
    re.I,
)
STATUS_RE = re.compile(
    r"\b(?:merged|completed|complete|done|closed|cancelled|canceled)\b|"
    r"\b(?:заверш[её]н\w*|выполнен\w*|закрыт\w*|отмен[её]н\w*|слит\w*)",
    re.I,
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_LINK_LABEL_RE = re.compile(r"!?\[([^\]]+)\]\([^)]+\)")
SUPERSESSION_FIELD_RE = re.compile(
    r"^\s*(?:[-*]\s*)?superseded by\s*:\s*(.*?)\s*$",
    re.I,
)
EMPTY_SUPERSESSION_VALUES = {
    "",
    "none",
    "n/a",
    "na",
    "not applicable",
    "adr link or none",
}


@dataclass
class AuditFile:
    absolute_path: Path
    relative_path: str
    scope: str
    size: int
    modified_at: str
    age_days: int
    location_state: str
    protected: bool
    binary: bool
    git_state: str = "not_checked"
    line_count: Optional[int] = None
    nonblank_lines: Optional[int] = None
    markdown_heading_count: int = 0
    task_heading_count: int = 0
    task_id_count: int = 0
    max_section_lines: int = 0
    dated_heading_count: int = 0
    unresolved_marker_count: int = 0
    superseded_marker_count: int = 0
    completed_marker_count: int = 0
    status_only_signal: bool = False
    task_ids: List[str] = field(default_factory=list)
    broken_targets: List[str] = field(default_factory=list)
    incoming_link_count: int = 0
    duplicate_group: Optional[str] = None
    fingerprint: Optional[str] = None


def fail(message: str, code: int = 2) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def parse_age_buckets(raw: str) -> List[int]:
    try:
        values = sorted({int(value.strip()) for value in raw.split(",") if value.strip()})
    except ValueError:
        fail("--age-buckets must contain comma-separated integers")
    if not values or any(value <= 0 for value in values):
        fail("--age-buckets values must be positive")
    return values


def compile_task_id_pattern(raw: Optional[str]) -> Optional[re.Pattern]:
    if not raw:
        return None
    try:
        return re.compile(raw)
    except re.error as error:
        fail(f"--task-id-regex is invalid: {error}")
    return None


def configured_task_ids(
    line: str, task_id_pattern: Optional[re.Pattern]
) -> Set[str]:
    if task_id_pattern is None:
        return set()
    # Inspect visible inline-link labels separately. Splitting the raw Markdown
    # alone leaves the destination attached to identifiers such as
    # ``[TASK_123](https://tracker/123)`` and prevents an exact fullmatch.
    candidate_sources = [line, *MARKDOWN_LINK_LABEL_RE.findall(line)]
    candidates = {
        raw.strip(TASK_ID_TOKEN_WRAPPERS)
        for source in candidate_sources
        for raw in source.split()
    }
    return {
        candidate
        for candidate in candidates
        if candidate and task_id_pattern.fullmatch(candidate)
    }


def resolve_inside(root: Path, raw: str, label: str, require_exists: bool) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    lexical = Path(os.path.abspath(str(candidate)))
    try:
        lexical_relative = lexical.relative_to(root)
    except ValueError:
        fail(f"{label} is outside --root: {raw}")
    cursor = root
    for part in lexical_relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            fail(f"{label} crosses a symlink boundary: {raw}")
    candidate = candidate.resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError:
        fail(f"{label} is outside --root: {raw}")
    if require_exists and not candidate.exists():
        fail(f"{label} does not exist: {raw}")
    return candidate


def contains(path: Path, roots: Sequence[Path]) -> bool:
    for root in roots:
        if path == root or root in path.parents:
            return True
    return False


def secret_like(path: Path) -> bool:
    name = path.name.lower()
    if name == ".env" or name.startswith(".env."):
        return True
    if name in {"id_rsa", "id_ed25519", "credentials.json", "secrets.json"}:
        return True
    if path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
        return True
    return bool(re.fullmatch(r"(?:secret|secrets|credentials)\.(?:json|ya?ml|toml)", name))


def looks_binary(path: Path) -> bool:
    if path.stat().st_size == 0:
        return False
    with path.open("rb") as handle:
        sample = handle.read(8192)
    return b"\x00" in sample


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_scope_files(
    scope: Path, excluded_dirs: Set[str]
) -> Iterable[Path]:
    if scope.is_symlink():
        return
    if scope.is_file():
        yield scope
        return
    for directory, dirnames, filenames in os.walk(scope, followlinks=False):
        current = Path(directory)
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in excluded_dirs and not (current / name).is_symlink()
        )
        for filename in sorted(filenames):
            path = current / filename
            if not path.is_symlink() and path.is_file():
                yield path


def location_state(
    path: Path,
    active_roots: Sequence[Path],
    canonical_roots: Sequence[Path],
    protected_roots: Sequence[Path],
    historical_roots: Sequence[Path],
    archive_roots: Sequence[Path],
) -> str:
    # Canonical and active are the primary lifecycle roles. Safety remains
    # independently visible through AuditFile.protected, so an overlapping
    # protected root must not hide lifecycle-specific diagnostic signals.
    if contains(path, canonical_roots):
        return "canonical"
    if contains(path, active_roots):
        return "active"
    if contains(path, protected_roots):
        return "protected"
    if contains(path, archive_roots):
        return "archive"
    if contains(path, historical_roots):
        return "historical"
    return "unclassified"


def run_git(root: Path, args: Sequence[str]) -> Optional[bytes]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def git_inventory(root: Path) -> Tuple[bool, Set[str], Dict[str, str]]:
    inside = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    if inside is None or inside.strip() != b"true":
        return False, set(), {}

    tracked_raw = run_git(root, ["ls-files", "-z"])
    status_raw = run_git(root, ["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    if tracked_raw is None or status_raw is None:
        return False, set(), {}

    tracked = {
        entry.decode("utf-8", errors="surrogateescape")
        for entry in tracked_raw.split(b"\0")
        if entry
    }
    status: Dict[str, str] = {}
    entries = status_raw.split(b"\0")
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        decoded = entry.decode("utf-8", errors="surrogateescape")
        if len(decoded) < 4:
            continue
        code = decoded[:2]
        path = decoded[3:]
        status[path] = "untracked" if code == "??" else f"modified:{code}"
        if "R" in code or "C" in code:
            if index < len(entries) and entries[index]:
                original = entries[index].decode("utf-8", errors="surrogateescape")
                status[original] = f"modified:{code}"
                index += 1
    return True, tracked, status


def normalize_link_target(root: Path, source: Path, raw_target: str) -> Optional[Path]:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    target = unquote(target.split("#", 1)[0].strip())
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:")):
        return None
    if any(token in target for token in ("<", ">", "{", "}", "$")):
        return None
    candidate = root / target.lstrip("/") if target.startswith("/") else source.parent / target
    candidate = candidate.resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def inspect_text(
    item: AuditFile,
    root: Path,
    task_id_pattern: Optional[re.Pattern],
) -> Set[Path]:
    links: Set[Path] = set()
    task_ids: Set[str] = set()
    line_count = 0
    nonblank = 0
    open_sections: List[Tuple[int, int]] = []
    markdown = item.absolute_path.suffix.lower() in {".md", ".markdown", ".mdx"}
    root_block_start: Optional[int] = 1 if markdown else None
    fence_character: Optional[str] = None
    fence_length = 0
    front_matter_open = False
    previous_setext_candidate: Optional[Tuple[int, str, Set[str]]] = None

    def register_heading(
        heading_level: int,
        heading_start: int,
        heading_task_ids: Set[str],
    ) -> None:
        nonlocal root_block_start
        while open_sections and open_sections[-1][0] >= heading_level:
            _, section_start = open_sections.pop()
            item.max_section_lines = max(
                item.max_section_lines, heading_start - section_start
            )
        # Treat content before H2+ and after every H1 as bounded root blocks.
        # H2+ sections include nested descendants without degenerating the
        # metric into the whole document length.
        if heading_level == 1:
            if root_block_start is not None:
                item.max_section_lines = max(
                    item.max_section_lines, heading_start - root_block_start
                )
            root_block_start = heading_start
        else:
            if root_block_start is not None:
                item.max_section_lines = max(
                    item.max_section_lines, heading_start - root_block_start
                )
                root_block_start = None
            open_sections.append((heading_level, heading_start))
        item.markdown_heading_count += 1
        # Only a project-validated identifier can prove that a heading belongs
        # to task chronology.
        if task_id_pattern is not None and heading_task_ids:
            item.task_heading_count += 1

    with item.absolute_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line_count += 1
            if line.strip():
                nonblank += 1
            if markdown:
                if line_count == 1 and MARKDOWN_FRONT_MATTER_START_RE.match(line):
                    front_matter_open = True
                    previous_setext_candidate = None
                    continue
                if front_matter_open:
                    if MARKDOWN_FRONT_MATTER_END_RE.match(line):
                        front_matter_open = False
                    previous_setext_candidate = None
                    continue
                fence_match = MARKDOWN_FENCE_RE.match(line)
                if fence_character is not None:
                    if (
                        fence_match
                        and fence_match.group(1)[0] == fence_character
                        and len(fence_match.group(1)) >= fence_length
                    ):
                        fence_character = None
                        fence_length = 0
                    previous_setext_candidate = None
                    continue
                if fence_match:
                    fence_character = fence_match.group(1)[0]
                    fence_length = len(fence_match.group(1))
                    previous_setext_candidate = None
                    continue
                if line.startswith("\t") or line.startswith("    "):
                    previous_setext_candidate = None
                    continue

            line_task_ids = configured_task_ids(line, task_id_pattern)
            task_ids.update(line_task_ids)
            heading_match = MARKDOWN_HEADING_RE.search(line) if markdown else None
            setext_match = MARKDOWN_SETEXT_RE.match(line) if markdown else None
            if heading_match:
                heading_level = len(heading_match.group(1))
                register_heading(heading_level, line_count, line_task_ids)
            elif setext_match and previous_setext_candidate is not None:
                heading_start, heading_text, heading_task_ids = previous_setext_candidate
                heading_level = 1 if setext_match.group(1).startswith("=") else 2
                register_heading(heading_level, heading_start, heading_task_ids)
                if re.search(r"\b20\d{2}-\d{2}-\d{2}\b", heading_text):
                    item.dated_heading_count += 1
            if heading_match and DATED_HEADING_RE.search(line):
                item.dated_heading_count += 1
            item.unresolved_marker_count += len(UNRESOLVED_RE.findall(line))
            supersession_field = SUPERSESSION_FIELD_RE.match(line)
            if supersession_field:
                value = supersession_field.group(1).strip().strip("`<>").strip().lower()
                if value not in EMPTY_SUPERSESSION_VALUES:
                    item.superseded_marker_count += 1
            else:
                item.superseded_marker_count += len(SUPERSEDED_RE.findall(line))
            item.completed_marker_count += len(STATUS_RE.findall(line))
            for raw_target in MARKDOWN_LINK_RE.findall(line):
                normalized = normalize_link_target(root, item.absolute_path, raw_target)
                if normalized is not None:
                    links.add(normalized)
            if markdown:
                is_candidate = bool(
                    line.strip()
                    and heading_match is None
                    and setext_match is None
                )
                previous_setext_candidate = (
                    (line_count, line.rstrip("\r\n"), line_task_ids)
                    if is_candidate
                    else None
                )
    for _, section_start in open_sections:
        item.max_section_lines = max(
            item.max_section_lines, line_count - section_start + 1
        )
    if root_block_start is not None and line_count:
        item.max_section_lines = max(
            item.max_section_lines, line_count - root_block_start + 1
        )
    if item.markdown_heading_count and not item.max_section_lines:
        item.max_section_lines = line_count
    item.line_count = line_count
    item.nonblank_lines = nonblank
    item.status_only_signal = bool(item.completed_marker_count and nonblank <= 40)
    item.task_id_count = len(task_ids)
    item.task_ids = sorted(task_ids)[:20]
    return links


def age_distribution(files: Sequence[AuditFile], buckets: Sequence[int]) -> Dict[str, int]:
    counts: Counter = Counter()
    for item in files:
        lower = 0
        placed = False
        for upper in buckets:
            if item.age_days < upper:
                label = f"<{upper}" if lower == 0 else f"{lower}-{upper - 1}"
                counts[label] += 1
                placed = True
                break
            lower = upper
        if not placed:
            counts[f">={buckets[-1]}"] += 1
    ordered: Dict[str, int] = {}
    lower = 0
    for upper in buckets:
        label = f"<{upper}" if lower == 0 else f"{lower}-{upper - 1}"
        ordered[label] = counts[label]
        lower = upper
    ordered[f">={buckets[-1]}"] = counts[f">={buckets[-1]}"]
    return ordered


def candidate_hints(item: AuditFile) -> List[str]:
    hints: List[str] = []
    if item.size == 0:
        hints.append("empty_file")
    if item.duplicate_group:
        hints.append("exact_duplicate")
    if item.broken_targets:
        hints.append("possible_broken_reference")
    if item.status_only_signal:
        hints.append("status_only_signal")
    if item.superseded_marker_count:
        hints.append("superseded_signal")
    if item.task_heading_count and item.location_state in {"active", "canonical"}:
        hints.append("task_chronology_signal")
    if item.dated_heading_count >= 2 and item.location_state in {"active", "canonical"}:
        hints.append("dated_chronology_signal")
    lifecycle_categories = sum(
        bool(value)
        for value in (
            item.unresolved_marker_count,
            item.superseded_marker_count,
            item.completed_marker_count,
        )
    )
    if lifecycle_categories >= 2 and item.location_state in {"active", "canonical"}:
        hints.append("mixed_lifecycle_signal")
    if hints and item.unresolved_marker_count:
        hints.append("unresolved_markers_present")
    if hints and item.location_state in {"active", "canonical", "protected"}:
        hints.append(f"{item.location_state}_location")
    if hints and item.git_state in {"untracked"}:
        hints.append("untracked_git_state")
    if hints and item.git_state.startswith("modified:"):
        hints.append("modified_git_state")
    return hints


def file_summary(item: AuditFile, hints: Optional[List[str]] = None) -> Dict[str, object]:
    data: Dict[str, object] = {
        "path": item.relative_path,
        "scope": item.scope,
        "bytes": item.size,
        "modified_at": item.modified_at,
        "age_days": item.age_days,
        "location_state": item.location_state,
        "protected": item.protected,
        "git_state": item.git_state,
    }
    if item.line_count is not None:
        data.update(
            {
                "lines": item.line_count,
                "markdown_headings": item.markdown_heading_count,
                "task_headings": item.task_heading_count,
                "task_heading_ratio": (
                    round(item.task_heading_count / item.markdown_heading_count, 4)
                    if item.markdown_heading_count
                    else 0.0
                ),
                "max_section_lines": item.max_section_lines,
                "dated_headings": item.dated_heading_count,
                "unresolved_markers": item.unresolved_marker_count,
                "superseded_markers": item.superseded_marker_count,
                "completed_markers": item.completed_marker_count,
                "task_id_count": item.task_id_count,
                "task_ids": item.task_ids,
                "incoming_links": item.incoming_link_count,
                "broken_targets": item.broken_targets,
            }
        )
    if item.duplicate_group:
        data["duplicate_group"] = item.duplicate_group
    if hints is not None:
        data["review_hints"] = hints
        data["review_category_hint"] = (
            "broken_reference" if "possible_broken_reference" in hints else "needs_human_decision"
        )
        data["sha256"] = item.fingerprint
    return data


def build_report(args: argparse.Namespace) -> Dict[str, object]:
    root = Path(args.root).expanduser().resolve(strict=True)
    if not root.is_dir():
        fail("--root must be a directory")

    scopes = [resolve_inside(root, raw, "--scope", True) for raw in args.scope]
    active_roots = [resolve_inside(root, raw, "--active-root", False) for raw in args.active_root]
    canonical_roots = [resolve_inside(root, raw, "--canonical", False) for raw in args.canonical]
    protected_roots = [resolve_inside(root, raw, "--protected", False) for raw in args.protected]
    historical_roots = [
        resolve_inside(root, raw, "--historical-root", False) for raw in args.historical_root
    ]
    archive_roots = [resolve_inside(root, raw, "--archive-root", False) for raw in args.archive_root]
    task_id_pattern = compile_task_id_pattern(args.task_id_regex)
    excluded_dirs = DEFAULT_EXCLUDED_DIRS | set(args.exclude_dir)
    now = datetime.now(timezone.utc)

    git_available = False
    tracked: Set[str] = set()
    git_status: Dict[str, str] = {}
    if args.include_git_state:
        git_available, tracked, git_status = git_inventory(root)

    files: List[AuditFile] = []
    seen: Set[Path] = set()
    skipped = Counter()
    scope_counts: Dict[str, Counter] = defaultdict(Counter)

    for scope in scopes:
        scope_label = scope.relative_to(root).as_posix() or "."
        for path in iter_scope_files(scope, excluded_dirs):
            resolved = path.resolve(strict=False)
            if resolved in seen:
                continue
            seen.add(resolved)
            if secret_like(path):
                skipped["secret_like"] += 1
                continue
            try:
                stat = path.stat()
                binary = looks_binary(path)
            except (OSError, PermissionError):
                skipped["unreadable"] += 1
                continue
            if binary:
                skipped["binary"] += 1
                continue
            relative = path.relative_to(root).as_posix()
            state = location_state(
                path.resolve(strict=False),
                active_roots,
                canonical_roots,
                protected_roots,
                historical_roots,
                archive_roots,
            )
            age_days = max(0, int((now.timestamp() - stat.st_mtime) // 86400))
            item = AuditFile(
                absolute_path=path,
                relative_path=relative,
                scope=scope_label,
                size=stat.st_size,
                modified_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                age_days=age_days,
                location_state=state,
                protected=state in {"protected", "canonical", "active"},
                binary=False,
            )
            if args.include_git_state and git_available:
                item.git_state = git_status.get(
                    relative, "tracked_clean" if relative in tracked else "not_tracked"
                )
            files.append(item)
            scope_counts[scope_label]["files"] += 1
            scope_counts[scope_label]["bytes"] += stat.st_size

    links_by_source: Dict[str, Set[Path]] = {}
    incoming: Counter = Counter()
    if args.include_content_signals:
        for item in files:
            if item.absolute_path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                targets = inspect_text(item, root, task_id_pattern)
            except (OSError, PermissionError):
                skipped["content_unreadable"] += 1
                continue
            links_by_source[item.relative_path] = targets
            for target in targets:
                incoming[target] += 1
        for item in files:
            item.incoming_link_count = incoming[item.absolute_path.resolve(strict=False)]
            broken = [
                target.relative_to(root).as_posix()
                for target in links_by_source.get(item.relative_path, set())
                if not target.exists()
            ]
            item.broken_targets = sorted(broken)[:20]

    same_size: Dict[int, List[AuditFile]] = defaultdict(list)
    for item in files:
        if item.size > 0:
            same_size[item.size].append(item)
    duplicate_groups: List[Dict[str, object]] = []
    for size, group in same_size.items():
        if len(group) < 2:
            continue
        hashes: Dict[str, List[AuditFile]] = defaultdict(list)
        for item in group:
            try:
                hashes[hash_file(item.absolute_path)].append(item)
            except (OSError, PermissionError):
                skipped["hash_unreadable"] += 1
        for digest, matches in hashes.items():
            if len(matches) < 2:
                continue
            group_id = digest[:12]
            paths = sorted(item.relative_path for item in matches)
            for item in matches:
                item.duplicate_group = group_id
            duplicate_groups.append(
                {"id": group_id, "sha256": digest, "bytes_each": size, "paths": paths}
            )
    duplicate_groups.sort(key=lambda group: (-int(group["bytes_each"]), str(group["id"])))

    candidate_rows: List[Tuple[AuditFile, List[str]]] = []
    for item in files:
        hints = candidate_hints(item)
        if hints:
            try:
                item.fingerprint = hash_file(item.absolute_path)
            except (OSError, PermissionError):
                item.fingerprint = None
                hints.append("fingerprint_unavailable")
            candidate_rows.append((item, hints))
    candidate_rows.sort(
        key=lambda row: (
            0 if "possible_broken_reference" in row[1] else 1,
            -row[0].size,
            row[0].relative_path,
        )
    )

    total_candidates = len(candidate_rows)
    selected_candidates = (
        candidate_rows if args.candidate_limit == 0 else candidate_rows[: args.candidate_limit]
    )
    largest = sorted(files, key=lambda item: (-item.size, item.relative_path))[: args.top]
    shown_duplicates = duplicate_groups[: args.top]

    report: Dict[str, object] = {
        "schema_version": 2,
        "generated_at": now.isoformat(),
        "read_only": True,
        "root": str(root),
        "scopes": [scope.relative_to(root).as_posix() or "." for scope in scopes],
        "options": {
            "content_signals": args.include_content_signals,
            "git_state": args.include_git_state,
            "age_buckets": args.age_buckets,
            "top": args.top,
            "candidate_limit": args.candidate_limit,
            "task_id_regex_configured": task_id_pattern is not None,
        },
        "summary": {
            "files": len(files),
            "bytes": sum(item.size for item in files),
            "lines": (
                sum(item.line_count or 0 for item in files)
                if args.include_content_signals
                else None
            ),
            "candidate_signals": total_candidates,
            "candidate_signals_shown": len(selected_candidates),
            "exact_duplicate_groups": len(duplicate_groups),
            "possible_broken_references": sum(bool(item.broken_targets) for item in files),
            "skipped": dict(sorted(skipped.items())),
            "git_available": git_available if args.include_git_state else None,
        },
        "by_scope": {
            scope: {"files": counts["files"], "bytes": counts["bytes"]}
            for scope, counts in sorted(scope_counts.items())
        },
        "by_location_state": dict(sorted(Counter(item.location_state for item in files).items())),
        "age_distribution_days": age_distribution(files, args.age_buckets),
        "largest_files": [file_summary(item) for item in largest],
        "exact_duplicate_groups": shown_duplicates,
        "candidates": [
            file_summary(item, hints=hints) for item, hints in selected_candidates
        ],
        "notice": (
            "No files were changed. Candidate signals require semantic review; "
            "age and size alone never authorize cleanup."
        ),
    }
    return report


def format_bytes(value: int) -> str:
    units = ["B", "KiB", "MiB", "GiB"]
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{value} B"


def print_text(report: Dict[str, object]) -> None:
    summary = report["summary"]
    print("Project context audit (read-only)")
    print(f"Root: {report['root']}")
    print(f"Scopes: {', '.join(report['scopes'])}")
    line_part = f", lines={summary['lines']}" if summary["lines"] is not None else ""
    print(
        f"Files: {summary['files']}, size={format_bytes(summary['bytes'])}{line_part}, "
        f"candidate signals={summary['candidate_signals']}"
    )
    print(f"Location states: {json.dumps(report['by_location_state'], ensure_ascii=False)}")
    print(f"Age buckets (days): {json.dumps(report['age_distribution_days'])}")
    if summary["skipped"]:
        print(f"Skipped: {json.dumps(summary['skipped'], ensure_ascii=False)}")

    print("Largest files:")
    for item in report["largest_files"]:
        structure = ""
        if "markdown_headings" in item:
            structure = (
                f" [headings={item['markdown_headings']}, "
                f"task_headings={item['task_headings']}, "
                f"max_section_lines={item['max_section_lines']}]"
            )
        print(f"  {format_bytes(item['bytes']):>10}  {item['path']}{structure}")

    print("Exact duplicate groups:")
    groups = report["exact_duplicate_groups"]
    if not groups:
        print("  none")
    for group in groups:
        print(f"  {group['id']} ({format_bytes(group['bytes_each'])} each)")
        for path in group["paths"]:
            print(f"    {path}")

    print("Candidate signals:")
    candidates = report["candidates"]
    if not candidates:
        print("  none")
    for item in candidates:
        hints = ", ".join(item["review_hints"])
        print(f"  {item['path']} [{hints}]")
    shown = summary["candidate_signals_shown"]
    total = summary["candidate_signals"]
    if shown < total:
        print(f"  ... {total - shown} more; use --candidate-limit 0 to show all")
    print(report["notice"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only inventory of explicit project-context scopes. "
            "It emits signals, not deletion decisions."
        )
    )
    parser.add_argument("--root", required=True, help="Workspace root")
    parser.add_argument(
        "--scope", action="append", required=True, help="File or directory to audit; repeatable"
    )
    parser.add_argument("--active-root", action="append", default=[], help="Active-context root")
    parser.add_argument("--canonical", action="append", default=[], help="Canonical path")
    parser.add_argument("--protected", action="append", default=[], help="Protected path")
    parser.add_argument(
        "--historical-root", action="append", default=[], help="Historical-context root"
    )
    parser.add_argument("--archive-root", action="append", default=[], help="Archive root")
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Additional directory basename to skip",
    )
    parser.add_argument(
        "--include-content-signals",
        action="store_true",
        help="Count lines and inspect bounded semantic/link signals without printing content",
    )
    parser.add_argument(
        "--include-git-state",
        action="store_true",
        help="Report tracked, modified, and untracked state when root is a Git worktree",
    )
    parser.add_argument(
        "--task-id-regex",
        help=(
            "Optional project validation regex applied with fullmatch to neutral "
            "identifier tokens"
        ),
    )
    parser.add_argument(
        "--age-buckets",
        default="30,90,180",
        help="Comma-separated display buckets in days; never deletion thresholds",
    )
    parser.add_argument("--top", type=int, default=20, help="Maximum summary rows")
    parser.add_argument(
        "--candidate-limit",
        type=int,
        default=50,
        help="Maximum candidate-signal rows; 0 shows all",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main() -> None:
    if sys.version_info < MIN_PYTHON:
        fail("Python 3.9 or newer is required", code=1)
    parser = build_parser()
    args = parser.parse_args()
    if args.top < 0 or args.candidate_limit < 0:
        fail("--top and --candidate-limit must be zero or greater")
    args.age_buckets = parse_age_buckets(args.age_buckets)
    report = build_report(args)
    if args.format == "json":
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        print_text(report)


if __name__ == "__main__":
    main()
