# Supersede an architecture decision

Use this reference to preserve accepted decision history while changing the
direction that should govern future work.

## Distinguish clarification from replacement

Clarify an accepted ADR in place only for:

- spelling or formatting corrections;
- more precise wording that does not change obligations;
- provenance, review date, or canonical links;
- an explicit note that implementation is transitional, when that was already
  true and does not alter the decision.

Create a new ADR when changing:

- the selected option;
- scope or affected boundaries materially;
- required invariants or exceptions;
- decision drivers or accepted trade-offs;
- compatibility, migration, security, privacy, reliability, or operational
  posture;
- consequences that would cause future work to choose differently.

## Apply the supersession sequence

1. Keep the old accepted ADR's original context, options, decision, and
   consequences intact.
2. If the configured proposed state is enabled, create a new proposed ADR that
   names the old ADR and explains the new evidence. If it is disabled, keep the
   unresolved replacement in the configured shaping owner without persisting
   an ADR yet.
3. Resolve the new decision through the configured shaping and authority gate.
4. When accepted, create or update the new ADR with the configured accepted
   label and add `Supersedes`.
5. Set the old ADR to the configured superseded label and add `Superseded by`.
6. Update the ADR index atomically with both status changes.
7. Link affected architecture and task artifacts without copying the complete
   rationale.
8. Track migration and implementation progress in tasks, specs, and pull
   requests rather than in either ADR.

Do not mark the old ADR superseded before the replacement is accepted. Do not
claim that the new architecture is current until its owning current-state
source verifies the transition.

## Handle deprecation and rejection

Resolve an already persisted proposal in place:

- when accepted by the configured authority, keep its ADR ID, set the accepted
  label, complete the decision date and authority, and update its index entry;
- when rejected by the configured authority, keep its ADR ID, set the rejected
  label, preserve the explicit rejection outcome and rationale, and update its
  index entry;
- never create a second ADR merely to represent the resolved lifecycle state of
  the same proposal.

- Use the configured deprecated label when the decision should not guide new
  work but no accepted replacement exists. Record the risk and next decision
  owner.
- Use the configured rejected label for a proposed option whose durable
  rejection rationale prevents costly reopening.
- Do not use the superseded state merely because one task received a bounded
  exception.

If a temporary exception is allowed, record its owner, scope, reason, expiry or
review trigger, and remediation task in the project-configured owner. Escalate
it to an ADR only when it changes the architecture materially.
