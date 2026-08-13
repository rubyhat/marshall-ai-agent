# Create or Resume a Task Workspace

Use the project repository map and workspace policy. Do not assume one repository, `main`, `origin`, or a fixed filesystem layout.

## Select repositories

Include only repositories whose tracked files must change for the exact task. Include the root or coordination repository only when its own files are implementation deliverables.

Reject or escalate a repository marked frozen, archived, read-only, or unsupported by project policy.

## Inspect before mutation

For every selected repository, inspect:

- repository identity and configured remote;
- default branch and available remote-tracking ref;
- project- or task-defined intended base and pull-request target for this exact
  repository, including whether either ref already exists locally or remotely;
- current branch and working-tree status in the main workspace;
- registered worktrees;
- existing task branch and proposed workspace path;
- branch-name or path collisions;
- relevant parallel task state.

Never move unfamiliar main-workspace changes into the new task workspace implicitly.

## Resume safely

Reuse an existing task workspace only when:

- its path belongs to the exact task;
- its worktree registration points to the expected repository;
- its branch belongs to the exact task;
- its recorded intended base and target still match current project and task
  policy;
- its dirty changes are understood as task state;
- no other active task or session owns it incompatibly.

Report the resumed branch and existing changes before continuing. Do not recreate or reset a valid dirty worktree.

## Create from a verified base

When a workspace does not exist:

1. resolve the configured remote, repository default branch, and any exact-task
   repository override for the intended task base and pull-request target as
   one record keyed by the task or aggregate anchor plus repository. Record
   whether it came from the exact task contract, project configuration, or the
   compatibility fallback; do not build a persisted branch registry;
2. when no override exists, use the repository default branch for both the
   intended base and target so existing projects keep their current behavior;
3. fetch and prune the relevant refs when network and policy allow;
4. verify the intended base when it exists. When it does not exist and project
   policy authorizes first-use establishment, derive it from the verified
   configured creation base, prove that no conflicting local or remote branch
   appeared, and create or prepare it without force, reset, or history rewrite;
5. when file-backed planning publication is configured and this repository also
   owns the canonical task specification, verify that the base contains or
   descends from the ordinary merged revision in the complete current
   capture-contract publication record;
6. when file-backed planning publication is configured and the specification
   owner is a different repository, verify the recorded matching exact-task
   ordinary tuple with Task ID, owner repository, canonical spec path, merged
   revision, capture-contract revision, publication-attempt ID,
   normalized-result hash, and complete matched reviewer session set instead of
   requiring impossible shared Git ancestry;
7. derive the configured task branch and workspace path;
8. ensure the task branch, intended base, intended target, and workspace do not
   collide with another task or owner;
9. create the feature branch and worktree from the resolved intended base;
10. verify branch, `HEAD`, base revision, intended target, worktree
    registration, and clean initial state. Retain the verified creation-source
    branch when the base was established, or an explicit not-applicable value
    when it already existed.

The intended base and pull-request target may be the same integration branch,
but do not assume that they are. If first-use preparation remains local because
execution authority excludes push, record the missing remote branch as an
explicit delivery gate. If a remote branch appears or moves before delivery,
reconcile its ownership and ancestry instead of overwriting it.

Apply the following evidence rules only when file-backed planning publication is
configured. Historical legacy derived revisions and cross-repository legacy
tuples are inventory/audit evidence only.
Missing or incomplete current ordinary evidence returns typed
`publication_upgrade_required` with `workspace_created: false`; do not create or
resume an implementation worktree before republication. When publication is not
configured, skip these evidence and upgrade-stop rules and use the verified
project base selected by the remaining workspace policy.

A typical command shape is:

```text
git -C <repository> fetch --prune <remote>
git -C <repository> worktree add -b <task-branch> <workspace-path> <resolved-base>
```

Adapt commands to the configured repository and Git version. Do not copy these placeholders literally.

## Handle unavailable remotes

If fetch fails:

- do not silently treat a stale local branch as current;
- report the failed remote operation and every affected intended base or target;
- continue from a local base only when project degraded-mode policy allows it;
- record the base ref or commit and the staleness risk;
- preserve a pending remote verification gate for delivery.

## Apply worktree exceptions

Honor a no-worktree request only when project policy permits an explicit exception. First inspect dirty and parallel-work risk. If the requested directory is unsafe, object and request a safe alternative instead of overwriting unfamiliar work.

## Continue after setup

Workspace setup is not completion of an implementation request. Continue into the task unless:

- the user explicitly requested setup only;
- readiness changed;
- repository state is unsafe;
- a real external blocker prevents implementation.
