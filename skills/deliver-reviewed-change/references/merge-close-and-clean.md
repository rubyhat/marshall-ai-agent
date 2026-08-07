# Merge, Close, and Clean

Run this sequence only when the authorized endpoint includes full delivery.

## Verify immediately before merge

Confirm:

- exact repository and pull request belong to the current task;
- current head SHA equals either the clean reviewed head or the exact
  deterministic-gate head of a verified documentation-only fast path;
- for a documentation-only fast path, current base SHA equals the validated
  base SHA; otherwise classification and deterministic validation have been
  rerun against the current head/base pair;
- for ordinary delivery, no new actionable review event appeared after the
  clean verdict;
- for a documentation-only fast path, the complete current PR diff still
  satisfies its configured roots, file types, and exclusions;
- an automatic ready-spec PR uses reference-only Issue linkage;
- for ordinary delivery, required CI and branch-protection checks pass, or a
  configured external-provider exception is evidenced and the merge can
  proceed without bypassing provider-enforced rules;
- for a documentation-only fast path, absence of reported checks or
  branch-protection evidence is allowed, while every reported check for the
  exact head is terminal and non-failing and the provider permits an ordinary
  merge without bypass;
- dependencies and multi-repository merge order are satisfied;
- pull request is open and mergeable;
- merge authority matches project policy;
- review heartbeat is already deleted or was never created for the
  documentation-only fast path.

If a required or reported check is pending, do not reuse the review heartbeat.
Continue synchronously or create a separate check/merge monitor only when the
authorized endpoint or an explicit request permits it.

## Merge the exact pull request

Use the configured merge method. Do not select another open PR by inference. Do not force merge, bypass protection, or merge stale code.

Verify the resulting merge commit and PR state from the provider.

## Close operational state

Through `manage-project-work`:

- after automatic ready-spec delivery, keep the task Issue open and apply only
  the configured execution-ready status;
- otherwise apply the configured done status and close the exact task Issue
  when policy requires it;
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
