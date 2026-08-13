# Create Multi-Repository Worktrees

Read this reference only when the exact implementation scope modifies more than one repository.

## Resolve task ownership

Determine whether project policy represents the work as:

- one multi-repository implementation task; or
- a coordination item with repo-specific sibling implementation tasks.

Do not use a parent coordination item as a substitute for required implementation-task identities. Resolve the task, specification, status, and branch owner for each repository.

## Build one bounded workspace

Use one configured task-workspace root with one worktree per modified repository. Keep repository names and paths from project configuration.

For each worktree:

- create or reuse its own task branch;
- resolve and use that repository's project- or task-defined intended base and
  pull-request target, falling back to its default branch for both;
- preserve its independent status and quality gates;
- map it to the exact owning implementation task when repo-specific task identities are required.

Do not create worktrees for repositories that will only be read.

## Define dependency order

Before editing, state:

- contract owner;
- provider and consumer repositories;
- implementation order;
- compatibility strategy while changes are not yet merged together;
- generated-client or schema synchronization needs;
- which gates verify cross-repository behavior.

Prefer backward-compatible contracts when repositories deploy independently. Do not rely on synchronized merge or deployment unless the specification and project policy explicitly require it.

## Keep state separate

Track per repository:

- task ID when distinct;
- branch and worktree path;
- base commit;
- intended base and pull-request target;
- routing source, exact target revision or explicit absence, and separate
  verified base- and target-creation source branches or not-applicable values;
- changed surfaces;
- gate results;
- blockers and dependency state.

Do not commit, push, or open pull requests from this skill. Preserve the repository mapping for the delivery handoff.

## Verify the workspace

After setup, confirm:

- every modified repository has exactly one expected task worktree;
- no task branch is checked out elsewhere;
- no read-only repository was added unnecessarily;
- branch names and task IDs are not accidentally reused;
- each repository's base and target match its own resolved routing rather than
  a branch inferred from another repository;
- dependency order still matches the specification;
- root or coordination files are included only when they are actual deliverables.
