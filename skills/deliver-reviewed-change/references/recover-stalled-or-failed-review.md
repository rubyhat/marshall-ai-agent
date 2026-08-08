# Recover a Stalled or Failed Review

Use separate counters for silence, acknowledged waiting, and explicit errors. Never collapse them into a generic “no new comments” state.

## Silent start failure

For each exact request:

1. wait one configured heartbeat;
2. if no acknowledgment or reviewer response exists, increment the silent count;
3. repeat until the per-request silent threshold;
4. if another request attempt remains, use both the `Create one request attempt`
   and `Attach and verify the request identity` sections of
   [start-codex-review-cycle.md](start-codex-review-cycle.md);
5. if the total request budget is exhausted, apply
   [finalize-codex-review-state.md](finalize-codex-review-state.md) with
   `request_budget_exhausted`.

Read both limits from project configuration. Apply them per exact request and per current head SHA; do not invent an implicit extra retry.

Technical request attempts are independent from review-driven correction
rounds. A retry caused by silence, acknowledgment without a result, or an
explicit error must not consume or reset either correction counter.

## Acknowledged but stalled

An allowed reviewer reaction on the exact request proves acknowledgment, not completion.

- reset the silent count;
- increment the acknowledged-wait count on each result-free heartbeat;
- do not post another request while the acknowledgment persists;
- after the configured acknowledged-without-result budget, apply the terminal
  procedure with `acknowledged_wait_budget_exhausted`.

Read the acknowledged-wait limit and cadence from project configuration. An acknowledgment must never create an unbounded wait loop.

## Explicit transient error

An explicit reviewer start, clone, access, or retry-later error consumes the current request attempt.

- if another attempt remains, use both the `Create one request attempt` and
  `Attach and verify the request identity` sections of
  [start-codex-review-cycle.md](start-codex-review-cycle.md);
- if the current request is the final allowed attempt, apply the terminal
  procedure with `request_budget_exhausted`;
- a new code push and head SHA create a fresh generation and request budget.

Do not retain a separate hidden error retry loop outside the configured total request budget.

## Lost or contradictory state

Stop when:

- the automation state cannot be updated or reread;
- current head changed without a new generation;
- the immutable delivery baseline, either correction counter, or ordered
  correction history cannot be proven;
- request comment cannot be found;
- reviewer actor cannot be distinguished safely;
- clean verdict and possible findings cannot be reconciled;
- PR identity or merge target becomes ambiguous.

Classify missing or contradictory baseline, counters, histories, or writable
state as `lost_or_contradictory_state`. Classify ambiguous repository or PR
identity as `pr_identity_ambiguous`. Apply
[finalize-codex-review-state.md](finalize-codex-review-state.md) with the exact
reason. Do not restate terminal storage, deletion, or pause behavior here.
