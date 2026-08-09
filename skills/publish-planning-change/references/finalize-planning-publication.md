# Finalize planning publication

Establish durable evidence before unlocking implementation.

## Verify canonical publication

After merge, verify:

- the exact pull request is merged into the configured canonical target;
- the merged head is the independently reviewed head or a provider-created
  equivalent whose tree contains the exact reviewed artifacts;
- the bound reviewed-head revision and tree OID resolve, and its complete
  publication-package path/blob-OID manifest equals both the captured clean-
  review manifest and the package manifest at the merged revision;
- the canonical branch contains the spec entrypoint and required annexes;
- task identity, links, and content verdict are unchanged;
- the clean-review record has a resolvable reviewer run/evidence identifier,
  model, effort, completion time, terminal clean verdict, review target kind,
  canonical base revision, binding method, current capture-contract revision,
  publication-attempt ID, normalized-result SHA-256, and complete matched
  reviewer session set;
- the merged revision and tree OID are recorded and can be resolved later;
- the specification-owner repository base used as future implementation
  authority contains or descends from that revision;
- a component repository with a separate Git history resolves the recorded
  exact-task reviewed-publication record described below and is not required to
  claim impossible cross-repository ancestry.

If any item is uncertain, keep publication incomplete and do not unlock
implementation.

## Update operational state

Ask `manage-project-work` to record one exact-task
`reviewed_canonical_publication` record containing:

- Task ID, specification-owner repository, canonical spec entrypoint, pull
  request URL, merged revision, and merged tree OID;
- bound reviewed-head revision and tree OID;
- the complete sorted reviewed package manifest with every project-relative
  path and blob OID, preserving each reviewed deletion as its base-relative
  `deleted:<base-blob-oid>` marker;
- reviewer run/evidence identifier, model, effort, completion time, terminal
  clean verdict, review target kind, canonical base revision, and binding
  method (`direct_committed_base_diff` or
  `verified_uncommitted_manifest_equivalence`);
- review capture-contract revision, publication-attempt ID, normalized-result
  SHA-256, and the complete matched reviewer session/event identities from the
  authoritative runner result;
- explicit `reviewed_package_manifest_equals_merged: true` verification after
  comparing the reviewed manifest with the package at the merged revision.

Then ask `manage-project-work` to:

- reread the persisted record and require exact equality for every identity,
  revision, tree, manifest, and clean-review field before returning success;
- apply the configured implementation-ready status only after publication
  evidence passes;
- preserve the implementation Issue as open;
- leave parent completion and implementation PR state unchanged.

Keep content verdict, publication state, and tracker status distinct in the
handoff.

## Synchronize and clean safely

1. Synchronize the configured main checkout after merge.
2. Confirm the complete reviewed-publication record was persisted and reread.
3. Confirm the planning worktree has no unique unmerged content.
4. Remove only the exact task planning worktree and branch allowed by policy.
5. Preserve unfamiliar or dirty work and report a cleanup blocker instead of
   deleting it.
6. Close or update any rolling planning note through `record-project-context`.

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
