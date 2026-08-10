---
name: publish-planning-change
description: Publish one exact project planning change, normally a task specification and only its directly related tracked planning artifacts, through isolated workspace verification, independent bounded specification review, intentional commit and push, pull-request checks, authorized merge, canonical-revision verification, and safe cleanup. Use when the user invokes `--publish-spec` with a Task ID, Issue URL, or spec path; asks to review, finalize, publish, or merge a prepared task specification; or when `write-task-spec` needs the configured planning workspace before writing a Git-tracked spec. Do not use for implementation code, ordinary implementation delivery, unrelated documentation, release or deployment, production mutations, broad dirty-worktree cleanup, or publishing an unreviewed draft.
---

# Publish Planning Change

Move one exact prepared planning change from a local specification workspace to
the canonical project branch without weakening planning-session boundaries or
mixing it with implementation delivery.

## Keep the responsibility narrow

- Own the isolated planning workspace lifecycle, exact publication manifest,
  independent spec review, Git publication, canonical-revision evidence, and
  safe post-merge cleanup.
- Treat the task specification as the primary artifact. Include supporting
  tracked memory or project documentation only when it is directly required by
  the same task handoff and explicitly allowed by project policy.
- Let `write-task-spec` own substantive specification content and materialize
  the provisional target content verdict before review. Let
  `manage-project-work` own Issue links, publication evidence, operational
  status, and typed evidence-migration state.
- Do not publish source code, migrations, generated application artifacts,
  implementation reports, unrelated dirty files, releases, deployments, or
  production changes.
- Do not close the implementation task merely because its specification was
  published.

## Establish mode and authority

Choose one mode:

- `prepare_workspace`: receive an authorized handoff from `write-task-spec`
  before the first file mutation and create or resume only the configured
  planning worktree and branch;
- `publish`: start from a verified `Spec ready` handoff and continue to the
  configured endpoint;
- `resume`: continue the exact existing planning branch or pull request;
- `inspect`: report publication state read-only without fixing it.

Treat `--publish-spec <Task ID, Issue URL, or spec path>` as explicit authority
for the configured publication lifecycle of only that exact specification. A
narrower request such as "open the PR but do not merge" limits the endpoint.
Ask for a missing or ambiguous anchor before mutations.

When project policy enables `planning_artifact_publication`, allow this alias
inside an active planning session without releasing that profile. The
capability authorizes only the exact planning publication manifest. It never
authorizes `--execute-task`, `--deliver-task`, implementation code, ordinary
delivery, release, or deploy.

## Resolve project policy

Read project instructions and workflow configuration. Resolve:

- the project configuration schema version. Before any publication workspace,
  file, Git, tracker, or pull-request mutation, require schema v4, the canonical
  authoritative-session runner command template, and the full bound-review
  evidence contract when this workflow is selected.
  Treat every other project schema or incomplete contract as invalid and stop
  direct `--publish-spec` before mutations, routing configuration repair to
  `configure-project-workflow`. Do not infer publication readiness from partial
  fields or silently upgrade the configuration;

- the canonical specification owner repository, spec root, and target branch;
- planning worktree root, branch format, base freshness, and cleanup policy;
- allowed planning artifact classes and forbidden path classes;
- required content verdict and publication-state transitions;
- independent reviewer runner, model, effort, rubric, isolation, correction
  budget, one-retry technical budget, and terminal-session settlement policy;
- deterministic validators, commit convention, PR policy, required checks,
  post-PR deterministic correction policy, conditional final-evidence review,
  merge authority, and allowed endpoint;
- Issue/spec linkage, operational status, canonical revision recording,
  specification-owner ancestry, and cross-repository linkage requirements.

Use the configured spec root. A newly configured project should normally use
`docs_ai/tasks` without asking the user to choose a path unless the user has
already selected another owner or inspection finds a coherent conflicting
convention.

## Run the publication workflow

### 1. Verify the exact handoff

Read [verify-planning-publication-readiness.md](references/verify-planning-publication-readiness.md).

Confirm one exact task, Issue when configured, specification package, content
verdict, owner repository, planning workspace, branch, base, and complete diff.
Accept either the normal `Spec ready` handoff or the configured
`stale_published_ready_spec` correction entry: the latter requires an existing
canonical publication, exact `Ready for implementation`, and typed
`publication_upgrade_required`. Close implementation authority before review.
Stop on an unrelated change, implementation file, missing task identity,
unpublished dependency, or ambiguous artifact owner.

Before computing the review manifest, ask `write-task-spec` to materialize the
final target verdict `Ready for implementation` in the isolated candidate.
Treat it as provisional until canonical merge and complete evidence readback.
For the stale-published correction entry, preserve the existing target verdict
instead of downgrading and re-promoting it. Reread the complete package before
continuing.

### 2. Establish the exact manifest

Classify every changed path as primary spec, required supporting planning
artifact, unrelated change, or forbidden change. Present the exact included and
excluded paths when scope is not already explicit. Never use a broad staging
operation to absorb an unfamiliar file.

If a legacy spec was written into a main checkout, do not silently transplant
or discard it. Show the exact recovery manifest needed to move only the owned
files into an isolated planning workspace and require the applicable authority.

### 3. Run independent bounded review

Read [run-independent-spec-review.md](references/run-independent-spec-review.md).

Use the configured deterministic runner to launch a fresh reviewer without the
planning discussion history. Give it the exact task anchor, shaped contract,
spec diff, and only the architecture, code, and policy context required to
verify the specification. Treat the author's self-check as useful evidence,
never as independent review. Treat outer process output and exit status as
diagnostics only; the normalized authoritative result comes from matched child
`task_complete.last_agent_message` records.

For one publication attempt, read the configured positive
`max_correction_rounds` and start `correction_rounds_used` at zero. Count one
round for one bounded package of corrections made after a non-clean review,
not for each finding or file. Increment the counter once after applying that
package, rerun affected validation, and review the corrected exact head. A
correction that reaches the configured maximum still receives this required
review.

When a correction package after a non-clean review changes a publication
manifest that already has an in-scope commit on the planning branch, require the
configured `committed_correction_review` contract. For the supported
`local_checkpoint_committed_base_diff` strategy, run deterministic checks and
preserve the provisional target verdict. Require the planning worktree to
contain no excluded dirty paths; otherwise stop before the checkpoint with an
exact preservation/recovery handoff. Stage only the exact publication manifest
and make one authorized local-only correction checkpoint commit before review.
Do not push that checkpoint until its exact head receives a clean
committed-base-diff review. The checkpoint belongs to the current correction
round; it is not publication evidence by itself.
Retain the exact uncommitted-review path only when the manifest has no in-scope
commit relative to the canonical base. Reject a mixed committed-plus-uncommitted
candidate before model invocation because `codex review --uncommitted` omits its
committed portion. Create an authorized clean checkpoint and review the complete
candidate with the committed-base selector. Bind a purely uncommitted candidate
to the eventual head by path/mode/blob-OID equality.

Evaluate every finding against the shaped scope and sources of truth. Route a
real content correction through `write-task-spec`; route a material outcome or
scope change back to `shape-project-work`. Rerun affected validation and obtain
a clean review for the current spec head. Do not expand the task for speculative
edge cases or general improvements.

Wait for every registered review process, matched outer session, and matched
review child to reach terminal state. Require two stable bounded scans and a
final rescan before accepting a result. Union and deduplicate findings from all
terminal results of the stable publication attempt, including a late result
from the initial invocation after a technical retry began. One or more
findings make the consolidated result non-clean. Invalid terminal JSON,
binding ambiguity, target drift, or settlement timeout is fail-closed and does
not consume a correction round.

Permit one automatic technical retry only after settled
`no_authoritative_terminal_result`. Preserve the same publication-attempt
boundary and rescan every invocation session. A second missing result becomes
`technical_retry_budget_exhausted`; no third model invocation is allowed.

If the corrected head is still not clean after the maximum round, stop before
another correction, review request, commit, push, or publication. Report a
bounded cycle analysis and return the specification to planning or the user.
Do not start a sixth correction when the configured maximum is five. On resume,
continue only when the exact counter and ordered review/correction history for
the same attempt are provable; otherwise fail closed and require an explicit
user decision to start a new publication attempt rather than resetting the
counter implicitly.

### 4. Publish the reviewed change

Read [publish-reviewed-planning-change.md](references/publish-reviewed-planning-change.md).

Publish the exact clean-reviewed candidate without any post-review verdict or
package-byte mutation. When review targeted a local correction checkpoint,
reuse that exact checkpoint. For an uncommitted-review candidate, create the
intentional commit only when its complete path/mode/blob-OID manifest is identical
to the reviewed manifest. Push without force, create or reconcile the exact
pull request, and obey reported checks and branch protection. Do not merge in
this phase; the exact current complete pull-request head must first receive the
clean GitHub generation and final evidence decision in step 5.

### 5. Handle post-PR corrections and final evidence

Read [run-planning-github-review-cycle.md](references/run-planning-github-review-cycle.md),
then read
[verify-post-pr-planning-correction.md](references/verify-post-pr-planning-correction.md).

Use the planning-owned trigger, reviewer matching, response channels, request
budgets, exact-PR heartbeat, state machine, and five-package GitHub correction
counter. Start or reconcile the configured head-bound GitHub review generation
for the initial complete pull-request head. Require a clean generation bound to
the exact current full head before selecting final evidence or entering merge
gates. Every corrected head replaces this requirement with its own new
generation; old or unbound response events cannot satisfy it. An applied
routine package must become a proved intentional exact-manifest commit before
non-force push and the next generation.

Do not run independent review after each routine GitHub correction package.
Use affected tests, configured deterministic gates, `git diff --check`, exact
correction-delta and scope verification, and finding-by-finding readback before
push. False, intentional-out-of-scope, and duplicate findings use the configured
fingerprinted no-edit contextual re-review path and consume no correction
round. Material or uncertain corrections stop before edits and return to the
owning planning workflow.

After the GitHub loop reaches a clean exact current head, reuse existing
independent evidence only when its head, tree, and complete manifest binding are
already current. Otherwise run exactly one final independent evidence review
through the canonical runner. A non-clean, invalid, unbound, or timed-out final
result terminates the publication attempt without automatic corrections, push,
merge, another GitHub request, or a second final evidence review.

Only after the clean exact-current-head GitHub generation and the zero-or-one
final evidence decision pass may the configured checks and merge-authority
gates continue.

### 6. Finalize the handoff

Read [finalize-planning-publication.md](references/finalize-planning-publication.md).

Verify the merged canonical branch contains the exact specification and that
the recorded revision belongs to the current evidence-bound pull-request head.
Ask
`manage-project-work` to persist the capture-contract revision, publication
attempt ID, normalized-result hash, complete matched reviewer session set,
canonical spec linkage, and configured implementation-ready status only after
this evidence exists and has been reread.
Synchronize and remove the planning workspace only after merge and safety
checks.

Stop at the authorized endpoint. An open pull request is not equivalent to a
canonical published specification, and an unmerged spec must not unlock
implementation.

## Coordinate with adjacent skills

- Receive shaped scope from `shape-project-work` and specification content from
  `write-task-spec`.
- Provide `write-task-spec` an isolated planning workspace before file-backed
  spec creation when this module is configured.
- Use `record-project-context` for directly required tracked supporting context;
  do not publish transient local-only notes.
- Ask `manage-project-work` to update only exact linkage and status checkpoints.
- Hand implementation to `execute-project-task` only after canonical
  publication evidence passes.
- Keep `deliver-reviewed-change` responsible for implementation changes. Never
  reuse its task-closing semantics for specification publication.
