---
name: execute-project-task
description: Execute an exact implementation-ready project task in an isolated, project-configured workspace and prepare the uncommitted changes for independent local review. Use when the user explicitly asks to implement, build, fix, start, continue, or resume a resolved task or specification, or invokes `--execute-task` with a Task ID, Issue URL, or spec path. Verify active conversation authority before task lookup or mutations, then verify readiness, select affected repositories, create or reuse task worktrees and branches, protect parallel work, implement against the agreed specification, control scope drift, run relevant quality gates, self-check the diff, and establish the local-review checkpoint. Do not use for discussion or diagnosis-only requests, shaping, specification writing, independent review, commit, push, pull-request creation, merge, workspace cleanup, or production mutations.
---

# Execute Project Task

Turn one authorized, ready implementation task into verified uncommitted changes without crossing into independent review or delivery.

## Keep the responsibility narrow

- Receive outcome and scope from the task specification or equivalent configured contract.
- Receive task identity and lifecycle mutations from `manage-project-work`.
- Own readiness preflight, repository selection, isolated workspace setup, implementation, relevant quality gates, diff self-check, and the local-review handoff.
- Do not reshape product scope, silently repair a material specification conflict, perform independent review, commit, push, create a pull request, merge, deploy, mutate production data, or clean the task workspace.
- Do not begin implementation merely because shaping or specification reached a ready verdict. Require explicit implementation authority.

## Resolve active conversation authority first

Before task lookup, status transition, workspace or branch creation, dependency
commands, file edits, or another mutation-capable action, inspect already
loaded conversation state and project policy for:

- an active planning-session profile;
- an explicit current-session no-code, no-implementation, read-only, or
  discussion-only constraint;
- another sticky negative constraint that excludes implementation.

Treat a conflicting alias or natural-language implementation request as a
conflict, not as an implicit override. Stop before mutations, state the
received request, active constraint, conflict, and exact configured release
action, and confirm that no task, Git, dependency, or file state changed.

A later request may narrow authority but cannot silently expand it beyond a
sticky constraint. Task readiness never overrides this gate.

## Resolve project policy

Read project instructions and workflow configuration. Resolve:

- implementation readiness gates and allowed overrides;
- task identity, specification, canonical publication revision, tracker, and
  status requirements;
- repository map, default branches, remotes, and frozen repositories;
- worktree policy, workspace root, branch naming, and explicit exceptions;
- degraded-mode behavior when a remote or task tracker is unavailable;
- project and repository quality gates;
- domain workflows for migrations, frontend, localization, security, data, rollout, or other impacts;
- start and local-review status checkpoints;
- recording and delivery handoffs.

Keep project names, repository paths, status labels, branch formats, test commands, and framework assumptions out of this reusable skill.

## Interpret the exact quick alias

After the active-conversation gate passes, treat `--execute-task <Task ID,
Issue URL, or spec path>` as authority to execute that exact task locally:

- resolve and validate the task;
- create or reuse configured worktrees and feature branches;
- edit task-scoped files;
- run local dependency, generation, build, test, and verification commands required by the task;
- apply routine configured task-status checkpoints.

The alias does not authorize commit, push, pull-request creation, merge, production access, destructive data operations, unrelated cleanup, or another task. Ask for the missing anchor when the alias is incomplete. Treat trailing text as task input, not broader authority.

## Run the execution workflow

### 1. Resolve one exact implementation scope

Resolve the strongest available anchor: exact Task ID, Issue, specification path, or an already established current task. Confirm whether the project models multi-repository work as one task or an exact set of repo-specific sibling tasks.

Do not implement an Epic, Feature, ambiguous search result, or unrelated task collection as though it were one implementation task.

### 2. Check implementation readiness

Read [check-task-readiness.md](references/check-task-readiness.md).

Require the configured ready verdict or equivalent readiness evidence. Check unresolved decisions, acceptance criteria, dependencies, repository ownership, required quality gates, and conflicts with current architecture or higher-priority instructions.

When specifications are file-backed and planning publication is configured,
select one complete readiness path in this precedence order:

- prefer ordinary publication evidence whenever it is complete: a clean
  independent spec review, a merged
  canonical specification revision, and proof that the specification-owner
  authority base contains or descends from that revision. Require the complete
  persisted and reread `reviewed_canonical_publication` record defined in
  [check-task-readiness.md](references/check-task-readiness.md);
- otherwise, when project policy explicitly enables it for specs that were already
  implementation-ready before planning publication was configured, the
  deterministic baseline evidence defined in
  [check-task-readiness.md](references/check-task-readiness.md).

An ordinary publication record supersedes legacy evidence for readiness
selection even when the historical legacy record remains available for audit.

For an implementation repository with a separate Git history, require the
matching exact-task record for the selected path: the ordinary publication
record with its reviewed-head, package-manifest, clean-review, and merged-
revision evidence, or the `legacy_ready_baseline` tuple with its explicit
evidence kind, complete package manifest, derived revision, and adoption
baseline. Do not require cross-repository ancestry. The legacy path
must not claim that
independent review occurred and is not a user override. An open PR, local file,
dirty main checkout, content verdict alone, incomplete record, or baseline
mismatch is insufficient. Route any unresolved publication gate to
`publish-planning-change` and recommend `--publish-spec <Task ID>`.

Route material outcome or decomposition gaps to `shape-project-work`. Route specification content gaps to `write-task-spec`. Apply a user override only when project policy permits it and after stating the exact missing gate and risk.

### 3. Establish the start checkpoint

Ask `manage-project-work` to apply the configured implementation-start status to every exact implementation task in scope. Treat the status update as a preparatory checkpoint, not completion.

If the tracker is unavailable, follow configured degraded-mode policy. Never claim a remote mutation succeeded when it did not.

### 4. Create or resume the task workspace

Read [create-or-resume-task-workspace.md](references/create-or-resume-task-workspace.md).

Select only repositories that will be modified. Include a root or coordination repository only when its files are implementation deliverables. Reuse an existing workspace only after verifying its task identity, branch, worktree registration, and working state.

For more than one repository, also read [create-multi-repo-worktrees.md](references/create-multi-repo-worktrees.md).

Workspace creation is preparation. Continue into implementation unless the user requested setup only or a real blocker prevents safe work.

### 5. Protect parallel work

Read [parallel-task-safety.md](references/parallel-task-safety.md).

Inspect branch, worktree, and dirty state before editing. Preserve unfamiliar changes. Stop and present a concrete objection when overlap creates a credible semantic, data, API, migration, shared-component, status, or lifecycle conflict.

### 6. Implement within authority and scope

Read [implement-with-scope-control.md](references/implement-with-scope-control.md).

Implement the smallest coherent change that satisfies the agreed outcome and acceptance criteria. Follow current project architecture and repository instructions. Use current code as evidence, not as silent authority to change promised behavior.

When discoveries change a durable contract, update the specification through `write-task-spec`. When they change outcome, scope, architecture, security posture, or dependency direction, stop and return to `shape-project-work`.

### 7. Run relevant quality gates

Read [run-implementation-quality-gates.md](references/run-implementation-quality-gates.md).

Run the configured gates relevant to the changed surface. Fix failures caused by the task. Verify suspected pre-existing or unrelated failures before excluding them, and do not expand scope silently.

Do not declare the implementation ready while a required gate fails unless project policy explicitly accepts the verified external blocker.

### 8. Self-check the implementation

Inspect the complete working-tree diff and status. Confirm:

- the diff maps to the exact task and acceptance criteria;
- no unrelated, generated, temporary, secret, debug, or local-only files leaked into the change;
- contracts, permissions, errors, migrations, localization, accessibility, observability, and documentation were handled when applicable;
- quality-gate evidence is current for the final diff;
- no known blocker or material assumption is hidden.

This is executor self-check, not independent local review.

### 9. Prepare the local-review handoff

Read [prepare-local-review-handoff.md](references/prepare-local-review-handoff.md).

Only after readiness, implementation, gates, and self-check succeed:

1. ask `manage-project-work` to apply the configured local-review status;
2. use `record-project-context` only for a useful rolling handoff or durable discovery;
3. report repositories, worktrees, branches, changes, checks, blockers, and assumptions;
4. hand the uncommitted state to `deliver-reviewed-change`.

Stop before independent review, commit, push, pull-request creation, merge, deployment, or workspace cleanup.

## Coordinate with adjacent skills

- Use `load-project-context` for bounded task orientation when current context is insufficient.
- Receive scope from `shape-project-work` and implementation contract from `write-task-spec`.
- Receive canonical specification publication evidence from
  `publish-planning-change` when configured.
- Use `manage-project-work` for exact task identity and lifecycle mutations.
- Use `record-project-context` for durable discoveries or multi-session handoff state, not routine command output.
- Hand independent review and delivery to `deliver-reviewed-change`.
- Invoke domain skills and project runbooks only when the task impact requires them.
