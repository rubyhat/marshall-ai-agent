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
[Titled guide][titled]
[Spanning title][spanning]

[guide]:
  target.md
[missing]:
  missing.md
[titled]: target.md
  "TODO completed"
[spanning]: target.md "TODO
completed"
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
            self.assertEqual(by_path["memory/source.md"]["unresolved_markers"], 0)
            self.assertEqual(by_path["memory/source.md"]["completed_markers"], 0)

    def test_inline_link_can_span_more_than_seven_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            continuation = "\n".join(f"line {index}" for index in range(1, 9))
            (memory / "source.md").write_text(
                f"[guide\n{continuation}\n](target.md)\n",
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_reference_root_counts_cross_scope_links_without_expanding_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history = root / "history"
            canonical = root / "canonical"
            history.mkdir()
            canonical.mkdir()
            target = history / "completed.md"
            source = canonical / "map.md"
            target.write_text("# Completed task\n", encoding="utf-8")
            source.write_text(
                "# Context map\n\n[Historical evidence](../history/completed.md)\n",
                encoding="utf-8",
            )

            base_command = [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(root),
                "--scope",
                "history",
                "--historical-root",
                "history",
                "--include-content-signals",
                "--candidate-limit",
                "0",
                "--format",
                "json",
            ]
            scoped_result = subprocess.run(
                base_command,
                check=False,
                capture_output=True,
                text=True,
            )
            configured_result = subprocess.run(
                [
                    *base_command[:-2],
                    "--reference-root",
                    "canonical",
                    *base_command[-2:],
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(scoped_result.returncode, 0, scoped_result.stderr)
            scoped_report = json.loads(scoped_result.stdout)
            scoped_target = scoped_report["largest_files"][0]
            self.assertEqual(scoped_target["incoming_links"], 0)
            self.assertEqual(
                scoped_target["incoming_links_coverage"], "scoped_only_incomplete"
            )
            self.assertFalse(
                scoped_report["link_coverage"]["complete_for_declared_roots"]
            )

            self.assertEqual(configured_result.returncode, 0, configured_result.stderr)
            configured_report = json.loads(configured_result.stdout)
            configured_target = configured_report["largest_files"][0]
            self.assertEqual(configured_report["summary"]["files"], 1)
            self.assertEqual(
                [item["path"] for item in configured_report["largest_files"]],
                ["history/completed.md"],
            )
            self.assertEqual(configured_target["incoming_links"], 1)
            self.assertEqual(
                configured_target["incoming_links_coverage"],
                "declared_reference_roots",
            )
            self.assertTrue(
                configured_report["link_coverage"]["complete_for_declared_roots"]
            )
            self.assertEqual(
                configured_report["link_coverage"]["configuration_match"],
                "not_checked_by_script",
            )
            self.assertEqual(
                configured_report["link_coverage"]["external_source_files_scanned"],
                1,
            )

    def test_self_reference_does_not_count_as_incoming_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                "# Source\n\n[Self](source.md)\n",
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
                    "--reference-root",
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
            source = report["largest_files"][0]
            self.assertEqual(source["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_oversized_content_source_is_skipped_with_incomplete_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "# Source\n\n[Target](target.md)\n" + ("x" * 128),
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
                    "--max-content-bytes",
                    "64",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)
            self.assertNotIn("lines", by_path["memory/source.md"])
            self.assertEqual(report["summary"]["skipped"]["content_too_large"], 1)
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertFalse(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_invalid_utf8_source_downgrades_reference_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "café.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_bytes(
                b"[Target](../context/caf\xe9.md)\n"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                report["summary"]["skipped"]["reference_content_decode_error"],
                1,
            )
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertFalse(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_inline_link_after_unmatched_opening_bracket_is_counted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                "[ note [target](../context/target.md)\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
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
            target = report["largest_files"][0]
            self.assertEqual(target["path"], "context/target.md")
            self.assertEqual(target["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_bare_inline_destinations_reject_unescaped_angle_characters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "foo<bar.md").write_text("# Less than\n", encoding="utf-8")
            (context / "foo>bar.md").write_text("# Greater than\n", encoding="utf-8")
            (references / "source.md").write_text(
                """[fake-lt](../context/foo<bar.md)
[fake-gt](../context/foo>bar.md)
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
                    "context",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
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
            self.assertEqual(by_path["context/foo<bar.md"]["incoming_links"], 0)
            self.assertEqual(by_path["context/foo>bar.md"]["incoming_links"], 0)
            self.assertFalse(
                report["link_coverage"]["complete_for_declared_roots"]
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"], 1
            )

    def test_bare_inline_destination_rejects_backslash_before_space(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "foo\\ bar.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "[fake](foo\\ bar.md)\n",
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/foo\\ bar.md"]["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_collapsed_reference_after_unmatched_opener_is_counted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                """[ note [target][]

[target]: target.md
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_reference_root_counts_local_targets_in_raw_html(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history = root / "history"
            references = root / "references"
            history.mkdir()
            references.mkdir()
            (history / "target.md").write_text("# Target\n", encoding="utf-8")
            (history / "image.md").write_text("# Image\n", encoding="utf-8")
            (history / "object.md").write_text("# Object\n", encoding="utf-8")
            (history / "srcset.md").write_text("# Srcset\n", encoding="utf-8")
            (history / "background.md").write_text(
                "# Background\n", encoding="utf-8"
            )
            (history / "ping.md").write_text("# Ping\n", encoding="utf-8")
            (history / "svg-image.md").write_text("# SVG image\n", encoding="utf-8")
            (history / "svg-use.md").write_text("# SVG use\n", encoding="utf-8")
            (references / "source.md").write_text(
                """<a href="../history/target.md">Target</a>
<img src='../history/image.md' alt="Image">
<object data="../history/object.md"></object>
<img srcset="data:image/png;base64,AAAA 1x, ../history/srcset.md 2x">
<body background="../history/background.md"></body>
<a href="https://example.invalid" ping="../history/ping.md https://example.invalid/ping">Ping</a>
<svg><image href="../history/svg-image.md"></image></svg>
<svg><use xlink:href="../history/svg-use.md"></use></svg>
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
                    "history",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
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
            self.assertEqual(by_path["history/target.md"]["incoming_links"], 1)
            self.assertEqual(by_path["history/image.md"]["incoming_links"], 1)
            self.assertEqual(by_path["history/object.md"]["incoming_links"], 1)
            self.assertEqual(by_path["history/srcset.md"]["incoming_links"], 1)
            self.assertEqual(by_path["history/background.md"]["incoming_links"], 1)
            self.assertEqual(by_path["history/ping.md"]["incoming_links"], 1)
            self.assertEqual(by_path["history/svg-image.md"]["incoming_links"], 1)
            self.assertEqual(by_path["history/svg-use.md"]["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_raw_html_scan_ignores_markdown_link_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "page.md").write_text("# Page\n", encoding="utf-8")
            (memory / "hidden.md").write_text("# Hidden\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "[Guide](page.md \"<a href='hidden.md'>\")\n",
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/page.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/hidden.md"]["incoming_links"], 0)

    def test_html_target_parser_does_not_cross_paragraph_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "Notes <a\n\nhref=\"target.md\">\n",
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)
            self.assertEqual(
                by_path["memory/target.md"]["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )

    def test_iframe_srcdoc_downgrades_reference_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                '<iframe srcdoc="<a href=\'target.md\'>target</a>"></iframe>\n',
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
                    "--reference-root",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"],
                1,
            )

    def test_inert_template_link_does_not_count_as_incoming(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                '<template><a href="target.md">target</a></template>\n',
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
                    "--reference-root",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_self_closing_template_syntax_still_opens_inert_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                '<template/><a href="target.md">target</a></template>\n',
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
                    "--reference-root",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_self_closing_raw_text_inside_template_remains_inert(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                (
                    "<template><script/></template></script>"
                    '<a href="target.md">target</a></template>\n'
                ),
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
                    "--reference-root",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_meta_refresh_downgrades_reference_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    '<meta http-equiv="refresh" '
                    'content="0; url=../context/target.md">\n'
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"],
                1,
            )

    def test_malformed_raw_html_does_not_create_incoming_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                '<a =bad href="target.md">literal text\n',
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)
            self.assertEqual(
                by_path["memory/target.md"]["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"], 1
            )

    def test_inline_non_element_html_tokens_do_not_create_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "service.md").write_text(
                """# Service memory

completed <? TODO ?> <!DECL TODO> <![CDATA[TODO]]>
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
            self.assertEqual(largest["unresolved_markers"], 0)

    def test_raw_html_attributes_do_not_create_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                '<a href="target.md" title="TODO completed">Guide</a>\n',
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/source.md"]["unresolved_markers"], 0)
            self.assertEqual(by_path["memory/source.md"]["completed_markers"], 0)

    def test_inline_raw_text_bodies_do_not_create_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                (
                    "Completed <script>TODO</script>\n"
                    "Visible <style>\n"
                    "FIXME </stylesheet> PENDING\n"
                    "</style> text\n"
                ),
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 1)
            self.assertEqual(source["unresolved_markers"], 0)

    def test_self_closing_script_syntax_still_opens_opaque_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                "Completed <script/>TODO</script>\n",
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 1)
            self.assertEqual(source["unresolved_markers"], 0)

    def test_inline_textarea_value_remains_visible_to_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                "Completed <textarea>TODO</textarea>\n",
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 1)
            self.assertEqual(source["unresolved_markers"], 1)

    def test_inline_title_value_is_opaque_to_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                "Completed <title>TODO</title>\n",
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 1)
            self.assertEqual(source["unresolved_markers"], 0)

    def test_inline_iframe_fallback_is_opaque_to_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                "Completed <iframe>TODO</iframe>\n",
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 1)
            self.assertEqual(source["unresolved_markers"], 0)

    def test_inline_legacy_fallbacks_are_opaque_to_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                (
                    "Completed <noframes>TODO</noframes>\n"
                    "Completed <noembed>FIXME</noembed>\n"
                ),
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 2)
            self.assertEqual(source["unresolved_markers"], 0)

    def test_inert_template_body_does_not_create_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                "<template>TODO completed</template>\n",
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 0)
            self.assertEqual(source["unresolved_markers"], 0)

    def test_shadowrootmode_word_in_other_attribute_keeps_template_inert(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                'Completed <template title="shadowrootmode">TODO</template>\n',
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 1)
            self.assertEqual(source["unresolved_markers"], 0)

    def test_duplicate_shadowrootmode_honors_first_attribute(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                (
                    "Completed <template shadowrootmode=\"invalid\" "
                    "shadowrootmode=\"open\">TODO</template>\n"
                ),
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 1)
            self.assertEqual(source["unresolved_markers"], 0)

    def test_nested_template_bodies_remain_opaque_to_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                (
                    "Completed <template><template>x</template>"
                    "TODO</template>\n"
                ),
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 1)
            self.assertEqual(source["unresolved_markers"], 0)

    def test_template_raw_text_keeps_template_close_opaque_to_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                (
                    "Completed <template><script></template></script>"
                    "TODO</template>\n"
                ),
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 1)
            self.assertEqual(source["unresolved_markers"], 0)

    def test_foreign_template_inside_inert_content_does_not_hide_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                "Completed <template><svg><template/></svg></template>TODO\n",
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
                    "memory/source.md",
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
            source = json.loads(result.stdout)["largest_files"][0]
            self.assertEqual(source["completed_markers"], 1)
            self.assertEqual(source["unresolved_markers"], 1)

    def test_html_backslash_target_downgrades_reference_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                r'<a href="../context\target.md">target</a>' + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            self.assertFalse(
                report["link_coverage"]["complete_for_declared_roots"]
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"],
                1,
            )

    def test_unparsed_style_body_downgrades_reference_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    "<style>body { background: "
                    "url('../context/target.md') }</style>\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"],
                1,
            )

    def test_unparsed_style_attribute_downgrades_reference_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    '<div style="background-image: '
                    "image-set('../context/target.md' 1x)\">Example</div>\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"],
                1,
            )

    def test_raw_html_target_is_not_entity_decoded_twice(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "foo&num;.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                '<a href="../context/foo&amp;num;.md">Target</a>\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
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
            target = report["largest_files"][0]
            self.assertEqual(target["path"], "context/foo&num;.md")
            self.assertEqual(target["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_first_base_href_follows_source_order_across_inline_and_block_html(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            one = context / "one"
            two = context / "two"
            references = root / "references"
            one.mkdir(parents=True)
            two.mkdir(parents=True)
            references.mkdir()
            (one / "target.md").write_text("# One\n", encoding="utf-8")
            (two / "target.md").write_text("# Two\n", encoding="utf-8")
            (references / "source.md").write_text(
                """Intro <base href="../context/one/">

<base href="../context/two/">
<a href="target.md">Target</a>
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
                    "context",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
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
            self.assertEqual(by_path["context/one/target.md"]["incoming_links"], 1)
            self.assertEqual(by_path["context/two/target.md"]["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_first_base_href_applies_to_targets_that_precede_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            nested = context / "nested"
            references = root / "references"
            nested.mkdir(parents=True)
            references.mkdir()
            (nested / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    '<a href="target.md">Target</a>\n'
                    '<base href="../context/nested/">\n'
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_base_href_is_resolution_context_not_incoming_resource(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            nested = context / "nested"
            references = root / "references"
            context.mkdir()
            nested.mkdir()
            references.mkdir()
            (context / "base-only.md").write_text("# Base\n", encoding="utf-8")
            (context / "actual.md").write_text("# Actual\n", encoding="utf-8")
            (nested / "nested.md").write_text("# Nested\n", encoding="utf-8")
            (references / "file-base.md").write_text(
                """<base href="../context/base-only.md">
<a href="actual.md">Actual</a>
""",
                encoding="utf-8",
            )
            (references / "directory-base.md").write_text(
                """<base href="../context/nested/">
<a href="nested.md">Nested</a>
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
                    "context",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
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
            self.assertEqual(by_path["context/base-only.md"]["incoming_links"], 0)
            self.assertEqual(by_path["context/actual.md"]["incoming_links"], 1)
            self.assertEqual(
                by_path["context/nested/nested.md"]["incoming_links"], 1
            )
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_raw_text_html_block_body_does_not_create_incoming_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "script.md").write_text("# Script\n", encoding="utf-8")
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    '<script src="../context/script.md">const template = '
                    "'<a href=\"../context/target.md\">';</script>\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
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
            self.assertEqual(by_path["context/script.md"]["incoming_links"], 1)
            self.assertEqual(by_path["context/target.md"]["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_html_script_href_is_not_counted_as_an_incoming_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                '<script href="../context/target.md"></script>\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )

    def test_html_namespace_svg_element_does_not_create_incoming_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                '<use href="../context/target.md"></use>\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )

    def test_html_image_alias_creates_incoming_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                '<image src="../context/target.md">\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_svg_namespace_element_creates_incoming_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    "<svg>\n"
                    '<use href="../context/target.md"></use>\n'
                    "</svg>\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_svg_template_is_not_treated_as_inert_html_template(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    "<svg><template>"
                    '<use href="../context/target.md"></use>'
                    "</template></svg>\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_svg_html_integration_point_downgrades_reference_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    "<svg><foreignObject>"
                    '<use href="../context/target.md"></use>'
                    "</foreignObject></svg>\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )

    def test_svg_breakout_reprocesses_following_elements_as_html(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                '<svg><p><use href="../context/target.md"></use>\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )

    def test_legacy_frame_src_creates_incoming_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                '<frameset><frame src="../context/target.md"></frameset>\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_form_control_resources_follow_effective_type(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            target_names = (
                "text-src.md",
                "text-action.md",
                "image-src.md",
                "image-action.md",
                "submit-action.md",
                "button-action.md",
                "invalid-button-action.md",
                "reset-action.md",
                "padded-reset-action.md",
                "padded-image-src.md",
                "padded-image-action.md",
            )
            for target_name in target_names:
                (context / target_name).write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                """<input type="text" src="../context/text-src.md" formaction="../context/text-action.md">
<input type="image" src="../context/image-src.md" formaction="../context/image-action.md">
<input type="submit" formaction="../context/submit-action.md">
<button formaction="../context/button-action.md">Submit</button>
<button type="invalid" formaction="../context/invalid-button-action.md">Submit</button>
<button type="reset" formaction="../context/reset-action.md">Reset</button>
<button type=" reset " formaction="../context/padded-reset-action.md">Submit</button>
<input type=" image " src="../context/padded-image-src.md" formaction="../context/padded-image-action.md">
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
                    "context",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
                    "--candidate-limit",
                    "0",
                    "--top",
                    "20",
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
            self.assertEqual(by_path["context/text-src.md"]["incoming_links"], 0)
            self.assertEqual(by_path["context/text-action.md"]["incoming_links"], 0)
            for target_name in (
                "image-src.md",
                "image-action.md",
                "submit-action.md",
                "button-action.md",
                "invalid-button-action.md",
                "padded-reset-action.md",
            ):
                self.assertEqual(
                    by_path[f"context/{target_name}"]["incoming_links"], 1
                )
            self.assertEqual(by_path["context/reset-action.md"]["incoming_links"], 0)
            self.assertEqual(
                by_path["context/padded-image-src.md"]["incoming_links"], 0
            )
            self.assertEqual(
                by_path["context/padded-image-action.md"]["incoming_links"], 0
            )
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_pre_block_downgrades_coverage_for_unparsed_nested_html(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                '<pre><a href="../context/target.md">target</a></pre>\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"],
                1,
            )

    def test_raw_text_closing_suffix_collects_rendered_sibling_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (context / "stale.md").write_text("# Stale\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    "<script>const hidden = "
                    "'<a href=\"../context/stale.md\">stale</a>';"
                    "</script><a href=\"../context/target.md\">target</a>\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
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
            self.assertEqual(by_path["context/target.md"]["incoming_links"], 1)
            self.assertEqual(by_path["context/stale.md"]["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_attributed_raw_text_closer_downgrades_reference_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    "<script>\n"
                    '</script foo><a href="../context/target.md">target</a>\n'
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            self.assertFalse(
                report["link_coverage"]["complete_for_declared_roots"]
            )
            self.assertEqual(
                report["link_coverage"]["status"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"],
                1,
            )

    def test_fragmented_raw_text_closer_downgrades_reference_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    "Intro <script>\n"
                    "</script\n"
                    '><a href="../context/target.md">target</a>\n'
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            self.assertFalse(
                report["link_coverage"]["complete_for_declared_roots"]
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"],
                1,
            )

    def test_multiline_script_body_does_not_create_incoming_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    "Intro <script>\n"
                    '<a href="../context/target.md">hidden</a>\n'
                    "</script>\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_multiline_template_raw_text_preserves_inert_template_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    "Intro <template><script>\n"
                    "</template></script>\n"
                    '<a href="../context/target.md">hidden</a>\n'
                    "</template>\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--reference-root",
                    "references",
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
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_raw_text_closing_suffix_comment_is_opaque(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                (
                    "<script>const value = 1;</script>"
                    "<!-- <a href=\"../context/target.md\">"
                    "TODO completed</a> -->\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "context",
                    "--scope",
                    "references",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
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
            self.assertEqual(by_path["context/target.md"]["incoming_links"], 0)
            self.assertEqual(
                by_path["references/source.md"]["unresolved_markers"], 0
            )
            self.assertEqual(
                by_path["references/source.md"]["completed_markers"], 0
            )
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_comment_inside_ordinary_html_block_is_opaque(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            references = root / "references"
            context.mkdir()
            references.mkdir()
            (context / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.md").write_text(
                """<div>
<!-- <a href="../context/target.md">TODO completed</a> -->
</div>

Visible content.
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
                    "context",
                    "--scope",
                    "references",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
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
            self.assertEqual(by_path["context/target.md"]["incoming_links"], 0)
            self.assertEqual(
                by_path["references/source.md"]["unresolved_markers"], 0
            )
            self.assertEqual(
                by_path["references/source.md"]["completed_markers"], 0
            )
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_duplicate_raw_html_resource_attribute_uses_first_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "page.md").write_text("# Page\n", encoding="utf-8")
            (memory / "stale.md").write_text("# Stale\n", encoding="utf-8")
            (memory / "source.md").write_text(
                '<a href="page.md" href="stale.md">Guide</a>\n',
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/page.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/stale.md"]["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_incomplete_html_like_text_remains_visible_to_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                "Notes <span TODO\n",
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
                    "memory/source.md",
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
            self.assertEqual(largest["unresolved_markers"], 1)

    def test_invalid_inline_comment_opener_remains_visible_to_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "source.md").write_text(
                "# Source\n\nNotes <!--> TODO\n",
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
                    "memory/source.md",
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
            self.assertEqual(largest["unresolved_markers"], 1)

    def test_inline_html_bracket_does_not_close_markdown_link_label(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "page.md").write_text("# Page\n", encoding="utf-8")
            (memory / "source.md").write_text(
                '[Guide <span title="]">hidden</span>](page.md)\n',
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/page.md"]["incoming_links"], 1)

    def test_reference_root_symlink_marks_link_coverage_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history = root / "history"
            references = root / "references"
            external = root / "external"
            history.mkdir()
            references.mkdir()
            external.mkdir()
            (history / "target.md").write_text("# Target\n", encoding="utf-8")
            source = external / "source.md"
            source.write_text(
                "[Target](../history/target.md)\n",
                encoding="utf-8",
            )
            try:
                (references / "source.md").symlink_to(source)
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "history",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                target["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertFalse(
                report["link_coverage"]["complete_for_declared_roots"]
            )
            self.assertEqual(report["summary"]["skipped"]["reference_symlink"], 1)

    def test_candidate_scope_records_symlink_and_excluded_directory_skips(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            vendor = memory / "vendor"
            external = root / "external.md"
            memory.mkdir()
            vendor.mkdir()
            (memory / "visible.md").write_text("# Visible\n", encoding="utf-8")
            (vendor / "hidden.md").write_text("# Hidden\n", encoding="utf-8")
            external.write_text("# External\n", encoding="utf-8")
            try:
                (memory / "linked.md").symlink_to(external)
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["summary"]["files"], 1)
            self.assertEqual(report["summary"]["skipped"]["scope_symlink"], 1)
            self.assertEqual(
                report["summary"]["skipped"]["scope_excluded_dir"], 1
            )

    def test_reference_root_excluded_subtree_marks_coverage_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history = root / "history"
            references = root / "references"
            vendor = references / "vendor"
            history.mkdir()
            vendor.mkdir(parents=True)
            (history / "target.md").write_text("# Target\n", encoding="utf-8")
            (vendor / "source.md").write_text(
                "[Target](../../history/target.md)\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "history",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                target["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_excluded_dir"], 1
            )

    def test_unsupported_reference_text_extension_marks_coverage_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history = root / "history"
            references = root / "references"
            history.mkdir()
            references.mkdir()
            (history / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "links.mdown").write_text(
                "[Target](../history/target.md)\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "history",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                target["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"][
                    "reference_unsupported_text_extension"
                ],
                1,
            )

    def test_structured_reference_source_marks_coverage_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history = root / "history"
            references = root / "references"
            history.mkdir()
            references.mkdir()
            (history / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "project-workflow.yaml").write_text(
                "project_context: ../history/target.md\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "history",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                target["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"][
                    "reference_unparsed_structured_source"
                ],
                1,
            )

    def test_mdx_reference_source_marks_coverage_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history = root / "history"
            references = root / "references"
            history.mkdir()
            references.mkdir()
            (history / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "source.mdx").write_text(
                "import Target from '../history/target.md'\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "history",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                target["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"][
                    "reference_unparsed_mdx_source"
                ],
                1,
            )

    def test_unreadable_reference_directory_marks_coverage_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history = root / "history"
            references = root / "references"
            unreadable = references / "private"
            history.mkdir()
            unreadable.mkdir(parents=True)
            (history / "target.md").write_text("# Target\n", encoding="utf-8")
            (unreadable / "links.md").write_text(
                "[Target](../../history/target.md)\n",
                encoding="utf-8",
            )
            unreadable.chmod(0o000)
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--root",
                        str(root),
                        "--scope",
                        "history",
                        "--reference-root",
                        "references",
                        "--include-content-signals",
                        "--format",
                        "json",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
            finally:
                unreadable.chmod(0o755)

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            if not report["summary"]["skipped"].get(
                "reference_traversal_error"
            ):
                self.skipTest("test process can read mode-000 directories")
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                target["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )

    def test_binary_reference_source_marks_coverage_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history = root / "history"
            references = root / "references"
            history.mkdir()
            references.mkdir()
            (history / "target.md").write_text("# Target\n", encoding="utf-8")
            (references / "binary.md").write_bytes(
                b"[Target](../history/target.md)\x00"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "history",
                    "--reference-root",
                    "references",
                    "--include-content-signals",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            target = report["largest_files"][0]
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                target["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertFalse(
                report["link_coverage"]["complete_for_declared_roots"]
            )
            self.assertEqual(report["summary"]["skipped"]["reference_binary"], 1)

    def test_reference_labels_decode_entities_and_backslash_escapes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "entity.md").write_text(
                "[Entity label][foo&amp;bar]\n\n[foo&bar]: target.md\n",
                encoding="utf-8",
            )
            (memory / "escape.md").write_text(
                "[Escaped label][foo\\&bar]\n\n[foo&bar]: target.md\n",
                encoding="utf-8",
            )
            (memory / "bracket.md").write_text(
                "[Escaped bracket][foo\\]]\n\n[foo\\]]: target.md\n",
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 3)

    def test_reference_uses_inside_inline_link_metadata_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "other.md").write_text("# Other\n", encoding="utf-8")
            (memory / "source.md").write_text(
                """# Source

[Guide](other.md "[hidden]")

[hidden]: target.md
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/source.md"]["broken_targets"], [])
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)

    def test_defined_nested_reference_link_wins_over_outer_inline_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "outer.md").write_text("# Outer\n", encoding="utf-8")
            (memory / "source.md").write_text(
                """# Source

[outer [inner][ref]](outer.md)

[ref]: target.md
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/source.md"]["broken_targets"], [])
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/outer.md"]["incoming_links"], 0)

    def test_reference_labels_enforce_commonmark_length_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            valid_label = "a" * 999
            invalid_label = "b" * 1000
            (memory / "valid.md").write_text("# Valid\n", encoding="utf-8")
            (memory / "invalid.md").write_text("# Invalid\n", encoding="utf-8")
            (memory / "source.md").write_text(
                (
                    f"[Valid][{valid_label}]\n"
                    f"[Invalid][{invalid_label}]\n\n"
                    f"[{valid_label}]: valid.md\n"
                    f"[{invalid_label}]: invalid.md\n"
                ),
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/valid.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/invalid.md"]["incoming_links"], 0)

    def test_whitespace_only_reference_labels_do_not_create_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "[Use][   ]\n\n[   ]: target.md\n",
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)

    def test_linked_image_counts_outer_and_nested_image_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "page.md").write_text("# Page\n", encoding="utf-8")
            (memory / "badge.md").write_text("# Badge\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "# Source\n\n[![Badge](badge.md)](page.md)\n",
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/page.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/badge.md"]["incoming_links"], 1)

    def test_linked_reference_image_counts_outer_and_image_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "page.md").write_text("# Page\n", encoding="utf-8")
            (memory / "badge.md").write_text("# Badge\n", encoding="utf-8")
            (memory / "source.md").write_text(
                """# Source

[![Badge][img]](page.md)

[img]: badge.md
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/page.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/badge.md"]["incoming_links"], 1)

    def test_reference_outer_link_counts_nested_reference_image_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "page.md").write_text("# Page\n", encoding="utf-8")
            (memory / "preview.md").write_text("# Preview\n", encoding="utf-8")
            (memory / "source.md").write_text(
                """# Source

[![Preview][image]][page]

[image]: preview.md
[page]: page.md
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/page.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/preview.md"]["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_reference_link_inside_inline_image_alt_is_not_a_resource(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "outer.md").write_text("# Outer\n", encoding="utf-8")
            (memory / "inner.md").write_text("# Inner\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "![outer [inner][ref]](outer.md)\n\n[ref]: inner.md\n",
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/outer.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/inner.md"]["incoming_links"], 0)

    def test_image_inside_image_alt_does_not_count_inner_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "outer.md").write_text("# Outer\n", encoding="utf-8")
            (memory / "inner.md").write_text("# Inner\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "# Source\n\n![outer ![inner](inner.md)](outer.md)\n",
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/outer.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/inner.md"]["incoming_links"], 0)

    def test_link_inside_image_alt_preserves_only_outer_image_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "outer.md").write_text("# Outer\n", encoding="utf-8")
            (memory / "inner.md").write_text("# Inner\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "# Source\n\n![outer [inner](inner.md)](outer.md)\n",
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/outer.md"]["incoming_links"], 1)
            self.assertEqual(by_path["memory/inner.md"]["incoming_links"], 0)

    def test_linked_image_title_is_hidden_from_heading_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "badge.md").write_text("# Badge\n", encoding="utf-8")
            (memory / "page.md").write_text("# Page\n", encoding="utf-8")
            (memory / "source.md").write_text(
                (
                    '# Source\n\n## [![Badge](badge.md "TASK_123 completed")]'
                    "(page.md)\n"
                ),
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
                    "memory/source.md",
                    "--task-id-regex",
                    r"TASK_[0-9]+",
                    "--include-content-signals",
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
            source = by_path["memory/source.md"]
            self.assertEqual(source["task_id_count"], 0)
            self.assertEqual(source["task_headings"], 0)
            self.assertEqual(source["completed_markers"], 0)

    def test_task_ids_inside_inline_link_titles_are_not_visible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                '# Source\n\n## [Guide](target.md "TASK_123")\n',
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
                    "memory/source.md",
                    "--task-id-regex",
                    r"TASK_[0-9]+",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/source.md"]["task_id_count"], 0)
            self.assertEqual(by_path["memory/source.md"]["task_headings"], 0)

    def test_escaped_reference_links_do_not_use_definitions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            source.write_text(
                """# Source

\\[shortcut]
\\[Full reference][full]

[shortcut]: missing-shortcut.md
[full]: missing-full.md
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

    def test_reference_definition_rejects_non_title_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            source.write_text(
                """# Source

[Guide][guide]

[guide]: missing.md TODO completed
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
            report = json.loads(result.stdout)
            largest = report["largest_files"][0]
            self.assertEqual(largest["broken_targets"], [])
            self.assertEqual(largest["unresolved_markers"], 1)
            self.assertEqual(largest["completed_markers"], 1)
            self.assertIn(
                "mixed_lifecycle_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_reference_definition_rejects_unbalanced_bare_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            source.write_text(
                "# Source\n\n[Guide][guide]\n\n[guide]: TODO.md)\n",
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

    def test_reference_definitions_accept_empty_angle_destinations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            source.write_text(
                r"""# Source

[Direct][direct]
[Continued][continued]

[direct]: <> "TODO completed"
[continued]:
  <> "TODO completed"
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
            self.assertEqual(largest["unresolved_markers"], 0)
            self.assertEqual(largest["completed_markers"], 0)

    def test_reference_definitions_honor_escaped_angle_closers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            source.write_text(
                """# Source

[Direct][direct]
[Continued][continued]

[direct]: <foo\>bar.md>
[continued]:
  <foo\>bar.md>
""",
                encoding="utf-8",
            )
            (memory / "foo>bar.md").write_text("# Target\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--reference-root",
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
            self.assertEqual(by_path["memory/source.md"]["broken_targets"], [])
            self.assertEqual(by_path["memory/foo>bar.md"]["incoming_links"], 1)

    def test_reference_definition_does_not_interrupt_paragraph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            source.write_text(
                """# Source

Visible paragraph
[guide]: TODO.md
[Guide][guide]
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

    def test_reference_title_can_close_after_seven_continuation_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                """# Source

[Use][guide]

[guide]: target.md "line zero
 line one
 line two
 line three
 line four
 line five
 line six
 line seven
 line eight"
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_multiline_reference_label_marks_link_coverage_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                """# Source

[Guide][my
 ref]

[my ref]: target.md
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)
            self.assertEqual(
                by_path["memory/target.md"]["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"], 1
            )

    def test_multiline_shortcut_label_marks_link_coverage_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                """# Source

[my
 ref]

[my ref]: target.md
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
                    "--reference-root",
                    "memory",
                    "--include-content-signals",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)
            self.assertEqual(
                by_path["memory/target.md"]["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"], 1
            )

    def test_multiline_reference_title_stops_at_heading_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            source.write_text(
                """# Source

[Guide][guide]

[guide]: missing.md "TODO
## TASK_123 completed"
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
            self.assertEqual(largest["broken_targets"], [])
            self.assertEqual(largest["markdown_headings"], 2)
            self.assertEqual(largest["task_headings"], 1)
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["unresolved_markers"], 1)
            self.assertEqual(largest["completed_markers"], 1)

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

Example `TASK_999
2. completed`

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

    def test_unescaped_nested_bracket_is_not_a_reference_label(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "[foo[bar\\]]\n\n[foo[bar\\]]: target.md\n",
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
                    "--reference-root",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 0)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_shortcut_reference_before_colon_counts_as_incoming(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "See [target]: details\n\n[target]: target.md\n",
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
                    "--reference-root",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

    def test_shortcut_reference_after_failed_inline_link_counts_as_incoming(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (memory / "source.md").write_text(
                "See [target](broken\n\n[target]: target.md\n",
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
                    "--reference-root",
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)
            self.assertTrue(
                report["link_coverage"]["complete_for_declared_roots"]
            )

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

    def test_semicolonless_entity_like_inline_target_remains_literal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            target = memory / "target&copy.md"
            source.write_text(
                "# Source\n\n[Guide](target&copy.md)\n",
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
            self.assertEqual(by_path["memory/source.md"]["broken_targets"], [])
            self.assertEqual(by_path["memory/target&copy.md"]["incoming_links"], 1)

    def test_balanced_parentheses_in_inline_link_target_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            docs = root / "docs"
            memory.mkdir()
            docs.mkdir()
            source = memory / "source.md"
            target = docs / "a(b).md"
            spaced_target = docs / "user guide.md"
            entity_target = docs / "target&one.md"
            source.write_text(
                """# Source

[Existing guide](../docs/a(b).md?view=full#current)
[Spaced guide](<../docs/user guide.md>)
[Entity guide](../docs/target&amp;one.md)
[Missing guide](../docs/missing(c).md)
""",
                encoding="utf-8",
            )
            target.write_text("# Target\n", encoding="utf-8")
            spaced_target.write_text("# Spaced target\n", encoding="utf-8")
            entity_target.write_text("# Entity target\n", encoding="utf-8")

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
            self.assertEqual(by_path["docs/user guide.md"]["incoming_links"], 1)
            self.assertEqual(by_path["docs/target&one.md"]["incoming_links"], 1)

    def test_nested_inline_link_prefers_rendered_inner_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "source.md"
            target = memory / "target.md"
            source.write_text(
                """# Source

[outer [inner](target.md)](missing.md)
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
            self.assertEqual(by_path["memory/source.md"]["broken_targets"], [])
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)

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
            self.assertEqual(largest["completed_markers"], 3)
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
            same_line_target = memory / "target.md"
            multiline_label_target = memory / "label-target.md"
            source.write_text(
                """# Source

[Same-line guide](target.md) [Existing guide](
TODO.md
)

[Opening-line destination](TODO.md
"title"
)

[Multiline
label](label-target.md)

[Missing guide](
missing.md
)

> [Quoted missing](
> quoted-missing.md) ## TASK_123 TODO completed
""",
                encoding="utf-8",
            )
            target.write_text("# Target\n", encoding="utf-8")
            same_line_target.write_text("# Same-line target\n", encoding="utf-8")
            multiline_label_target.write_text(
                "# Multiline label target\n", encoding="utf-8"
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
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)
            self.assertEqual(
                by_path["memory/label-target.md"]["incoming_links"], 1
            )
            self.assertEqual(by_path["memory/source.md"]["markdown_headings"], 1)
            self.assertEqual(by_path["memory/source.md"]["unresolved_markers"], 1)
            self.assertEqual(by_path["memory/source.md"]["completed_markers"], 1)
            candidate_by_path = {
                item["path"]: item for item in report["candidates"]
            }
            self.assertIn(
                "mixed_lifecycle_signal",
                candidate_by_path["memory/source.md"]["review_hints"],
            )

    def test_multiline_inline_link_stops_at_heading_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

[Guide](
# "TASK_123 completed")
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

    def test_multiline_inline_link_does_not_start_in_atx_heading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                "# Service memory\n\n## [Guide\ntext](TODO.md)\n",
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
            self.assertEqual(largest["broken_targets"], [])
            self.assertEqual(largest["unresolved_markers"], 1)

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

Another paragraph.
1. ## TASK_456 completed
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
            self.assertEqual(largest["task_id_count"], 2)
            self.assertEqual(largest["completed_markers"], 2)
            self.assertIn(
                "task_chronology_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_non_one_ordered_marker_does_not_interrupt_paragraph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

Active paragraph.
2. ## TASK_123 completed
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
            self.assertEqual(largest["task_id_count"], 1)
            self.assertEqual(largest["completed_markers"], 1)
            hints = report["candidates"][0]["review_hints"]
            self.assertNotIn("task_chronology_signal", hints)

    def test_indented_heading_like_text_does_not_interrupt_paragraph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

Visible paragraph
    ## TASK_123 TODO completed
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
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["unresolved_markers"], 1)
            self.assertEqual(largest["completed_markers"], 1)
            self.assertNotIn(
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

    def test_list_indent_preserves_residual_tab_columns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

- Canonical fact
\t  ## TASK_123 completed
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
            self.assertEqual(largest["task_headings"], 0)
            self.assertEqual(largest["task_id_count"], 0)
            self.assertEqual(largest["completed_markers"], 0)

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
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["completed_markers"], 1)

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

    def test_cdata_closes_only_at_cdata_terminator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

<![CDATA[
comparison > baseline
## TASK_123 completed
]]>

## Current behavior

TODO verify behavior.
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
            self.assertEqual(largest["unresolved_markers"], 1)

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

    def test_inline_html_comment_ends_at_paragraph_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

Visible text <!-- unclosed comment

## TASK_123 completed

Visible text <!-- unclosed comment
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
            report = json.loads(result.stdout)
            largest = report["largest_files"][0]
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
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["completed_markers"], 1)

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

    def test_raw_html_blocks_do_not_create_markdown_structure(self) -> None:
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
            self.assertEqual(largest["task_ids"], ["TASK_456"])
            self.assertEqual(largest["completed_markers"], 0)
            self.assertEqual(largest["superseded_markers"], 1)
            self.assertEqual(largest["unresolved_markers"], 0)

    def test_ordinary_html_block_text_creates_lifecycle_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            (memory / "service.md").write_text(
                "# Service memory\n\n<div>TODO completed</div>\n",
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
            self.assertEqual(largest["unresolved_markers"], 1)
            self.assertEqual(largest["completed_markers"], 1)
            self.assertIn(
                "mixed_lifecycle_signal",
                report["candidates"][0]["review_hints"],
            )

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

    def test_escaped_html_comment_opener_stays_visible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

\\<!-- TODO completed -->
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
            self.assertEqual(largest["unresolved_markers"], 1)
            self.assertEqual(largest["completed_markers"], 1)
            self.assertIn(
                "mixed_lifecycle_signal",
                report["candidates"][0]["review_hints"],
            )
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

    def test_markdown_front_matter_marks_link_coverage_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            docs = root / "docs"
            memory.mkdir()
            docs.mkdir()
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")
            (docs / "source.md").write_text(
                """---
related: ../memory/target.md
---

# Source

No rendered link to the target.
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
                    "--reference-root",
                    "docs",
                    "--include-content-signals",
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
            target = report["largest_files"][0]
            self.assertEqual(target["path"], "memory/target.md")
            self.assertEqual(target["incoming_links"], 0)
            self.assertEqual(
                target["incoming_links_coverage"],
                "declared_reference_roots_with_skips_incomplete",
            )
            self.assertEqual(
                report["summary"]["skipped"]["reference_parse_incomplete"], 1
            )

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
            self.assertEqual(report["schema_version"], 3)
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

    def test_balanced_reference_link_text_hides_reference_label_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                """# Service memory

[Guide [nested]][TODO completed]

[TODO completed]: target.md
""",
                encoding="utf-8",
            )
            (memory / "target.md").write_text("# Target\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--scope",
                    "memory",
                    "--reference-root",
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
            by_path = {item["path"]: item for item in report["largest_files"]}
            self.assertEqual(by_path["memory/service.md"]["unresolved_markers"], 0)
            self.assertEqual(by_path["memory/service.md"]["completed_markers"], 0)
            self.assertEqual(by_path["memory/target.md"]["incoming_links"], 1)

    def test_undefined_reference_syntax_remains_visible_to_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                "# Service memory\n\n[Guide][TODO completed]\n",
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
            self.assertEqual(largest["unresolved_markers"], 1)
            self.assertEqual(largest["completed_markers"], 1)
            self.assertIn(
                "mixed_lifecycle_signal",
                report["candidates"][0]["review_hints"],
            )

    def test_undefined_reference_task_id_remains_visible_in_heading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            memory.mkdir()
            source = memory / "service.md"
            source.write_text(
                "# Service memory\n\n## [Guide][TASK_123]\n",
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
            self.assertEqual(largest["task_ids"], ["TASK_123"])
            self.assertEqual(largest["task_headings"], 1)


if __name__ == "__main__":
    unittest.main()
