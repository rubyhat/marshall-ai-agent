# Monitor the Codex Review State Machine

Execute exactly one deterministic decision on each heartbeat.

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

1. `pr_terminal`: PR is merged or closed; delete the heartbeat.
2. `head_mismatch`: current head differs from persisted head; stop unless a known local push already initialized a new generation.
3. `findings_received`: current-generation reviewer events contain possible findings.
4. `clean`: a current-generation clean verdict exists and there are no new actionable findings.
5. `transient_error`: a current-generation explicit start or access error exists.
6. `in_progress`: an allowed reviewer acknowledgment is present on the exact current request.
7. `not_started`: no reviewer acknowledgment, response, verdict, or error exists.
8. `unclassified_response`: a reviewer response exists but cannot be classified; stop and report it.

Never evaluate silence before checking every response channel. Never let an acknowledgment override a clean verdict or finding.

## Apply state transitions

### `findings_received`

Pause waiting counters and run the finding workflow. Before a code fix, verify
the finding is in scope and that another GitHub correction package is allowed.
A permitted package increments this PR's GitHub counter exactly once; its code
fix and push create a new head-bound generation without resetting that counter.
An evidenced dismissal creates a contextual re-review and persists its semantic
fingerprint in the same PR heartbeat without consuming a correction round.

### `clean`

Treat clean as absorbing and terminal for review:

- persist `clean`;
- delete the review heartbeat immediately;
- do not request another review for the unchanged head;
- apply the merge-ready checkpoint;
- continue only through a separate authorized CI/merge phase.

### `transient_error`

Apply the configured total request budget. The error consumes the current attempt. Retry only if another attempt remains; otherwise delete the heartbeat and report failure.

### `in_progress`

Reset silent count, increment acknowledged-wait count, and persist state. Do not post a duplicate request while acknowledgment remains. Stop after the configured acknowledged-without-result budget.

### `not_started`

Increment the silent count for the current request. When its threshold is reached:

- create the next request attempt if the total budget permits;
- otherwise delete the heartbeat and report that review never started.

### Terminal and unknown states

Delete the heartbeat and report once for terminal PR state, exhausted budgets, repeated dismissed finding, lost state, or unclassified reviewer response.

## Persist every transition

Update:

- current state;
- counters;
- immutable delivery baseline and both correction-round histories;
- request identity;
- last-seen event IDs;
- dismissed-finding fingerprints;
- terminal reason.

Update and read back only this exact PR heartbeat. Its GitHub correction
counter, history, dismissed fingerprints, technical counters, and review state
must never be copied to or derived from another PR. If update or verification
fails, stop rather than running a stateless next cycle.
