import copy
import json
import re
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # The dependency-free repository validator may run without it.
    Draft202012Validator = None


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
PUBLISH_PREPARE = (
    SKILL_ROOT.parent
    / "publish-planning-change"
    / "references"
    / "publish-reviewed-planning-change.md"
)
PUBLISH_FINALIZE = (
    SKILL_ROOT.parent
    / "publish-planning-change"
    / "references"
    / "finalize-planning-publication.md"
)
PUBLISH_SKILL = SKILL_ROOT.parent / "publish-planning-change" / "SKILL.md"


def complete_current_config():
    required_evidence_fields = [
        "evidence_kind",
        "task_id",
        "specification_owner_repository",
        "canonical_spec_path",
        "pull_request_url",
        "merged_revision",
        "merged_tree_oid",
        "reviewed_head_revision",
        "reviewed_head_tree_oid",
        "complete_reviewed_package_manifest",
        "reviewer_evidence_identifier",
        "reviewer_model",
        "reviewer_effort",
        "review_completed_at",
        "terminal_clean_verdict",
        "review_target_kind",
        "canonical_base_revision",
        "review_binding_method",
        "reviewed_package_manifest_equals_merged",
    ]
    return {
        "schema_version": 3,
        "workflow_kit": {
            "source": "https://github.com/rubyhat/marshall-ai-agent",
            "revision": "v0.0.0-test",
            "installation_mode": "centralized",
            "selected_modules": ["publish-planning-change"],
        },
        "project": {
            "name": "fixture",
            "product_type": "test",
            "repositories": {"root": {"path": "."}},
        },
        "language": {
            "interaction": "en",
            "project_docs": "en",
            "internal_memory": "en",
        },
        "interaction": {
            "clarifying_questions": {},
            "conflict_and_risk_gate": {},
        },
        "paths": {
            "root_instructions": "AGENTS.md",
            "project_docs": "docs_ai",
            "task_specs": "docs_ai/tasks",
            "internal_memory": "local_memory_ai",
        },
        "protection": {
            "default_setup_boundary": "enforced",
            "additional_restrictions": [],
        },
        "planning_publication": {
            "quick_alias": {
                "command": "--publish-spec",
                "capability": "planning_artifact_publication",
                "exact_task_scope_only": True,
            },
            "artifact_policy": {
                "default_spec_root": "docs_ai/tasks",
                "ask_for_spec_root_when_default_is_available": False,
                "explicit_override_allowed": True,
                "implementation_changes_forbidden": True,
                "unrelated_changes_forbidden": True,
            },
            "workspace": {
                "isolated": True,
                "main_checkout_must_remain_clean": True,
            },
            "independent_review": {
                "required": True,
                "fresh_context": True,
                "author_self_check_is_not_independent": True,
                "working_directory": "exact_planning_worktree",
                "working_directory_placeholder": "<PLANNING_WORKTREE>",
                "verify_reported_workdir_and_branch": True,
                "model": "test-reviewer",
                "effort": "medium",
                "max_correction_rounds": 5,
            },
            "readiness": {
                "input_content_verdict": "spec_ready",
                "canonical_merge_required_before_implementation": True,
                "implementation_base_must_contain_publication_revision": True,
                "ordinary_publication_evidence": {
                    "record_kind": "reviewed_canonical_publication",
                    "required_fields": required_evidence_fields,
                    "allowed_review_binding_methods": [
                        "direct_committed_base_diff",
                        "verified_uncommitted_manifest_equivalence",
                    ],
                    "complete_package_manifest_required": True,
                    "reviewed_package_manifest_equals_merged": True,
                    "persist_and_reread_before_cleanup": True,
                },
            },
            "completion_gate": {
                "require_clean_independent_review": True,
                "require_clean_review_bound_to_published_package": True,
                "require_canonical_merge": True,
                "require_persisted_publication_record_readback": True,
                "implementation_issue_remains_open": True,
                "release_or_deploy_forbidden": True,
            },
        },
        "skills": {"active": {"publish-planning-change": "skills/publish"}},
        "commands": {
            "aliases_are_plain_text": True,
            "aliases_do_not_expand_authority": True,
            "sequence_guard": {
                "enabled": True,
                "stop_before_mutation_on_mismatch": True,
                "report_current_state_and_unmet_prerequisite": True,
                "recommend_exact_next_alias_or_action": True,
            },
            "aliases": {"--publish-spec": {}},
        },
    }


class PlanningPublicationContractTest(unittest.TestCase):
    def test_template_uses_out_of_box_documentation_defaults(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("schema_version: 3\n"))
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
            "max_correction_rounds",
        ):
            self.assertIn(required_key, independent_review["required"])
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
        self.assertIn("max_correction_rounds", independent_review["required"])
        self.assertEqual(
            independent_review["properties"]["max_correction_rounds"]["default"],
            5,
        )
        self.assertEqual(
            independent_review["properties"]["max_correction_rounds"]["minimum"],
            1,
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
        self.assertEqual(schema["properties"]["schema_version"]["const"], 3)
        readiness = properties["readiness"]
        self.assertIn("ordinary_publication_evidence", readiness["required"])
        ordinary_evidence = readiness["properties"]["ordinary_publication_evidence"]
        self.assertEqual(
            ordinary_evidence["required"],
            [
                "record_kind",
                "required_fields",
                "allowed_review_binding_methods",
                "complete_package_manifest_required",
                "reviewed_package_manifest_equals_merged",
                "persist_and_reread_before_cleanup",
            ],
        )
        self.assertEqual(
            ordinary_evidence["properties"]["record_kind"]["const"],
            "reviewed_canonical_publication",
        )
        self.assertEqual(
            ordinary_evidence["properties"]["required_fields"]["const"],
            [
                "evidence_kind",
                "task_id",
                "specification_owner_repository",
                "canonical_spec_path",
                "pull_request_url",
                "merged_revision",
                "merged_tree_oid",
                "reviewed_head_revision",
                "reviewed_head_tree_oid",
                "complete_reviewed_package_manifest",
                "reviewer_evidence_identifier",
                "reviewer_model",
                "reviewer_effort",
                "review_completed_at",
                "terminal_clean_verdict",
                "review_target_kind",
                "canonical_base_revision",
                "review_binding_method",
                "reviewed_package_manifest_equals_merged",
            ],
        )
        self.assertEqual(
            ordinary_evidence["properties"]["allowed_review_binding_methods"][
                "const"
            ],
            [
                "direct_committed_base_diff",
                "verified_uncommitted_manifest_equivalence",
            ],
        )
        for required_true_key in (
            "complete_package_manifest_required",
            "reviewed_package_manifest_equals_merged",
            "persist_and_reread_before_cleanup",
        ):
            self.assertIn(required_true_key, ordinary_evidence["required"])
            self.assertTrue(
                ordinary_evidence["properties"][required_true_key]["const"]
            )
        completion_gate = properties["completion_gate"]
        for required_true_key in (
            "require_clean_review_bound_to_published_package",
            "require_persisted_publication_record_readback",
        ):
            self.assertIn(required_true_key, completion_gate["required"])
            self.assertTrue(
                completion_gate["properties"][required_true_key]["const"]
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

    @unittest.skipIf(Draft202012Validator is None, "jsonschema is not installed")
    def test_schema_accepts_only_a_complete_current_publication_config(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        complete = complete_current_config()

        self.assertEqual(list(validator.iter_errors(complete)), [])

        old_version = copy.deepcopy(complete)
        old_version["schema_version"] = 2
        self.assertTrue(list(validator.iter_errors(old_version)))

        missing_paths = (
            ("planning_publication", "independent_review", "working_directory"),
            (
                "planning_publication",
                "independent_review",
                "working_directory_placeholder",
            ),
            (
                "planning_publication",
                "independent_review",
                "verify_reported_workdir_and_branch",
            ),
            ("planning_publication", "readiness", "ordinary_publication_evidence"),
            (
                "planning_publication",
                "readiness",
                "ordinary_publication_evidence",
                "record_kind",
            ),
            (
                "planning_publication",
                "readiness",
                "ordinary_publication_evidence",
                "required_fields",
            ),
            (
                "planning_publication",
                "readiness",
                "ordinary_publication_evidence",
                "allowed_review_binding_methods",
            ),
            (
                "planning_publication",
                "readiness",
                "ordinary_publication_evidence",
                "complete_package_manifest_required",
            ),
            (
                "planning_publication",
                "readiness",
                "ordinary_publication_evidence",
                "reviewed_package_manifest_equals_merged",
            ),
            (
                "planning_publication",
                "readiness",
                "ordinary_publication_evidence",
                "persist_and_reread_before_cleanup",
            ),
            (
                "planning_publication",
                "completion_gate",
                "require_clean_review_bound_to_published_package",
            ),
            (
                "planning_publication",
                "completion_gate",
                "require_persisted_publication_record_readback",
            ),
        )
        for path in missing_paths:
            with self.subTest(missing=".".join(path)):
                incomplete = copy.deepcopy(complete)
                owner = incomplete
                for key in path[:-1]:
                    owner = owner[key]
                del owner[path[-1]]
                self.assertTrue(list(validator.iter_errors(incomplete)))

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
        self.assertIn("fields to be materialized in the current configuration", validation)
        self.assertIn("process working directory to the exact planning worktree", review)
        self.assertIn("current-schema pre-mutation", review)
        self.assertIn("Do not apply compatibility", review)
        self.assertIn("stopped direct publication", review)

    def test_existing_ready_specs_get_deterministic_adoption_evidence(self):
        generated = GENERATE.read_text(encoding="utf-8")
        validation = VALIDATE.read_text(encoding="utf-8")
        readiness = (
            SKILL_ROOT.parent
            / "execute-project-task"
            / "references"
            / "check-task-readiness.md"
        ).read_text(encoding="utf-8")
        execution_skill = (
            SKILL_ROOT.parent / "execute-project-task" / "SKILL.md"
        ).read_text(encoding="utf-8")
        workspace = (
            SKILL_ROOT.parent
            / "execute-project-task"
            / "references"
            / "create-or-resume-task-workspace.md"
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
        self.assertIn("select one complete readiness path", execution_skill)
        self.assertIn("ordinary publication record supersedes legacy", execution_skill)
        self.assertIn("matching exact-task record for the selected path", execution_skill)
        self.assertRegex(readiness, r"select one complete\s+evidence path")
        self.assertIn("prefer ordinary independent review", readiness)
        self.assertIn("missing or incomplete", readiness)
        self.assertIn("partial ordinary record neither", readiness)
        self.assertIn("legacy tuple with its full", readiness)
        self.assertIn("ordinary merged", workspace)
        self.assertIn("or the legacy tuple", workspace)
        self.assertIn("separate recording handoff", task_linkage)
        self.assertIn("legacy_ready_baseline", task_linkage)
        self.assertIn("existing ready status", task_linkage)
        self.assertIn("Reread the persisted tuple", task_linkage)
        self.assertIn("complete path/OID set", task_linkage)

    def test_review_evidence_is_bound_to_the_published_head(self):
        review = PUBLISH_REVIEW.read_text(encoding="utf-8")
        prepare = PUBLISH_PREPARE.read_text(encoding="utf-8")
        finalize = PUBLISH_FINALIZE.read_text(encoding="utf-8")
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

        self.assertIn("Capture a bindable clean-review record", review)
        self.assertIn("reviewer run or session identifier", review)
        self.assertIn("complete sorted publication-package manifest", review)
        self.assertIn("Bind the candidate", prepare)
        self.assertIn("exact path/OID equality", prepare)
        self.assertIn("reviewed_canonical_publication", finalize)
        self.assertIn("bound reviewed-head revision and tree OID", finalize)
        self.assertIn("reviewed_package_manifest_equals_merged: true", finalize)
        self.assertIn("reviewed_canonical_publication", readiness)
        self.assertIn("reviewer run or", readiness)
        self.assertIn("infer clean review from PR prose", task_linkage)

    def test_review_correction_limit_is_an_executable_stop_condition(self):
        publication_skill = PUBLISH_SKILL.read_text(encoding="utf-8")
        review = PUBLISH_REVIEW.read_text(encoding="utf-8")
        generated = GENERATE.read_text(encoding="utf-8")

        self.assertIn("correction-round counter", publication_skill)
        self.assertIn("never start a correction round beyond", publication_skill)
        self.assertIn("correction_rounds_used", review)
        self.assertIn("Do not start a sixth correction", review)
        self.assertIn("review-cycle analysis", review)
        self.assertIn("Preserve the counter", review)
        self.assertIn("max_correction_rounds", generated)

    def test_direct_publication_requires_schema_v3(self):
        publication_skill = PUBLISH_SKILL.read_text(encoding="utf-8")
        validation_contract = VALIDATE.read_text(encoding="utf-8")

        self.assertIn("Before any publication workspace", publication_skill)
        self.assertIn("require schema v3", publication_skill)
        self.assertIn("stop\n  direct `--publish-spec` before mutations", publication_skill)
        self.assertIn("configure-project-workflow", publication_skill)
        self.assertIn("not infer publication readiness", publication_skill)
        self.assertIn(
            "Require project configuration schema v3",
            validation_contract,
        )
        self.assertIn(
            "Treat every other project schema as\n  unsupported",
            validation_contract,
        )


if __name__ == "__main__":
    unittest.main()
