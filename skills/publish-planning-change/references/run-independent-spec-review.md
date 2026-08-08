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

Before the initial review, read the positive integer `max_correction_rounds`
and `review_cycle_state` contract from project configuration. Resolve the
specification-owner repository's Git common directory with
`git rev-parse --git-common-dir`; never put runtime state in the planning
worktree or publication manifest. Under the configured relative directory,
derive one path-safe attempt key from the exact Task ID, specification-owner
repository, and publication branch. Permit only one active attempt for that
key.

Create a non-tracked JSON record before the first review with at least:

- `record_kind`, `attempt_id`, and the exact attempt-key tuple;
- Task ID, specification-owner repository, publication branch, planning
  worktree, and canonical base revision at attempt start;
- `max_correction_rounds`, `correction_rounds_used: 0`, and current stage;
- an initially empty `rounds` array plus created/updated timestamps.

Write with a same-directory temporary file and atomic rename, then reread and
verify the complete record before continuing. Serialize creation and every
read-modify-write transition with a sibling per-attempt lock directory acquired
by atomic `mkdir`. Store the configured lock-owner fields inside it. If the lock
already exists, stop without reading stale state or mutating content; never
steal it by timeout. Stale-lock recovery requires explicit inspection of the
record, owner, process, worktree, and Git state. Hold the lock through state
readback, advance a monotonic `state_revision` on every write, and release it
only after successful verification. Atomic rename protects record integrity;
the exclusive lock protects transition serialization.

On resume, acquire that lock, then locate and reread the single active record by
its exact attempt key. Confirm its task, repository, branch, configured maximum,
worktree/branch identity, counter, round history, state revision, and current
Git state. If the record is missing, duplicated, unreadable, or inconsistent,
stop without resetting or guessing. A new session, process, commit, worktree
relocation, or reviewer run never creates a new attempt.

A correction round is one bounded package of accepted current-spec changes
made after a non-clean verdict; multiple findings fixed together count as one
round. Before editing, verify `correction_rounds_used < max_correction_rounds`,
reserve the next round by incrementing the counter and appending its source
review/head and accepted finding fingerprints with stage `reserved`, then
atomically write and reread the record. Only after that readback may the content
mutation begin. A crash after reservation consumes that round; resume must
reconcile and finish or explicitly abandon it, never decrement it. After the
package, record its exact changed-path/blob manifest and stage, reread again,
rerun affected checks, and review the new exact head.

The corrected head after `correction_rounds_used == max_correction_rounds`
still receives its required review. If that review is clean, continue. If it
still contains any verified `blocking` or `actionable` finding, stop before a
further content mutation, review request, commit, push, or publication action.
Do not start a sixth correction when the configured maximum is five.

At that stop, produce a bounded review-cycle analysis containing the reviewed
head and finding fingerprints for every round, classification and disposition
of each finding, the correction package applied in each round, the still-open
findings, and whether repetition, scope instability, or an unresolved product
or architecture decision is driving the loop. Return the specification to
discussion/planning and require explicit user direction or a materially revised
shaped contract before starting a new publication attempt. Mark the record
`limit_reached`, persist the analysis reference, and retain it. Remove the
active record only after successful publication and canonical evidence
readback. Starting a replacement attempt after a limit stop requires explicit
user direction and archival of the stopped record; never overwrite it.

When a verified pre-limit finding instead requires material product,
architecture, scope, or decomposition reshaping, do not leave an unusable
active record. Under the same exclusive lock, mark it
`superseded_by_reshaping`, persist the triggering finding and complete consumed-
round history, atomically move it to the configured archive directory, and
reread the archive before releasing the lock. Stop publication and hand off to
`shape-project-work`. Only after the user explicitly accepts a materially
revised shaped contract may a new attempt ID be created for the same task and
branch; its record must name the archived `supersedes_attempt_id`. Without that
accepted contract and archived readback, resume or replacement remains blocked.

One clean generation for the current head is terminal. Do not keep requesting
review for an unchanged clean spec. Apply separate configured request-attempt
budgets and stop on repeated dismissed findings or scope instability.

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
