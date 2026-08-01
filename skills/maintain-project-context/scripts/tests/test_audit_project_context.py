#!/usr/bin/env python3
"""Representative tests for the read-only context audit."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "audit_project_context.py"


class AuditProjectContextTest(unittest.TestCase):
    def test_largest_section_includes_root_preamble_before_first_h2(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            lines = ["# Service memory", ""]
            lines.extend(f"root fact {index}" for index in range(40))
            lines.extend(["## Small section", "current fact"])
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--canonical",
                    "memory/service.md",
                    "--include-content-signals",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["max_section_lines"], 42)

    def test_preserves_active_signals_inside_protected_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "active.md"
            source.write_text(
                """# Active memory

## 2026-01-01

First active entry.

## 2026-02-01

Second active entry.
""",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--active-root",
                    "memory/active.md",
                    "--protected",
                    "memory",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            largest = report["largest_files"][0]
            self.assertEqual(largest["location_state"], "active")
            self.assertTrue(largest["protected"])
            self.assertIn(
                "dated_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_reports_repeated_dated_headings_in_canonical_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "history.md"
            source.write_text(
                """# Service memory

## 2026-01-01

First historical entry.

## 2026-02-01

Second historical entry.
""",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--canonical",
                    "memory/history.md",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            largest = report["largest_files"][0]
            self.assertEqual(largest["dated_headings"], 2)
            self.assertIn(
                "dated_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_preserves_canonical_signals_inside_protected_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

## TASK-ONE-01 completed

Merged implementation history.
""",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--canonical",
                    "memory/service.md",
                    "--protected",
                    "memory",
                    "--task-id-regex",
                    r"TASK-[A-Z]+-\d+",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            largest = report["largest_files"][0]
            self.assertEqual(largest["location_state"], "canonical")
            self.assertTrue(largest["protected"])
            self.assertEqual(largest["task_headings"], 1)
            self.assertIn(
                "task_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_ignores_empty_superseded_by_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "adr.md"
            source.write_text(
                """# ADR-001: Current decision

- Status: accepted
- Supersedes: ADR-000
- Superseded by: `<ADR link or none>`

## Decision

Use the current boundary.
""",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--canonical",
                    "memory/adr.md",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            largest = report["largest_files"][0]
            self.assertEqual(largest["superseded_markers"], 0)
            hints = report["candidates"][0]["review_hints"] if report["candidates"] else []
            self.assertNotIn("superseded_signal", hints)

    def test_parent_section_includes_nested_heading_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            lines = ["# Service memory", "", "## Large domain"]
            for index in range(10):
                lines.extend([f"### Detail {index}", "fact", "fact"])
            lines.extend(["## Next domain", "current fact"])
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--canonical",
                    "memory/service.md",
                    "--include-content-signals",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 13)
            self.assertEqual(largest["max_section_lines"], 31)

    def test_does_not_treat_hyphenated_heading_as_task_without_project_regex(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

## Current-state behavior

The canonical description remains active.
""",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--canonical",
                    "memory/service.md",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            largest = report["largest_files"][0]
            self.assertEqual(largest["task_headings"], 0)
            candidate_hints = (
                report["candidates"][0]["review_hints"]
                if report["candidates"]
                else []
            )
            self.assertNotIn("task_chronology_signal", candidate_hints)

    def test_reports_mixed_task_chronology_without_mutating_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

## TASK-ONE-01 completed 2026-01-01

Merged implementation history.

## Current behavior

TODO: verify a still unresolved boundary.

## TASK-TWO-02 superseded

This decision was replaced by a newer source.
""",
                encoding="utf-8",
            )
            before = hashlib.sha256(source.read_bytes()).hexdigest()

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--canonical",
                    "memory/service.md",
                    "--task-id-regex",
                    r"TASK-[A-Z]+-\d+",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["schema_version"], 2)
            self.assertTrue(report["read_only"])
            largest = report["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 4)
            self.assertEqual(largest["task_headings"], 2)
            self.assertEqual(largest["task_id_count"], 2)
            self.assertGreaterEqual(largest["max_section_lines"], 3)
            candidate = report["candidates"][0]
            self.assertIn("task_chronology_signal", candidate["review_hints"])
            self.assertIn("mixed_lifecycle_signal", candidate["review_hints"])
            after = hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
