from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # Repository validation remains dependency-free.
    Draft202012Validator = None


SKILL_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = SKILL_ROOT / "assets"
TEMPLATE = ASSETS_ROOT / "templates" / "project-workflow.yaml"
SCHEMA = ASSETS_ROOT / "project-workflow.schema.json"
GENERATE = SKILL_ROOT / "references" / "generate-project-setup.md"
VALIDATE = SKILL_ROOT / "references" / "validate-project-setup.md"
PUBLISH_ROOT = SKILL_ROOT.parent / "publish-planning-change"
PUBLISH_SKILL = PUBLISH_ROOT / "SKILL.md"
PUBLISH_REVIEW = PUBLISH_ROOT / "references" / "run-independent-spec-review.md"
PUBLISH_PREPARE = PUBLISH_ROOT / "references" / "publish-reviewed-planning-change.md"
PUBLISH_FINALIZE = PUBLISH_ROOT / "references" / "finalize-planning-publication.md"
RUNNER = PUBLISH_ROOT / "scripts" / "run_codex_spec_review.py"
WRITE_SKILL = SKILL_ROOT.parent / "write-task-spec" / "SKILL.md"
EXECUTE_SKILL = SKILL_ROOT.parent / "execute-project-task" / "SKILL.md"
EXECUTE_READINESS = (
    SKILL_ROOT.parent
    / "execute-project-task"
    / "references"
    / "check-task-readiness.md"
)
EXECUTE_WORKSPACE = (
    SKILL_ROOT.parent
    / "execute-project-task"
    / "references"
    / "create-or-resume-task-workspace.md"
)
MANAGE_LINKAGE = (
    SKILL_ROOT.parent
    / "manage-project-work"
    / "references"
    / "link-and-close-project-task.md"
)


EVIDENCE_FIELDS = [
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
    "review_capture_contract_revision",
    "review_publication_attempt_id",
    "review_result_sha256",
    "matched_reviewer_session_ids",
]


def runner_config():
    return {
        "kind": "codex_review_authoritative_session_runner",
        "active_skill_relative_path": "scripts/run_codex_spec_review.py",
        "command_template": (
            'python3 "<ACTIVE_SKILL_PATH>/scripts/run_codex_spec_review.py" '
            '--worktree "<PLANNING_WORKTREE>" --task-id "<TASK_ID>" '
            '--target-kind "<REVIEW_TARGET_KIND>" --base "<CANONICAL_BASE_REF>" '
            '--model "<REVIEWER_MODEL>" --effort "<REVIEWER_EFFORT>" '
            '--minimum-stable-scans "<MINIMUM_STABLE_SCANS>" '
            '--settle-interval-seconds "<SETTLE_INTERVAL_SECONDS>" '
            '--settlement-timeout-seconds "<SETTLEMENT_TIMEOUT_SECONDS>"'
        ),
        "required_placeholders": [
            "<ACTIVE_SKILL_PATH>",
            "<PLANNING_WORKTREE>",
            "<TASK_ID>",
            "<REVIEW_TARGET_KIND>",
            "<CANONICAL_BASE_REF>",
            "<REVIEWER_MODEL>",
            "<REVIEWER_EFFORT>",
            "<MINIMUM_STABLE_SCANS>",
            "<SETTLE_INTERVAL_SECONDS>",
            "<SETTLEMENT_TIMEOUT_SECONDS>",
        ],
        "direct_codex_review_allowed": False,
    }


def result_capture_config():
    return {
        "authoritative_source": "child_session_task_complete_last_agent_message",
        "outer_session_id_source": "captured_subprocess_startup_header",
        "require_invocation_parent_session_match": True,
        "require_outer_session_meta_id_source_cwd_and_boundary_match": True,
        "require_review_subagent_source": True,
        "require_exact_worktree_and_target": True,
        "outer_process_output_is_diagnostic_only": True,
        "terminal_schema": "native_codex_review_v1",
        "multiple_terminal_policy": "union_deduplicate_fail_closed",
        "technical_retry_only_without_authoritative_terminal": True,
        "max_technical_retries_per_publication_attempt": 1,
        "preserve_attempt_boundary_across_retries": True,
        "require_terminal_session_settlement": True,
        "require_matched_child_terminal_state": True,
        "minimum_stable_scans": 2,
        "settle_interval_seconds": 2,
        "settlement_timeout_seconds": 30,
        "final_rescan_before_verdict": True,
        "capture_cumulative_token_usage": True,
    }


def ordinary_implementation_path():
    return {
        "tuple": EVIDENCE_FIELDS,
        "required_evidence_kind": "reviewed_canonical_publication",
        "review_capture_contract_revision": 1,
        "persisted_record_readback_required": True,
        "independent_review_required": True,
        "specification_owner_authority_base_must_contain_revision": True,
        "current_authority_base_package_manifest_must_equal_selected_record": True,
    }


def complete_current_config():
    return {
        "schema_version": 4,
        "workflow_kit": {
            "source": "https://github.com/example/workflow-kit",
            "revision": "v0.0.0-test",
            "installation_mode": "centralized",
            "selected_modules": [
                "publish-planning-change",
                "execute-project-task",
            ],
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
                "committed_correction_review": {
                    "strategy": "local_checkpoint_committed_base_diff",
                    "checkpoint_commit_allowed": True,
                    "deterministic_checks_before_checkpoint": True,
                    "checkpoint_exact_manifest_only": True,
                    "push_before_clean_review": False,
                },
                "runner": runner_config(),
                "result_capture": result_capture_config(),
            },
            "readiness": {
                "input_content_verdict": "spec_ready",
                "canonical_merge_required_before_implementation": True,
                "implementation_base_must_contain_publication_revision": True,
                "ordinary_publication_evidence": {
                    "record_kind": "reviewed_canonical_publication",
                    "required_fields": EVIDENCE_FIELDS,
                    "allowed_review_binding_methods": [
                        "direct_committed_base_diff",
                        "verified_uncommitted_manifest_equivalence",
                    ],
                    "complete_package_manifest_required": True,
                    "reviewed_package_manifest_equals_merged": True,
                    "persist_and_reread_before_cleanup": True,
                },
                "legacy_ready_adoption": {"enabled": False},
                "correction_entry": {
                    "kind": "stale_published_ready_spec",
                    "accepted_content_verdict": "ready_for_implementation",
                    "required_readiness_status": "publication_upgrade_required",
                    "require_existing_canonical_publication": True,
                    "close_implementation_authority_before_review": True,
                    "provisional_target_verdict": "ready_for_implementation",
                },
                "evidence_migration": {
                    "classification": "publication_upgrade_required",
                    "inventory_all_ready_specs": True,
                    "preserve_historical_evidence_for_audit": True,
                    "downgrade_only_exact_ready_status": "ready_for_implementation",
                    "other_configured_status_action": "audit_only",
                    "post_merge_authoritative_rescan": True,
                    "completion_predicate": "zero_old_evidence_items_still_ready_for_implementation",
                    "next_action_template": "--publish-spec <TASK_ID>",
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
        "implementation": {
            "readiness": {
                "publication_evidence": {
                    "required": True,
                    "selection_precedence": ["ordinary_reviewed_publication"],
                    "accepted_paths": {
                        "ordinary_reviewed_publication": ordinary_implementation_path()
                    },
                    "ordinary_only_before_workspace_mutation": True,
                },
                "publication_upgrade_stop": {
                    "status": "publication_upgrade_required",
                    "required_capture_contract_revision": 1,
                    "workspace_created": False,
                    "next_action_template": "--publish-spec <TASK_ID>",
                },
            }
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
            "aliases": {"--publish-spec": {}, "--execute-task": {}},
        },
    }


class PlanningPublicationContractTest(unittest.TestCase):
    def test_template_materializes_schema4_runner_and_ordinary_only_readiness(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("schema_version: 4\n"))
        self.assertIn("scripts/run_codex_spec_review.py", text)
        self.assertIn("direct_codex_review_allowed: false", text)
        self.assertIn("max_technical_retries_per_publication_attempt: 1", text)
        self.assertIn('--minimum-stable-scans "<MINIMUM_STABLE_SCANS>"', text)
        self.assertIn('--settle-interval-seconds "<SETTLE_INTERVAL_SECONDS>"', text)
        self.assertIn(
            '--settlement-timeout-seconds "<SETTLEMENT_TIMEOUT_SECONDS>"', text
        )
        self.assertIn("legacy_ready_adoption:\n      enabled: false", text)
        self.assertIn("selection_precedence:\n        - ordinary_reviewed_publication", text)
        self.assertIn("publication_upgrade_required", text)

    def test_schema_requires_authoritative_runner_and_capture_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema_version"]["const"], 4)
        review = schema["properties"]["planning_publication"]["properties"][
            "independent_review"
        ]
        self.assertIn("runner", review["required"])
        self.assertIn("result_capture", review["required"])
        runner_schema = review["properties"]["runner"]
        self.assertEqual(
            runner_schema["properties"]["active_skill_relative_path"]["const"],
            "scripts/run_codex_spec_review.py",
        )
        self.assertFalse(
            runner_schema["properties"]["direct_codex_review_allowed"]["const"]
        )
        capture = review["properties"]["result_capture"]
        self.assertEqual(
            capture["properties"]["max_technical_retries_per_publication_attempt"]["const"],
            1,
        )
        self.assertEqual(capture["properties"]["minimum_stable_scans"]["minimum"], 2)
        self.assertEqual(capture["properties"]["settle_interval_seconds"]["type"], "integer")
        self.assertEqual(capture["properties"]["settle_interval_seconds"]["maximum"], 10)
        self.assertEqual(capture["properties"]["settlement_timeout_seconds"]["maximum"], 120)
        self.assertEqual(
            runner_schema["properties"]["required_placeholders"]["const"][-3:],
            [
                "<MINIMUM_STABLE_SCANS>",
                "<SETTLE_INTERVAL_SECONDS>",
                "<SETTLEMENT_TIMEOUT_SECONDS>",
            ],
        )

    def test_schema_requires_current_evidence_and_disables_legacy_readiness(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        readiness = schema["properties"]["planning_publication"]["properties"][
            "readiness"
        ]
        self.assertIn("legacy_ready_adoption", readiness["required"])
        self.assertFalse(
            readiness["properties"]["legacy_ready_adoption"]["properties"]["enabled"]["const"]
        )
        fields = readiness["properties"]["ordinary_publication_evidence"][
            "properties"
        ]["required_fields"]["const"]
        for required in (
            "review_capture_contract_revision",
            "review_publication_attempt_id",
            "review_result_sha256",
            "matched_reviewer_session_ids",
        ):
            self.assertIn(required, fields)
        implementation = schema["properties"]["implementation"]["properties"][
            "readiness"
        ]["properties"]
        evidence = implementation["publication_evidence"]["properties"]
        self.assertEqual(
            evidence["selection_precedence"]["const"],
            ["ordinary_reviewed_publication"],
        )
        self.assertFalse(
            evidence["accepted_paths"].get("additionalProperties", True)
        )
        self.assertEqual(
            implementation["publication_upgrade_stop"]["properties"]["workspace_created"]["const"],
            False,
        )

    @unittest.skipIf(Draft202012Validator is None, "jsonschema is not installed")
    def test_schema_accepts_complete_contract_and_rejects_partial_or_old_variants(self):
        validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
        complete = complete_current_config()
        self.assertEqual(list(validator.iter_errors(complete)), [])

        old_schema = copy.deepcopy(complete)
        old_schema["schema_version"] = 3
        self.assertTrue(list(validator.iter_errors(old_schema)))

        enabled_legacy = copy.deepcopy(complete)
        enabled_legacy["planning_publication"]["readiness"]["legacy_ready_adoption"][
            "enabled"
        ] = True
        self.assertTrue(list(validator.iter_errors(enabled_legacy)))

        direct_codex = copy.deepcopy(complete)
        direct_codex["planning_publication"]["independent_review"]["runner"][
            "command_template"
        ] = "codex review --base main"
        self.assertTrue(list(validator.iter_errors(direct_codex)))

        invalid_settlement_window = copy.deepcopy(complete)
        invalid_settlement_window["planning_publication"]["independent_review"][
            "result_capture"
        ]["settlement_timeout_seconds"] = 2
        self.assertTrue(list(validator.iter_errors(invalid_settlement_window)))

        missing_runtime_placeholder = copy.deepcopy(complete)
        missing_runtime_placeholder["planning_publication"]["independent_review"][
            "runner"
        ]["command_template"] = (
            'python3 "<ACTIVE_SKILL_PATH>/scripts/run_codex_spec_review.py" '
            '--worktree "<PLANNING_WORKTREE>" --task-id "<TASK_ID>" '
            '--target-kind "<REVIEW_TARGET_KIND>" --base "<CANONICAL_BASE_REF>" '
            '--model "<REVIEWER_MODEL>"'
        )
        self.assertTrue(list(validator.iter_errors(missing_runtime_placeholder)))

        legacy_path = copy.deepcopy(complete)
        legacy_path["implementation"]["readiness"]["publication_evidence"][
            "accepted_paths"
        ]["legacy_ready_baseline"] = {}
        self.assertTrue(list(validator.iter_errors(legacy_path)))

        missing_provenance = copy.deepcopy(complete)
        missing_provenance["planning_publication"]["readiness"][
            "ordinary_publication_evidence"
        ]["required_fields"] = EVIDENCE_FIELDS[:-1]
        self.assertTrue(list(validator.iter_errors(missing_provenance)))

        for key in ("runner", "result_capture"):
            with self.subTest(missing=key):
                incomplete = copy.deepcopy(complete)
                del incomplete["planning_publication"]["independent_review"][key]
                self.assertTrue(list(validator.iter_errors(incomplete)))

    def test_verdict_lifecycle_has_one_review_per_semantic_revision(self):
        publication_skill = PUBLISH_SKILL.read_text(encoding="utf-8")
        review = PUBLISH_REVIEW.read_text(encoding="utf-8")
        prepare = PUBLISH_PREPARE.read_text(encoding="utf-8")
        write_skill = WRITE_SKILL.read_text(encoding="utf-8")
        combined = "\n".join((publication_skill, review, prepare))
        for removed in (
            "downgrade that stale verdict",
            "apply only that verdict mutation",
            "replacement local-only checkpoint containing the promoted verdict",
        ):
            self.assertNotIn(removed, combined)
        self.assertIn("Before computing the review manifest", publication_skill)
        self.assertIn("provisional `Ready for implementation`", write_skill)
        self.assertIn("preserving the\nprovisional `Ready for implementation`", review)
        self.assertIn("without any post-review verdict", publication_skill)
        self.assertIn("One clean review for the current head is terminal", review)

    def test_authoritative_result_capture_is_fail_closed_and_bounded(self):
        review = PUBLISH_REVIEW.read_text(encoding="utf-8")
        for required in (
            "event_msg.task_complete.payload.last_agent_message",
            "two consecutive stable scans",
            "session_settlement_timeout",
            "no_authoritative_terminal_result",
            "technical_retry_budget_exhausted",
            "incorrect_without_findings",
            "publication-attempt ID",
            "normalized-result SHA-256",
            "`clean` → `0`",
            "exit code `64`",
        ):
            self.assertIn(required, review)
        self.assertTrue(RUNNER.is_file())
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn("CAPTURE_CONTRACT_REVISION = 1", runner)
        self.assertIn("build_review_instructions", runner)
        self.assertIn('"developer_instructions="', runner)
        self.assertIn("specification-contract rubric", review)

    def test_execution_and_workspace_reject_legacy_authority(self):
        execution = EXECUTE_SKILL.read_text(encoding="utf-8")
        readiness = EXECUTE_READINESS.read_text(encoding="utf-8")
        workspace = EXECUTE_WORKSPACE.read_text(encoding="utf-8")
        linkage = MANAGE_LINKAGE.read_text(encoding="utf-8")
        self.assertIn("Historical legacy\nbaseline evidence remains audit input only", execution)
        self.assertIn("Stop for publication evidence upgrade", readiness)
        self.assertIn("workspace_created: false", readiness)
        self.assertIn("Historical legacy derived revisions", workspace)
        self.assertIn("audit history but never become\nimplementation authority", linkage)
        self.assertNotIn("or valid recorded `legacy_ready_baseline`", workspace)
        self.assertNotIn("Ready by configured migration evidence", readiness)

    def test_cutover_preserves_non_ready_statuses_and_requires_rescan(self):
        generated = GENERATE.read_text(encoding="utf-8")
        validation = VALIDATE.read_text(encoding="utf-8")
        linkage = MANAGE_LINKAGE.read_text(encoding="utf-8")
        for text in (generated, validation, linkage):
            self.assertIn("publication_upgrade_required", text)
        self.assertIn("status-preserving reconciliation", generated)
        self.assertIn("post-merge rescan", validation)
        self.assertIn("Preserve\nevery other configured lifecycle", linkage)
        self.assertIn("zero old-evidence items", linkage)

    def test_publication_record_persists_capture_provenance(self):
        finalize = PUBLISH_FINALIZE.read_text(encoding="utf-8")
        linkage = MANAGE_LINKAGE.read_text(encoding="utf-8")
        for text in (finalize, linkage):
            self.assertIn("capture-contract revision", text)
            self.assertIn("publication-attempt ID", text)
            self.assertIn("normalized-result SHA-256", text)
            self.assertIn("matched reviewer session", text)

    def test_generation_and_validation_require_schema4_without_compatibility(self):
        generated = GENERATE.read_text(encoding="utf-8")
        validation = VALIDATE.read_text(encoding="utf-8")
        publication = PUBLISH_SKILL.read_text(encoding="utf-8")
        self.assertIn("configuration schema v4", generated)
        self.assertIn("project configuration schema v4", validation)
        self.assertIn("require schema v4", publication)
        self.assertIn("Reject a direct `codex review`", generated)
        self.assertIn("ordinary reviewed publication as\n  the only implementation-readiness path", generated)


if __name__ == "__main__":
    unittest.main()
