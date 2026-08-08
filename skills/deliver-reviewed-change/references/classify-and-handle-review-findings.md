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

1. compare the proposed package with the immutable delivery baseline and task
   contract;
2. stop on material scope, contract, architecture, ownership, or unexplained
   cumulative-diff growth;
3. verify another GitHub correction round is available before editing;
4. apply the smallest coherent fix in the task worktree and increment the
   GitHub counter once for the complete package;
5. add or update relevant tests and run affected implementation gates;
6. repeat local review when configured or material;
7. commit and push intentionally;
8. capture the new head SHA;
9. start a new review generation with reset technical request counters and the
   unchanged GitHub correction counter.

Old clean verdicts and comments cannot complete the new head.

The head produced by the final allowed GitHub correction round still receives
review. If another real package is required, delete the heartbeat and stop
before editing, commit, push, or another review request. Return the bounded
cycle analysis instead.

## Answer a false or intentionally excluded finding

Do not change code. Reply with:

- the exact disputed behavior;
- evidence from code, specification, non-goal, or follow-up task;
- why no change belongs in the current PR;
- a request to ignore that item and continue reviewing the remaining diff.

Then create a contextual review request containing the configured trigger only if the current head still has request budget. If no attempt remains, stop and report the finding plus rationale instead of exceeding the configured limit. Do not claim a follow-up is tracked unless its canonical task exists.

Do not automatically resolve the thread. Preserve the visible rationale.

## Fingerprint dismissed findings

Persist a semantic fingerprint using:

- repository and PR;
- file/path and symbol or behavior;
- reviewer rule or risk;
- dismissal reason and evidence owner.

Do not rely on exact comment text. If the reviewer returns the same semantic finding once after the contextual re-review:

1. stop the heartbeat;
2. do not argue or request review again;
3. report the repeated finding and prior rationale to the user.

## Stop on uncertainty

Return to the user or owning workflow when resolving a finding would change outcome, task scope, architecture, permissions, security posture, data contract, dependency order, or explicit non-goal.
