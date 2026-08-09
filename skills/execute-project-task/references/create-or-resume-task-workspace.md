# Create or Resume a Task Workspace

Use the project repository map and workspace policy. Do not assume one repository, `main`, `origin`, or a fixed filesystem layout.

## Select repositories

Include only repositories whose tracked files must change for the exact task. Include the root or coordination repository only when its own files are implementation deliverables.

Reject or escalate a repository marked frozen, archived, read-only, or unsupported by project policy.

## Inspect before mutation

For every selected repository, inspect:

- repository identity and configured remote;
- default branch and available remote-tracking ref;
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
- its dirty changes are understood as task state;
- no other active task or session owns it incompatibly.

Report the resumed branch and existing changes before continuing. Do not recreate or reset a valid dirty worktree.

## Create from a verified base

When a workspace does not exist:

1. resolve the configured remote and default branch;
2. fetch and prune when network and policy allow;
3. verify the intended remote-tracking base;
4. when file-backed planning publication is configured and this repository also
   owns the canonical task specification, verify that the base contains or
   descends from the ordinary merged revision in the complete current
   capture-contract publication record;
5. when file-backed planning publication is configured and the specification
   owner is a different repository, verify the recorded matching exact-task
   ordinary tuple with Task ID, owner repository, canonical spec path, merged
   revision, capture-contract revision, publication-attempt ID,
   normalized-result hash, and complete matched reviewer session set instead of
   requiring impossible shared Git ancestry;
6. derive the configured task branch and workspace path;
7. ensure neither collides with another task;
8. create the feature branch and worktree from that base;
9. verify branch, `HEAD`, worktree registration, and clean initial state.

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
git -C <repository> worktree add -b <task-branch> <workspace-path> <remote>/<default-branch>
```

Adapt commands to the configured repository and Git version. Do not copy these placeholders literally.

## Handle unavailable remotes

If fetch fails:

- do not silently treat a stale local branch as current;
- report the failed remote operation and known local base;
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
