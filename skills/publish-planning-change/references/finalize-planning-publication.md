# Finalize planning publication

Establish durable evidence before unlocking implementation.

## Verify canonical publication

After merge, verify:

- the exact pull request is merged into the configured canonical target;
- the merged head is the independently reviewed head or a provider-created
  equivalent whose tree contains the exact reviewed artifacts;
- the canonical branch contains the spec entrypoint and required annexes;
- task identity, links, and content verdict are unchanged;
- the merged revision is recorded and can be resolved later;
- the specification-owner repository base used as future implementation
  authority contains or descends from that revision;
- a component repository with a separate Git history resolves the recorded
  exact-task publication tuple — Task ID, owner repository, canonical spec
  path, and merged revision — and is not required to claim impossible
  cross-repository ancestry.

If any item is uncertain, keep publication incomplete and do not unlock
implementation.

## Update operational state

Ask `manage-project-work` to:

- record the Task ID, specification-owner repository, canonical spec path, and
  merged revision as one resolvable publication tuple on the exact task;
- apply the configured implementation-ready status only after publication
  evidence passes;
- preserve the implementation Issue as open;
- leave parent completion and implementation PR state unchanged.

Keep content verdict, publication state, and tracker status distinct in the
handoff.

## Synchronize and clean safely

1. Synchronize the configured main checkout after merge.
2. Confirm the planning worktree has no unique unmerged content.
3. Remove only the exact task planning worktree and branch allowed by policy.
4. Preserve unfamiliar or dirty work and report a cleanup blocker instead of
   deleting it.
5. Close or update any rolling planning note through `record-project-context`.

## Report the handoff

Report:

- Task ID and title;
- canonical spec path;
- content verdict;
- independent-review result;
- pull request and merged revision;
- publication state;
- operational task status;
- implementation repositories;
- exact next alias or blocker.

Recommend `--execute-task <Task ID>` in a new conversation only when every
configured publication and dependency gate passes.
