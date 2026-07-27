# Recover a Stalled or Failed Review

Use separate counters for silence, acknowledged waiting, and explicit errors. Never collapse them into a generic “no new comments” state.

## Silent start failure

For each exact request:

1. wait one configured heartbeat;
2. if no acknowledgment or reviewer response exists, increment the silent count;
3. repeat until the per-request silent threshold;
4. if another request attempt remains, post it and reset per-request counters;
5. if the total request budget is exhausted, delete the heartbeat and report that review never started.

Read both limits from project configuration. Apply them per exact request and per current head SHA; do not invent an implicit extra retry.

## Acknowledged but stalled

An allowed reviewer reaction on the exact request proves acknowledgment, not completion.

- reset the silent count;
- increment the acknowledged-wait count on each result-free heartbeat;
- do not post another request while the acknowledgment persists;
- stop after the configured acknowledged-without-result budget.

Read the acknowledged-wait limit and cadence from project configuration. An acknowledgment must never create an unbounded wait loop.

## Explicit transient error

An explicit reviewer start, clone, access, or retry-later error consumes the current request attempt.

- if another attempt remains, post a new request and reset per-request counters;
- if the current request is the final allowed attempt, delete the heartbeat and report the exact error;
- a new code push and head SHA create a fresh generation and request budget.

Do not retain a separate hidden error retry loop outside the configured total request budget.

## Lost or contradictory state

Stop when:

- the automation state cannot be updated or reread;
- current head changed without a new generation;
- request comment cannot be found;
- reviewer actor cannot be distinguished safely;
- clean verdict and possible findings cannot be reconciled;
- the same dismissed finding repeats;
- PR identity or merge target becomes ambiguous.

Delete or pause the heartbeat before reporting. Never leave an unattended recurring monitor after declaring a stop.
