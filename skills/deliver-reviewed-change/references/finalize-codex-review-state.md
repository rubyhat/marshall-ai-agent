# Finalize Codex Review State

Use this procedure for every terminal GitHub review exit. Other runbooks must
select a `terminal_reason` and call this procedure instead of restating pause,
reactivation, or deletion rules.

## Contents

- [Apply the terminal matrix](#apply-the-terminal-matrix)
- [Prove state before mutation](#prove-state-before-mutation)
- [Pause an open pull request](#pause-an-open-pull-request)
- [Reactivate only the same pull request](#reactivate-only-the-same-pull-request)
- [Delete only after pull-request closure](#delete-only-after-pull-request-closure)

## Apply the terminal matrix

Use the exact disposition for the selected reason:

```json
{
  "pr_terminal": {
    "on_provable": "delete_report",
    "on_unprovable": "pause_report"
  },
  "clean": {
    "on_provable": "pause_merge_ready",
    "on_unprovable": "pause_report"
  },
  "github_correction_budget_exhausted": {
    "on_provable": "pause_cycle_analysis",
    "on_unprovable": "pause_report"
  },
  "request_budget_exhausted": {
    "on_provable": "pause_report",
    "on_unprovable": "pause_report"
  },
  "acknowledged_wait_budget_exhausted": {
    "on_provable": "pause_report",
    "on_unprovable": "pause_report"
  },
  "repeated_dismissed_finding": {
    "on_provable": "pause_report",
    "on_unprovable": "pause_report"
  },
  "scope_or_contract_stop": {
    "on_provable": "pause_owner_handoff",
    "on_unprovable": "pause_report"
  },
  "unclassified_response": {
    "on_provable": "pause_report",
    "on_unprovable": "pause_report"
  },
  "head_mismatch": {
    "on_provable": "pause_report",
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
  "heartbeat_persistence_failure": {
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

When the exact heartbeat is addressable but its required state is unprovable,
preserve it and pause it without fabricating missing fields. When even the PR
identity is ambiguous, do not mutate or delete any candidate heartbeat.

## Pause an open pull request

Every terminal review outcome while the PR remains open uses `pause_*`:

1. persist the terminal reason in the exact PR heartbeat;
2. persist `terminal_head_sha` separately from the generation's `head_sha`;
3. set the heartbeat state to terminal and its automation status to paused;
4. read back identity, complete state, terminal reason, observed terminal head,
   and paused status;
5. on a write or readback failure, use `heartbeat_persistence_failure`, retain
   the addressable heartbeat, and report the uncertainty;
6. return the matrix suffix action: report, merge-ready, cycle analysis, or
   owning-workflow handoff.

Do not copy terminal GitHub state into retained task state. Do not create a
terminal snapshot. Do not delete the heartbeat while the PR remains open.

## Reactivate only the same pull request

A later authorized continuation of the same open PR must read the same paused
heartbeat. If the current head still equals `terminal_head_sha`, return the
recorded terminal outcome and keep the heartbeat paused without another review
request. If the same PR has a later head and current authority permits review,
reactivate that heartbeat, preserve its GitHub correction history and
fingerprints, refresh only authoritative local correction state after baseline
verification, initialize a new head-bound generation, and read back the active
state before any request.

Never use a paused heartbeat to initialize, constrain, or complete another PR.

## Delete only after pull-request closure

Use `delete_report` only for `pr_terminal` after provider evidence proves that
the exact PR is merged or closed:

1. persist and read back `pr_terminal`, the observed `terminal_head_sha`, and
   the provider terminal state in the exact heartbeat;
2. verify the repository and immutable PR identity again;
3. delete that heartbeat and verify its absence;
4. report the proven PR outcome and cleanup result.

If persistence, readback, identity, or provider state is uncertain, return
`pause_report` and do not delete anything. No review-terminal outcome other
than proven merge or close may delete the exact PR heartbeat.
