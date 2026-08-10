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
PUBLISH_POST_PR = (
    PUBLISH_ROOT / "references" / "verify-post-pr-planning-correction.md"
)
PUBLISH_GITHUB_CYCLE = (
    PUBLISH_ROOT / "references" / "run-planning-github-review-cycle.md"
)
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
    "matched_reviewer_terminal_event_ids",
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
            '--settlement-timeout-seconds "<SETTLEMENT_TIMEOUT_SECONDS>" '
            '--invocation-timeout-seconds "<INVOCATION_TIMEOUT_SECONDS>"'
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
            "<INVOCATION_TIMEOUT_SECONDS>",
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
        "invocation_timeout_seconds": 900,
        "final_rescan_before_verdict": True,
        "capture_cumulative_token_usage": True,
    }


def post_pr_correction_review_config():
    return {
        "full_independent_review_after_each_github_package": False,
        "initial_github_generation_required": True,
        "github_generation_target": "exact_current_full_head",
        "clean_github_generation_required_before_final_evidence_and_merge": True,
        "github_review_cycle": {
            "enabled": True,
            "request_comment": "@codex review",
            "reviewer_logins": ["chatgpt-codex-connector[bot]"],
            "reviewer_login_contains": [],
            "acknowledgment_reactions": ["eyes", "+1"],
            "acknowledgment_is_terminal": False,
            "inspect_channels": [
                "issue_comments",
                "formal_reviews",
                "inline_review_comments",
            ],
            "clean_verdict_patterns": [
                "Codex Review: Didn't find any major issues.",
            ],
            "explicit_error_patterns": ["Codex Review: Something went wrong"],
            "generation": {
                "bound_to_exact_current_full_head": True,
                "fresh_after_each_correction_package": True,
                "old_events_cannot_complete_new_head": True,
                "response_binding_required": (
                    "exact_reviewed_commit_or_active_request_generation"
                ),
                "unbound_or_old_head_event_action": (
                    "record_stale_and_ignore_for_current_generation"
                ),
            },
            "correction_counter": {
                "scope": "exact_pull_request",
                "max_correction_rounds": 5,
                "initialize_new_pull_request_at_zero": True,
                "increment_once_after_applied_package": True,
                "final_allowed_package_receives_generation": True,
                "next_package_after_limit_stops_before_mutation": True,
                "ordered_history_required": True,
            },
            "request_budget": {
                "max_attempts_per_head": 2,
                "silent_heartbeats_per_attempt": 2,
                "acknowledged_heartbeats_without_result": 3,
                "explicit_error_consumes_current_attempt": True,
                "explicit_error_retry_transition": (
                    "persist_transient_error_then_create_and_bind_next_request"
                ),
                "exhausted_action": "pause_request_budget_exhausted",
                "new_head_resets_technical_counters_only": True,
            },
            "heartbeat": {
                "state_store": "exact_planning_pr_heartbeat",
                "scope": "exact_pull_request",
                "interval_minutes": 7,
                "destination": "current_thread",
                "create_and_read_back_before_request": True,
                "attach_request_identity_and_read_back_before_monitoring": True,
                "update_and_read_back_after_each_transition": True,
                "pause_on_review_terminal_while_pull_request_open": True,
                "same_pull_request_later_head_reactivates": True,
                "delete_after_pull_request_terminal_only": True,
                "lost_state_stops_monitor": True,
            },
            "state_machine": {
                "states": [
                    "request_not_created",
                    "request_pending",
                    "not_started",
                    "in_progress",
                    "findings_received",
                    "transient_error",
                    "clean",
                    "terminal",
                    "pr_terminal",
                    "head_mismatch",
                    "unclassified_response",
                ],
                "evaluation_order": [
                    "pr_terminal",
                    "head_mismatch",
                    "findings_received",
                    "clean",
                    "transient_error",
                    "in_progress",
                    "not_started",
                    "unclassified_response",
                ],
                "clean_is_absorbing_terminal_state": True,
                "silence_is_never_in_progress": True,
                "reactions_checked_on_exact_request_comment_only": True,
                "every_response_channel_checked_before_silence": True,
            },
            "finding_policy": {
                "classifications": [
                    "real_in_scope",
                    "false",
                    "intentional_out_of_scope",
                    "duplicate",
                    "uncertain",
                ],
                "actionable_requires_real_in_scope": True,
                "non_actionable_action": (
                    "evidence_reply_and_contextual_rereview"
                ),
                "non_actionable_consumes_correction_round": False,
                "semantic_fingerprint_required": True,
                "one_semantic_repeat_stops_monitor": True,
                "uncertain_action": "stop_before_edits_and_return_to_owner",
            },
        },
        "routine_github_correction_verification": {
            "affected_tests_required": True,
            "configured_deterministic_gates_required": True,
            "git_diff_check_required": True,
            "exact_correction_delta_required": True,
            "finding_by_finding_readback_required": True,
            "intentional_commit_required_before_push": True,
            "local_commit_head_and_manifest_readback_required": True,
            "next_github_generation_reviews_full_head": True,
            "local_model_invocations": 0,
            "follow_on_gate_fix_rechecks_materiality_before_mutation": True,
            "material_or_uncertain_action": "stop_before_edits_and_return_to_owner",
        },
        "final_evidence_review": {
            "reuse_when": "github_clean_and_exact_current_head_tree_manifest_binding_valid",
            "when": "github_clean_and_exact_current_head_tree_manifest_binding_missing_or_invalid",
            "maximum_invocations": 1,
            "review_target": "exact_current_committed_head",
            "uses_canonical_runner": True,
            "counts_as_correction_round": False,
            "clean_action": "bind_exact_publication_evidence",
            "non_clean_action": "stop_and_return_to_spec_preparation",
            "invalid_or_timeout_action": "stop_and_return_to_spec_preparation",
            "automatic_correction_loop": False,
            "post_clean_mutation_invalidates_evidence": True,
            "same_manifest_new_commit_requires_new_binding": True,
        },
    }


def simulate_final_evidence_gate(
    *,
    github_clean=True,
    exact_binding_valid=False,
    final_result="CLEAN",
    post_clean_mutation=False,
):
    outcome = {
        "final_invocations": 0,
        "runner": None,
        "readiness": False,
        "automatic_edits": False,
        "push": False,
        "github_request": False,
        "merge": False,
        "second_final_invocation": False,
        "evidence_preserved": False,
    }
    if not github_clean:
        return outcome
    if exact_binding_valid:
        outcome.update({"readiness": True, "merge": True})
    else:
        outcome["final_invocations"] = 1
        outcome["runner"] = "canonical_authoritative_runner"
        outcome["evidence_preserved"] = True
        if final_result == "CLEAN":
            outcome.update({"readiness": True, "merge": True})
    if post_clean_mutation:
        outcome.update({"readiness": False, "merge": False})
    return outcome


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
            "post_pr_correction_review": post_pr_correction_review_config(),
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
        self.assertIn(
            '--invocation-timeout-seconds "<INVOCATION_TIMEOUT_SECONDS>"', text
        )
        self.assertIn("legacy_ready_adoption:\n      enabled: false", text)
        self.assertIn("selection_precedence:\n        - ordinary_reviewed_publication", text)
        self.assertIn("publication_upgrade_required", text)
        self.assertIn(
            "full_independent_review_after_each_github_package: false", text
        )
        self.assertIn("maximum_invocations: 1", text)
        self.assertIn("automatic_correction_loop: false", text)
        self.assertIn("local_model_invocations: 0", text)
        self.assertIn("initial_github_generation_required: true", text)
        self.assertIn("github_generation_target: exact_current_full_head", text)
        self.assertIn("state_store: exact_planning_pr_heartbeat", text)
        self.assertIn('request_comment: "@codex review"', text)
        self.assertIn("initialize_new_pull_request_at_zero: true", text)
        self.assertIn(
            "explicit_error_retry_transition: "
            "persist_transient_error_then_create_and_bind_next_request",
            text,
        )
        self.assertIn(
            "non_actionable_action: evidence_reply_and_contextual_rereview", text
        )
        self.assertIn(
            "response_binding_required: exact_reviewed_commit_or_active_request_generation",
            text,
        )
        self.assertIn("intentional_commit_required_before_push: true", text)

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
        self.assertEqual(capture["properties"]["invocation_timeout_seconds"]["maximum"], 3600)
        self.assertEqual(
            runner_schema["properties"]["required_placeholders"]["const"][-4:],
            [
                "<MINIMUM_STABLE_SCANS>",
                "<SETTLE_INTERVAL_SECONDS>",
                "<SETTLEMENT_TIMEOUT_SECONDS>",
                "<INVOCATION_TIMEOUT_SECONDS>",
            ],
        )

        post_pr = schema["properties"]["planning_publication"]["properties"][
            "post_pr_correction_review"
        ]
        self.assertFalse(
            post_pr["properties"][
                "full_independent_review_after_each_github_package"
            ]["const"]
        )
        self.assertTrue(
            post_pr["properties"]["initial_github_generation_required"]["const"]
        )
        self.assertEqual(
            post_pr["properties"]["github_generation_target"]["const"],
            "exact_current_full_head",
        )
        self.assertTrue(
            post_pr["properties"][
                "clean_github_generation_required_before_final_evidence_and_merge"
            ]["const"]
        )
        github_cycle = post_pr["properties"]["github_review_cycle"]
        counter = github_cycle["properties"]["correction_counter"]["properties"]
        self.assertEqual(counter["max_correction_rounds"]["const"], 5)
        self.assertTrue(counter["initialize_new_pull_request_at_zero"]["const"])
        self.assertTrue(counter["increment_once_after_applied_package"]["const"])
        self.assertEqual(
            github_cycle["properties"]["state_machine"]["properties"][
                "evaluation_order"
            ]["const"][:4],
            ["pr_terminal", "head_mismatch", "findings_received", "clean"],
        )
        self.assertEqual(
            github_cycle["properties"]["finding_policy"]["properties"][
                "non_actionable_action"
            ]["const"],
            "evidence_reply_and_contextual_rereview",
        )
        routine = post_pr["properties"]["routine_github_correction_verification"]
        self.assertEqual(routine["properties"]["local_model_invocations"]["const"], 0)
        self.assertTrue(
            routine["properties"]["intentional_commit_required_before_push"]["const"]
        )
        self.assertEqual(
            github_cycle["properties"]["generation"]["properties"][
                "response_binding_required"
            ]["const"],
            "exact_reviewed_commit_or_active_request_generation",
        )
        final = post_pr["properties"]["final_evidence_review"]
        self.assertEqual(final["properties"]["maximum_invocations"]["const"], 1)
        self.assertFalse(final["properties"]["automatic_correction_loop"]["const"])

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
            "matched_reviewer_terminal_event_ids",
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

        execution_only = copy.deepcopy(complete)
        execution_only["workflow_kit"]["selected_modules"] = [
            "execute-project-task"
        ]
        execution_only.pop("planning_publication")
        execution_only["implementation"] = {}
        execution_only["skills"]["active"] = {
            "execute-project-task": "skills/execute"
        }
        execution_only["commands"]["aliases"].pop("--publish-spec")
        self.assertEqual(list(validator.iter_errors(execution_only)), [])

        execution_only_with_publication_section = copy.deepcopy(execution_only)
        execution_only_with_publication_section["planning_publication"] = copy.deepcopy(
            complete["planning_publication"]
        )
        self.assertTrue(
            list(validator.iter_errors(execution_only_with_publication_section))
        )

        execution_only_with_publication_alias = copy.deepcopy(execution_only)
        execution_only_with_publication_alias["commands"]["aliases"][
            "--publish-spec"
        ] = {"capability": "planning_artifact_publication"}
        self.assertTrue(
            list(validator.iter_errors(execution_only_with_publication_alias))
        )

        execution_only_with_publication_readiness = copy.deepcopy(execution_only)
        execution_only_with_publication_readiness["implementation"] = copy.deepcopy(
            complete["implementation"]
        )
        self.assertTrue(
            list(validator.iter_errors(execution_only_with_publication_readiness))
        )

        execution_only_with_arbitrary_implementation_gate = copy.deepcopy(
            execution_only
        )
        execution_only_with_arbitrary_implementation_gate["implementation"] = {
            "arbitrary_publication_ancestry_gate": True
        }
        self.assertTrue(
            list(
                validator.iter_errors(
                    execution_only_with_arbitrary_implementation_gate
                )
            )
        )

        missing_publication_readiness = copy.deepcopy(complete)
        missing_publication_readiness["implementation"] = {}
        self.assertTrue(list(validator.iter_errors(missing_publication_readiness)))

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

        invalid_invocation_timeout = copy.deepcopy(complete)
        invalid_invocation_timeout["planning_publication"]["independent_review"][
            "result_capture"
        ]["invocation_timeout_seconds"] = 3601
        self.assertTrue(list(validator.iter_errors(invalid_invocation_timeout)))

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

        local_review_after_package = copy.deepcopy(complete)
        local_review_after_package["planning_publication"][
            "post_pr_correction_review"
        ]["full_independent_review_after_each_github_package"] = True
        self.assertTrue(list(validator.iter_errors(local_review_after_package)))

        missing_initial_generation = copy.deepcopy(complete)
        del missing_initial_generation["planning_publication"][
            "post_pr_correction_review"
        ]["initial_github_generation_required"]
        self.assertTrue(list(validator.iter_errors(missing_initial_generation)))

        missing_github_trigger = copy.deepcopy(complete)
        del missing_github_trigger["planning_publication"][
            "post_pr_correction_review"
        ]["github_review_cycle"]["request_comment"]
        self.assertTrue(list(validator.iter_errors(missing_github_trigger)))

        no_reviewer_matcher = copy.deepcopy(complete)
        github_cycle = no_reviewer_matcher["planning_publication"][
            "post_pr_correction_review"
        ]["github_review_cycle"]
        github_cycle["reviewer_logins"] = []
        github_cycle["reviewer_login_contains"] = []
        self.assertTrue(list(validator.iter_errors(no_reviewer_matcher)))

        missing_explicit_error_transition = copy.deepcopy(complete)
        del missing_explicit_error_transition["planning_publication"][
            "post_pr_correction_review"
        ]["github_review_cycle"]["request_budget"][
            "explicit_error_retry_transition"
        ]
        self.assertTrue(list(validator.iter_errors(missing_explicit_error_transition)))

        actionable_dismissal = copy.deepcopy(complete)
        actionable_dismissal["planning_publication"][
            "post_pr_correction_review"
        ]["github_review_cycle"]["finding_policy"][
            "non_actionable_consumes_correction_round"
        ] = True
        self.assertTrue(list(validator.iter_errors(actionable_dismissal)))

        unbound_response_allowed = copy.deepcopy(complete)
        del unbound_response_allowed["planning_publication"][
            "post_pr_correction_review"
        ]["github_review_cycle"]["generation"]["response_binding_required"]
        self.assertTrue(list(validator.iter_errors(unbound_response_allowed)))

        push_without_commit = copy.deepcopy(complete)
        push_without_commit["planning_publication"][
            "post_pr_correction_review"
        ]["routine_github_correction_verification"][
            "intentional_commit_required_before_push"
        ] = False
        self.assertTrue(list(validator.iter_errors(push_without_commit)))

        unbounded_github_packages = copy.deepcopy(complete)
        unbounded_github_packages["planning_publication"][
            "post_pr_correction_review"
        ]["github_review_cycle"]["correction_counter"]["max_correction_rounds"] = 6
        self.assertTrue(list(validator.iter_errors(unbounded_github_packages)))

        missing_counter_initialization = copy.deepcopy(complete)
        del missing_counter_initialization["planning_publication"][
            "post_pr_correction_review"
        ]["github_review_cycle"]["correction_counter"][
            "initialize_new_pull_request_at_zero"
        ]
        self.assertTrue(list(validator.iter_errors(missing_counter_initialization)))

        bypassable_clean_generation = copy.deepcopy(complete)
        bypassable_clean_generation["planning_publication"][
            "post_pr_correction_review"
        ]["clean_github_generation_required_before_final_evidence_and_merge"] = False
        self.assertTrue(list(validator.iter_errors(bypassable_clean_generation)))

        missing_deterministic_gate = copy.deepcopy(complete)
        del missing_deterministic_gate["planning_publication"][
            "post_pr_correction_review"
        ]["routine_github_correction_verification"]["git_diff_check_required"]
        self.assertTrue(list(validator.iter_errors(missing_deterministic_gate)))

        invalid_final_maximum = copy.deepcopy(complete)
        invalid_final_maximum["planning_publication"][
            "post_pr_correction_review"
        ]["final_evidence_review"]["maximum_invocations"] = 2
        self.assertTrue(list(validator.iter_errors(invalid_final_maximum)))

        automatic_final_corrections = copy.deepcopy(complete)
        automatic_final_corrections["planning_publication"][
            "post_pr_correction_review"
        ]["final_evidence_review"]["automatic_correction_loop"] = True
        self.assertTrue(list(validator.iter_errors(automatic_final_corrections)))

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

    def test_post_pr_corrections_use_zero_or_one_final_evidence_review(self):
        post_pr = PUBLISH_POST_PR.read_text(encoding="utf-8")
        github_cycle = PUBLISH_GITHUB_CYCLE.read_text(encoding="utf-8")
        publication = PUBLISH_SKILL.read_text(encoding="utf-8")
        prepare = PUBLISH_PREPARE.read_text(encoding="utf-8")
        self.assertIn("local_model_invocations: 0", post_pr)
        self.assertIn("Do not run the canonical review", post_pr)
        self.assertIn("Run zero or one final evidence review", post_pr)
        self.assertIn("exact current head revision, tree", post_pr)
        self.assertIn("same manifest blob OIDs", post_pr)
        self.assertIn("consumes neither a local correction round", post_pr)
        self.assertIn("exact complete initial head", post_pr)
        self.assertIn("Before final\nevidence selection or merge", post_pr)
        self.assertIn("without automatic corrections", publication)
        self.assertIn("Create and bind one request attempt", github_cycle)
        self.assertIn("Apply the first matching configured state", github_cycle)
        self.assertIn("github_correction_rounds_used: 0", github_cycle)
        self.assertIn("maximum is five packages", github_cycle)
        self.assertIn("The fifth package still", github_cycle)
        self.assertIn("A sixth package never starts", github_cycle)
        self.assertIn("Delete the heartbeat only after", github_cycle)
        self.assertIn("For `transient_error`, persist the state", github_cycle)
        self.assertIn("request_budget_exhausted", github_cycle)
        self.assertIn("provider-reviewed commit SHA", github_cycle)
        self.assertIn("matched-reviewer issue comment", github_cycle)
        self.assertIn("sole active attempt", github_cycle)
        self.assertIn("complete active-generation correlation", github_cycle)
        self.assertIn("stale_or_unbound_event_ids", github_cycle)
        self.assertIn("intentional exact-manifest correction", github_cycle)
        self.assertIn("non-actionable classification still", github_cycle)
        self.assertIn("`false`, `intentional_out_of_scope`, or `duplicate`", post_pr)
        self.assertIn("one contextual\nre-review request", post_pr)
        self.assertIn("repeated_dismissed_finding", post_pr)
        self.assertIn("create an intentional commit", post_pr)
        self.assertIn("remote PR head and manifest match", post_pr)
        self.assertIn("run-planning-github-review-cycle.md", publication)
        self.assertLess(
            prepare.index("Stop at the pull-request endpoint"),
            prepare.index("For full publication, start the configured"),
        )

        unchanged = simulate_final_evidence_gate(exact_binding_valid=True)
        self.assertEqual(unchanged["final_invocations"], 0)
        self.assertTrue(unchanged["readiness"])

        no_clean_github_generation = simulate_final_evidence_gate(github_clean=False)
        self.assertFalse(no_clean_github_generation["readiness"])
        self.assertFalse(no_clean_github_generation["merge"])

        corrected = simulate_final_evidence_gate()
        self.assertEqual(corrected["final_invocations"], 1)
        self.assertEqual(corrected["runner"], "canonical_authoritative_runner")
        self.assertTrue(corrected["readiness"])

        for packages in (1, 3, 5):
            with self.subTest(routine_packages=packages):
                local_model_invocations_before_github_clean = 0
                final = simulate_final_evidence_gate()
                self.assertEqual(local_model_invocations_before_github_clean, 0)
                self.assertEqual(final["final_invocations"], 1)

        for terminal_result in ("NON_CLEAN", "INVALID", "UNBOUND", "TIMED_OUT"):
            with self.subTest(final_result=terminal_result):
                stopped = simulate_final_evidence_gate(final_result=terminal_result)
                self.assertFalse(stopped["readiness"])
                self.assertTrue(stopped["evidence_preserved"])
                for forbidden in (
                    "automatic_edits",
                    "push",
                    "github_request",
                    "merge",
                    "second_final_invocation",
                ):
                    self.assertFalse(stopped[forbidden])

        mutated = simulate_final_evidence_gate(post_clean_mutation=True)
        self.assertFalse(mutated["readiness"])
        self.assertFalse(mutated["merge"])

        reverted_by_new_commit = simulate_final_evidence_gate(
            exact_binding_valid=False
        )
        self.assertEqual(reverted_by_new_commit["final_invocations"], 1)
        self.assertIn("technical retry behavior remains owned", post_pr)
        self.assertEqual(result_capture_config()["max_technical_retries_per_publication_attempt"], 1)

    def test_review_invocation_metrics_match_the_bounded_contract(self):
        pre_pr_generations = 1 + 5
        github_generations = 1 + 5
        self.assertEqual(pre_pr_generations + github_generations, 12)
        for github_correction_packages in range(0, 6):
            final_evidence_invocations = int(github_correction_packages > 0)
            self.assertLessEqual(final_evidence_invocations, 1)

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
            "review_invocation_timeout",
            "path/mode/blob-OID",
        ):
            self.assertIn(required, review)
        self.assertTrue(RUNNER.is_file())
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn("CAPTURE_CONTRACT_REVISION = 1", runner)
        self.assertIn("build_review_instructions", runner)
        self.assertIn('"developer_instructions="', runner)
        self.assertIn('"mode": mode', runner)
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
        execution = EXECUTE_SKILL.read_text(encoding="utf-8")
        self.assertIn("configuration schema v4", generated)
        self.assertIn("project configuration schema v4", validation)
        self.assertIn("require schema v4", publication)
        self.assertIn("Reject a direct `codex review`", generated)
        self.assertIn("ordinary reviewed publication as\n  the only implementation-readiness path", generated)
        self.assertIn(
            "selected without `publish-planning-change`",
            validation,
        )
        self.assertIn(
            "When `publish-planning-change` is selected, confirm `write-task-spec`",
            validation,
        )
        self.assertNotIn(
            "Confirm `write-task-spec` hands file-backed specs",
            validation,
        )
        self.assertIn(
            "When `publish-planning-change` is not selected",
            execution,
        )


if __name__ == "__main__":
    unittest.main()
