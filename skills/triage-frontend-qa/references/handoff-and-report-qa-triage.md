# Handoff and Report Frontend QA Triage

End triage at the correct workflow boundary.

## Hand off a confirmed actionable defect

Require:

- direct confirmation of the failing behavior;
- a defensible expected behavior;
- reproducible steps or equivalent decisive evidence;
- sufficiently resolved owner and task boundary;
- priority, risk, dependency order, and specification depth;
- applicable error and recovery contract;
- redacted evidence safe for the destination.

Then:

1. Invoke the configured task-management workflow idempotently to find, create, or reconcile the exact Task ID, Issue, hierarchy, Project item, and fields.
2. Invoke the configured specification workflow with the normalized defect, evidence, scope, dependencies, non-goals, and required depth.
3. Link or summarize evidence; do not duplicate a separate QA report by default.
4. Report the exact artifacts created or reused.

The confirmed and sufficiently localized result supplies artifact handoff authority when project policy declares these artifacts mandatory. Do not ask the user to approve the same Issue/spec creation again.

## Preserve the implementation boundary

Continue to implementation only when:

- the user explicitly requested a fix or implementation for this exact defect;
- the required task identity and specification exist;
- the specification has the configured implementation-ready verdict;
- no unresolved ownership, safety, or access blocker remains.

The request may come in the original report or later. Preserve it without asking twice. Locality, low effort, high urgency, or an obvious patch never substitutes for explicit implementation authority.

## Handle non-confirmed outcomes

- `confirmed but ownership unresolved`: report the exact ownership decision or evidence still needed; do not create a confirmed implementation task automatically.
- `not reproduced`: report attempts, environment, evidence, and the smallest blocking questions; do not create a confirmed bug artifact.
- `expected behavior`: explain the governing contract and offer enhancement shaping; do not relabel it as a bug.
- `environment or test-data issue`: identify the responsible setup boundary and safe corrective owner; create a tracked task only under explicit or configured authority for that exact confirmed setup defect.
- `blocked by access or environment`: state what is unavailable, what fallback was attempted, and what input or environment change would unblock triage.
- `security or privacy escalation`: use the restricted configured path and omit sensitive details from ordinary Issues or chat.

A no-repro Discovery item or an enhancement Issue requires explicit user agreement unless project policy supplies separate authority. Do not interpret “track bugs if confirmed” as approval to track an unconfirmed observation.

## Return a concise result packet

Report:

- primary result and confidence;
- expected and actual behavior;
- reproduction and environment;
- decisive evidence and localization;
- priority, risk, owner, dependencies, and specification depth;
- safety or access constraints;
- artifact links or the reason none were created;
- whether implementation is authorized;
- exact next action or blocking question.

Stop once the result and owner are established. Do not poll, monitor, implement, or start unrelated QA after the handoff.
