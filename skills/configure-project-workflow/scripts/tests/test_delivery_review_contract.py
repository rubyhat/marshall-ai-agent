import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # The dependency-free repository validator may run without it.
    Draft202012Validator = None


SKILL_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
SCHEMA = SKILL_ROOT / "assets" / "project-workflow.schema.json"
GENERATE = SKILL_ROOT / "references" / "generate-project-setup.md"
VALIDATE = SKILL_ROOT / "references" / "validate-project-setup.md"
DELIVERY_ROOT = SKILL_ROOT.parent / "deliver-reviewed-change"
DELIVERY_SKILL = DELIVERY_ROOT / "SKILL.md"
BOUND_CYCLES = DELIVERY_ROOT / "references" / "bound-review-correction-cycles.md"
LOCAL_REVIEW = DELIVERY_ROOT / "references" / "run-independent-local-review.md"
START_CYCLE = DELIVERY_ROOT / "references" / "start-codex-review-cycle.md"
FINDINGS = DELIVERY_ROOT / "references" / "classify-and-handle-review-findings.md"
ROUTINE_CORRECTION = (
    DELIVERY_ROOT / "references" / "verify-routine-github-correction.md"
)
RECOVERY = DELIVERY_ROOT / "references" / "recover-stalled-or-failed-review.md"
FINALIZATION = DELIVERY_ROOT / "references" / "finalize-codex-review-state.md"
PLANNING_TEST = Path(__file__).with_name("test_planning_publication_contract.py")

REQUIRED_GITHUB_REVIEW_STATES = (
    "request_not_created",
    "request_pending",
    "not_started",
    "in_progress",
    "findings_received",
    "scope_disagreement",
    "transient_error",
    "clean",
    "stopped",
    "terminal",
    "pr_terminal",
    "head_mismatch",
    "unclassified_response",
)


def resolve_public_aliases(repository_root=REPOSITORY_ROOT):
    candidates = (
        repository_root / "docs" / "workflow-aliases.md",
        repository_root / "workflows" / "agent_commands.md",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"Public alias contract not found; searched: {searched}")


ALIASES = resolve_public_aliases()


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
            "refresh_local_state_before_each_github_generation": True,
            "github_correction_budget_scope": "pull_request",
            "github_counter_owner": "exact_pr_state",
            "github_state_store": "exact_pr_heartbeat",
            "open_pull_request_terminal_state_pauses_heartbeat": True,
            "same_pull_request_resume_reactivates_heartbeat": True,
            "owned_head_changing_push_requires_paused_heartbeat": True,
            "heartbeat_deletion_requires_pull_request_terminal": True,
            "terminal_head_records_observed_pr_head": True,
            "terminal_finalization_procedure": "finalize_codex_review_state",
            "terminal_state_matrix_required": True,
            "terminal_rules_must_not_be_duplicated": True,
            "new_pull_request_starts_github_counter_at_zero": True,
            "different_pull_requests_do_not_share_counters_or_histories": True,
            "different_pull_requests_do_not_share_terminal_state": True,
            "github_dismissed_finding_fingerprints_scope": "pull_request",
            "github_heartbeat_state_scope": "pull_request",
            "github_heartbeat_exists_before_review_request": True,
            "same_terminal_head_forbids_new_request": True,
            "different_conversation_requires_proven_state": True,
            "resume_requires_provable_counters_and_history": True,
            "lost_history_stops_delivery": True,
            "bounded_cycle_analysis_required": True,
            "pre_pr_local_phase_closes_on_pull_request": True,
            "pre_pr_local_gate_evidence_required_before_github_phase": True,
            "pre_pr_local_gate_missing_action": "pre_pr_local_gate_missing",
            "accepted_blocker_or_owner_override_cannot_bypass_pre_pr_local_gate": True,
            "full_local_model_review_after_routine_github_correction": False,
            "routine_github_correction_verification": {
                "affected_tests_required": True,
                "configured_deterministic_gates_required": True,
                "git_diff_check_required": True,
                "exact_correction_delta_required": True,
                "finding_by_finding_readback_required": True,
                "next_github_generation_reviews_full_head": True,
                "local_model_invocations": 0,
                "follow_on_gate_fix_rechecks_materiality_before_mutation": True,
            },
            "material_github_correction": {
                "action": "stop_before_edits_and_return_to_owner",
                "uncertain_uses_same_stop": True,
                "terminal_reason": "scope_or_contract_stop",
                "stop_before_counter_increment_commit_push_or_request": True,
            },
        },
        "local": {
            "max_correction_rounds": 5,
            "fresh_review_after_each_correction_package": True,
        },
        "github_codex": {
            "max_correction_rounds": 5,
            "fresh_generation_after_each_correction_package": True,
            "new_head_resets_request_budget_only": True,
            "generation": {
                "bound_to_head_sha": True,
                "old_events_cannot_complete_new_head": True,
                "response_binding_required": (
                    "exact_reviewed_commit_or_active_request_generation"
                ),
                "issue_comment_binding_requires_unsuperseded_request": True,
                "issue_comment_binding_requires_current_head_match": True,
                "stale_or_unbound_event_action": (
                    "record_and_ignore_until_binding_proven"
                ),
            },
            "heartbeat": {
                "delete_on_review_terminal_state": False,
                "delete_after_pr_terminal": True,
            },
            "state_machine": {"states": list(REQUIRED_GITHUB_REVIEW_STATES)},
            "post_clean": {"delete_review_heartbeat_immediately": False},
        },
    }


def v0_8_2_review_contract():
    contract = complete_review_contract()
    del contract["github_codex"]["generation"]
    policy = contract["correction_policy"]
    for key in (
        "pre_pr_local_phase_closes_on_pull_request",
        "pre_pr_local_gate_evidence_required_before_github_phase",
        "pre_pr_local_gate_missing_action",
        "accepted_blocker_or_owner_override_cannot_bypass_pre_pr_local_gate",
        "full_local_model_review_after_routine_github_correction",
        "routine_github_correction_verification",
        "material_github_correction",
    ):
        del policy[key]
    return contract


def simulate_github_correction(
    *,
    findings=("finding-a",),
    pre_pr_gate_bound=True,
    owner_override=False,
    classification="routine",
    github_rounds_used=0,
    local_rounds_used=0,
    gates_pass=True,
    exact_scope=True,
):
    outcome = {
        "findings": list(findings),
        "github_rounds_used": github_rounds_used,
        "local_rounds_used": local_rounds_used,
        "local_model_invocations": 0,
        "edits": False,
        "counter_incremented": False,
        "commit": False,
        "push": False,
        "github_request": False,
        "full_head_review": False,
        "finding_readback": [],
        "owner_handoff": None,
        "terminal_reason": None,
    }
    if not pre_pr_gate_bound:
        outcome["terminal_reason"] = "pre_pr_local_gate_missing"
        outcome["owner_override_ignored"] = owner_override
        return outcome
    if classification in {"material", "uncertain"}:
        outcome["terminal_reason"] = "scope_or_contract_stop"
        outcome["owner_handoff"] = "return_to_owning_workflow"
        return outcome
    if github_rounds_used >= 5:
        outcome["terminal_reason"] = "github_correction_budget_exhausted"
        return outcome

    outcome["edits"] = True
    outcome["counter_incremented"] = True
    outcome["github_rounds_used"] += 1
    if not gates_pass or not exact_scope:
        outcome["terminal_reason"] = "deterministic_correction_gate_failed"
        return outcome

    outcome.update(
        {
            "commit": True,
            "push": True,
            "github_request": True,
            "full_head_review": True,
            "finding_readback": list(findings),
        }
    )
    return outcome


def complete_delivery_config():
    config = load_planning_fixture()
    config["workflow_kit"]["selected_modules"].append("deliver-reviewed-change")
    config["review"] = complete_review_contract()
    config["skills"]["active"]["deliver-reviewed-change"] = "skills/deliver"
    config["commands"]["aliases"]["--deliver-task"] = {}
    return config


class DeliveryReviewContractTest(unittest.TestCase):
    def test_public_alias_resolver_accepts_vendored_project_layout(self):
        with tempfile.TemporaryDirectory() as directory:
            repository_root = Path(directory)
            expected = repository_root / "workflows" / "agent_commands.md"
            expected.parent.mkdir(parents=True)
            expected.write_text("vendored alias contract", encoding="utf-8")

            self.assertEqual(resolve_public_aliases(repository_root), expected)

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
                self.assertEqual(limit["const"], 5)
                self.assertEqual(limit["default"], 5)

        github = review["properties"]["github_codex"]
        for required in ("generation", "heartbeat", "state_machine", "post_clean"):
            self.assertIn(required, github["required"])
        generation = github["properties"]["generation"]["properties"]
        self.assertEqual(
            generation["response_binding_required"]["const"],
            "exact_reviewed_commit_or_active_request_generation",
        )
        self.assertTrue(
            generation["issue_comment_binding_requires_unsuperseded_request"][
                "const"
            ]
        )
        self.assertFalse(
            github["properties"]["heartbeat"]["properties"]
            ["delete_on_review_terminal_state"]["const"]
        )
        self.assertTrue(
            github["properties"]["heartbeat"]["properties"]
            ["delete_after_pr_terminal"]["const"]
        )
        self.assertFalse(
            github["properties"]["post_clean"]["properties"]
            ["delete_review_heartbeat_immediately"]["const"]
        )
        required_states = {
            item["contains"]["const"]
            for item in github["properties"]["state_machine"]["properties"]
            ["states"]["allOf"]
        }
        self.assertEqual(required_states, set(REQUIRED_GITHUB_REVIEW_STATES))

        policy = review["properties"]["correction_policy"]
        self.assertEqual(
            policy["properties"]["round_unit"]["const"],
            "review_driven_correction_package",
        )
        self.assertEqual(
            policy["properties"]["github_correction_budget_scope"]["const"],
            "pull_request",
        )
        self.assertEqual(
            policy["properties"]["github_counter_owner"]["const"],
            "exact_pr_state",
        )
        self.assertEqual(
            policy["properties"]["github_state_store"]["const"],
            "exact_pr_heartbeat",
        )
        self.assertEqual(
            policy["properties"]["terminal_finalization_procedure"]["const"],
            "finalize_codex_review_state",
        )
        self.assertEqual(
            policy["properties"]["github_dismissed_finding_fingerprints_scope"][
                "const"
            ],
            "pull_request",
        )
        self.assertEqual(
            policy["properties"]["github_heartbeat_state_scope"]["const"],
            "pull_request",
        )
        self.assertTrue(
            policy["properties"]["pre_pr_local_phase_closes_on_pull_request"][
                "const"
            ]
        )
        self.assertFalse(
            policy["properties"][
                "full_local_model_review_after_routine_github_correction"
            ]["const"]
        )
        routine = policy["properties"]["routine_github_correction_verification"]
        self.assertEqual(routine["properties"]["local_model_invocations"]["const"], 0)
        for key in routine["required"]:
            if key != "local_model_invocations":
                self.assertTrue(routine["properties"][key]["const"])
        material = policy["properties"]["material_github_correction"]
        self.assertEqual(
            material["properties"]["action"]["const"],
            "stop_before_edits_and_return_to_owner",
        )

        delivery_condition = next(
            item
            for item in schema["allOf"]
            if item.get("if", {})
            .get("properties", {})
            .get("workflow_kit", {})
            .get("properties", {})
            .get("selected_modules", {})
            .get("contains", {})
            .get("const")
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
            ("review", "github_codex", "generation"),
            ("review", "github_codex", "heartbeat"),
            ("review", "github_codex", "state_machine"),
            ("review", "github_codex", "post_clean"),
            (
                "review",
                "correction_policy",
                "routine_github_correction_verification",
            ),
            ("review", "correction_policy", "material_github_correction"),
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

        for invalid_value in (4, 6):
            with self.subTest(invalid_value=invalid_value):
                invalid_limit = copy.deepcopy(complete)
                invalid_limit["review"]["github_codex"][
                    "max_correction_rounds"
                ] = invalid_value
                self.assertTrue(list(validator.iter_errors(invalid_limit)))

        invalid_heartbeat = copy.deepcopy(complete)
        invalid_heartbeat["review"]["github_codex"]["heartbeat"][
            "delete_on_review_terminal_state"
        ] = True
        self.assertTrue(list(validator.iter_errors(invalid_heartbeat)))

        invalid_pr_terminal_deletion = copy.deepcopy(complete)
        invalid_pr_terminal_deletion["review"]["github_codex"]["heartbeat"][
            "delete_after_pr_terminal"
        ] = False
        self.assertTrue(list(validator.iter_errors(invalid_pr_terminal_deletion)))

        invalid_post_clean = copy.deepcopy(complete)
        invalid_post_clean["review"]["github_codex"]["post_clean"][
            "delete_review_heartbeat_immediately"
        ] = True
        self.assertTrue(list(validator.iter_errors(invalid_post_clean)))

        unbound_delivery_responses = copy.deepcopy(complete)
        del unbound_delivery_responses["review"]["github_codex"]["generation"][
            "response_binding_required"
        ]
        self.assertTrue(list(validator.iter_errors(unbound_delivery_responses)))

        invalid_local_rereview = copy.deepcopy(complete)
        invalid_local_rereview["review"]["correction_policy"][
            "full_local_model_review_after_routine_github_correction"
        ] = True
        self.assertTrue(list(validator.iter_errors(invalid_local_rereview)))

        missing_deterministic_gate = copy.deepcopy(complete)
        del missing_deterministic_gate["review"]["correction_policy"][
            "routine_github_correction_verification"
        ]["git_diff_check_required"]
        self.assertTrue(list(validator.iter_errors(missing_deterministic_gate)))

        bypassable_pre_pr_gate = copy.deepcopy(complete)
        bypassable_pre_pr_gate["review"]["correction_policy"][
            "accepted_blocker_or_owner_override_cannot_bypass_pre_pr_local_gate"
        ] = False
        self.assertTrue(list(validator.iter_errors(bypassable_pre_pr_gate)))

        for missing_state in REQUIRED_GITHUB_REVIEW_STATES:
            with self.subTest(missing_state=missing_state):
                invalid_states = copy.deepcopy(complete)
                invalid_states["review"]["github_codex"]["state_machine"][
                    "states"
                ].remove(missing_state)
                self.assertTrue(list(validator.iter_errors(invalid_states)))

    def test_delivery_skill_fails_closed_before_a_sixth_package(self):
        skill = DELIVERY_SKILL.read_text(encoding="utf-8")
        cycles = BOUND_CYCLES.read_text(encoding="utf-8")
        local = LOCAL_REVIEW.read_text(encoding="utf-8")
        findings = FINDINGS.read_text(encoding="utf-8")
        routine = ROUTINE_CORRECTION.read_text(encoding="utf-8")

        self.assertIn("bound-review-correction-cycles.md", skill)
        self.assertIn("## Contents", cycles)
        self.assertIn("local_correction_rounds_used", cycles)
        self.assertIn("github_correction_rounds_used", cycles)
        self.assertIn("Multiple findings corrected together consume one round", cycles)
        self.assertIn("resets only the configured technical\nrequest-attempt", cycles)
        self.assertIn("final allowed local round still receives", cycles)
        self.assertIn("final allowed GitHub round still receives", cycles)
        self.assertIn("stop before editing", cycles)
        self.assertIn("bounded\ncycle analysis", cycles)
        self.assertIn("machine-readable delivery-state\nblock", cycles)
        self.assertIn("retained state of the current Codex task", cycles)
        self.assertIn("immutable delivery baseline", local)
        self.assertIn("final allowed round still\nreceives review", local)
        self.assertIn("unchanged GitHub correction counter", findings)
        self.assertIn("pre_pr_local_gate_missing", routine)
        self.assertIn("local_model_invocations: 0", routine)
        self.assertIn("finding-by-finding readback", routine)
        self.assertIn("Do not use a targeted or full local model review", routine)

    def test_routine_github_package_uses_deterministic_gates_only(self):
        single = simulate_github_correction()
        self.assertEqual(single["github_rounds_used"], 1)
        self.assertEqual(single["local_model_invocations"], 0)
        self.assertTrue(single["full_head_review"])

        multiple = simulate_github_correction(
            findings=("finding-a", "finding-b")
        )
        self.assertEqual(multiple["github_rounds_used"], 1)
        self.assertEqual(multiple["finding_readback"], ["finding-a", "finding-b"])

        failed_test = simulate_github_correction(gates_pass=False)
        self.assertEqual(failed_test["github_rounds_used"], 1)
        self.assertFalse(failed_test["commit"])
        self.assertFalse(failed_test["push"])
        self.assertFalse(failed_test["github_request"])

        unexplained_path = simulate_github_correction(exact_scope=False)
        self.assertFalse(unexplained_path["push"])

        exhausted_local = simulate_github_correction(local_rounds_used=5)
        self.assertEqual(exhausted_local["local_rounds_used"], 5)
        self.assertTrue(exhausted_local["github_request"])

        final_round = simulate_github_correction(github_rounds_used=4)
        self.assertEqual(final_round["github_rounds_used"], 5)
        self.assertTrue(final_round["full_head_review"])
        exhausted_github = simulate_github_correction(github_rounds_used=5)
        self.assertEqual(
            exhausted_github["terminal_reason"],
            "github_correction_budget_exhausted",
        )

        missing_gate = simulate_github_correction(pre_pr_gate_bound=False)
        overridden_missing_gate = simulate_github_correction(
            pre_pr_gate_bound=False, owner_override=True
        )
        for outcome in (missing_gate, overridden_missing_gate):
            self.assertEqual(outcome["terminal_reason"], "pre_pr_local_gate_missing")
            self.assertFalse(outcome["edits"])
            self.assertFalse(outcome["github_request"])

        follow_on_uncertain = simulate_github_correction(classification="uncertain")
        self.assertEqual(
            follow_on_uncertain["terminal_reason"], "scope_or_contract_stop"
        )
        self.assertFalse(follow_on_uncertain["counter_incremented"])

    def test_material_correction_categories_stop_before_every_mutation(self):
        routine = ROUTINE_CORRECTION.read_text(encoding="utf-8")
        normalized_routine = " ".join(routine.split())
        material_categories = (
            "outcome, scope, acceptance criteria",
            "architecture",
            "permissions",
            "security or tenant boundary",
            "data contract",
            "migration or backfill",
            "repository ownership",
            "dependency direction",
            "unexplained cumulative diff growth",
        )
        for category in material_categories:
            with self.subTest(category=category):
                self.assertIn(category, normalized_routine)
                outcome = simulate_github_correction(classification="material")
                self.assertEqual(outcome["terminal_reason"], "scope_or_contract_stop")
                self.assertEqual(outcome["owner_handoff"], "return_to_owning_workflow")
                self.assertEqual(outcome["local_model_invocations"], 0)
                for mutation in (
                    "edits",
                    "counter_incremented",
                    "commit",
                    "push",
                    "github_request",
                ):
                    self.assertFalse(outcome[mutation])

    def test_clean_head_needs_no_final_local_review_and_model_budget_is_bounded(self):
        skill = DELIVERY_SKILL.read_text(encoding="utf-8")
        routine = ROUTINE_CORRECTION.read_text(encoding="utf-8")
        self.assertIn("only active full local-review phase", skill)
        self.assertIn("only this PR's GitHub counter is active", skill)
        self.assertIn("local\n  counter is audit history", skill)
        self.assertIn("active-generation candidate, never a verdict", skill)
        self.assertIn("do not reopen", routine)
        self.assertEqual(1 + 5 + 1 + 5, 12)

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
        readiness = (
            DELIVERY_ROOT / "references" / "verify-delivery-readiness.md"
        ).read_text(encoding="utf-8")
        cycles = BOUND_CYCLES.read_text(encoding="utf-8")

        self.assertIn("## Contents", start)
        for key in (
            "github_counter_scope: pull_request",
            "delivery_baseline:",
            "issue:",
            "specification_or_equivalent_contract:",
            "acceptance_criteria:",
            "non_goals:",
            "pre_review_destination_revisions_or_not_applicable:",
            "initial_diff_manifest:",
            "initial_diff_stats:",
            "delivery_baseline_fingerprint",
            "local_correction_rounds_used",
            "local_correction_history",
            "github_correction_rounds_used",
            "github_correction_history",
            "request_author:",
            "request_url:",
            "terminal_head_sha:",
        ):
            self.assertIn(key, start)
        self.assertIn("new head of the same PR, preserve that PR's GitHub counter", start)
        self.assertIn("Before every initial or later GitHub generation", start)
        self.assertIn("authoritative local correction counter", start)
        self.assertIn("Never copy PR-owned GitHub state back", start)
        self.assertIn("equal to `terminal_head_sha` does not\nstart another review cycle", start)
        self.assertIn("reactivate that same heartbeat", start)
        self.assertIn("Before a workflow-owned push that will change", start)
        self.assertIn("Before posting a remote review trigger", start)
        self.assertIn("state is `request_not_created`", start)
        self.assertIn("per-repository pre-review destination-revision mapping", start)
        self.assertIn("For every initial, retry, or contextual request attempt", start)
        self.assertIn("must not consume or reset either correction counter", recovery)
        self.assertIn("Initialize only the local correction counter", readiness)
        self.assertIn("Initialize GitHub correction state only\nafter", readiness)
        self.assertIn("## Finalize paused per-PR state centrally", cycles)

        monitor = (
            DELIVERY_ROOT / "references" / "monitor-codex-review-state-machine.md"
        ).read_text(encoding="utf-8")
        commits = (
            DELIVERY_ROOT / "references" / "commit-push-and-open-pr.md"
        ).read_text(encoding="utf-8")
        findings = (
            DELIVERY_ROOT / "references" / "classify-and-handle-review-findings.md"
        ).read_text(encoding="utf-8")
        self.assertIn("only this exact PR heartbeat", monitor)
        self.assertIn("must never be copied to or derived from another PR", monitor)
        self.assertIn("`head_mismatch`", monitor)
        self.assertIn("give every PR its own GitHub correction counter", commits)
        self.assertIn("`scope_or_contract_stop`", findings)
        self.assertIn("active_request_generation_candidate", monitor)
        self.assertIn("stale_or_unbound_event_ids:", start)
        self.assertIn("response_binding_evidence:", start)
        self.assertIn("paused automation\n   status", findings)
        self.assertIn("paused automation status", monitor)
        for path in (
            DELIVERY_ROOT / "references" / "monitor-codex-review-state-machine.md",
            RECOVERY,
            FINDINGS,
        ):
            with self.subTest(request_transition=path.name):
                text = path.read_text(encoding="utf-8")
                normalized = " ".join(text.split())
                self.assertIn("Create one request attempt", normalized)
                self.assertIn("Attach and verify the request identity", normalized)
                self.assertIn("start-codex-review-cycle.md", text)

    def test_paused_heartbeat_distinguishes_generation_and_observed_head(self):
        start = START_CYCLE.read_text(encoding="utf-8")
        finalization = FINALIZATION.read_text(encoding="utf-8")

        self.assertIn("terminal reason and distinct\n`terminal_head_sha`", start)
        self.assertIn("Do not use the generation's `head_sha`", start)
        self.assertIn("equal to `terminal_head_sha`", start)
        self.assertIn("distinct `terminal_head_sha` observed", finalization)
        self.assertIn("For `head_mismatch`", finalization)
        self.assertIn("persist `terminal_head_sha` separately", finalization)
        self.assertIn("Do not create a\nterminal snapshot", finalization)

    def test_terminal_finalization_is_centralized_and_exhaustive(self):
        finalization = FINALIZATION.read_text(encoding="utf-8")
        lines = finalization.splitlines()
        contents_start = lines.index("## Contents") + 1
        contents_end = next(
            index
            for index in range(contents_start, len(lines))
            if lines[index].startswith("## ")
        )
        contents_lines = lines[contents_start:contents_end]
        for heading, link in (
            (
                "Apply the terminal matrix",
                "- [Apply the terminal matrix](#apply-the-terminal-matrix)",
            ),
            (
                "Prove state before mutation",
                "- [Prove state before mutation](#prove-state-before-mutation)",
            ),
            (
                "Pause an open pull request",
                "- [Pause an open pull request](#pause-an-open-pull-request)",
            ),
            (
                "Reactivate only the same pull request",
                "- [Reactivate only the same pull request](#reactivate-only-the-same-pull-request)",
            ),
            (
                "Delete only after pull-request closure",
                "- [Delete only after pull-request closure](#delete-only-after-pull-request-closure)",
            ),
        ):
            with self.subTest(toc_link=link):
                self.assertIn(f"## {heading}", lines)
                self.assertIn(link, contents_lines)
        documented_matrix = finalization.split("```json\n", 1)[1].split(
            "\n```", 1
        )[0]
        matrix = json.loads(documented_matrix)

        dispositions = {
            "pr_terminal": "delete_report",
            "clean": "pause_merge_ready",
            "github_correction_budget_exhausted": "pause_cycle_analysis",
            "pre_pr_local_gate_missing": "pause_report",
            "request_budget_exhausted": "pause_report",
            "acknowledged_wait_budget_exhausted": "pause_report",
            "repeated_dismissed_finding": "pause_report",
            "scope_or_contract_stop": "pause_owner_handoff",
            "unclassified_response": "pause_report",
            "head_mismatch": "pause_report",
        }
        pause_reasons = {
            "lost_or_contradictory_state",
            "pr_identity_ambiguous",
            "heartbeat_persistence_failure",
        }
        self.assertEqual(set(matrix), set(dispositions) | pause_reasons)
        for reason, disposition in dispositions.items():
            self.assertEqual(matrix[reason]["on_provable"], disposition)
            self.assertEqual(matrix[reason]["on_unprovable"], "pause_report")
        for reason in pause_reasons:
            self.assertEqual(
                matrix[reason],
                {"on_provable": "pause_report", "on_unprovable": "pause_report"},
            )

        delegates = (
            DELIVERY_SKILL,
            BOUND_CYCLES,
            START_CYCLE,
            FINDINGS,
            RECOVERY,
            DELIVERY_ROOT / "references" / "monitor-codex-review-state-machine.md",
            DELIVERY_ROOT / "references" / "merge-close-and-clean.md",
        )
        for path in delegates:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("finalize-codex-review-state.md", text)
                self.assertNotIn("terminal snapshot", text.lower())

        merge = (DELIVERY_ROOT / "references" / "merge-close-and-clean.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`pause_merge_ready`", merge)
        self.assertIn("with\n`pr_terminal`", merge)
        self.assertIn("No review-terminal outcome other\nthan proven merge or close", finalization)

    def test_setup_and_human_alias_document_the_contract(self):
        generated = GENERATE.read_text(encoding="utf-8")
        validation = VALIDATE.read_text(encoding="utf-8")
        aliases = ALIASES.read_text(encoding="utf-8")
        normalized_generated = " ".join(generated.split())

        self.assertIn("each materialized as `5`", generated)
        self.assertIn("separate positive `max_correction_rounds`", generated)
        self.assertIn("new PR head resetting only technical request attempts", generated)
        self.assertIn("machine-readable pre-PR state block", generated)
        self.assertIn("authoritative local correction state refreshed", generated)
        self.assertIn("single exact-PR heartbeat for active and paused", generated)
        self.assertIn(
            "delete it only after provider evidence proves", normalized_generated
        )
        self.assertIn(
            "workflow-owned push that changes the PR head", normalized_generated
        )
        self.assertIn("centralized `finalize_codex_review_state` procedure", generated)
        self.assertIn("terminal-reason matrix", generated)
        self.assertIn("observed at terminal transition as `terminal_head_sha`", generated)
        self.assertIn("provisional exact-PR heartbeat created and read back", generated)
        self.assertIn("unchanged terminal head from a paused heartbeat", generated)
        self.assertIn("every initial, retry, and contextual request", generated)
        self.assertIn("separate positive correction-round limits set to five", validation)
        self.assertIn("не более пяти correction packages каждый", aliases)
        self.assertIn("heartbeat остаётся paused без удаления", aliases)
        self.assertIn("Перед workflow-owned push", aliases)
        self.assertIn("Все terminal branches выбирают reason из единой матрицы", aliases)
        self.assertIn("отдельный `terminal_head_sha`", aliases)
        self.assertIn("сначала создаёт и перечитывает provisional", aliases)
        self.assertIn("повторно читает authoritative\nlocal counter/history", aliases)
        self.assertIn("technical retry и contextual re-review", aliases)
        self.assertIn("без нового review request", aliases)
        self.assertIn("Если ему нужна\nшестая правка", aliases)
        self.assertIn("Переход на workflow kit v0.8.2", aliases)
        self.assertIn("корневую секцию `review` с четырьмя полными группами", aliases)
        migration = aliases.split("### Переход на workflow kit v0.8.2", 1)[1]
        documented_contract = migration.split("```json\n", 1)[1].split("\n```", 1)[0]
        self.assertEqual(
            json.loads(documented_contract),
            {"review": v0_8_2_review_contract()},
        )
        self.assertIn("материализовать указанный `review` contract", migration)
        self.assertIn("`workflow_kit.revision: v0.8.2`", migration)
        self.assertIn("и выполнить validation записанной revision", migration)
        self.assertIn("`--deliver-task` остаётся fail-closed", migration)
        self.assertIn("Безопасный откат требует вернуть и project configuration", aliases)
        self.assertIn("весь выбранный набор skills на один прежний exact release tag", migration)
        self.assertIn("или смешивать revisions нельзя", migration)
        self.assertIn("Параметризованный release handoff", aliases)
        self.assertIn("full_local_model_review_after_routine_github_correction", aliases)
        self.assertIn("mismatch_behavior: stop_before_affected_alias_mutations", aliases)
        handoff = aliases.split("### Параметризованный release handoff", 1)[1]
        required_handoff_fragments = (
            "source_task: <source-task-id>",
            "parent_task_or_issue: <parent-task-or-issue>",
            "consumer_task: <consumer-task-id>",
            "previous_release:\n    tag: <previous-release-tag>",
            "schema_version: 4",
            "required_configuration_delta:",
            "initial_github_generation_required: true",
            "github_generation_target: exact_current_full_head",
            "skills/deliver-reviewed-change",
            "test_delivery_review_contract.py",
            "mismatch_behavior: stop_before_affected_alias_mutations",
            "rollback_target:\n    tag: <previous-release-tag>",
            "repository: <consumer-tracker-repository>",
            "marker: <project-owned-unique-marker>",
            "comment_id: <canonical-comment-id>",
            "comment_url: <canonical-comment-url>",
        )
        for fragment in required_handoff_fragments:
            with self.subTest(handoff_fragment=fragment):
                self.assertIn(fragment, handoff)
                self.assertNotIn(fragment, handoff.replace(fragment, "", 1))
        self.assertEqual(
            handoff.count(
                "response_binding_required: "
                "exact_reviewed_commit_or_active_request_generation"
            ),
            2,
        )


if __name__ == "__main__":
    unittest.main()
