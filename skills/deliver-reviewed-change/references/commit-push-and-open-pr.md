# Commit, Push, and Open the Pull Request

Apply project Git and pull-request policy only after independent local review passes.

## Create intentional commits

Before commit:

- inspect final status and diff;
- verify task-scoped file ownership;
- rerun any gate invalidated by the final edit;
- choose the configured commit structure and message style.

Stage only task files. Do not include unrelated dirty changes. Verify the created commit and working-tree state.

## Push safely

- Resolve the configured remote and exact task branch.
- Fetch or inspect remote state before the first push when policy requires it.
- Push the task branch without force.
- If the remote branch diverged unexpectedly, stop and inspect ownership instead of overwriting it.
- Verify the remote head after push.

## Create or reconcile one exact pull request

Search by repository, head branch, task ID, and existing task links before creating a PR. Reuse the exact existing PR after verifying identity.

Apply configured:

- base branch;
- title and detailed description language;
- task/spec links and close/reference semantics;
- test and review evidence;
- dependencies and merge order;
- draft or ready state.

Do not create a duplicate PR after partial success.

## Establish the PR-review checkpoint

After PR creation or reconciliation:

1. verify PR URL, repository, head, base, state, and current head SHA;
2. link it through `manage-project-work`;
3. apply the configured PR-review status;
4. read back Issue, Project, and PR state;
5. report any partial mutation honestly.

Stop when the authorized endpoint is PR creation only. Do not start external review or merge without the corresponding endpoint authority.

## Handle multi-repository delivery

Use one PR per configured repository task unless project policy says otherwise.
Preserve dependency order and give every PR its own GitHub correction counter,
ordered history, technical request state, and heartbeat. The first generation
of each PR starts its GitHub counter at zero; later heads of that same PR
preserve it. Never synchronize counters between PRs or let a clean verdict on
one PR complete another PR's review generation.
