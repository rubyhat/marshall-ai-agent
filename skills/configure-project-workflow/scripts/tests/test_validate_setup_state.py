import copy
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
            "schema_version": 2,
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
                "enabled_aliases": ["--workflow-check", "--context-audit"],
                "enabled_capabilities": [],
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

    def test_unknown_conditional_alias_dependency_fails(self):
        catalog = copy.deepcopy(self.catalog)
        shape = next(
            item for item in catalog["modules"] if item["name"] == "shape-project-work"
        )
        shape["conditional_aliases"][0]["requires"] = ["missing-writer"]
        with self.assertRaisesRegex(
            ValueError, "requires unknown module missing-writer"
        ):
            self.module.module_index(catalog)

    def test_duplicate_conditional_alias_fails(self):
        catalog = copy.deepcopy(self.catalog)
        shape = next(
            item for item in catalog["modules"] if item["name"] == "shape-project-work"
        )
        shape["conditional_aliases"][0]["command"] = "--shape-work"
        with self.assertRaisesRegex(ValueError, "Duplicate alias --shape-work"):
            self.module.module_index(catalog)

    def test_enabled_conditional_alias_requires_selected_module(self):
        state = self.valid_state()
        state["modules"]["selected"] = [
            "configure-project-workflow",
            "record-project-context",
            "shape-project-work",
        ]
        state["modules"]["enabled_aliases"] = ["--prepare-spec"]
        errors, _ = self.module.validate(state, self.catalog)
        self.assertIn("Alias --prepare-spec requires module write-task-spec", errors)

    def test_next_spec_requires_task_manager_and_spec_writer(self):
        state = self.valid_state()
        state["modules"]["selected"] = [
            "configure-project-workflow",
            "record-project-context",
            "shape-project-work",
        ]
        state["modules"]["enabled_aliases"] = ["--next-spec"]
        errors, _ = self.module.validate(state, self.catalog)
        self.assertIn(
            "Alias --next-spec requires module manage-project-work", errors
        )
        self.assertIn(
            "Alias --next-spec requires module write-task-spec", errors
        )

    def test_enabled_alias_requires_selected_owner(self):
        state = self.valid_state()
        state["modules"]["enabled_aliases"] = ["--shape-work"]
        errors, _ = self.module.validate(state, self.catalog)
        self.assertIn(
            "Alias --shape-work requires owning module shape-project-work", errors
        )

    def test_enabled_aliases_field_is_required(self):
        state = self.valid_state()
        del state["modules"]["enabled_aliases"]
        errors, _ = self.module.validate(state, self.catalog)
        self.assertIn("modules.enabled_aliases is required", errors)

    def test_enabled_capability_requires_runtime_modules(self):
        state = self.valid_state()
        state["modules"]["selected"] = [
            "configure-project-workflow",
            "record-project-context",
            "shape-project-work",
            "write-task-spec",
        ]
        state["modules"]["enabled_aliases"] = ["--prepare-spec"]
        state["modules"]["enabled_capabilities"] = [
            "specification_documentation_delivery"
        ]
        errors, _ = self.module.validate(state, self.catalog)
        self.assertIn(
            "Capability specification_documentation_delivery requires module deliver-reviewed-change",
            errors,
        )
        self.assertIn(
            "Capability specification_documentation_delivery requires module manage-project-work",
            errors,
        )

    def test_enabled_capability_passes_with_complete_runtime(self):
        state = self.valid_state()
        state["modules"]["selected"] = [
            "configure-project-workflow",
            "record-project-context",
            "shape-project-work",
            "write-task-spec",
            "manage-project-work",
            "execute-project-task",
            "deliver-reviewed-change",
        ]
        state["modules"]["enabled_aliases"] = ["--prepare-spec"]
        state["modules"]["enabled_capabilities"] = [
            "specification_documentation_delivery"
        ]
        errors, _ = self.module.validate(state, self.catalog)
        self.assertEqual(errors, [])

    def test_unknown_enabled_capability_fails(self):
        state = self.valid_state()
        state["modules"]["enabled_capabilities"] = ["missing-capability"]
        errors, _ = self.module.validate(state, self.catalog)
        self.assertIn("Unknown enabled capability: missing-capability", errors)


if __name__ == "__main__":
    unittest.main()
