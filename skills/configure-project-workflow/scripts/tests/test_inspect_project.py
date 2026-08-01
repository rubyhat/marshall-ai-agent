import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "inspect_project.py"

class InspectProjectTest(unittest.TestCase):
    def run_inspector(self, root: Path):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--format", "json"],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_inventory_detects_safe_metadata_and_skips_sensitive_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Instructions\n")
            (root / "package.json").write_text(
                json.dumps({"dependencies": {"next": "1", "react": "1"}, "workspaces": ["apps/*"]})
            )
            (root / ".env.production").write_text("SECRET=do-not-read\n")
            (root / "node_modules").mkdir()
            (root / "node_modules/hidden.json").write_text("{}")

            result = self.run_inspector(root)

            self.assertTrue(result["read_only"])
            self.assertEqual(result["files"]["instructions"], ["AGENTS.md"])
            self.assertEqual(result["files"]["manifests"], ["package.json"])
            self.assertEqual(result["technology"]["frameworks"], ["nextjs", "react"])
            self.assertEqual(
                result["topology_candidates"],
                [
                    {
                        "path": ".",
                        "evidence_kinds": ["instruction_root", "manifest_root"],
                        "evidence_paths": ["AGENTS.md", "package.json"],
                    }
                ],
            )
            self.assertGreaterEqual(result["skipped"]["sensitive_entries"], 1)
            flattened = json.dumps(result)
            self.assertNotIn("SECRET=do-not-read", flattened)
            self.assertNotIn("hidden.json", flattened)

    def test_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside_directory:
            root = Path(directory)
            outside = Path(outside_directory)
            (outside / "package.json").write_text('{"dependencies":{"vue":"1"}}')
            (root / "external").symlink_to(outside, target_is_directory=True)

            result = self.run_inspector(root)

            self.assertEqual(result["files"]["manifests"], [])
            self.assertEqual(result["technology"]["frameworks"], [])
            self.assertEqual(result["skipped"]["symlinks"], 1)

    def test_git_file_link_is_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").write_text("gitdir: /outside/worktree/git\n")

            result = self.run_inspector(root)

            self.assertEqual(result["git"], [])
            self.assertEqual(result["skipped"]["external_git_links"], 1)

    def test_topology_candidates_group_nested_structural_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            service = root / "apps" / "api"
            service.mkdir(parents=True)
            (service / "package.json").write_text("{}")
            (service / "AGENTS.md").write_text("# API instructions\n")
            (service / "ARCHITECTURE.md").write_text("# API architecture\n")

            result = self.run_inspector(root)

            self.assertEqual(
                result["topology_candidates"],
                [
                    {
                        "path": "apps/api",
                        "evidence_kinds": [
                            "architecture_root",
                            "instruction_root",
                            "manifest_root",
                        ],
                        "evidence_paths": [
                            "apps/api/AGENTS.md",
                            "apps/api/ARCHITECTURE.md",
                            "apps/api/package.json",
                        ],
                    }
                ],
            )

if __name__ == "__main__":
    unittest.main()
