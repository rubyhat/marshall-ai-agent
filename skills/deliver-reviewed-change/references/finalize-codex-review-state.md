# Finalize Codex Review State

Use this procedure for every terminal GitHub review exit. Other runbooks must
select a `terminal_reason` and call this procedure instead of restating snapshot,
deletion, or pause rules.

## Apply the terminal matrix

Use the exact disposition for the selected reason:

```json
{
  "pr_terminal": {
    "on_provable": "archive_delete_report",
    "on_unprovable": "pause_report"
  },
  "clean": {
    "on_provable": "archive_delete_merge_ready",
    "on_unprovable": "pause_report"
  },
  "github_correction_budget_exhausted": {
    "on_provable": "archive_delete_cycle_analysis",
    "on_unprovable": "pause_report"
  },
  "request_budget_exhausted": {
    "on_provable": "archive_delete_report",
    "on_unprovable": "pause_report"
  },
  "acknowledged_wait_budget_exhausted": {
    "on_provable": "archive_delete_report",
    "on_unprovable": "pause_report"
  },
  "repeated_dismissed_finding": {
    "on_provable": "archive_delete_report",
    "on_unprovable": "pause_report"
  },
  "scope_or_contract_stop": {
    "on_provable": "archive_delete_owner_handoff",
    "on_unprovable": "pause_report"
  },
  "unclassified_response": {
    "on_provable": "archive_delete_report",
    "on_unprovable": "pause_report"
  },
  "head_mismatch": {
    "on_provable": "archive_delete_report",
    "on_unprovable": "pause_report"
  },
  "lost_or_contradictory_state": {
    "on_provable": "pause_report",
    "on_unprovable": "pause_report"
  },
  "pr_identity_ambiguous": {
    "on_provable": "pause_report",
    "on_unprovable": "pause_report"
  },
  "snapshot_persistence_failure": {
    "on_provable": "pause_report",
    "on_unprovable": "pause_report"
  }
}
```

## Prove state before mutation

Require the exact repository and immutable PR identity, complete delivery
baseline, local and this-PR GitHub counters and ordered histories, current or
last-reviewed generation head, the distinct `terminal_head_sha` observed from
the PR in the atomic terminal evidence snapshot, generation, dismissed
fingerprints, last-seen event IDs, and terminal reason. For `head_mismatch`, the
generation `head_sha` and observed `terminal_head_sha` are expected to differ.
Treat missing, contradictory, unwriteable, or unreadable required state as
unprovable.

For `pause_report`, pause the addressable heartbeat, do not create or overwrite
a terminal snapshot, do not delete the heartbeat, and report once.

## Archive and delete provable state

For an `archive_delete_*` disposition:

1. persist and read back the terminal reason in the active heartbeat;
2. persist and read back `terminal_head_sha` separately from the generation's
   `head_sha`;
3. store one terminal snapshot in retained current-task state under the exact
   repository plus immutable PR identity;
4. include the complete proven state and a content fingerprint;
5. read back and compare the exact key, identity, fields, and fingerprint;
6. on any failure, switch to `snapshot_persistence_failure`;
7. only after successful readback, delete the heartbeat and verify its absence;
8. return the matrix suffix action: report, merge-ready, cycle analysis, or
   owning-workflow handoff.

The snapshot replaces only that PR's deleted heartbeat. A later head of the
same PR may resume from it. Never use it to seed, limit, complete, or derive
state for another PR, and never create repository-local runtime state for this
procedure.
