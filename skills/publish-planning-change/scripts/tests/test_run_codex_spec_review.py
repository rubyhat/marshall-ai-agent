from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "run_codex_spec_review.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_codex_spec_review", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = load_runner()


FIXED_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)
OUTER_ID = "11111111-1111-7111-8111-111111111111"


def write_fixture(name: str, destination: Path, worktree: Path, **replacements):
    text = (FIXTURES / name).read_text(encoding="utf-8")
    text = text.replace("__WORKTREE__", str(worktree))
    for source, target in replacements.items():
        text = text.replace(source, target)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def make_invocation(parent_id=OUTER_ID, kind="initial"):
    return runner.Invocation(
        invocation_id=f"invocation-{kind}",
        kind=kind,
        correlation_id=f"correlation-{kind}",
        started_at=FIXED_TIME,
        completed_at=FIXED_TIME,
        review_parent_session_id=parent_id,
        process_exit_code=0,
    )


def make_target(worktree: Path):
    return runner.TargetSnapshot(
        kind="uncommitted",
        worktree=str(worktree),
        branch="codex/test",
        base_revision="a" * 40,
        head_revision=None,
        manifest=(("spec.md", "100644", "b" * 40),),
        manifest_fingerprint="c" * 64,
        state_fingerprint="d" * 64,
    )


def git(repository: Path, *arguments: str):
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def initialize_git_fixture(root: Path):
    git(root, "init", "-q")
    git(root, "config", "user.name", "Fixture")
    git(root, "config", "user.email", "fixture@example.test")
    (root / "spec.md").write_text("base\n", encoding="utf-8")
    git(root, "add", "spec.md")
    git(root, "commit", "-qm", "base")
    base = git(root, "rev-parse", "HEAD")
    git(root, "switch", "-qc", "codex/test")
    (root / "spec.md").write_text("base\nchanged\n", encoding="utf-8")
    return base


def write_session(
    sessions_root: Path,
    *,
    session_id: str,
    parent_id: str | None,
    worktree: Path,
    source,
    terminal_message: dict | str | None,
    terminal=True,
    metadata_session_id="from_path",
):
    path = sessions_root / f"{session_id}.jsonl"
    session_meta = {
        "parent_thread_id": parent_id,
        "cwd": str(worktree),
        "source": source,
    }
    if metadata_session_id == "from_path":
        session_meta["id"] = session_id
    elif metadata_session_id is not None:
        session_meta["id"] = metadata_session_id
    records = [
        {
            "timestamp": runner.format_time(runner.utc_now()),
            "type": "session_meta",
            "payload": session_meta,
        }
    ]
    if terminal:
        payload = {"type": "task_complete"}
        if terminal_message is not None:
            payload["last_agent_message"] = (
                json.dumps(terminal_message, separators=(",", ":"))
                if isinstance(terminal_message, dict)
                else terminal_message
            )
        records.append(
            {
                "timestamp": runner.format_time(runner.utc_now()),
                "type": "event_msg",
                "payload": payload,
            }
        )
    path.write_text(
        "".join(json.dumps(record, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )
    return path


def clean_message():
    return {
        "findings": [],
        "overall_correctness": "patch is correct",
        "overall_explanation": "No material defects found.",
        "overall_confidence_score": 0.97,
    }


def finding_message(worktree: Path, title="[P1] Preserve finding", priority=1):
    finding = {
        "title": title,
        "body": "The current contract is incomplete.",
        "confidence_score": 0.94,
        "code_location": {
            "absolute_file_path": str(worktree / "spec.md"),
            "line_range": {"start": 1, "end": 1},
        },
    }
    if priority != "missing":
        finding["priority"] = priority
    return {
        "findings": [finding],
        "overall_correctness": "patch is incorrect",
        "overall_explanation": "A bounded correction is required.",
        "overall_confidence_score": 0.92,
    }


class TerminalContractTest(unittest.TestCase):
    def test_target_result_serializes_complete_manifest(self):
        target = make_target(Path("/tmp/review"))

        self.assertEqual(
            target.as_result()["manifest"],
            [
                {
                    "path": "spec.md",
                    "mode": "100644",
                    "blob_oid": "b" * 40,
                }
            ],
        )

    def test_clean_native_message_is_valid(self):
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            normalized, errors = runner.validate_terminal_message(
                json.dumps(clean_message()), worktree, {"spec.md"}
            )
        self.assertEqual(errors, [])
        self.assertEqual(normalized["overall_correctness"], "patch is correct")

    def test_finding_location_preserves_final_symlink_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            (worktree / "spec.md").write_text("target\n", encoding="utf-8")
            (worktree / "linked.md").symlink_to("spec.md")
            message = finding_message(worktree)
            message["findings"][0]["code_location"]["absolute_file_path"] = str(
                worktree / "linked.md"
            )

            normalized, errors = runner.validate_terminal_message(
                json.dumps(message), worktree, {"linked.md"}
            )

        self.assertEqual(errors, [])
        self.assertEqual(
            normalized["findings"][0]["code_location"]["path"], "linked.md"
        )

    def test_missing_and_null_priority_are_valid_and_stable(self):
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            missing, missing_errors = runner.validate_terminal_message(
                json.dumps(finding_message(worktree, priority="missing")),
                worktree,
                {"spec.md"},
            )
            null_value, null_errors = runner.validate_terminal_message(
                json.dumps(finding_message(worktree, priority=None)),
                worktree,
                {"spec.md"},
            )
        self.assertEqual(missing_errors, [])
        self.assertEqual(null_errors, [])
        self.assertEqual(
            missing["findings"][0]["fingerprint"],
            null_value["findings"][0]["fingerprint"],
        )
        self.assertNotIn("priority", missing["findings"][0])
        self.assertIsNone(null_value["findings"][0]["priority"])

    def test_invalid_native_required_fields_fail_closed(self):
        cases = []
        missing_explanation = clean_message()
        missing_explanation["overall_explanation"] = ""
        cases.append((missing_explanation, "missing_overall_explanation"))
        bad_overall_confidence = clean_message()
        bad_overall_confidence["overall_confidence_score"] = 2
        cases.append((bad_overall_confidence, "invalid_overall_confidence_score"))
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            bad_finding = finding_message(worktree)
            bad_finding["findings"][0]["confidence_score"] = -0.1
            cases.append((bad_finding, "finding_0_invalid_confidence_score"))
            for message, expected in cases:
                with self.subTest(expected=expected):
                    normalized, errors = runner.validate_terminal_message(
                        json.dumps(message), worktree, {"spec.md"}
                    )
                    self.assertIsNone(normalized)
                    self.assertIn(expected, errors)

    def test_incorrect_without_findings_is_contract_error(self):
        message = clean_message()
        message["overall_correctness"] = "patch is incorrect"
        with tempfile.TemporaryDirectory() as temporary:
            normalized, errors = runner.validate_terminal_message(
                json.dumps(message), Path(temporary), {"spec.md"}
            )
        self.assertIsNone(normalized)
        self.assertIn("incorrect_without_findings", errors)

    def test_markdown_fence_is_not_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            normalized, errors = runner.validate_terminal_message(
                "```json\n{}\n```", Path(temporary), {"spec.md"}
            )
        self.assertIsNone(normalized)
        self.assertEqual(errors, ["invalid_terminal_json"])

    def test_unknown_native_fields_fail_closed_instead_of_being_dropped(self):
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            top_level = clean_message()
            top_level["future_verdict"] = "unknown"
            normalized, errors = runner.validate_terminal_message(
                json.dumps(top_level), worktree, {"spec.md"}
            )
            self.assertIsNone(normalized)
            self.assertIn("unsupported_top_level_fields:future_verdict", errors)

            finding = finding_message(worktree)
            finding["findings"][0]["future_priority"] = 4
            normalized, errors = runner.validate_terminal_message(
                json.dumps(finding), worktree, {"spec.md"}
            )
            self.assertIsNone(normalized)
            self.assertIn("finding_0_unsupported_fields:future_priority", errors)


class SessionBindingTest(unittest.TestCase):
    def test_sanitized_fixture_consolidates_non_clean_result_and_usage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions = root / "sessions"
            sessions.mkdir()
            worktree = root / "review"
            worktree.mkdir()
            write_fixture("outer_terminal.jsonl", sessions / "outer.jsonl", worktree)
            write_fixture("non_clean_child.jsonl", sessions / "child.jsonl", worktree)
            documents = runner.scan_session_documents(sessions, FIXED_TIME)
            bound = runner.bind_sessions(documents, [make_invocation()], str(worktree))
            status, findings, matched, errors = runner.consolidate_terminal_results(
                bound, make_target(worktree)
            )
        self.assertEqual(status, "non_clean")
        self.assertEqual(errors, [])
        self.assertEqual(len(findings), 1)
        self.assertEqual(matched[0]["token_usage"], None)

    def test_fixture_token_usage_reads_last_cumulative_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions = root / "sessions"
            sessions.mkdir()
            worktree = root / "review"
            worktree.mkdir()
            write_fixture("outer_terminal.jsonl", sessions / "outer.jsonl", worktree)
            write_fixture("clean_child.jsonl", sessions / "child.jsonl", worktree)
            documents = runner.scan_session_documents(sessions, FIXED_TIME)
            bound = runner.bind_sessions(documents, [make_invocation()], str(worktree))
            status, findings, matched, errors = runner.consolidate_terminal_results(
                bound, make_target(worktree)
            )
        self.assertEqual(status, "clean")
        self.assertEqual(findings, [])
        self.assertEqual(errors, [])
        self.assertEqual(matched[0]["token_usage"]["total_tokens"], 110)

    def test_cumulative_usage_sums_each_child_once(self):
        usage = {
            "input_tokens": 100,
            "cached_input_tokens": 25,
            "output_tokens": 10,
            "reasoning_output_tokens": 4,
            "total_tokens": 110,
        }
        matched = [
            {"session_id": "child-a", "token_usage": usage},
            {"session_id": "child-a", "token_usage": usage},
            {
                "session_id": "child-b",
                "token_usage": {key: value * 2 for key, value in usage.items()},
            },
        ]
        cumulative = runner.cumulative_token_usage(matched)
        self.assertEqual(cumulative["total_tokens"], 330)
        self.assertEqual(cumulative["matched_sessions_with_usage"], 2)

    def test_multiple_terminals_union_and_deduplicate_findings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions = root / "sessions"
            sessions.mkdir()
            worktree = root / "review"
            worktree.mkdir()
            write_fixture("outer_terminal.jsonl", sessions / "outer.jsonl", worktree)
            first = finding_message(worktree, title="[P1] First")
            duplicate = finding_message(worktree, title="[P1] First")
            second = finding_message(worktree, title="[P2] Second", priority=2)
            write_session(
                sessions,
                session_id="22222222-2222-7222-8222-222222222222",
                parent_id=OUTER_ID,
                worktree=worktree,
                source={"subagent": "review"},
                terminal_message=first,
            )
            other = write_session(
                sessions,
                session_id="33333333-3333-7333-8333-333333333333",
                parent_id=OUTER_ID,
                worktree=worktree,
                source={"subagent": "review"},
                terminal_message=duplicate,
            )
            with other.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "timestamp": runner.format_time(runner.utc_now()),
                            "type": "event_msg",
                            "payload": {
                                "type": "task_complete",
                                "last_agent_message": json.dumps(second),
                            },
                        }
                    )
                    + "\n"
                )
            documents = runner.scan_session_documents(sessions, FIXED_TIME)
            bound = runner.bind_sessions(documents, [make_invocation()], str(worktree))
            status, findings, _, errors = runner.consolidate_terminal_results(
                bound, make_target(worktree)
            )
        self.assertEqual(status, "non_clean")
        self.assertEqual(errors, [])
        self.assertEqual([item["title"] for item in findings], ["[P1] First", "[P2] Second"])

    def test_finding_wins_over_a_later_clean_terminal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions = root / "sessions"
            sessions.mkdir()
            worktree = root / "review"
            worktree.mkdir()
            write_fixture("outer_terminal.jsonl", sessions / "outer.jsonl", worktree)
            write_session(
                sessions,
                session_id="22222222-2222-7222-8222-222222222222",
                parent_id=OUTER_ID,
                worktree=worktree,
                source={"subagent": "review"},
                terminal_message=clean_message(),
            )
            write_session(
                sessions,
                session_id="33333333-3333-7333-8333-333333333333",
                parent_id=OUTER_ID,
                worktree=worktree,
                source={"subagent": "review"},
                terminal_message=finding_message(worktree),
            )
            documents = runner.scan_session_documents(sessions, FIXED_TIME)
            bound = runner.bind_sessions(documents, [make_invocation()], str(worktree))
            status, findings, _, errors = runner.consolidate_terminal_results(
                bound, make_target(worktree)
            )
        self.assertEqual(status, "non_clean")
        self.assertEqual(len(findings), 1)
        self.assertEqual(errors, [])

    def test_matched_child_without_terminal_times_out_without_retry_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions = root / "sessions"
            sessions.mkdir()
            worktree = root / "review"
            worktree.mkdir()
            write_fixture("outer_terminal.jsonl", sessions / "outer.jsonl", worktree)
            write_fixture(
                "child_without_terminal.jsonl", sessions / "child.jsonl", worktree
            )
            settlement = runner.settle_sessions(
                sessions,
                FIXED_TIME,
                [make_invocation()],
                str(worktree),
                minimum_stable_scans=2,
                settle_interval_seconds=0.002,
                settlement_timeout_seconds=0.02,
            )
        self.assertEqual(settlement.status, "session_settlement_timeout")
        self.assertFalse(settlement.bound.matched_child_sessions_terminal)

    def test_different_parent_session_is_excluded(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions = root / "sessions"
            sessions.mkdir()
            worktree = root / "review"
            worktree.mkdir()
            write_fixture("outer_terminal.jsonl", sessions / "outer.jsonl", worktree)
            write_session(
                sessions,
                session_id="99999999-9999-7999-8999-999999999999",
                parent_id="88888888-8888-7888-8888-888888888888",
                worktree=worktree,
                source={"subagent": "review"},
                terminal_message=clean_message(),
            )
            documents = runner.scan_session_documents(sessions, FIXED_TIME)
            bound = runner.bind_sessions(documents, [make_invocation()], str(worktree))
        self.assertEqual(bound.children, [])
        self.assertEqual(bound.binding_errors, [])

    def test_review_child_requires_a_string_session_id(self):
        for label, metadata_session_id in (
            ("missing", None),
            ("empty", ""),
            ("non_string", 42),
        ):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                sessions = root / "sessions"
                sessions.mkdir()
                worktree = root / "review"
                worktree.mkdir()
                write_fixture("outer_terminal.jsonl", sessions / "outer.jsonl", worktree)
                write_session(
                    sessions,
                    session_id="99999999-9999-7999-8999-999999999999",
                    parent_id=OUTER_ID,
                    worktree=worktree,
                    source={"subagent": "review"},
                    terminal_message=clean_message(),
                    metadata_session_id=metadata_session_id,
                )

                documents = runner.scan_session_documents(sessions, FIXED_TIME)
                bound = runner.bind_sessions(
                    documents, [make_invocation()], str(worktree)
                )

            self.assertEqual(bound.children, [])
            self.assertEqual(
                bound.binding_errors[0]["code"],
                "review_child_missing_or_invalid_session_id",
            )

    def test_duplicate_outer_session_id_is_binding_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions = root / "sessions"
            sessions.mkdir()
            worktree = root / "review"
            worktree.mkdir()
            write_fixture("outer_terminal.jsonl", sessions / "outer-a.jsonl", worktree)
            write_fixture("outer_terminal.jsonl", sessions / "outer-b.jsonl", worktree)
            documents = runner.scan_session_documents(sessions, FIXED_TIME)
            bound = runner.bind_sessions(documents, [make_invocation()], str(worktree))
        self.assertEqual(bound.missing_outer_invocations, [])
        self.assertEqual(bound.binding_errors[0]["code"], "duplicate_outer_session")

    def test_outer_session_must_be_inside_invocation_time_boundary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions = root / "sessions"
            sessions.mkdir()
            worktree = root / "review"
            worktree.mkdir()
            write_session(
                sessions,
                session_id=OUTER_ID,
                parent_id=None,
                worktree=worktree,
                source="exec",
                terminal_message="launcher complete",
            )
            documents = runner.scan_session_documents(sessions, FIXED_TIME)
            bound = runner.bind_sessions(documents, [make_invocation()], str(worktree))
        self.assertEqual(
            bound.binding_errors[0]["code"], "outer_session_boundary_mismatch"
        )

    def test_changed_artifact_resets_stable_scan_count(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions = root / "sessions"
            sessions.mkdir()
            worktree = root / "review"
            worktree.mkdir()
            write_fixture("outer_terminal.jsonl", sessions / "outer.jsonl", worktree)
            child = sessions / "child.jsonl"
            write_fixture("clean_child.jsonl", child, worktree)
            original_scan = runner.scan_session_documents
            scans = 0

            def changing_scan(sessions_root, attempt_started_at):
                nonlocal scans
                scans += 1
                if scans == 2:
                    with child.open("a", encoding="utf-8") as handle:
                        handle.write("\n")
                return original_scan(sessions_root, attempt_started_at)

            runner.scan_session_documents = changing_scan
            try:
                settlement = runner.settle_sessions(
                    sessions,
                    FIXED_TIME,
                    [make_invocation()],
                    str(worktree),
                    minimum_stable_scans=2,
                    settle_interval_seconds=0.001,
                    settlement_timeout_seconds=0.05,
                )
            finally:
                runner.scan_session_documents = original_scan
        self.assertEqual(settlement.status, "settled_with_terminal_result")
        self.assertEqual(settlement.stable_scans_observed, 2)
        self.assertGreaterEqual(scans, 4)


class EndToEndNoModelTest(unittest.TestCase):
    def make_args(self, worktree: Path, sessions: Path, base: str):
        return argparse.Namespace(
            worktree=str(worktree),
            task_id="ROOT-TEST-1",
            target_kind="uncommitted",
            base=base,
            head=None,
            model="test-reviewer",
            effort="medium",
            caller_thread_id="caller-thread",
            codex_bin="codex",
            sessions_root=str(sessions),
            minimum_stable_scans=2,
            settle_interval_seconds=0.002,
            settlement_timeout_seconds=0.03,
            invocation_timeout_seconds=900.0,
            technical_retry_limit=1,
        )

    def test_fake_launcher_captures_startup_uuid_and_stream_diagnostics(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            worktree.mkdir()
            base = initialize_git_fixture(worktree)
            fake_codex = root / "fake-codex"
            captured_arguments = root / "captured-arguments"
            fake_codex.write_text(
                "#!/bin/sh\n"
                f"printf '%s\\n' \"$@\" > '{captured_arguments}'\n"
                f"printf 'session id: {OUTER_ID}\\n'\n"
                "printf 'diagnostic stream\\n' >&2\n"
                "exit 23\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            target = runner.build_target_snapshot(
                str(worktree), "uncommitted", base
            )
            invocation = runner.launch_codex_review(
                codex_bin=str(fake_codex),
                target=target,
                task_id="ROOT-TEST-1",
                model="test-reviewer",
                effort="medium",
                invocation_kind="initial",
                correlation_id="correlation-initial",
            )
            arguments = captured_arguments.read_text(encoding="utf-8").splitlines()
        self.assertEqual(invocation.review_parent_session_id, OUTER_ID)
        self.assertEqual(invocation.process_exit_code, 23)
        self.assertFalse(invocation.timed_out)
        self.assertGreater(invocation.stdout_bytes, 0)
        self.assertGreater(invocation.stderr_bytes, 0)
        self.assertEqual(len(invocation.stdout_sha256), 64)
        self.assertEqual(len(invocation.stderr_sha256), 64)
        developer_instructions = next(
            item for item in arguments if item.startswith("developer_instructions=")
        )
        self.assertIn("independent specification-contract review", developer_instructions)
        self.assertIn("ROOT-TEST-1", developer_instructions)
        self.assertIn('complete changed-path manifest is [\\"spec.md\\"]', developer_instructions)
        self.assertIn("--uncommitted", arguments)
        self.assertNotIn("--base", arguments)
        self.assertNotIn(base, arguments)

    def test_invocation_timeout_is_reaped_and_fails_closed_without_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            sessions = root / "sessions"
            worktree.mkdir()
            sessions.mkdir()
            base = initialize_git_fixture(worktree)
            fake_codex = root / "fake-codex"
            fake_codex.write_text(
                "#!/bin/sh\n"
                f"printf 'session id: {OUTER_ID}\\n'\n"
                "exec sleep 10\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            args = self.make_args(worktree, sessions, base)
            args.codex_bin = str(fake_codex)
            args.invocation_timeout_seconds = 0.05

            result = runner.execute(args)

        self.assertEqual(result["status"], "review_invocation_timeout")
        self.assertEqual(result["technical_retries_used"], 0)
        self.assertEqual(len(result["invocations"]), 1)
        self.assertTrue(result["invocations"][0]["timed_out"])
        self.assertNotEqual(result["invocations"][0]["process_exit_code"], 0)
        self.assertEqual(
            result["diagnostics"]["timed_out_invocation_ids"],
            [result["invocations"][0]["invocation_id"]],
        )
        self.assertEqual(runner.EXIT_BY_STATUS["review_invocation_timeout"], 17)

    def test_committed_target_selects_base_review_mode(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            worktree.mkdir()
            base = initialize_git_fixture(worktree)
            git(worktree, "add", "spec.md")
            git(worktree, "commit", "-qm", "change spec")
            head = git(worktree, "rev-parse", "HEAD")
            captured_arguments = root / "captured-arguments"
            fake_codex = root / "fake-codex"
            fake_codex.write_text(
                "#!/bin/sh\n"
                f"printf '%s\\n' \"$@\" > '{captured_arguments}'\n"
                f"printf 'session id: {OUTER_ID}\\n'\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            target = runner.build_target_snapshot(
                str(worktree), "committed", base, head
            )

            runner.launch_codex_review(
                codex_bin=str(fake_codex),
                target=target,
                task_id="ROOT-TEST-1",
                model="test-reviewer",
                effort="medium",
                invocation_kind="initial",
                correlation_id="correlation-initial",
            )
            arguments = captured_arguments.read_text(encoding="utf-8").splitlines()

        self.assertIn("--base", arguments)
        self.assertIn(base, arguments)
        self.assertNotIn("--uncommitted", arguments)

    def test_uncommitted_target_rejects_committed_plus_dirty_candidate(self):
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            base = initialize_git_fixture(worktree)
            git(worktree, "add", "spec.md")
            git(worktree, "commit", "-qm", "committed candidate")
            (worktree / "spec.md").write_text(
                "base\ncommitted\ndirty\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(
                runner.RunnerConfigurationError,
                "cannot include committed changes",
            ):
                runner.build_target_snapshot(
                    str(worktree), "uncommitted", base
                )

    def test_deleted_tracked_artifact_has_stable_manifest_marker(self):
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            base = initialize_git_fixture(worktree)
            base_blob_oid = git(worktree, "rev-parse", f"{base}:spec.md")
            (worktree / "spec.md").unlink()

            target = runner.build_target_snapshot(
                str(worktree), "uncommitted", base
            )
            repeated = runner.build_target_snapshot(
                str(worktree), "uncommitted", base
            )

        self.assertEqual(
            target.manifest,
            (
                (
                    "spec.md",
                    f"{runner.DELETED_MODE_PREFIX}100644",
                    f"{runner.DELETED_BLOB_PREFIX}{base_blob_oid}",
                ),
            ),
        )
        self.assertEqual(target.manifest_fingerprint, repeated.manifest_fingerprint)
        self.assertEqual(target.state_fingerprint, repeated.state_fingerprint)

    def test_chmod_only_target_records_mode_with_unchanged_blob(self):
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            base = initialize_git_fixture(worktree)
            git(worktree, "restore", "spec.md")
            base_blob_oid = git(worktree, "rev-parse", f"{base}:spec.md")
            (worktree / "spec.md").chmod(0o755)

            target = runner.build_target_snapshot(
                str(worktree), "uncommitted", base
            )

        self.assertEqual(
            target.manifest,
            (("spec.md", "100755", base_blob_oid),),
        )

    def test_staged_chmod_uses_index_mode_when_filemode_is_ignored(self):
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            base = initialize_git_fixture(worktree)
            git(worktree, "restore", "spec.md")
            git(worktree, "config", "core.filemode", "false")
            base_blob_oid = git(worktree, "rev-parse", f"{base}:spec.md")
            git(worktree, "update-index", "--chmod=+x", "spec.md")

            target = runner.build_target_snapshot(
                str(worktree), "uncommitted", base
            )

        self.assertEqual(
            target.manifest,
            (("spec.md", "100755", base_blob_oid),),
        )

    def test_symlink_target_records_symlink_mode_and_target_blob(self):
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            base = initialize_git_fixture(worktree)
            git(worktree, "restore", "spec.md")
            (worktree / "linked.md").symlink_to("spec.md")
            link_blob_oid = runner.run_git(
                worktree,
                ["hash-object", "--stdin"],
                input_bytes=b"spec.md",
            ).decode().strip()

            target = runner.build_target_snapshot(
                str(worktree), "uncommitted", base
            )

        self.assertEqual(
            target.manifest,
            (("linked.md", "120000", link_blob_oid),),
        )

    def test_rename_manifest_includes_new_blob_and_deleted_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            worktree = Path(temporary)
            base = initialize_git_fixture(worktree)
            git(worktree, "restore", "spec.md")
            base_blob_oid = git(worktree, "rev-parse", f"{base}:spec.md")
            git(worktree, "mv", "spec.md", "renamed.md")

            target = runner.build_target_snapshot(
                str(worktree), "uncommitted", base
            )

        self.assertEqual(
            target.manifest,
            (
                ("renamed.md", "100644", base_blob_oid),
                (
                    "spec.md",
                    f"{runner.DELETED_MODE_PREFIX}100644",
                    f"{runner.DELETED_BLOB_PREFIX}{base_blob_oid}",
                ),
            ),
        )

    def test_late_initial_finding_survives_technical_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            sessions = root / "sessions"
            worktree.mkdir()
            sessions.mkdir()
            base = initialize_git_fixture(worktree)
            parent_ids = [
                "11111111-1111-7111-8111-111111111111",
                "66666666-6666-7666-8666-666666666666",
            ]
            calls = []

            def launcher(**kwargs):
                index = len(calls)
                parent_id = parent_ids[index]
                invocation = runner.Invocation(
                    invocation_id=f"invocation-{index}",
                    kind=kwargs["invocation_kind"],
                    correlation_id=kwargs["correlation_id"],
                    started_at=runner.utc_now(),
                    completed_at=runner.utc_now(),
                    review_parent_session_id=parent_id,
                    process_exit_code=0,
                )
                write_session(
                    sessions,
                    session_id=parent_id,
                    parent_id=None,
                    worktree=worktree,
                    source="exec",
                    terminal_message="launcher complete",
                )
                if index == 1:
                    write_session(
                        sessions,
                        session_id="77777777-7777-7777-8777-777777777777",
                        parent_id=parent_ids[0],
                        worktree=worktree,
                        source={"subagent": "review"},
                        terminal_message=finding_message(worktree),
                    )
                    write_session(
                        sessions,
                        session_id="88888888-8888-7888-8888-888888888888",
                        parent_id=parent_ids[1],
                        worktree=worktree,
                        source={"subagent": "review"},
                        terminal_message=clean_message(),
                    )
                calls.append(invocation)
                return invocation

            result = runner.execute(
                self.make_args(worktree, sessions, base), launcher=launcher
            )
        self.assertEqual(result["status"], "non_clean")
        self.assertEqual(result["technical_retries_used"], 1)
        self.assertEqual(len(result["invocations"]), 2)
        self.assertEqual(len(result["matched_sessions"]), 2)
        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual(result["diagnostics"]["terminal_contract_errors"], [])

    def test_two_missing_results_exhaust_retry_budget(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            sessions = root / "sessions"
            worktree.mkdir()
            sessions.mkdir()
            base = initialize_git_fixture(worktree)
            parents = iter(
                [
                    "11111111-1111-7111-8111-111111111111",
                    "66666666-6666-7666-8666-666666666666",
                ]
            )

            def launcher(**kwargs):
                parent_id = next(parents)
                invocation = runner.Invocation(
                    invocation_id=str(parent_id),
                    kind=kwargs["invocation_kind"],
                    correlation_id=kwargs["correlation_id"],
                    started_at=runner.utc_now(),
                    completed_at=runner.utc_now(),
                    review_parent_session_id=parent_id,
                    process_exit_code=0,
                )
                write_session(
                    sessions,
                    session_id=parent_id,
                    parent_id=None,
                    worktree=worktree,
                    source="exec",
                    terminal_message="launcher complete",
                )
                return invocation

            result = runner.execute(
                self.make_args(worktree, sessions, base), launcher=launcher
            )
        self.assertEqual(result["status"], "technical_retry_budget_exhausted")
        self.assertEqual(len(result["invocations"]), 2)
        self.assertEqual(result["matched_sessions"], [])

    def test_startup_binding_error_stops_without_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            sessions = root / "sessions"
            worktree.mkdir()
            sessions.mkdir()
            base = initialize_git_fixture(worktree)
            calls = []

            def launcher(**kwargs):
                calls.append(kwargs["invocation_kind"])
                return runner.Invocation(
                    invocation_id="invocation-0",
                    kind=kwargs["invocation_kind"],
                    correlation_id=kwargs["correlation_id"],
                    started_at=runner.utc_now(),
                    completed_at=runner.utc_now(),
                    review_parent_session_id=None,
                    process_exit_code=1,
                    binding_error="missing_startup_session_id",
                )

            result = runner.execute(
                self.make_args(worktree, sessions, base), launcher=launcher
            )
        self.assertEqual(result["status"], "invocation_binding_error")
        self.assertEqual(calls, ["initial"])
        self.assertEqual(result["technical_retries_used"], 0)

    def test_target_change_after_review_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            sessions = root / "sessions"
            worktree.mkdir()
            sessions.mkdir()
            base = initialize_git_fixture(worktree)

            def launcher(**kwargs):
                parent_id = OUTER_ID
                invocation = runner.Invocation(
                    invocation_id="invocation-0",
                    kind=kwargs["invocation_kind"],
                    correlation_id=kwargs["correlation_id"],
                    started_at=runner.utc_now(),
                    completed_at=runner.utc_now(),
                    review_parent_session_id=parent_id,
                    process_exit_code=0,
                )
                write_session(
                    sessions,
                    session_id=parent_id,
                    parent_id=None,
                    worktree=worktree,
                    source="exec",
                    terminal_message="launcher complete",
                )
                write_session(
                    sessions,
                    session_id="22222222-2222-7222-8222-222222222222",
                    parent_id=parent_id,
                    worktree=worktree,
                    source={"subagent": "review"},
                    terminal_message=clean_message(),
                )
                (worktree / "spec.md").write_text(
                    "base\nchanged while reviewing\n", encoding="utf-8"
                )
                return invocation

            result = runner.execute(
                self.make_args(worktree, sessions, base), launcher=launcher
            )
        self.assertEqual(result["status"], "target_changed")
        self.assertEqual(len(result["invocations"]), 1)
        self.assertIsNone(result["diagnostics"]["target_change_error"])

    def test_branch_switch_after_review_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            sessions = root / "sessions"
            worktree.mkdir()
            sessions.mkdir()
            base = initialize_git_fixture(worktree)

            def launcher(**kwargs):
                invocation = runner.Invocation(
                    invocation_id="invocation-0",
                    kind=kwargs["invocation_kind"],
                    correlation_id=kwargs["correlation_id"],
                    started_at=runner.utc_now(),
                    completed_at=runner.utc_now(),
                    review_parent_session_id=OUTER_ID,
                    process_exit_code=0,
                )
                write_session(
                    sessions,
                    session_id=OUTER_ID,
                    parent_id=None,
                    worktree=worktree,
                    source="exec",
                    terminal_message="launcher complete",
                )
                write_session(
                    sessions,
                    session_id="22222222-2222-7222-8222-222222222222",
                    parent_id=OUTER_ID,
                    worktree=worktree,
                    source={"subagent": "review"},
                    terminal_message=clean_message(),
                )
                git(worktree, "switch", "-qc", "codex/switched")
                return invocation

            result = runner.execute(
                self.make_args(worktree, sessions, base), launcher=launcher
            )

        self.assertEqual(result["status"], "target_changed")
        self.assertEqual(result["review_target"]["branch"], "codex/test")
        self.assertEqual(len(result["invocations"]), 1)

    def test_mode_change_after_review_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            sessions = root / "sessions"
            worktree.mkdir()
            sessions.mkdir()
            base = initialize_git_fixture(worktree)

            def launcher(**kwargs):
                invocation = runner.Invocation(
                    invocation_id="invocation-0",
                    kind=kwargs["invocation_kind"],
                    correlation_id=kwargs["correlation_id"],
                    started_at=runner.utc_now(),
                    completed_at=runner.utc_now(),
                    review_parent_session_id=OUTER_ID,
                    process_exit_code=0,
                )
                write_session(
                    sessions,
                    session_id=OUTER_ID,
                    parent_id=None,
                    worktree=worktree,
                    source="exec",
                    terminal_message="launcher complete",
                )
                write_session(
                    sessions,
                    session_id="22222222-2222-7222-8222-222222222222",
                    parent_id=OUTER_ID,
                    worktree=worktree,
                    source={"subagent": "review"},
                    terminal_message=clean_message(),
                )
                (worktree / "spec.md").chmod(0o755)
                return invocation

            result = runner.execute(
                self.make_args(worktree, sessions, base), launcher=launcher
            )

        self.assertEqual(result["status"], "target_changed")
        self.assertEqual(len(result["invocations"]), 1)

    def test_invalid_post_review_snapshot_returns_normalized_target_changed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            sessions = root / "sessions"
            worktree.mkdir()
            sessions.mkdir()
            base = initialize_git_fixture(worktree)

            def launcher(**kwargs):
                invocation = runner.Invocation(
                    invocation_id="invocation-0",
                    kind=kwargs["invocation_kind"],
                    correlation_id=kwargs["correlation_id"],
                    started_at=runner.utc_now(),
                    completed_at=runner.utc_now(),
                    review_parent_session_id=OUTER_ID,
                    process_exit_code=0,
                )
                write_session(
                    sessions,
                    session_id=OUTER_ID,
                    parent_id=None,
                    worktree=worktree,
                    source="exec",
                    terminal_message="launcher complete",
                )
                write_session(
                    sessions,
                    session_id="22222222-2222-7222-8222-222222222222",
                    parent_id=OUTER_ID,
                    worktree=worktree,
                    source={"subagent": "review"},
                    terminal_message=clean_message(),
                )
                (worktree / "spec.md").write_text("base\n", encoding="utf-8")
                return invocation

            result = runner.execute(
                self.make_args(worktree, sessions, base), launcher=launcher
            )

        self.assertEqual(result["status"], "target_changed")
        self.assertEqual(result["findings"], [])
        self.assertIn(
            "review target has an empty diff manifest",
            result["diagnostics"]["target_change_error"],
        )
        normalized_hash = result.pop("normalized_result_sha256")
        self.assertEqual(normalized_hash, runner.sha256_json(result))

    def test_normalized_hash_covers_the_complete_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            sessions = root / "sessions"
            worktree.mkdir()
            sessions.mkdir()
            base = initialize_git_fixture(worktree)

            def launcher(**kwargs):
                invocation = runner.Invocation(
                    invocation_id="invocation-0",
                    kind=kwargs["invocation_kind"],
                    correlation_id=kwargs["correlation_id"],
                    started_at=runner.utc_now(),
                    completed_at=runner.utc_now(),
                    review_parent_session_id=OUTER_ID,
                    process_exit_code=23,
                )
                write_session(
                    sessions,
                    session_id=OUTER_ID,
                    parent_id=None,
                    worktree=worktree,
                    source="exec",
                    terminal_message="launcher diagnostic only",
                )
                write_session(
                    sessions,
                    session_id="22222222-2222-7222-8222-222222222222",
                    parent_id=OUTER_ID,
                    worktree=worktree,
                    source={"subagent": "review"},
                    terminal_message=clean_message(),
                )
                return invocation

            result = runner.execute(
                self.make_args(worktree, sessions, base), launcher=launcher
            )
        recorded = result.pop("normalized_result_sha256")
        self.assertEqual(recorded, runner.sha256_json(result))
        self.assertEqual(result["status"], "clean")
        self.assertEqual(result["diagnostics"]["process_exit_codes"], [23])

    def test_runtime_duration_bounds_fail_before_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            sessions = root / "sessions"
            worktree.mkdir()
            sessions.mkdir()
            base = initialize_git_fixture(worktree)
            args = self.make_args(worktree, sessions, base)
            for interval, timeout in ((0, 30), (11, 30), (2, 2), (2, 121)):
                with self.subTest(interval=interval, timeout=timeout):
                    args.settle_interval_seconds = interval
                    args.settlement_timeout_seconds = timeout
                    with self.assertRaises(runner.RunnerConfigurationError):
                        runner.validate_runtime_contract(args)
            args.settle_interval_seconds = 0.002
            args.settlement_timeout_seconds = 0.03
            for timeout in (0, 3601):
                with self.subTest(invocation_timeout=timeout):
                    args.invocation_timeout_seconds = timeout
                    with self.assertRaises(runner.RunnerConfigurationError):
                        runner.validate_runtime_contract(args)

    def test_runtime_accepts_documented_boundary_values(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worktree = root / "repository"
            sessions = root / "sessions"
            worktree.mkdir()
            sessions.mkdir()
            base = initialize_git_fixture(worktree)
            args = self.make_args(worktree, sessions, base)
            args.settle_interval_seconds = 10
            args.settlement_timeout_seconds = 120
            args.invocation_timeout_seconds = 3600
            args.effort = "xhigh"
            runner.validate_runtime_contract(args)


class FixtureHygieneTest(unittest.TestCase):
    def test_fixtures_are_sanitized_jsonl_without_reasoning(self):
        for fixture in FIXTURES.glob("*.jsonl"):
            with self.subTest(fixture=fixture.name):
                text = fixture.read_text(encoding="utf-8")
                self.assertNotIn("reasoning_content", text)
                for line in text.splitlines():
                    json.loads(line)


if __name__ == "__main__":
    unittest.main()
