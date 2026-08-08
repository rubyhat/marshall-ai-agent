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
Before launch, require that the owning workflow's current-schema pre-mutation
gate has passed and that the reviewer worktree, placeholder, branch-readback,
and bound-review fields are materialized and valid. Do not apply compatibility
defaults inside the publication lifecycle; invalid configuration must already
have stopped direct publication.
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

## Capture a bindable clean-review record

Before accepting a clean verdict, capture a bounded durable candidate record:

- exact reviewer run or session identifier, model, effort, completion time, and
  terminal clean verdict;
- review target kind, canonical base revision, planning worktree, branch, and
  the reviewed commit when the target was already committed;
- the complete sorted publication-package manifest with every allowed
  project-relative path and content blob OID.

Do not treat model and effort alone, a PR-description claim, or an unbound
verdict as review evidence. A full private reasoning transcript is neither
required nor copied into the specification. When the clean review targeted
uncommitted content, keep the manifest as candidate evidence; the publication
workflow must bind it to the eventual committed PR head by exact path/OID
equality before merge. Any manifest change invalidates the clean verdict and
requires a fresh review.
