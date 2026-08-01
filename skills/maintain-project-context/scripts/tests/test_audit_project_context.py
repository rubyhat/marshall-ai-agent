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
    def test_fenced_code_block_as_first_list_content_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

- ```text
  ## TASK_123 completed
  TODO blocked
  ```

## Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["unresolved_markers"], 0)

    def test_fenced_code_block_inside_block_quote_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

> ```text
> ## TASK_123 completed
> TODO blocked
> ```

## Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["unresolved_markers"], 0)

    def test_type_7_html_tag_does_not_interrupt_list_paragraph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

- Active list paragraph
<span>
## TASK_123 completed

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["completed_markers"], 1)

    def test_multiline_reference_definitions_feed_link_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            target = memory / "target.md"
            source.write_text(
                """# Source

[Existing guide][guide]
[Missing guide][missing]

[guide]:
  target.md
[missing]:
  missing.md
""",
                encoding="utf-8",
            )
            target.write_text("# Target\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--canonical",
                    "memory",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--top",
                    "10",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            by_path = {item["path"]: item for item in report["largest_files"]}
            self.assertEqual(
                by_path["memory/source.md"]["broken_targets"],
                ["memory/missing.md"],
            )
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)

    def test_multiline_reference_definition_does_not_cross_container(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            source.write_text(
                """# Source

[Missing guide][guide]

[guide]:
>   missing.md TODO
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["broken_targets"], [])
            self.assertEqual(largest["unresolved_markers"], 1)

    def test_html_comment_block_closing_line_stays_non_structural(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

<!--
hidden example
--> ## TASK_123 completed

## Current behavior

TODO: verify current behavior.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["unresolved_markers"], 1)

    def test_multiline_code_span_inside_block_quote_is_masked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

> Example `TASK_123
> completed`

> Lazy continuation `TASK_456
completed`

- > Nested example `TASK_789
  > completed`

TODO: verify current behavior.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["unresolved_markers"], 1)
            hints = report["candidates"][0]["review_hints"] if report["candidates"] else []
            self.assertNotIn("mixed_lifecycle_signal", hints)

    def test_reference_style_links_feed_broken_and_incoming_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            target = memory / "target.md"
            source.write_text(
                """# Source

[Existing guide][guide]
[Missing guide][missing]

[guide]: target.md
[missing]: missing.md
""",
                encoding="utf-8",
            )
            target.write_text("# Target\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--canonical",
                    "memory",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--top",
                    "10",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            by_path = {item["path"]: item for item in report["largest_files"]}
            self.assertEqual(
                by_path["memory/source.md"]["broken_targets"],
                ["memory/missing.md"],
            )
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)

    def test_mixed_space_tab_indentation_is_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

 \t## TASK_123 completed
  \tTODO: example only.

## Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["unresolved_markers"], 0)

    def test_indented_code_inside_block_quote_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

>     ## TASK_123 completed
>     TODO blocked

## Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["unresolved_markers"], 0)

    def test_external_uri_schemes_are_not_broken_project_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            source.write_text(
                """# Source

[FTP](ftp://example.com/file)
[Telephone](tel:+123)
[Uppercase HTTPS](HTTPS://example.com/path)
[Custom](vscode://workspace/file)
[Protocol relative](//example.com/file)
[Missing internal](missing.md)
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["broken_targets"], ["memory/missing.md"])

    def test_balanced_parentheses_in_inline_link_target_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            docs = root / "docs"
            memory.mkdir()
            docs.mkdir()
            source = memory / "source.md"
            target = docs / "a(b).md"
            source.write_text(
                """# Source

[Existing guide](../docs/a(b).md?view=full#current)
[Missing guide](../docs/missing(c).md)
""",
                encoding="utf-8",
            )
            target.write_text("# Target\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--scope",
                    "docs",
                    "--canonical",
                    "memory",
                    "--canonical",
                    "docs",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--top",
                    "10",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            by_path = {
                item["path"]: item
                for item in json.loads(result.stdout)["largest_files"]
            }
            self.assertEqual(
                by_path["memory/source.md"]["broken_targets"],
                ["docs/missing(c).md"],
            )
            self.assertEqual(by_path["docs/a(b).md"]["incoming_links"], 1)

    def test_raw_html_blocks_inside_markdown_containers_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

> <script>
> ## TASK_123 completed
> TODO blocked
> </script>

- <pre>
  ## TASK_456 completed
  FIXME superseded
  </pre>

## Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["unresolved_markers"], 0)
            self.assertEqual(largest["superseded_markers"], 0)

    def test_html_block_ends_on_quoted_blank_and_container_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

> <section>
> hidden completed
>
> TASK_123 completed

> <script>
> hidden completed
## TASK_456 completed

TODO blocked
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123", "TASK_456"])
            self.assertEqual(largest["completed_markers"], 2)
            self.assertEqual(largest["unresolved_markers"], 2)

    def test_excess_list_padding_remains_indented_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

-     ## TASK_123 completed

## Current behavior
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)

    def test_multiline_inline_links_feed_broken_and_incoming_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            target = memory / "TODO.md"
            source.write_text(
                """# Source

[Existing guide](
TODO.md
)

[Missing guide](
missing.md
)

> [Quoted missing](
> quoted-missing.md) TODO completed
""",
                encoding="utf-8",
            )
            target.write_text("# Target\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--canonical",
                    "memory",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--top",
                    "10",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            by_path = {
                item["path"]: item
                for item in report["largest_files"]
            }
            self.assertEqual(
                by_path["memory/source.md"]["broken_targets"],
                ["memory/missing.md", "memory/quoted-missing.md"],
            )
            self.assertEqual(by_path["memory/TODO.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/source.md"]["unresolved_markers"], 1)
            self.assertEqual(by_path["memory/source.md"]["completed_markers"], 1)
            candidate_by_path = {
                item["path"]: item for item in report["candidates"]
            }
            self.assertIn(
                "mixed_lifecycle_signal",
                candidate_by_path["memory/source.md"]["review_hints"],
            )

    def test_ordered_list_paragraph_continuation_is_not_indented_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

100. Canonical fact
     TODO completed
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["completed_markers"], 1)
            self.assertEqual(largest["unresolved_markers"], 1)

    def test_interrupting_list_preserves_nested_task_heading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

Active paragraph.
- ## TASK_123 completed
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_id_count"], 1)
            self.assertEqual(largest["completed_markers"], 1)
            self.assertIn(
                "task_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_loose_ordered_list_paragraph_keeps_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

100. Canonical fact

     TODO completed
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
            self.assertEqual(largest["completed_markers"], 1)
            self.assertEqual(largest["unresolved_markers"], 1)
            self.assertIn(
                "mixed_lifecycle_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_type_7_html_block_starts_after_entering_new_container(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

Active paragraph.
> <span>
> ## TASK_123 completed
>

## Current behavior
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)

    def test_invalid_type_7_closer_and_lowercase_cdata_stay_visible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

</span bogus>
## TASK_123 completed

<![cdata[
## TASK_456 completed
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 3)
            self.assertEqual(largest["task_headings"], 2)
            self.assertEqual(largest["task_ids"], ["TASK_123", "TASK_456"])
            self.assertEqual(largest["completed_markers"], 2)

    def test_headings_inside_markdown_containers_are_counted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

> ## TASK_123 completed
>
> TASK_456 completed
> ------------------

- ## TASK_789 completed

- TASK_012 completed
  ------------------
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 5)
            self.assertEqual(largest["task_headings"], 4)
            self.assertEqual(
                largest["task_ids"],
                ["TASK_012", "TASK_123", "TASK_456", "TASK_789"],
            )
            self.assertIn(
                "task_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_heading_inside_combined_markdown_containers_is_counted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

- > ## TASK_123 completed

> - ## TASK_456 completed
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 3)
            self.assertEqual(largest["task_headings"], 2)
            self.assertEqual(largest["task_ids"], ["TASK_123", "TASK_456"])
            self.assertIn(
                "task_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_setext_heading_inside_list_wrapped_quote_is_counted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

- > TASK_123 completed
  > ------------------
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertIn(
                "task_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_html_comment_ends_when_markdown_container_exits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

> <!-- hidden completed
## TASK_123 completed

- <!-- hidden blocked
## TASK_456 completed

TODO blocked
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 3)
            self.assertEqual(largest["task_headings"], 2)
            self.assertEqual(largest["task_ids"], ["TASK_123", "TASK_456"])
            self.assertEqual(largest["completed_markers"], 2)
            self.assertEqual(largest["unresolved_markers"], 2)

    def test_reference_definitions_inside_block_quote_feed_link_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            target = memory / "target.md"
            source.write_text(
                """# Source

> [existing]: target.md
> [missing]:
>   missing.md

[Existing guide][existing]
[Missing guide][missing]
""",
                encoding="utf-8",
            )
            target.write_text("# Target\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--canonical",
                    "memory",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--top",
                    "10",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            by_path = {
                item["path"]: item
                for item in json.loads(result.stdout)["largest_files"]
            }
            self.assertEqual(
                by_path["memory/source.md"]["broken_targets"],
                ["memory/missing.md"],
            )
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)

    def test_raw_html_opener_inside_multiline_comment_does_not_leak_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

<!--
<script>
-->

## TASK_123 completed

TODO: verify current behavior.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["completed_markers"], 1)
            self.assertEqual(largest["unresolved_markers"], 1)

    def test_multiline_code_span_stops_before_html_comment_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

Syntax: `unclosed example
<!-- ` not a code-span closer -->

## TASK_123 completed
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["completed_markers"], 1)

    def test_multiline_code_span_stops_before_html_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

Syntax: `unclosed example
<pre>
` not a code-span closer
</pre>

## TASK_123 completed

TODO: verify current behavior.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["completed_markers"], 1)
            self.assertEqual(largest["unresolved_markers"], 1)

    def test_type_7_html_tag_does_not_interrupt_active_paragraph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

Active paragraph.
<span>
## TASK_123 completed

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["completed_markers"], 1)

    def test_type_7_html_tag_after_blank_starts_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

<span>
## TASK_123 completed
</span>

## Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)

    def test_thematic_break_resets_multiline_setext_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

TASK_123 completed
* * *
Current behavior
----------------

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            hints = report["candidates"][0]["review_hints"] if report["candidates"] else []
            self.assertNotIn("task_chronology_signal", hints)

    def test_raw_html_blocks_do_not_create_structure_or_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

<pre>
## TASK_123 completed
TODO: example only.
</pre>

<div>
## TASK_456 superseded
</div>

## Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["superseded_markers"], 0)
            self.assertEqual(largest["unresolved_markers"], 0)

    def test_multiline_code_span_does_not_create_semantic_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

Syntax: `TASK_123
completed`

TODO: verify the current prose boundary.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["unresolved_markers"], 1)
            hints = report["candidates"][0]["review_hints"] if report["candidates"] else []
            self.assertNotIn("mixed_lifecycle_signal", hints)

    def test_comment_and_code_delimiters_do_not_cross_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

Text <!-- unfinished ` --> then `code`

## TASK_123 completed

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["completed_markers"], 1)

    def test_multiline_setext_heading_preserves_all_semantic_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

TASK_123 2026-01-01
completed
---------

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["dated_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertIn(
                "task_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_inline_code_does_not_create_task_or_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

## Format `TASK_123 completed`

## Literal backslash `TASK_456 completed\`

TODO: verify the current prose boundary.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            hints = report["candidates"][0]["review_hints"] if report["candidates"] else []
            self.assertNotIn("task_chronology_signal", hints)
            self.assertNotIn("mixed_lifecycle_signal", hints)

    def test_reference_definition_is_not_setext_task_heading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

[TASK_123]: /tasks/123
---

## Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            hints = report["candidates"][0]["review_hints"] if report["candidates"] else []
            self.assertNotIn("task_chronology_signal", hints)

    def test_link_destination_does_not_create_lifecycle_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            target = memory / "completed.md"
            target.write_text("# Rollout notes\n", encoding="utf-8")
            source.write_text(
                """# Current behavior

TODO: verify the current boundary.

[Rollout notes](completed.md)
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
                    "memory/service.md",
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
            self.assertEqual(largest["unresolved_markers"], 1)
            self.assertEqual(largest["completed_markers"], 0)
            hints = report["candidates"][0]["review_hints"] if report["candidates"] else []
            self.assertNotIn("mixed_lifecycle_signal", hints)

    def test_reference_style_task_link_counts_as_task_heading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

## [TASK_123][ticket] completed

Historical implementation entry.

[ticket]: https://tracker.example/tasks/123
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["task_headings"], 1)
            self.assertIn(
                "task_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_excludes_html_comments_from_structure_and_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

<!--
## TASK_123 completed
TODO: obsolete draft.
[internal](missing.md)
-->

## Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["unresolved_markers"], 0)
            self.assertEqual(largest["broken_targets"], [])

    def test_unmatched_leading_thematic_break_does_not_hide_document(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """---

# TASK_123 completed

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 1)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])

    def test_fence_with_trailing_text_does_not_close_code_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

```markdown
```not-a-close
## TASK_123 completed
```

## Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)

    def test_backtick_in_info_string_does_not_open_fenced_code_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

```bad`info

## TASK_123 completed

TODO blocked
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            largest = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["completed_markers"], 1)
            self.assertEqual(largest["unresolved_markers"], 2)

    def test_list_item_before_thematic_break_is_not_setext_heading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

- TASK_123 completed
---

## Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            hints = report["candidates"][0]["review_hints"] if report["candidates"] else []
            self.assertNotIn("task_chronology_signal", hints)

    def test_excludes_yaml_front_matter_from_structure_and_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """---
title: Service memory
task: TASK_123
status: completed
---

# Current behavior

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 1)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            hints = report["candidates"][0]["review_hints"] if report["candidates"] else []
            self.assertNotIn("task_chronology_signal", hints)

    def test_configured_task_id_inside_markdown_link_counts_as_task_heading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

## [TASK_123](https://tracker.example/tasks/123) completed

Historical implementation entry.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["task_headings"], 1)
            self.assertIn(
                "task_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_setext_headings_contribute_to_structure_and_task_chronology(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """Service memory
==============

TASK_123 completed 2026-01-01
-----------------------------

Historical implementation entry.

Current behavior
----------------

Canonical fact.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 3)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["dated_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertLess(largest["max_section_lines"], largest["lines"])
            self.assertIn(
                "task_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_configured_task_id_regex_accepts_underscore_syntax(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

## TASK_123 completed

Historical implementation entry.
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
                    "--task-id-regex",
                    r"TASK_[0-9]+",
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
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["task_headings"], 1)
            self.assertIn(
                "task_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_ignores_markdown_code_blocks_for_structure_and_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

## Current behavior

Canonical fact.

```markdown
## TASK-999 completed
TODO: example only.
```

    ## TASK-888 superseded
    FIXME: indented example only.

Canonical conclusion.
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
                    "--task-id-regex",
                    r"TASK-[0-9]+",
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
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["superseded_markers"], 0)
            self.assertEqual(largest["unresolved_markers"], 0)
            hints = report["candidates"][0]["review_hints"] if report["candidates"] else []
            self.assertNotIn("task_chronology_signal", hints)
            self.assertNotIn("mixed_lifecycle_signal", hints)

    def test_largest_section_includes_root_block_after_later_h1(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "mixed.md"
            lines = ["# First domain", "## Small section", "current fact", "# Second domain"]
            lines.extend(f"legacy fact {index}" for index in range(50))
            lines.extend(["## Final small section", "current fact"])
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
                    "memory/mixed.md",
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
            self.assertEqual(largest["max_section_lines"], 51)

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
