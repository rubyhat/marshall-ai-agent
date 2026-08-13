# Classify and Handle Review Findings

Evaluate findings against the actual task instead of optimizing for reviewer agreement.

## Classify each finding

Use:

- `real_in_scope`: correct and required by the current specification or safety constraints;
- `false`: based on incorrect code or behavior assumptions;
- `intentional_out_of_scope`: valid generally but explicitly excluded from this task;
- `duplicate`: already addressed or already dismissed with the same semantic basis;
- `uncertain`: evidence is insufficient or resolution would change scope or architecture.

Check code, tests, contracts, task specification, non-goals, follow-up tasks, and project instructions. Do not dismiss a security, tenant-isolation, data, billing, or legal finding merely because it is inconvenient.

Require a `real_in_scope` finding to identify a concrete current-task failure or
credible mandatory risk related to the reviewed diff. Classify generalized
hardening, stylistic cleanup, speculative edge cases without a credible task
path, unrelated pre-existing defects, future scaling, and already assigned
follow-up work as non-actionable for this delivery.

## Fix a real finding

1. require bound passed pre-PR local-gate evidence; otherwise stop as
   `pre_pr_local_gate_missing` without an override path;
2. compare the proposed package with the immutable delivery baseline and task
   contract;
3. stop before edits on material scope, contract, architecture, permissions,
   security or tenant boundary, data, migration, ownership, dependency, or
   unexplained cumulative-diff growth, and use the same stop for `uncertain`;
4. verify another GitHub correction round is available before editing;
5. persist and read back this finding, reviewed head, and paused automation
   status in the exact PR heartbeat before editing;
6. apply the smallest coherent fix in the delivery-owned task worktree or, for
   aggregate promotion, its delivery-owned source/helper worktree, and increment
   the GitHub counter once for the complete package. Never route a promotion
   correction through a completed child task's workspace;
7. run the deterministic routine-correction gate from
   [verify-routine-github-correction.md](verify-routine-github-correction.md),
   including affected tests, configured gates, `git diff --check`, exact delta
   and scope verification, and finding readback;
8. record `local_model_invocations: 0`; do not run a full, targeted, or hidden
   local model review for this routine package;
9. classify every follow-on gate-fix edit again before mutation and stop if it
   is material or uncertain;
10. commit intentionally, then re-read the still-paused exact PR heartbeat before
   a head-changing push;
11. push and capture the new head SHA;
12. reactivate that same heartbeat and start a new review generation with reset
   technical request counters and the
   unchanged GitHub correction counter.

If the heartbeat was active during the push or the owned transition cannot be
proven, stop with `head_mismatch`; do not relabel an unknown external head as a
workflow-owned push.

If the scope, contract, architecture, ownership, or cumulative-diff gate in
step 2 stops the finding workflow, apply
[finalize-codex-review-state.md](finalize-codex-review-state.md) with
`scope_or_contract_stop` before returning its owning-workflow handoff.

Old clean verdicts and comments cannot complete the new head.

The head produced by the final allowed GitHub correction round still receives
review. If another real package is required, apply the terminal procedure with
`github_correction_budget_exhausted` and stop before editing, commit, push, or
another review request. Return its bounded cycle analysis instead.

## Answer a false or intentionally excluded finding

Do not change code. Reply with:

- the exact disputed behavior;
- evidence from code, specification, non-goal, or follow-up task;
- why no change belongs in the current PR;
- a request to ignore that item and continue reviewing the remaining diff.

Then create a contextual review request containing the configured trigger only
if the current head still has request budget. Use both the `Create one request
attempt` and `Attach and verify the request identity` sections of
[start-codex-review-cycle.md](start-codex-review-cycle.md). If no attempt remains,
apply the terminal procedure with `request_budget_exhausted` and report the
finding plus rationale instead of exceeding the configured limit. Do not claim
a follow-up is tracked unless its canonical task exists.

Do not automatically resolve the thread. Preserve the visible rationale.

## Fingerprint dismissed findings

Persist a semantic fingerprint using:

- repository and PR;
- file/path and symbol or behavior;
- reviewer rule or risk;
- dismissal reason and evidence owner.

Do not rely on exact comment text. If the reviewer returns the same semantic finding once after the contextual re-review:

1. apply the terminal procedure with `repeated_dismissed_finding`;
2. do not argue or request review again;
3. report the repeated finding and prior rationale to the user.

## Stop on uncertainty

When uncertainty would change outcome, task scope, architecture, permissions,
security posture, data contract, dependency order, or an explicit non-goal,
apply the terminal procedure with `scope_or_contract_stop` and return its
owning-workflow handoff.
