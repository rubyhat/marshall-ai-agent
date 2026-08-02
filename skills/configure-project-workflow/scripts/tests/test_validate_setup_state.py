import copy
import importlib.util
import re
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_setup_state.py"
CATALOG = Path(__file__).resolve().parents[2] / "assets" / "workflow-modules.json"
PROJECT_SCHEMA = Path(__file__).resolve().parents[2] / "assets" / "project-workflow.schema.json"


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
        cls.project_schema = cls.module.load_json(PROJECT_SCHEMA)

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

    def test_adr_aliases_are_registered_for_selected_module(self):
        state = self.valid_state()
        state["modules"]["selected"].append("record-architecture-decision")
        state["modules"]["enabled_aliases"] = ["--adr-review", "--record-adr"]
        errors, _ = self.module.validate(state, self.catalog)
        self.assertEqual(errors, [])

    def test_adr_module_requires_context_recorder(self):
        state = self.valid_state()
        state["modules"]["selected"] = [
            "configure-project-workflow",
            "record-architecture-decision",
        ]
        state["modules"]["enabled_aliases"] = ["--adr-review"]
        errors, _ = self.module.validate(state, self.catalog)
        self.assertIn(
            "Module record-architecture-decision requires record-project-context",
            errors,
        )

    def test_adr_config_contract_persists_policy_fields(self):
        adr = self.project_schema["properties"]["architecture_decisions"]
        self.assertIn("materiality_policy", adr["required"])
        self.assertIn("applicability_policy", adr["required"])
        blocking = adr["properties"]["applicability_policy"]["properties"][
            "blocking_results"
        ]
        self.assertEqual(
            set(blocking["items"]["enum"]), {"review required", "unclear"}
        )
        self.assertEqual(blocking["minItems"], 2)
        self.assertEqual(blocking["maxItems"], 2)

        conditional = self.project_schema["allOf"][0]
        selected = conditional["if"]["properties"]["workflow_kit"]["properties"][
            "selected_modules"
        ]
        self.assertEqual(
            selected["contains"]["const"], "record-architecture-decision"
        )
        self.assertIn("architecture_decisions", conditional["then"]["required"])

    def test_adr_paths_must_stay_project_relative(self):
        adr_properties = self.project_schema["properties"][
            "architecture_decisions"
        ]["properties"]

        valid_paths = {
            "root": "docs/architecture/decisions",
            "index": "docs/architecture/decisions/README.md",
        }
        for field, valid_path in valid_paths.items():
            pattern = adr_properties[field]["pattern"]
            self.assertIsNotNone(re.search(pattern, valid_path))
            for unsafe_path in (
                "/tmp/decisions",
                "../outside.md",
                "docs/../outside.md",
                "docs/./decisions.md",
                "docs/decisions/",
                "C:decisions",
                "C:\\outside\\decisions",
                "docs\\..\\outside.md",
                "docs/decisions.md\n",
                "docs/decisions\t/index.md",
            ):
                self.assertIsNone(
                    re.search(pattern, unsafe_path),
                    f"{field} accepted unsafe path {unsafe_path!r}",
                )

        index_pattern = adr_properties["index"]["pattern"]
        self.assertIsNone(re.search(index_pattern, "docs/architecture/index"))

    def test_adr_identifier_and_filename_contract_is_bounded(self):
        adr_properties = self.project_schema["properties"][
            "architecture_decisions"
        ]["properties"]
        id_pattern = adr_properties["id_pattern"]["pattern"]

        for value in ("ADR-[0-9]{4}", "DECISION-LOG-[0-9]{3}", "[0-9]{4}"):
            self.assertIsNotNone(re.search(id_pattern, value))
        for value in (
            "[",
            "../[A-Z]+",
            "ADR-[0-9]+",
            "[A-Z]{4}",
            "(?i:k+)",
            "ADR-[0-9]{12}",
            "ADR-[0-9]{4}\n",
        ):
            self.assertIsNone(re.search(id_pattern, value))

        self.assertEqual(adr_properties["filename_pattern"]["const"], "<ID>.md")

    def test_adr_required_text_rejects_whitespace_only_values(self):
        adr_properties = self.project_schema["properties"][
            "architecture_decisions"
        ]["properties"]
        text_schemas = [
            adr_properties["materiality_policy"],
            adr_properties["applicability_policy"]["properties"][
                "review_triggers"
            ]["items"],
            adr_properties["required_sections"]["items"],
            *adr_properties["status_mapping"]["properties"].values(),
            *adr_properties["decision_authority"]["properties"].values(),
        ]
        for schema in text_schemas:
            self.assertIsNone(re.search(schema["pattern"], "   \t"))
            self.assertIsNotNone(re.search(schema["pattern"], "configured value"))

        self.assertFalse(adr_properties["status_mapping"]["additionalProperties"])
        self.assertFalse(adr_properties["decision_authority"]["additionalProperties"])

    def test_enabled_aliases_field_is_required(self):
        state = self.valid_state()
        del state["modules"]["enabled_aliases"]
        errors, _ = self.module.validate(state, self.catalog)
        self.assertIn("modules.enabled_aliases is required", errors)


if __name__ == "__main__":
    unittest.main()
