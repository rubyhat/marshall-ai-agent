import json
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
        self.assertFalse(
            artifact_policy["ask_for_spec_root_when_default_is_available"]["const"]
        )
        self.assertTrue(
            properties["independent_review"]["properties"]["required"]["const"]
        )
        self.assertIn(
            "model", properties["independent_review"]["required"]
        )
        self.assertIn(
            "effort", properties["independent_review"]["required"]
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
        self.assertIn("process working directory to the exact planning worktree", review)


if __name__ == "__main__":
    unittest.main()
