# Run independent specification review

Use a fresh read-only reviewer for the exact current specification head.

## Preserve reviewer independence

Do not give the reviewer the planning discussion transcript, the author's
private reasoning, expected findings, or intended verdict. Provide only:

- the exact task and tracker anchor;
- the agreed shaped outcome, scope, non-goals, and dependencies;
- the complete spec package and diff against the canonical base;
- applicable project instructions, architecture, code, contracts, and tests;
- the configured review rubric and stop conditions.

Use the configured model and effort. Keep reusable instructions model-neutral.
Set the reviewer process working directory to the exact planning worktree
before starting an uncommitted review. Do not rely on the checkout from which
the publication alias was invoked, a path added only for read access, or prompt
text to select the reviewed diff. Verify the reviewer reports the expected
planning worktree and branch before accepting its verdict.

## Review the specification contract

Check for concrete defects in:

- task identity, outcome, scope, and non-goals;
- consistency with the Issue, roadmap, architecture, and current code;
- requirements, permissions, states, errors, recovery, and lifecycle behavior;
- API, data, migration, compatibility, rollout, privacy, security, billing,
  localization, accessibility, observability, or operations when applicable;
- dependency ordering and cross-repository ownership;
- acceptance-criteria coverage and actionable verification;
- invented technical detail, hidden blockers, or an oversized task.

Do not request general improvements, stylistic rewrites, speculative edge cases
without a credible current-task risk, or work assigned to another task.

## Classify and handle findings

Classify each finding as:

- `blocking`: implementation would be unsafe, ambiguous, or materially wrong;
- `actionable`: a bounded current-spec correction is required;
- `non_blocking`: useful but not required for this task;
- `out_of_scope_or_unsubstantiated`: unsupported or intentionally deferred.

Verify findings against primary sources before editing. Use `write-task-spec`
for an in-scope content correction. Return a material product, architecture,
scope, or decomposition change to `shape-project-work`.

After a content change, rerun affected checks and review the new exact head.
One clean generation for the current head is terminal. Do not keep requesting
review for an unchanged clean spec. Apply configured attempt budgets and stop
on repeated dismissed findings or scope instability.

Report the clean-review evidence without copying the full review transcript
into the specification.
