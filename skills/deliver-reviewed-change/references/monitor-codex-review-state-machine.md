# Monitor the Codex Review State Machine

Execute exactly one deterministic decision on each heartbeat.

## Contents

- [Read one atomic evidence snapshot](#read-one-atomic-evidence-snapshot)
- [Evaluate in strict order](#evaluate-in-strict-order)
- [Apply state transitions](#apply-state-transitions)
- [Persist every transition](#persist-every-transition)

## Read one atomic evidence snapshot

For the persisted PR and request:

1. read PR state and current head SHA;
2. read reactions on the exact request comment;
3. read configured top-level comments, formal reviews, and inline comments after the request timestamp;
4. identify reviewer-owned events separately from human or other-bot events;
5. compare event IDs with the persisted last-seen set.

Prefer the bundled inspector for mechanical collection. Do not let its pattern matches replace semantic finding assessment.

## Evaluate in strict order

Apply the first matching state:

1. `pr_terminal`: PR is merged or closed; apply
   [finalize-codex-review-state.md](finalize-codex-review-state.md) with
   `pr_terminal`.
2. `head_mismatch`: current head differs from persisted head; continue only
   when a known local push already initialized a new generation. Otherwise apply
   the terminal procedure with `head_mismatch`.
3. `findings_received`: current-generation reviewer events contain possible findings.
4. `clean`: a current-generation clean verdict exists and there are no new actionable findings.
5. `transient_error`: a current-generation explicit start or access error exists.
6. `in_progress`: an allowed reviewer acknowledgment is present on the exact current request.
7. `not_started`: no reviewer acknowledgment, response, verdict, or error exists.
8. `unclassified_response`: a reviewer response exists but cannot be classified;
   apply the terminal procedure with `unclassified_response`.

Never evaluate silence before checking every response channel. Never let an acknowledgment override a clean verdict or finding.

## Apply state transitions

### `findings_received`

Pause waiting counters and run the finding workflow. Before a code fix, verify
the finding is in scope and that another GitHub correction package is allowed.
A workflow-owned fix may begin only after this exact PR heartbeat persists and
reads back `findings_received`, the reviewed head, and paused automation status.
Keep it paused through the head-changing push so this monitor cannot classify
that controlled transition as an external `head_mismatch`.
A permitted package increments this PR's GitHub counter exactly once; its code
fix and push create a new head-bound generation without resetting that counter.
An evidenced dismissal creates a contextual re-review and persists its semantic
fingerprint in the same PR heartbeat without consuming a correction round.

### `clean`

Treat clean as absorbing and terminal for review. Apply
[finalize-codex-review-state.md](finalize-codex-review-state.md) with `clean`.
Continue to the merge-ready checkpoint and separate authorized CI/merge phase
only when it returns `pause_merge_ready`. Never request another review
for the unchanged head.

### `transient_error`

Apply the configured total request budget. The error consumes the current
attempt. Retry only if another attempt remains; otherwise apply the terminal
procedure with `request_budget_exhausted`.

### `in_progress`

Reset silent count, increment acknowledged-wait count, and persist state. Do not
post a duplicate request while acknowledgment remains. When the configured
acknowledged-without-result budget is exhausted, apply the terminal procedure
with `acknowledged_wait_budget_exhausted`.

### `not_started`

Increment the silent count for the current request. When its threshold is reached:

- if the total budget permits, use both the `Create one request attempt` and
  `Attach and verify the request identity` sections of
  [start-codex-review-cycle.md](start-codex-review-cycle.md);
- otherwise apply the terminal procedure with `request_budget_exhausted`.

### Terminal and unknown states

Map every remaining terminal outcome to one reason from
[finalize-codex-review-state.md](finalize-codex-review-state.md):

- exhausted GitHub correction budget → `github_correction_budget_exhausted`;
- repeated dismissed finding → `repeated_dismissed_finding`;
- lost or contradictory state → `lost_or_contradictory_state`;
- ambiguous repository or PR identity → `pr_identity_ambiguous`.

Apply that procedure exactly once. Do not restate or improvise terminal storage,
deletion, or pause behavior in this state machine.

## Persist every transition

Update:

- current state;
- counters;
- immutable delivery baseline and both correction-round histories;
- request identity;
- last-seen event IDs;
- dismissed-finding fingerprints;
- terminal reason.

Update and read back only this exact PR heartbeat while review is active and
when review becomes terminal. Preserve it paused while its PR remains open. Its
GitHub correction counter, history, dismissed fingerprints, technical counters,
and review state must never be copied to or derived from another PR. If update
or verification fails, apply the terminal procedure with
`lost_or_contradictory_state` rather than running a stateless next cycle.
