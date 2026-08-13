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
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
SCHEMA = SKILL_ROOT / "assets" / "project-workflow.schema.json"
TEMPLATE = SKILL_ROOT / "assets" / "templates" / "project-workflow.yaml"
GENERATE = SKILL_ROOT / "references" / "generate-project-setup.md"
VALIDATE = SKILL_ROOT / "references" / "validate-project-setup.md"
EXECUTION_ROOT = SKILL_ROOT.parent / "execute-project-task"
DELIVERY_ROOT = SKILL_ROOT.parent / "deliver-reviewed-change"
ALIASES = REPOSITORY_ROOT / "docs" / "workflow-aliases.md"
DELIVERY_TEST = Path(__file__).with_name("test_delivery_review_contract.py")


def load_delivery_fixture():
    spec = importlib.util.spec_from_file_location("delivery_fixture", DELIVERY_TEST)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.complete_delivery_config()


def branch_routing_contract():
    return {
        "fallback": {
            "task_base": "repository_default_branch",
            "pull_request_target": "resolved_task_base_branch",
        },
        "override_scope": {
            "owner": "project_configuration_or_task_contract",
            "granularity": "exact_task_and_repository",
            "resolution_precedence": [
                "exact_task_contract",
                "project_configuration",
            ],
            "resolved_record": {
                "key": ["task_or_aggregate_anchor", "repository"],
                "required_context": [
                    "task_or_aggregate_anchor",
                    "repository",
                    "intended_base_branch",
                    "intended_target_branch",
                    "base_creation_source_branch_or_not_applicable",
                    "target_revision_or_absent",
                    "target_creation_source_branch_or_not_applicable",
                ],
                "values": [
                    {
                        "task_or_aggregate_anchor": "MAI-EPIC-BRANCH-WORKFLOW-72",
                        "repository": "rubyhat/marshall-ai-agent",
                        "intended_base_branch": "integration/epic-72",
                        "intended_target_branch": "main",
                        "base_creation_source_branch_or_not_applicable": "main",
                        "target_revision_or_absent": "verified_target_revision",
                        "target_creation_source_branch_or_not_applicable": (
                            "not_applicable"
                        ),
                        "aggregate_source_branch": "integration/epic-72",
                        "aggregate_destination_branch": "main",
                        "routing_source": "project_configuration",
                    }
                ],
            },
            "branch_registry_required": False,
        },
        "execution_handoff": {
            "required_context": [
                "repository",
                "task_branch",
                "intended_base_branch",
                "intended_target_branch",
                "routing_source",
                "base_creation_source_branch_or_not_applicable",
                "target_revision_or_absent",
                "target_creation_source_branch_or_not_applicable",
                "base_revision",
            ]
        },
        "safety": {
            "missing_intended_base": (
                "establish_from_verified_project_base_without_rewrite"
            ),
            "existing_intended_base": (
                "resume_after_ownership_and_ancestry_verification"
            ),
            "remote_ref_race": "stop_and_reconcile",
            "force_or_history_rewrite_allowed": False,
        },
        "aggregate_promotion": {
            "enabled": True,
            "source_and_target_owner": "project_policy",
            "route_resolution": {
                "policy_reference": (
                    "branch_routing.override_scope.resolved_record.values"
                ),
                "record_key": ["task_or_aggregate_anchor", "repository"],
                "required_context": [
                    "aggregate_source_branch",
                    "aggregate_destination_branch",
                    "routing_source",
                ],
            },
            "readiness_owner": "project_policy",
            "delivery_workspace": {
                "owner": "delivery_workflow",
                "remote_only_source_action": (
                    "materialize_delivery_owned_source_or_helper_worktree"
                ),
                "correction_worktree": "delivery_owned_source_or_helper",
                "completed_child_worktree_reuse_allowed": False,
            },
            "allowed_direct_delivery_evidence_counts": True,
            "meaningful_diff_or_proven_already_integrated_required": True,
            "integrate_current_target_before_review": True,
            "pre_review_integration_commit_allowed": False,
            "conflicts_resolved_on_source_or_helper": True,
            "reuse_standard_review_ci_and_merge_gates": True,
        },
    }


def aggregate_scope_binding():
    return {
        "exact_aggregate_contract_required": True,
        "required_context": [
            "task_or_aggregate_anchor",
            "issue",
            "specification_or_equivalent_contract",
            "specification_revision_or_not_applicable",
            "acceptance_criteria",
            "non_goals",
            "repositories",
            "worktrees",
            "branches",
            "target_branches",
            "aggregate_readiness_evidence",
            "direct_delivery_evidence",
            "pre_review_destination_revisions",
            "initial_diff_manifest",
            "initial_diff_stats",
        ],
        "initial_diff_baseline_required": True,
        "baseline_immutable_for_delivery_attempt": True,
    }


class BranchRoutingContractTest(unittest.TestCase):
    def test_schema_materializes_compatible_routing_and_optional_promotion(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        routing = schema["properties"]["branch_routing"]

        self.assertNotIn("aggregate_promotion", routing["required"])
        self.assertEqual(
            "repository_default_branch",
            routing["properties"]["fallback"]["properties"]["task_base"][
                "const"
            ],
        )
        self.assertFalse(
            routing["properties"]["safety"]["properties"][
                "force_or_history_rewrite_allowed"
            ]["const"]
        )
        self.assertFalse(
            routing["properties"]["aggregate_promotion"]["properties"][
                "enabled"
            ]["default"]
        )
        promotion = routing["properties"]["aggregate_promotion"]
        self.assertEqual(["enabled"], promotion["required"])
        self.assertIn(
            "route_resolution",
            promotion["allOf"][0]["then"]["required"],
        )
        self.assertIn(
            "delivery_workspace",
            promotion["allOf"][0]["then"]["required"],
        )
        self.assertFalse(
            promotion["properties"]["pre_review_integration_commit_allowed"][
                "const"
            ]
        )
        route_resolution = routing["properties"]["aggregate_promotion"][
            "properties"
        ]["route_resolution"]
        self.assertEqual(
            "branch_routing.override_scope.resolved_record.values",
            route_resolution["properties"]["policy_reference"]["const"],
        )
        self.assertEqual(
            ["task_or_aggregate_anchor", "repository"],
            route_resolution["properties"]["record_key"]["const"],
        )
        override = routing["properties"]["override_scope"]["properties"]
        self.assertEqual(
            ["task_or_aggregate_anchor", "repository"],
            override["resolved_record"]["properties"]["key"]["const"],
        )
        self.assertFalse(override["branch_registry_required"]["const"])
        values = override["resolved_record"]["properties"]["values"]
        self.assertEqual("array", values["type"])
        self.assertNotIn("minItems", values)
        self.assertEqual(
            [
                "task_or_aggregate_anchor",
                "repository",
                "intended_base_branch",
                "intended_target_branch",
                "base_creation_source_branch_or_not_applicable",
                "target_revision_or_absent",
                "target_creation_source_branch_or_not_applicable",
            ],
            values["items"]["required"],
        )
        enabled_values = schema["allOf"][0]["then"]["properties"][
            "branch_routing"
        ]["properties"]["override_scope"]["properties"]["resolved_record"][
            "properties"
        ]["values"]
        self.assertEqual(1, enabled_values["minItems"])
        for field in (
            "task_or_aggregate_anchor",
            "repository",
            "aggregate_source_branch",
            "aggregate_destination_branch",
            "routing_source",
        ):
            self.assertEqual(
                "string", values["items"]["properties"][field]["type"]
            )

    def test_schema_accepts_optional_project_owned_branch_routing(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        config = load_delivery_fixture()
        config["branch_routing"] = branch_routing_contract()
        config["review"]["aggregate_scope_binding"] = aggregate_scope_binding()

        errors = list(Draft202012Validator(schema).iter_errors(config))
        self.assertEqual([], [error.message for error in errors])

    def test_schema_preserves_default_branch_compatibility(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        config = load_delivery_fixture()

        errors = list(Draft202012Validator(schema).iter_errors(config))
        self.assertEqual([], [error.message for error in errors])

    def test_schema_accepts_minimal_explicitly_disabled_promotion(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        config = load_delivery_fixture()
        config["branch_routing"] = branch_routing_contract()
        config["branch_routing"]["aggregate_promotion"] = {"enabled": False}
        config["branch_routing"]["override_scope"]["resolved_record"][
            "values"
        ] = []

        errors = list(Draft202012Validator(schema).iter_errors(config))
        self.assertEqual([], [error.message for error in errors])

    def test_schema_requires_ordinary_fields_on_every_populated_route(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        config = load_delivery_fixture()
        config["branch_routing"] = branch_routing_contract()
        config["branch_routing"]["aggregate_promotion"] = {"enabled": False}
        route = config["branch_routing"]["override_scope"]["resolved_record"][
            "values"
        ][0]
        for field in (
            "aggregate_source_branch",
            "aggregate_destination_branch",
            "routing_source",
        ):
            del route[field]

        validator = Draft202012Validator(schema)
        self.assertEqual([], list(validator.iter_errors(config)))
        del route["intended_target_branch"]
        self.assertTrue(list(validator.iter_errors(config)))

        config = load_delivery_fixture()
        config["branch_routing"] = branch_routing_contract()
        config["branch_routing"]["aggregate_promotion"] = {"enabled": False}
        del config["branch_routing"]["override_scope"]["resolved_record"][
            "values"
        ][0]["target_creation_source_branch_or_not_applicable"]
        self.assertTrue(list(validator.iter_errors(config)))

    def test_schema_rejects_history_rewrite_permission(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        config = load_delivery_fixture()
        config["branch_routing"] = copy.deepcopy(branch_routing_contract())
        config["review"]["aggregate_scope_binding"] = aggregate_scope_binding()
        config["branch_routing"]["safety"][
            "force_or_history_rewrite_allowed"
        ] = True

        errors = list(Draft202012Validator(schema).iter_errors(config))
        self.assertTrue(errors)

    def test_schema_rejects_enabled_promotion_without_delivery_module(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        config = load_delivery_fixture()
        config["workflow_kit"]["selected_modules"].remove(
            "deliver-reviewed-change"
        )
        config["branch_routing"] = branch_routing_contract()
        config["review"]["aggregate_scope_binding"] = aggregate_scope_binding()

        validator = Draft202012Validator(schema)
        self.assertTrue(list(validator.iter_errors(config)))

        config["branch_routing"]["aggregate_promotion"] = {"enabled": False}
        self.assertEqual([], list(validator.iter_errors(config)))

    def test_enabled_promotion_requires_aggregate_review_scope(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        config = load_delivery_fixture()
        config["branch_routing"] = branch_routing_contract()
        validator = Draft202012Validator(schema)

        self.assertTrue(list(validator.iter_errors(config)))
        config["review"]["aggregate_scope_binding"] = aggregate_scope_binding()
        self.assertEqual([], list(validator.iter_errors(config)))

    def test_enabled_promotion_requires_resolvable_source_and_destination_route(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        config = load_delivery_fixture()
        config["branch_routing"] = branch_routing_contract()
        config["review"]["aggregate_scope_binding"] = aggregate_scope_binding()
        validator = Draft202012Validator(schema)

        del config["branch_routing"]["aggregate_promotion"]["route_resolution"]
        self.assertTrue(list(validator.iter_errors(config)))

        config["branch_routing"] = branch_routing_contract()
        config["branch_routing"]["aggregate_promotion"]["route_resolution"][
            "policy_reference"
        ] = "untyped.project.policy"
        self.assertTrue(list(validator.iter_errors(config)))

        config["branch_routing"] = branch_routing_contract()
        del config["branch_routing"]["override_scope"]["resolved_record"]["values"][
            0
        ]["aggregate_source_branch"]
        self.assertTrue(list(validator.iter_errors(config)))

        config["branch_routing"] = branch_routing_contract()
        config["branch_routing"]["override_scope"]["resolved_record"]["values"][
            0
        ]["aggregate_destination_branch"] = ""
        self.assertTrue(list(validator.iter_errors(config)))

    def test_enabled_promotion_accepts_one_route_per_repository(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        config = load_delivery_fixture()
        config["branch_routing"] = branch_routing_contract()
        config["review"]["aggregate_scope_binding"] = aggregate_scope_binding()
        config["branch_routing"]["override_scope"]["resolved_record"]["values"].append(
            {
                "task_or_aggregate_anchor": "MAI-EPIC-BRANCH-WORKFLOW-72",
                "repository": "rubyhat/consumer-repository",
                "intended_base_branch": "integration/epic-72",
                "intended_target_branch": "main",
                "base_creation_source_branch_or_not_applicable": "main",
                "target_revision_or_absent": "verified_target_revision",
                "target_creation_source_branch_or_not_applicable": (
                    "not_applicable"
                ),
                "aggregate_source_branch": "integration/epic-72",
                "aggregate_destination_branch": "main",
                "routing_source": "exact_task_contract",
            }
        )

        errors = list(Draft202012Validator(schema).iter_errors(config))
        self.assertEqual([], [error.message for error in errors])

    def test_enabled_promotion_requires_delivery_owned_correction_worktree(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        config = load_delivery_fixture()
        config["branch_routing"] = branch_routing_contract()
        config["review"]["aggregate_scope_binding"] = aggregate_scope_binding()
        validator = Draft202012Validator(schema)

        del config["branch_routing"]["aggregate_promotion"]["delivery_workspace"]
        self.assertTrue(list(validator.iter_errors(config)))

        config["branch_routing"] = branch_routing_contract()
        config["branch_routing"]["aggregate_promotion"]["delivery_workspace"][
            "completed_child_worktree_reuse_allowed"
        ] = True
        self.assertTrue(list(validator.iter_errors(config)))

    def test_execution_contract_resolves_each_repository_and_missing_base(self):
        execution_skill = (EXECUTION_ROOT / "SKILL.md").read_text(encoding="utf-8")
        workspace = (
            EXECUTION_ROOT / "references" / "create-or-resume-task-workspace.md"
        ).read_text(encoding="utf-8")
        multi_repo = (
            EXECUTION_ROOT / "references" / "create-multi-repo-worktrees.md"
        ).read_text(encoding="utf-8")

        for fragment in (
            "repository default branch for both",
            "intended task base and pull-request target",
            "without force, reset, or history rewrite",
            "remote base or target branch appears or moves before delivery",
        ):
            self.assertIn(fragment, execution_skill + workspace)
        self.assertIn("repository's project- or task-defined intended base", multi_repo)
        self.assertIn("rather than\n  a branch inferred from another repository", multi_repo)
        self.assertIn("verify the intended target independently", workspace)
        self.assertIn("target revision or\n    explicit absence", workspace)
        self.assertIn("target-creation source branches", workspace)

    def test_delivery_contract_uses_actual_target_and_aggregate_mode(self):
        delivery_skill = (DELIVERY_ROOT / "SKILL.md").read_text(encoding="utf-8")
        readiness = (
            DELIVERY_ROOT / "references" / "verify-delivery-readiness.md"
        ).read_text(encoding="utf-8")
        pull_request = (
            DELIVERY_ROOT / "references" / "commit-push-and-open-pr.md"
        ).read_text(encoding="utf-8")
        cleanup = (
            DELIVERY_ROOT / "references" / "merge-close-and-clean.md"
        ).read_text(encoding="utf-8")
        normalized_readiness = " ".join(readiness.split())

        self.assertIn("`promote`", delivery_skill)
        self.assertIn("standalone aggregate delivery", readiness)
        self.assertIn("delivery-owned source/helper worktree", delivery_skill)
        self.assertIn("source exists only as a remote ref", readiness)
        self.assertIn("completed child task's worktree", readiness)
        self.assertIn("return `Already integrated`", readiness)
        self.assertIn(
            "return `Already integrated` only when every selected repository",
            normalized_readiness,
        )
        self.assertIn("return `Not ready` and fail closed", normalized_readiness)
        self.assertIn("actual target branch resolved", pull_request)
        self.assertIn("Never push, forward, or", pull_request)
        self.assertIn("ordinary delivery pushes to that source branch", pull_request)
        self.assertIn("Only when execution prepared the target locally", pull_request)
        self.assertIn("provider-supported non-overwriting creation", pull_request)
        self.assertIn("non-committing strategy", readiness)
        self.assertIn("first point where newly prepared", pull_request)
        self.assertIn("mark that\n   repository route satisfied", readiness)
        self.assertIn("only when every selected repository", readiness)
        self.assertIn("exact destination revision", readiness)
        self.assertIn("pre-review destination revision", cleanup)
        self.assertIn("repository owned by the exact pull request", cleanup)
        self.assertIn("Previously\n  completed repositories", cleanup)
        self.assertIn("rerun every invalidated local\n  review", cleanup)
        self.assertIn("update the actual merged target branch", cleanup)
        self.assertIn("Do not remove an aggregate or integration source branch", cleanup)

    def test_setup_and_public_aliases_cover_positive_recovery_and_noop_paths(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (TEMPLATE, GENERATE, VALIDATE, ALIASES)
        )

        for fragment in (
            "task_base: repository_default_branch",
            "granularity: exact_task_and_repository",
            "remote_ref_race: stop_and_reconcile",
            "aggregate_promotion:",
            "policy_reference: branch_routing.override_scope.resolved_record.values",
            "aggregate_source_branch",
            "aggregate_destination_branch",
            "remote_only_source_action: materialize_delivery_owned_source_or_helper_worktree",
            "completed_child_worktree_reuse_allowed: false",
            "meaningful_diff_or_proven_already_integrated_required: true",
            "pre_review_integration_commit_allowed: false",
            "base_creation_source_branch_or_not_applicable",
            "target_revision_or_absent",
            "target_creation_source_branch_or_not_applicable",
            "branch_registry_required: false",
            "aggregate_scope_binding:",
            "aggregate_readiness_evidence",
            "pre_review_destination_revisions",
            "safe helper",
            "не создаёт пустую ветку\nили PR",
        ):
            self.assertIn(fragment, combined)


if __name__ == "__main__":
    unittest.main()
