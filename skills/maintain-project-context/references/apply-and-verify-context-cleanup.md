# Apply and verify context cleanup

Use this runbook only after the user explicitly approves an exact current manifest.

## Manifest contract

Each entry must contain:

- project-relative source path;
- action: `consolidate`, `archive`, `delete`, or `update_reference`;
- reason and retention evidence;
- canonical replacement or archive destination;
- incoming references to update;
- Git state and recovery source;
- SHA-256 fingerprint captured during preparation;
- post-action validation.

Approval applies only to the listed paths, actions, and destinations. It does not authorize wildcard expansion, recursive cleanup, newly discovered candidates, commits, pushes, pull requests, or external-system changes.

## Revalidate before mutation

1. Confirm the workspace and selected scope.
2. Confirm every path still resolves inside the workspace.
3. Recompute each fingerprint.
4. Recheck Git status and tracked history.
5. Recheck protected-path membership and active-task ownership.
6. Recheck incoming links, maps, configuration, and replacement destinations.
7. Exclude any entry that changed, became ambiguous, or has uncommitted content not covered by the approved recovery plan.

Report excluded entries. Do not silently refresh the manifest and continue.

## Apply in safe order

1. Consolidate durable facts through `record-project-context`.
2. Update exact links, maps, and configured routes included in the manifest.
3. Archive exact approved files to exact approved destinations.
4. Delete exact approved files.
5. Remove a directory only when it is empty, noncanonical, explicitly listed, and no symlink boundary is involved.

Never use wildcards, broad recursive deletion, or a directory-level action to stand in for file-level approval.

## Verify

1. Inspect the resulting diff and unexpected workspace changes.
2. Confirm canonical replacements contain the promoted facts.
3. Confirm links, maps, configuration, and external spec paths still resolve.
4. Rerun the same read-only audit scope.
5. Compare file counts, bytes, duplicate groups, broken references, and remaining candidates.
6. Record only durable maintenance outcomes; do not create a permanent cleanup log by default.
7. Remove the rolling maintenance manifest after its lifecycle closes and no unique unresolved information remains.

Return applied, excluded, and failed entries separately. Stop on uncertainty instead of expanding scope.
