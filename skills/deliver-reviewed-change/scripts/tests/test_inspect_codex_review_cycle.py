from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


TEST_ROOT = Path(__file__).resolve().parent
SCRIPT = TEST_ROOT.parent / "inspect_codex_review_cycle.py"
FIXTURES = TEST_ROOT / "fixtures"


class InspectCodexReviewCycleTest(unittest.TestCase):
    def inspect(self, fixture: str, *, head_sha: str = "head-1") -> dict:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--fixture",
                str(FIXTURES / fixture),
                "--request-comment-id",
                "100",
                "--requested-at",
                "2026-07-27T10:00:00Z",
                "--head-sha",
                head_sha,
                "--reviewer-login",
                "codex-reviewer[bot]",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_silent_cycle_ignores_old_and_human_events(self) -> None:
        result = self.inspect("silent.json")
        self.assertEqual(result["signals"]["mechanical_state"], "silent")
        self.assertEqual(result["signals"]["reviewer_event_count"], 0)
        self.assertEqual(result["signals"]["other_actor_event_count"], 1)

    def test_exact_request_acknowledgment_is_non_terminal(self) -> None:
        result = self.inspect("acknowledged.json")
        self.assertEqual(result["signals"]["mechanical_state"], "acknowledged")
        self.assertTrue(result["signals"]["acknowledged"])
        self.assertEqual(
            {item["content"] for item in result["signals"]["acknowledgments"]},
            {"eyes", "+1"},
        )

    def test_clean_verdict_is_identified_as_candidate(self) -> None:
        result = self.inspect("clean.json")
        self.assertEqual(result["signals"]["mechanical_state"], "clean_candidate")
        self.assertEqual(result["signals"]["clean_candidate_count"], 1)
        self.assertEqual(result["signals"]["response_candidate_count"], 0)

    def test_possible_finding_takes_precedence_over_clean(self) -> None:
        result = self.inspect("mixed.json")
        self.assertEqual(
            result["signals"]["mechanical_state"], "mixed_reviewer_response"
        )
        self.assertEqual(result["signals"]["clean_candidate_count"], 1)
        self.assertEqual(result["signals"]["response_candidate_count"], 1)

    def test_explicit_error_is_identified(self) -> None:
        result = self.inspect("error.json")
        self.assertEqual(result["signals"]["mechanical_state"], "explicit_error")
        self.assertEqual(result["signals"]["error_candidate_count"], 1)

    def test_empty_changes_requested_review_is_not_treated_as_silence(self) -> None:
        result = self.inspect("formal-state-only.json")
        self.assertEqual(result["signals"]["mechanical_state"], "reviewer_response")
        self.assertEqual(result["signals"]["response_candidate_count"], 1)

    def test_head_mismatch_precedes_review_signals(self) -> None:
        result = self.inspect("clean.json", head_sha="old-head")
        self.assertEqual(result["signals"]["mechanical_state"], "head_mismatch")
        self.assertFalse(result["pull_request"]["head_matches"])

    def test_merged_pr_is_terminal(self) -> None:
        result = self.inspect("merged.json")
        self.assertEqual(result["signals"]["mechanical_state"], "pr_terminal")


if __name__ == "__main__":
    unittest.main()
