import json
import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = SKILL_ROOT / "assets"
TEMPLATE = ASSETS_ROOT / "templates" / "project-workflow.yaml"
SCHEMA = ASSETS_ROOT / "project-workflow.schema.json"
INTERVIEW = SKILL_ROOT / "references" / "configuration-interview.md"
GENERATE = SKILL_ROOT / "references" / "generate-project-setup.md"
VALIDATE = SKILL_ROOT / "references" / "validate-project-setup.md"
PUBLISH_REVIEW = (
    SKILL_ROOT.parent
    / "publish-planning-change"
    / "references"
    / "run-independent-spec-review.md"
)


class PlanningPublicationContractTest(unittest.TestCase):
    def test_template_uses_out_of_box_documentation_defaults(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn('project_docs: "docs_ai"', text)
        self.assertIn('task_specs: "docs_ai/tasks"', text)
        self.assertIn('internal_memory: "local_memory_ai"', text)
        self.assertIn("ask_only_decision_changing_or_unknown_facts: true", text)
        self.assertIn("apply_safe_defaults_before_asking: true", text)
        self.assertIn("question_quota: false", text)

    def test_schema_requires_safe_planning_publication_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        publication = schema["properties"]["planning_publication"]
        properties = publication["properties"]
        artifact_policy = properties["artifact_policy"]["properties"]
        spec_root = artifact_policy["default_spec_root"]
        self.assertEqual(spec_root["type"], "string")
        self.assertEqual(spec_root["default"], "docs_ai/tasks")
        self.assertNotIn("const", spec_root)
        spec_root_pattern = re.compile(spec_root["pattern"])
        for valid_root in ("docs_ai/tasks", "specifications", "docs/task specs"):
            with self.subTest(valid_root=valid_root):
                self.assertRegex(valid_root, spec_root_pattern)
        for unsafe_root in (
            "../other-repo",
            "docs/../other-repo",
            "/tmp/specs",
            "C:\\tmp\\specs",
            "C:..\\other-repo",
            "D:specifications",
        ):
            with self.subTest(unsafe_root=unsafe_root):
                self.assertNotRegex(unsafe_root, spec_root_pattern)
        self.assertFalse(
            artifact_policy["ask_for_spec_root_when_default_is_available"]["const"]
        )
        independent_review = properties["independent_review"]
        for required_key in (
            "working_directory",
            "working_directory_placeholder",
            "verify_reported_workdir_and_branch",
        ):
            self.assertNotIn(required_key, independent_review["required"])
            self.assertIn("default", independent_review["properties"][required_key])
        self.assertEqual(
            independent_review["properties"]["working_directory"]["const"],
            "exact_planning_worktree",
        )
        self.assertEqual(
            independent_review["properties"]["working_directory"]["default"],
            "exact_planning_worktree",
        )
        self.assertEqual(
            independent_review["properties"]["working_directory_placeholder"]
            ["const"],
            "<PLANNING_WORKTREE>",
        )
        self.assertEqual(
            independent_review["properties"]["working_directory_placeholder"]
            ["default"],
            "<PLANNING_WORKTREE>",
        )
        self.assertTrue(
            independent_review["properties"]
            ["verify_reported_workdir_and_branch"]["const"]
        )
        self.assertTrue(
            independent_review["properties"]
            ["verify_reported_workdir_and_branch"]["default"]
        )
        self.assertTrue(
            independent_review["properties"]["required"]["const"]
        )
        self.assertIn(
            "model", independent_review["required"]
        )
        self.assertIn(
            "effort", independent_review["required"]
        )
        self.assertTrue(
            properties["readiness"]["properties"]
            ["canonical_merge_required_before_implementation"]["const"]
        )
        self.assertTrue(
            properties["readiness"]["properties"]
            ["implementation_base_must_contain_publication_revision"]["const"]
        )
        self.assertIn(
            "repository that owns the specification revision",
            properties["readiness"]["properties"]
            ["implementation_base_must_contain_publication_revision"]
            ["description"],
        )
        legacy_adoption = properties["readiness"]["properties"][
            "legacy_ready_adoption"
        ]
        self.assertEqual(legacy_adoption["default"], {"enabled": False})
        self.assertNotIn("legacy_ready_adoption", properties["readiness"]["required"])
        self.assertEqual(
            legacy_adoption["properties"]["baseline_revision"]["pattern"],
            "^(?:[0-9a-f]{40}|[0-9a-f]{64})$",
        )
        self.assertEqual(
            legacy_adoption["properties"]["evidence_mode"]["const"],
            "canonical_baseline_package_manifest",
        )
        self.assertTrue(
            legacy_adoption["properties"]
            ["baseline_must_be_ancestor_of_current_authority_base"]["const"]
        )
        self.assertTrue(
            legacy_adoption["properties"]
            ["persist_complete_baseline_package_manifest"]["const"]
        )
        enabled_branch = legacy_adoption["allOf"][0]
        self.assertEqual(
            enabled_branch["if"]["properties"]["enabled"]["const"], True
        )
        self.assertIn(
            "baseline_revision", enabled_branch["then"]["required"]
        )
        self.assertIn(
            "baseline_must_be_ancestor_of_current_authority_base",
            enabled_branch["then"]["required"],
        )
        self.assertIn(
            "persist_complete_baseline_package_manifest",
            enabled_branch["then"]["required"],
        )
        self.assertFalse(
            legacy_adoption["properties"]["claim_independent_review"]["const"]
        )
        self.assertEqual(
            legacy_adoption["properties"]["record_evidence_kind"]["const"],
            "legacy_ready_baseline",
        )
        publication_condition = schema["allOf"][0]
        self.assertEqual(
            publication_condition["if"]["properties"]["workflow_kit"]
            ["properties"]["selected_modules"]["contains"]["const"],
            "publish-planning-change",
        )
        self.assertIn(
            "planning_publication", publication_condition["then"]["required"]
        )

    def test_interview_does_not_ask_for_default_spec_root(self):
        text = INTERVIEW.read_text(encoding="utf-8")
        self.assertIn(
            "default to the project root repository and `docs_ai/tasks` without asking",
            text,
        )

    def test_review_is_bound_to_the_exact_planning_worktree(self):
        generated = GENERATE.read_text(encoding="utf-8")
        validation = VALIDATE.read_text(encoding="utf-8")
        review = PUBLISH_REVIEW.read_text(encoding="utf-8")

        self.assertIn("process working directory", generated)
        self.assertIn("exact planning worktree as its working directory", validation)
        self.assertIn("effective values from the schema defaults", validation)
        self.assertIn("process working directory to the exact planning worktree", review)
        self.assertIn("schema defaults in memory", review)

    def test_existing_ready_specs_get_deterministic_adoption_evidence(self):
        generated = GENERATE.read_text(encoding="utf-8")
        validation = VALIDATE.read_text(encoding="utf-8")
        readiness = (
            SKILL_ROOT.parent
            / "execute-project-task"
            / "references"
            / "check-task-readiness.md"
        ).read_text(encoding="utf-8")
        task_linkage = (
            SKILL_ROOT.parent
            / "manage-project-work"
            / "references"
            / "link-and-close-project-task.md"
        ).read_text(encoding="utf-8")

        self.assertIn("exact full Git object ID", generated)
        self.assertIn("64-hex SHA-256", generated)
        self.assertIn("legacy_ready_baseline", generated)
        self.assertIn("immutable full baseline Git object ID", validation)
        self.assertIn("current-versus-baseline package manifests", validation)
        self.assertIn("Resolve pre-adoption ready specifications", readiness)
        self.assertIn("without claiming independent review", readiness)
        self.assertIn("Git blob OID", readiness)
        self.assertIn("baseline revision is an ancestor", readiness)
        self.assertIn("not a prerequisite for constructing the candidate", readiness)
        self.assertIn("baseline package manifest with every path", readiness)
        self.assertIn("separate recording handoff", task_linkage)
        self.assertIn("legacy_ready_baseline", task_linkage)
        self.assertIn("existing ready status", task_linkage)
        self.assertIn("Reread the persisted tuple", task_linkage)
        self.assertIn("complete path/OID set", task_linkage)


if __name__ == "__main__":
    unittest.main()
