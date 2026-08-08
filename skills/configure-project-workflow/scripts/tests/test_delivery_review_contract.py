import copy
import importlib.util
import json
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # The dependency-free repository validator may run without it.
    Draft202012Validator = None


SKILL_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = SKILL_ROOT / "assets" / "project-workflow.schema.json"
GENERATE = SKILL_ROOT / "references" / "generate-project-setup.md"
VALIDATE = SKILL_ROOT / "references" / "validate-project-setup.md"
DELIVERY_ROOT = SKILL_ROOT.parent / "deliver-reviewed-change"
DELIVERY_SKILL = DELIVERY_ROOT / "SKILL.md"
BOUND_CYCLES = DELIVERY_ROOT / "references" / "bound-review-correction-cycles.md"
LOCAL_REVIEW = DELIVERY_ROOT / "references" / "run-independent-local-review.md"
START_CYCLE = DELIVERY_ROOT / "references" / "start-codex-review-cycle.md"
FINDINGS = DELIVERY_ROOT / "references" / "classify-and-handle-review-findings.md"
RECOVERY = DELIVERY_ROOT / "references" / "recover-stalled-or-failed-review.md"
ALIASES = SKILL_ROOT.parents[1] / "docs" / "workflow-aliases.md"
PLANNING_TEST = Path(__file__).with_name("test_planning_publication_contract.py")


def load_planning_fixture():
    spec = importlib.util.spec_from_file_location("planning_fixture", PLANNING_TEST)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.complete_current_config()


def complete_review_contract():
    return {
        "scope_binding": {
            "exact_task_contract_required": True,
            "required_context": [
                "task_id",
                "issue",
                "specification_or_equivalent_contract",
                "specification_revision_or_not_applicable",
                "acceptance_criteria",
                "non_goals",
                "repositories",
                "worktrees",
                "branches",
                "target_branches",
                "initial_diff_manifest",
                "initial_diff_stats",
            ],
            "initial_diff_baseline_required": True,
            "baseline_immutable_for_delivery_attempt": True,
            "actionable_finding_requires_concrete_current_task_failure": True,
            "speculative_or_general_hardening_is_non_actionable": True,
            "material_scope_or_contract_change_returns_to_owner": True,
            "material_cumulative_diff_growth_stops_for_analysis": True,
        },
        "correction_policy": {
            "round_unit": "review_driven_correction_package",
            "separate_local_and_github_counters": True,
            "multiple_findings_in_one_result_consume_one_round": True,
            "technical_retry_consumes_no_round": True,
            "unchanged_head_contextual_rereview_consumes_no_round": True,
            "final_allowed_round_receives_review": True,
            "next_required_round_stops_before_mutation": True,
            "new_head_resets_request_attempts_only": True,
            "ordered_history_required": True,
            "pre_pr_state_store": "current_codex_task",
            "persist_and_read_back_after_each_local_transition": True,
            "different_conversation_requires_proven_state": True,
            "resume_requires_provable_counters_and_history": True,
            "lost_history_stops_delivery": True,
            "bounded_cycle_analysis_required": True,
        },
        "local": {
            "max_correction_rounds": 5,
            "fresh_review_after_each_correction_package": True,
        },
        "github_codex": {
            "max_correction_rounds": 5,
            "fresh_generation_after_each_correction_package": True,
            "new_head_resets_request_budget_only": True,
        },
    }


def complete_delivery_config():
    config = load_planning_fixture()
    config["workflow_kit"]["selected_modules"].append("deliver-reviewed-change")
    config["review"] = complete_review_contract()
    config["skills"]["active"]["deliver-reviewed-change"] = "skills/deliver"
    config["commands"]["aliases"]["--deliver-task"] = {}
    return config


class DeliveryReviewContractTest(unittest.TestCase):
    def test_schema_materializes_two_independent_five_round_budgets(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        review = schema["properties"]["review"]

        self.assertEqual(
            review["required"],
            ["scope_binding", "correction_policy", "local", "github_codex"],
        )
        for channel in ("local", "github_codex"):
            with self.subTest(channel=channel):
                limit = review["properties"][channel]["properties"][
                    "max_correction_rounds"
                ]
                self.assertEqual(limit["type"], "integer")
                self.assertEqual(limit["minimum"], 1)
                self.assertEqual(limit["maximum"], 5)
                self.assertEqual(limit["default"], 5)

        policy = review["properties"]["correction_policy"]
        self.assertEqual(
            policy["properties"]["round_unit"]["const"],
            "review_driven_correction_package",
        )
        for key in policy["required"]:
            if key != "round_unit":
                self.assertTrue(policy["properties"][key]["const"])

        delivery_condition = next(
            item
            for item in schema["allOf"]
            if item["if"]["properties"]["workflow_kit"]["properties"]
            ["selected_modules"]["contains"]["const"]
            == "deliver-reviewed-change"
        )
        self.assertEqual(delivery_condition["then"]["required"], ["review"])

    @unittest.skipIf(Draft202012Validator is None, "jsonschema is not installed")
    def test_delivery_selection_requires_complete_review_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        complete = complete_delivery_config()
        self.assertEqual(list(validator.iter_errors(complete)), [])

        without_review = copy.deepcopy(complete)
        del without_review["review"]
        self.assertTrue(list(validator.iter_errors(without_review)))

        for path in (
            ("review", "scope_binding", "initial_diff_baseline_required"),
            ("review", "correction_policy", "ordered_history_required"),
            ("review", "local", "max_correction_rounds"),
            ("review", "github_codex", "max_correction_rounds"),
        ):
            with self.subTest(missing=".".join(path)):
                incomplete = copy.deepcopy(complete)
                owner = incomplete
                for key in path[:-1]:
                    owner = owner[key]
                del owner[path[-1]]
                self.assertTrue(list(validator.iter_errors(incomplete)))

        invalid_limit = copy.deepcopy(complete)
        invalid_limit["review"]["local"]["max_correction_rounds"] = 0
        self.assertTrue(list(validator.iter_errors(invalid_limit)))

        above_limit = copy.deepcopy(complete)
        above_limit["review"]["github_codex"]["max_correction_rounds"] = 6
        self.assertTrue(list(validator.iter_errors(above_limit)))

    def test_delivery_skill_fails_closed_before_a_sixth_package(self):
        skill = DELIVERY_SKILL.read_text(encoding="utf-8")
        cycles = BOUND_CYCLES.read_text(encoding="utf-8")
        local = LOCAL_REVIEW.read_text(encoding="utf-8")
        findings = FINDINGS.read_text(encoding="utf-8")

        self.assertIn("bound-review-correction-cycles.md", skill)
        self.assertIn("## Contents", cycles)
        self.assertIn("local_correction_rounds_used", cycles)
        self.assertIn("github_correction_rounds_used", cycles)
        self.assertIn("Multiple findings corrected together consume one round", cycles)
        self.assertIn("resets only the configured technical request-attempt", cycles)
        self.assertIn("final allowed local round still receives", cycles)
        self.assertIn("final allowed GitHub round still receives", cycles)
        self.assertIn("stop before editing", cycles)
        self.assertIn("bounded\ncycle analysis", cycles)
        self.assertIn("machine-readable delivery-state block", cycles)
        self.assertIn("retained state of the current Codex task", cycles)
        self.assertIn("immutable delivery baseline", local)
        self.assertIn("final allowed round still\nreceives review", local)
        self.assertIn("unchanged GitHub correction counter", findings)

    def test_reviewer_context_and_drift_guards_are_explicit(self):
        cycles = BOUND_CYCLES.read_text(encoding="utf-8")
        local = LOCAL_REVIEW.read_text(encoding="utf-8")

        self.assertIn("acceptance criteria, explicit non-goals", cycles)
        self.assertIn("complete initial task diff manifest", cycles)
        self.assertIn("concrete\ncurrent-task failure", cycles)
        self.assertIn("speculative edge case without", cycles)
        self.assertIn("material cumulative diff growth", cycles)
        self.assertIn("Do not let reviewer preference silently redefine", cycles)
        self.assertIn("Do not leak the implementation discussion", local)

    def test_github_heartbeat_retains_correction_state(self):
        start = START_CYCLE.read_text(encoding="utf-8")
        recovery = RECOVERY.read_text(encoding="utf-8")

        self.assertIn("## Contents", start)
        for key in (
            "delivery_baseline:",
            "issue:",
            "specification_or_equivalent_contract:",
            "acceptance_criteria:",
            "non_goals:",
            "initial_diff_manifest:",
            "initial_diff_stats:",
            "delivery_baseline_fingerprint",
            "local_correction_rounds_used",
            "local_correction_history",
            "github_correction_rounds_used",
            "github_correction_history",
        ):
            self.assertIn(key, start)
        self.assertIn("preserve both\ncorrection counters", start)
        self.assertIn("must not consume or reset either correction counter", recovery)

    def test_setup_and_human_alias_document_the_contract(self):
        generated = GENERATE.read_text(encoding="utf-8")
        validation = VALIDATE.read_text(encoding="utf-8")
        aliases = ALIASES.read_text(encoding="utf-8")

        self.assertIn("each materialized as `5`", generated)
        self.assertIn("separate positive `max_correction_rounds`", generated)
        self.assertIn("new PR head resetting only technical request attempts", generated)
        self.assertIn("machine-readable pre-PR state block", generated)
        self.assertIn("separate positive correction-round limits set to five", validation)
        self.assertIn("не более пяти correction packages каждый", aliases)
        self.assertIn("Если ему нужна\nшестая правка", aliases)
        self.assertIn("Переход на workflow kit v0.8.0", aliases)
        self.assertIn("корневую секцию `review` с четырьмя полными группами", aliases)
        migration = aliases.split("### Переход на workflow kit v0.8.0", 1)[1]
        documented_contract = migration.split("```json\n", 1)[1].split("\n```", 1)[0]
        self.assertEqual(
            json.loads(documented_contract),
            {"review": complete_review_contract()},
        )
        self.assertIn("материализовать указанный `review` contract", aliases)
        self.assertIn("`workflow_kit.revision: v0.8.0`", migration)
        self.assertIn("и выполнить validation записанной revision", migration)
        self.assertIn("`--deliver-task` остаётся fail-closed", migration)
        self.assertIn("Безопасный откат требует вернуть и project configuration", aliases)
        self.assertIn("весь выбранный набор skills на один прежний exact release tag", migration)
        self.assertIn("или смешивать revisions нельзя", migration)


if __name__ == "__main__":
    unittest.main()
