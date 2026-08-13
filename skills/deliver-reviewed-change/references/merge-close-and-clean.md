# Merge, Close, and Clean

Run this sequence only when the authorized endpoint includes full delivery.

## Verify immediately before merge

Confirm:

- exact repository and pull request belong to the current task or aggregate result;
- current head SHA equals the clean reviewed head;
- no new actionable review event appeared after the clean verdict;
- required CI and branch-protection checks pass, or a configured external-provider exception is evidenced and the merge can proceed without bypassing branch protection;
- dependencies and multi-repository merge order are satisfied;
- pull request is open and mergeable;
- merge authority matches project policy;
- for aggregate promotion, the current fetched destination revision for the
  repository owned by the exact pull request equals that repository's
  pre-review destination revision bound to the clean generation. Previously
  completed repositories are outside this PR's drift gate; each later PR checks
  its own repository entry. If the current PR's destination advanced, stop
  before merge, integrate the new destination on the delivery-owned source or
  helper, recompute the candidate manifest, and rerun every invalidated local
  review, GitHub Codex review, CI, and mergeability gate;
- [finalize-codex-review-state.md](finalize-codex-review-state.md) returned
  `pause_merge_ready` for the exact current PR and its heartbeat remains paused.

If CI is pending, do not reactivate the review heartbeat. Continue synchronously
or create a separate CI/merge monitor only when the authorized endpoint or an
explicit request permits it.

## Merge the exact pull request

Use the configured merge method. Do not select another open PR by inference. Do not force merge, bypass protection, or merge stale code.

Verify the resulting merge commit and PR state from the provider. Then apply
[finalize-codex-review-state.md](finalize-codex-review-state.md) with
`pr_terminal`; continue cleanup only after it returns `delete_report` or report
the paused-heartbeat cleanup blocker without deleting uncertain state.

## Close operational state

Through `manage-project-work`:

- for ordinary task delivery, apply the configured done status and close the
  exact implementation Issue when policy requires it;
- after each repository PR in aggregate promotion, retain per-PR provider
  verification, synchronization, recording, and safe cleanup, but keep the
  aggregate or Epic anchor active while any selected repository route remains
  unsatisfied or unmerged;
- only after every selected repository route is proven satisfied and every
  required repository PR is merged, reconcile the aggregate or Epic anchor
  from project-owned readiness and the achieved outcome, apply its configured
  done status, and close it when policy requires. Child count alone is not
  completion evidence;
- preserve completed child-task state and do not close unrelated tasks;
- read back Issue and Project state.

Do not close unrelated or parent work automatically.

## Synchronize safely

Fetch and update the actual merged target branch to the merge commit. The target
may be an intermediate integration branch for task delivery or the repository
default branch for aggregate promotion. Do not silently substitute the default
branch. If unrelated dirty changes prevent safe synchronization:

- preserve them;
- record the exact blocker;
- continue only with cleanup steps proven safe.

Do not reset, discard, or overwrite user work.

## Close recording and cleanup

Run the `record-project-context` closing cycle:

1. promote durable findings to canonical owners;
2. update any required implementation report;
3. remove transient content from the rolling task note;
4. delete the note only when no unique unresolved state remains.

Then remove delivery-owned worktrees and local task branches only when:

- merge is verified;
- no unique uncommitted changes remain;
- default branch or remote refs establish recoverability;
- no other task owns the workspace or branch;
- project cleanup policy permits removal.

Do not remove an aggregate or integration source branch merely because one
child task merged into it. Remove or retain it only according to explicit
project lifecycle policy after the aggregate delivery is proven complete.

Report merge, task closure, sync, recording, and cleanup independently. A partial completion must remain visible.
