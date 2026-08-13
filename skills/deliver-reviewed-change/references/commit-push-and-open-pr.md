# Commit, Push, and Open the Pull Request

Apply project Git and pull-request policy only after independent local review passes.

## Create intentional commits

Before commit:

- inspect final status and diff;
- verify task-scoped file ownership;
- rerun any gate invalidated by the final edit;
- choose the configured commit structure and message style.

Stage only task files. Do not include unrelated dirty changes. Verify the created commit and working-tree state.

In aggregate promotion mode, preserve the source branch's existing commits.
Commit only delivery-owned synchronization, conflict resolution, or review
corrections that passed the independent local-review gate while uncommitted.
This authorized commit phase is the first point where newly prepared
synchronization may be committed. Do not squash, reset, rebase, or
otherwise rewrite shared integration history merely to make the promotion look
like an ordinary task delivery.

## Push safely

- Resolve the configured remote and exact task or aggregate delivery source
  branch. A promotion source may be the configured integration branch or the
  safe delivery-owned helper prepared for conflict resolution.
- Fetch or inspect remote state before the first push when policy requires it.
- When the actual remote target already exists, observe and reconcile its
  current head after verifying ownership and ancestry. Never push, forward, or
  commit directly to that target during delivery; it changes only through the
  authorized pull-request merge. Recompute the target-to-candidate comparison
  and rerun any gate or independent-review evidence invalidated by a material
  comparison change or conflict.
- Only when execution prepared the target locally and the remote target is
  still absent, require both its recorded `target_revision_or_absent` evidence
  and verified target-creation source branch, prove that the prepared local
  target still equals that clean creation base without candidate changes, then
  use a provider-supported non-overwriting creation and read back the resulting
  remote revision. If another owner creates the ref during that operation,
  stop and reconcile ownership and ancestry instead of overwriting it.
- Push the delivery source branch without force.
- Limit ordinary delivery pushes to that source branch. Creating a previously
  absent target at its verified creation base is the only target-ref exception
  and must not include candidate changes.
- If the remote branch diverged unexpectedly, stop and inspect ownership instead of overwriting it.
- Verify the remote head after push.

## Create or reconcile one exact pull request

Search by repository, head branch, task ID, and existing task links before creating a PR. Reuse the exact existing PR after verifying identity.

Before creating or accepting the pull request as the GitHub-review boundary,
persist and read back passed pre-PR local-gate evidence bound to the immutable
delivery baseline and candidate head. Pull-request creation closes the active
local-review phase. Preserve its counter and ordered history as provenance. If
an existing pull request cannot prove this evidence, stop with
`pre_pr_local_gate_missing` before GitHub correction, request, or merge; an
accepted blocker or owner override cannot bypass this stop.

Apply configured:

- actual target branch resolved for this exact task or aggregate promotion;
- title and detailed description language;
- task/spec links and close/reference semantics;
- test and review evidence;
- dependencies and merge order;
- draft or ready state.

Do not create a duplicate PR after partial success.

## Establish the PR-review checkpoint

After PR creation or reconciliation:

1. verify PR URL, repository, source head, actual target, state, and current head SHA;
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
