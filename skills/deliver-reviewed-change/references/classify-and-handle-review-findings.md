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

## Fix a real finding

1. apply the smallest coherent fix in the task worktree;
2. add or update relevant tests;
3. run affected implementation gates;
4. repeat local review when configured or material;
5. commit and push intentionally;
6. capture the new head SHA;
7. start a new review generation with a reset request budget.

Old clean verdicts and comments cannot complete the new head.

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
