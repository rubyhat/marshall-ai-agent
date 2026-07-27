#!/usr/bin/env python3
"""Collect a read-only, bounded snapshot of one GitHub Codex review request."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


DEFAULT_CLEAN_PATTERNS = (
    "codex review: didn't find any major issues.",
    "codex review: did not find any major issues.",
)
DEFAULT_ERROR_PATTERNS = (
    "codex review: something went wrong",
    "try again later by commenting",
    "you don't have the ability to clone this repository",
)
DEFAULT_ACK_REACTIONS = ("eyes", "+1")
DEFAULT_BODY_LIMIT = 1200


class InspectionError(RuntimeError):
    """Raised when the evidence snapshot cannot be collected safely."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect one exact GitHub Codex review request without mutating GitHub."
        )
    )
    parser.add_argument("--repo", help="GitHub repository in OWNER/REPO form.")
    parser.add_argument("--pr", type=int, help="Pull request number.")
    parser.add_argument(
        "--request-comment-id",
        type=int,
        required=True,
        help="Exact issue-comment ID containing the current review request.",
    )
    parser.add_argument(
        "--requested-at",
        help="ISO-8601 request timestamp. Defaults to request comment created_at.",
    )
    parser.add_argument(
        "--head-sha",
        help="Persisted head SHA for the current generation.",
    )
    parser.add_argument(
        "--reviewer-login",
        action="append",
        default=[],
        help="Exact reviewer login. Repeat for multiple identities.",
    )
    parser.add_argument(
        "--reviewer-login-contains",
        action="append",
        default=[],
        help="Case-insensitive reviewer-login substring. Defaults to 'codex'.",
    )
    parser.add_argument(
        "--ack-reaction",
        action="append",
        default=[],
        help="Allowed GitHub reaction content. Defaults to eyes and +1.",
    )
    parser.add_argument(
        "--clean-pattern",
        action="append",
        default=[],
        help="Case-insensitive clean-verdict substring.",
    )
    parser.add_argument(
        "--error-pattern",
        action="append",
        default=[],
        help="Case-insensitive explicit-error substring.",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=50,
        help="Maximum normalized events returned per group.",
    )
    parser.add_argument(
        "--body-limit",
        type=int,
        default=DEFAULT_BODY_LIMIT,
        help="Maximum response body characters retained in output.",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        help="Read fixture JSON instead of calling gh; intended for tests.",
    )
    return parser.parse_args()


def parse_timestamp(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise InspectionError(f"Invalid ISO-8601 timestamp: {value}") from exc
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def run_gh(endpoint: str, *, paginated: bool = False) -> Any:
    command = ["gh", "api", endpoint]
    if paginated:
        command.extend(["--paginate", "--slurp"])
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise InspectionError(f"Cannot execute gh: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise InspectionError(f"gh api failed for {endpoint}: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise InspectionError(f"gh api returned invalid JSON for {endpoint}") from exc
    if not paginated:
        return payload
    if not isinstance(payload, list):
        raise InspectionError(f"Expected paginated list for {endpoint}")
    if payload and all(isinstance(page, list) for page in payload):
        return [item for page in payload for item in page]
    return payload


def load_evidence(args: argparse.Namespace) -> dict[str, Any]:
    if args.fixture:
        try:
            payload = json.loads(args.fixture.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise InspectionError(f"Cannot read fixture {args.fixture}: {exc}") from exc
        required = {
            "pull_request",
            "request_comment",
            "reactions",
            "issue_comments",
            "reviews",
            "inline_comments",
        }
        missing = sorted(required.difference(payload))
        if missing:
            raise InspectionError(f"Fixture is missing keys: {', '.join(missing)}")
        return payload

    if not args.repo or not args.pr:
        raise InspectionError("--repo and --pr are required without --fixture")
    base = f"repos/{args.repo}"
    return {
        "pull_request": run_gh(f"{base}/pulls/{args.pr}"),
        "request_comment": run_gh(
            f"{base}/issues/comments/{args.request_comment_id}"
        ),
        "reactions": run_gh(
            f"{base}/issues/comments/{args.request_comment_id}/reactions?per_page=100",
            paginated=True,
        ),
        "issue_comments": run_gh(
            f"{base}/issues/{args.pr}/comments?per_page=100",
            paginated=True,
        ),
        "reviews": run_gh(
            f"{base}/pulls/{args.pr}/reviews?per_page=100",
            paginated=True,
        ),
        "inline_comments": run_gh(
            f"{base}/pulls/{args.pr}/comments?per_page=100",
            paginated=True,
        ),
    }


def actor_login(item: dict[str, Any]) -> str:
    user = item.get("user") or {}
    return str(user.get("login") or "")


def is_reviewer(
    login: str,
    *,
    exact_logins: set[str],
    login_fragments: tuple[str, ...],
) -> bool:
    folded = login.casefold()
    if folded in exact_logins:
        return True
    return any(fragment in folded for fragment in login_fragments)


def event_timestamp(item: dict[str, Any], channel: str) -> str | None:
    candidates = (
        ("submitted_at", "created_at", "updated_at")
        if channel == "formal_review"
        else ("created_at", "submitted_at", "updated_at")
    )
    for key in candidates:
        value = item.get(key)
        if value:
            return str(value)
    return None


def body_digest(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def normalize_event(
    item: dict[str, Any],
    channel: str,
    *,
    body_limit: int,
) -> dict[str, Any]:
    body = str(item.get("body") or "")
    timestamp = event_timestamp(item, channel)
    return {
        "channel": channel,
        "id": item.get("id"),
        "actor": actor_login(item),
        "created_at": timestamp,
        "url": item.get("html_url"),
        "state": item.get("state"),
        "path": item.get("path"),
        "line": item.get("line") or item.get("original_line"),
        "commit_id": item.get("commit_id"),
        "body": body[:body_limit],
        "body_truncated": len(body) > body_limit,
        "body_sha256": body_digest(body),
    }


def current_events(
    items: Iterable[dict[str, Any]],
    channel: str,
    requested_at: datetime,
    *,
    body_limit: int,
    request_comment_id: int,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in items:
        if channel == "issue_comment" and item.get("id") == request_comment_id:
            continue
        timestamp = event_timestamp(item, channel)
        if not timestamp:
            continue
        if parse_timestamp(timestamp) < requested_at:
            continue
        result.append(normalize_event(item, channel, body_limit=body_limit))
    result.sort(key=lambda event: (event["created_at"] or "", event["id"] or 0))
    return result


def contains_pattern(body: str, patterns: tuple[str, ...]) -> bool:
    folded = body.casefold()
    return any(pattern in folded for pattern in patterns)


def bounded(
    events: list[dict[str, Any]], max_events: int
) -> tuple[list[dict[str, Any]], int]:
    if max_events < 1:
        raise InspectionError("--max-events must be positive")
    omitted = max(0, len(events) - max_events)
    return events[-max_events:], omitted


def inspect(args: argparse.Namespace) -> dict[str, Any]:
    if args.body_limit < 1:
        raise InspectionError("--body-limit must be positive")

    evidence = load_evidence(args)
    pull_request = evidence["pull_request"]
    request_comment = evidence["request_comment"]

    if request_comment.get("id") != args.request_comment_id:
        raise InspectionError("Request comment ID does not match the requested cycle")
    if args.pr and request_comment.get("issue_url"):
        expected_suffix = f"/issues/{args.pr}"
        if not str(request_comment["issue_url"]).endswith(expected_suffix):
            raise InspectionError("Request comment does not belong to the pull request")

    requested_at_text = args.requested_at or request_comment.get("created_at")
    if not requested_at_text:
        raise InspectionError("Request timestamp is unavailable")
    requested_at = parse_timestamp(str(requested_at_text))

    exact_logins = {value.casefold() for value in args.reviewer_login}
    fragments = tuple(value.casefold() for value in args.reviewer_login_contains)
    if not exact_logins and not fragments:
        fragments = ("codex",)

    ack_reactions = tuple(args.ack_reaction or DEFAULT_ACK_REACTIONS)
    clean_patterns = tuple(
        value.casefold() for value in (args.clean_pattern or DEFAULT_CLEAN_PATTERNS)
    )
    error_patterns = tuple(
        value.casefold() for value in (args.error_pattern or DEFAULT_ERROR_PATTERNS)
    )

    all_events: list[dict[str, Any]] = []
    channel_map = (
        ("issue_comment", evidence["issue_comments"]),
        ("formal_review", evidence["reviews"]),
        ("inline_comment", evidence["inline_comments"]),
    )
    for channel, items in channel_map:
        all_events.extend(
            current_events(
                items,
                channel,
                requested_at,
                body_limit=args.body_limit,
                request_comment_id=args.request_comment_id,
            )
        )
    all_events.sort(key=lambda event: (event["created_at"] or "", event["id"] or 0))

    reviewer_events = [
        event
        for event in all_events
        if is_reviewer(
            event["actor"],
            exact_logins=exact_logins,
            login_fragments=fragments,
        )
    ]
    other_actor_events = [event for event in all_events if event not in reviewer_events]

    clean_candidates = [
        event
        for event in reviewer_events
        if contains_pattern(event["body"], clean_patterns)
    ]
    error_candidates = [
        event
        for event in reviewer_events
        if contains_pattern(event["body"], error_patterns)
    ]
    classified_ids = {
        (event["channel"], event["id"])
        for event in clean_candidates + error_candidates
    }
    response_candidates = [
        event
        for event in reviewer_events
        if (event["channel"], event["id"]) not in classified_ids
        and (
            event["body"].strip()
            or event["channel"] == "inline_comment"
            or (
                event["channel"] == "formal_review"
                and str(event["state"] or "").casefold()
                in {"changes_requested", "commented"}
            )
        )
    ]

    acknowledgments = []
    for reaction in evidence["reactions"]:
        login = actor_login(reaction)
        if reaction.get("content") not in ack_reactions:
            continue
        if not is_reviewer(
            login,
            exact_logins=exact_logins,
            login_fragments=fragments,
        ):
            continue
        acknowledgments.append(
            {
                "id": reaction.get("id"),
                "actor": login,
                "content": reaction.get("content"),
                "created_at": reaction.get("created_at"),
            }
        )

    current_head = str((pull_request.get("head") or {}).get("sha") or "")
    expected_head = args.head_sha
    head_matches = expected_head is None or current_head == expected_head
    merged = bool(pull_request.get("merged_at"))
    pr_state = str(pull_request.get("state") or "").casefold()
    terminal = merged or pr_state == "closed"

    if terminal:
        mechanical_state = "pr_terminal"
    elif not head_matches:
        mechanical_state = "head_mismatch"
    elif clean_candidates and response_candidates:
        mechanical_state = "mixed_reviewer_response"
    elif response_candidates:
        mechanical_state = "reviewer_response"
    elif clean_candidates:
        mechanical_state = "clean_candidate"
    elif error_candidates:
        mechanical_state = "explicit_error"
    elif acknowledgments:
        mechanical_state = "acknowledged"
    elif reviewer_events:
        mechanical_state = "unclassified_reviewer_response"
    else:
        mechanical_state = "silent"

    bounded_reviewer, omitted_reviewer = bounded(reviewer_events, args.max_events)
    bounded_other, omitted_other = bounded(other_actor_events, args.max_events)
    bounded_clean, omitted_clean = bounded(clean_candidates, args.max_events)
    bounded_errors, omitted_errors = bounded(error_candidates, args.max_events)
    bounded_responses, omitted_responses = bounded(
        response_candidates, args.max_events
    )

    return {
        "schema_version": 1,
        "input": {
            "repository": args.repo,
            "pull_request": args.pr,
            "request_comment_id": args.request_comment_id,
            "requested_at": requested_at.isoformat(),
            "expected_head_sha": expected_head,
            "fixture": str(args.fixture) if args.fixture else None,
        },
        "pull_request": {
            "state": pull_request.get("state"),
            "merged_at": pull_request.get("merged_at"),
            "url": pull_request.get("html_url"),
            "current_head_sha": current_head,
            "head_matches": head_matches,
        },
        "request_comment": {
            "id": request_comment.get("id"),
            "actor": actor_login(request_comment),
            "created_at": request_comment.get("created_at"),
            "url": request_comment.get("html_url"),
        },
        "signals": {
            "mechanical_state": mechanical_state,
            "acknowledged": bool(acknowledgments),
            "acknowledgments": acknowledgments,
            "reviewer_event_count": len(reviewer_events),
            "other_actor_event_count": len(other_actor_events),
            "clean_candidate_count": len(clean_candidates),
            "error_candidate_count": len(error_candidates),
            "response_candidate_count": len(response_candidates),
        },
        "events": {
            "reviewer": bounded_reviewer,
            "other_actors": bounded_other,
            "clean_candidates": bounded_clean,
            "error_candidates": bounded_errors,
            "response_candidates": bounded_responses,
        },
        "omitted_event_counts": {
            "reviewer": omitted_reviewer,
            "other_actors": omitted_other,
            "clean_candidates": omitted_clean,
            "error_candidates": omitted_errors,
            "response_candidates": omitted_responses,
        },
    }


def main() -> int:
    args = parse_args()
    try:
        result = inspect(args)
    except InspectionError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
