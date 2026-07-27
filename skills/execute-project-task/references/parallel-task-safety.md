# Parallel Task Safety

Assume another task may be active in every repository.

## Protect filesystem and Git state

- Do not switch the main workspace to a task branch.
- Do not work inside another task's worktree.
- Inspect branch, `HEAD`, worktree registration, and status before editing.
- Preserve unfamiliar tracked and untracked changes.
- Do not reset, discard, clean, stash, move, or overwrite unfamiliar work to make the task convenient.
- Do not reuse a branch or workspace merely because its name looks similar.
- Treat generated files, lockfiles, schemas, migrations, and shared snapshots as potentially shared state.

If existing changes appear to belong to the exact task, verify that identity before resuming them. If ownership remains ambiguous, stop and ask rather than guessing.

## Check semantic overlap

Worktrees prevent checkout collisions, not conceptual conflicts. Compare active work when available and flag overlap involving:

- the same database table, migration sequence, or backfill;
- an API, event, schema, or generated client contract;
- shared authentication, authorization, tenant isolation, billing, or legal behavior;
- a shared component, design token, localization key, route, or lifecycle status;
- release, deployment, environment, or dependency configuration.

Minor file overlap is not automatically blocking. Stop when the overlap can change behavior, ordering, compatibility, data safety, or the agreed outcome.

## Handle conflicts explicitly

When a credible conflict exists:

1. identify both task anchors and affected surfaces;
2. explain the semantic risk, not only the matching filenames;
3. propose ordering, contract separation, rebasing, or scope adjustment;
4. wait for resolution when continuing could corrupt work or violate an earlier decision.

Do not resolve merge or rebase conflicts by mechanically choosing one side. Preserve both tasks' intent and rerun affected gates.

## Keep scope isolated

- Do not cherry-pick, merge, or copy another task's changes without explicit task-level justification.
- Do not opportunistically fix unrelated changes found in the workspace.
- Record a cross-task dependency in the configured operational source rather than duplicating its full details in local memory.
