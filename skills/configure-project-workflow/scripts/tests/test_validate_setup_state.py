import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_setup_state.py"
CATALOG = Path(__file__).resolve().parents[2] / "assets" / "workflow-modules.json"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_setup_state", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ValidateSetupStateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        cls.catalog = cls.module.load_json(CATALOG)

    def valid_state(self):
        return {
            "schema_version": 1,
            "setup_id": "project-workflow-setup",
            "mode": "initialize",
            "phase": "interview",
            "project_root": "/tmp/example-project",
            "workflow_kit": {},
            "protection": {
                "default_boundary_confirmed": True,
                "additional_restrictions": [],
            },
            "facts": [],
            "decisions": [],
            "modules": {
                "profile": "context_only",
                "selected": [
                    "configure-project-workflow",
                    "load-project-context",
                    "record-project-context",
                    "maintain-project-context",
                ],
            },
            "questions": [
                {"id": "SAFE-01", "stage": "safety", "status": "answered", "answer": "confirmed"}
            ],
            "assumptions": [],
            "conflicts": [],
            "deferred_topics": [],
            "manifest": [
                {"operation": "update_managed_section", "scope": "project", "target": "AGENTS.md"},
                {
                    "operation": "install",
                    "scope": "active_install",
                    "target": "~/.codex/skills/load-project-context",
                },
            ],
            "validation": {"status": "not_run", "checks": []},
        }

    def test_valid_state_passes(self):
        errors, warnings = self.module.validate(self.valid_state(), self.catalog)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_missing_dependency_fails(self):
        state = self.valid_state()
        state["modules"]["selected"] = ["configure-project-workflow", "deliver-reviewed-change"]
        errors, _ = self.module.validate(state, self.catalog)
        self.assertTrue(any("requires execute-project-task" in error for error in errors))

    def test_sensitive_key_fails(self):
        state = self.valid_state()
        state["workflow_kit"]["token"] = "never-store-this"
        errors, _ = self.module.validate(state, self.catalog)
        self.assertTrue(any("Sensitive key names" in error for error in errors))

    def test_unsafe_project_manifest_target_fails(self):
        state = self.valid_state()
        state["manifest"][0]["target"] = "../outside"
        errors, _ = self.module.validate(state, self.catalog)
        self.assertTrue(any("safe relative path" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
