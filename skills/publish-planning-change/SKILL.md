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
- Let `write-task-spec` own substantive specification content and its content
  verdict. Let `manage-project-work` own Issue links and operational status.
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
  file, Git, tracker, or pull-request mutation, require schema v3 and the full
  configured bound-review evidence contract when this workflow is selected.
  Treat every other project schema or incomplete contract as invalid and stop
  direct `--publish-spec` before mutations, routing configuration repair to
  `configure-project-workflow`. Do not infer publication readiness from partial
  fields or silently upgrade the configuration;

- the canonical specification owner repository, spec root, and target branch;
- planning worktree root, branch format, base freshness, and cleanup policy;
- allowed planning artifact classes and forbidden path classes;
- required content verdict and publication-state transitions;
- independent reviewer command, model, effort, rubric, isolation, and retry
  budget;
- deterministic validators, commit convention, PR policy, required checks,
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
Stop on an unrelated change, implementation file, missing task identity,
unpublished dependency, or ambiguous artifact owner.

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

Use a fresh configured reviewer without the planning discussion history. Give
it the exact task anchor, shaped contract, spec diff, and only the architecture,
code, and policy context required to verify the specification. Treat the
author's self-check as useful evidence, never as independent review.

Before the first review, initialize a correction-round counter for this exact
publication attempt from the configured `max_correction_rounds`. Count one
round for each bounded correction package applied after a non-clean review,
not for each finding or edited file. Preserve the counter across resumes of the
same publication attempt.

Evaluate every finding against the shaped scope and sources of truth. Route a
real content correction through `write-task-spec`; route a material outcome or
scope change back to `shape-project-work`. Rerun affected validation and obtain
a clean review for the current spec head. Do not expand the task for speculative
edge cases or general improvements. Review the corrected head, including after
the final allowed correction round. If that review still has blocking or
actionable findings, stop before another correction or publication mutation
and return the specification to planning with the required review-cycle
analysis; never start a correction round beyond the configured limit.

### 4. Publish the reviewed change

Read [publish-reviewed-planning-change.md](references/publish-reviewed-planning-change.md).

After clean review, let `write-task-spec` assign the highest supported content
verdict for the reviewed head. Run deterministic checks, stage only the exact
manifest, commit intentionally, push without force, create or reconcile the
exact pull request, and obey reported checks and branch protection. Merge only
when the configured endpoint and current user authority allow it.

### 5. Finalize the handoff

Read [finalize-planning-publication.md](references/finalize-planning-publication.md).

Verify the merged canonical branch contains the exact specification and that
the recorded revision belongs to the reviewed pull-request head. Ask
`manage-project-work` to link the canonical spec and apply the configured
implementation-ready operational status only after this evidence exists.
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
