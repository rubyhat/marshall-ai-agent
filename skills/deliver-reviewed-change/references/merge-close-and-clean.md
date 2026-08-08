# Merge, Close, and Clean

Run this sequence only when the authorized endpoint includes full delivery.

## Verify immediately before merge

Confirm:

- exact repository and pull request belong to the current task;
- current head SHA equals the clean reviewed head;
- no new actionable review event appeared after the clean verdict;
- required CI and branch-protection checks pass, or a configured external-provider exception is evidenced and the merge can proceed without bypassing branch protection;
- dependencies and multi-repository merge order are satisfied;
- pull request is open and mergeable;
- merge authority matches project policy;
- [finalize-codex-review-state.md](finalize-codex-review-state.md) returned
  `archive_delete_merge_ready` for the exact current PR.

If CI is pending, do not reuse the review heartbeat. Continue synchronously or create a separate CI/merge monitor only when the authorized endpoint or an explicit request permits it.

## Merge the exact pull request

Use the configured merge method. Do not select another open PR by inference. Do not force merge, bypass protection, or merge stale code.

Verify the resulting merge commit and PR state from the provider.

## Close operational state

Through `manage-project-work`:

- apply the configured done status;
- close the exact implementation Issue when policy requires it;
- reconcile parent state only from acceptance and remaining scope, not child count alone;
- read back Issue and Project state.

Do not close unrelated or parent work automatically.

## Synchronize safely

Fetch and update configured local default branches to the merge commit. If unrelated dirty changes prevent safe synchronization:

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

Then remove task worktrees and local task branches only when:

- merge is verified;
- no unique uncommitted changes remain;
- default branch or remote refs establish recoverability;
- no other task owns the workspace or branch;
- project cleanup policy permits removal.

Report merge, task closure, sync, recording, and cleanup independently. A partial completion must remain visible.
