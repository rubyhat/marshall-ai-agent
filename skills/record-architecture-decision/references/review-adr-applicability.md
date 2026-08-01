# Review ADR applicability

Use this reference before requiring a current task or implementation to conform
to an ADR, and whenever new evidence may have invalidated an accepted decision.

## Inspect bounded evidence

Read only:

- the exact ADR and its supersession links;
- the owning current architecture section;
- the exact task outcome or specification;
- current code, schema, or runtime configuration needed to verify the conflict;
- the new requirement or evidence that triggered review.

Do not load an entire ADR library, architecture history, or project memory for
completeness.

## Test applicability

Check:

1. **Status** — the ADR is accepted and has not been superseded, deprecated, or
   rejected.
2. **Scope** — the affected component, domain, lifecycle, and decision type are
   covered.
3. **Assumptions** — recorded scale, ownership, technology, product, security,
   regulatory, operational, or cost premises still hold.
4. **Decision drivers** — their relative importance has not changed
   materially.
5. **Review triggers** — none has fired, or every fired trigger was already
   reviewed with durable evidence.
6. **Current architecture** — the canonical current-state source still treats
   the decision as active.
7. **Implementation evidence** — code divergence is classified as a bug,
   accidental drift, partial rollout, explicit exception, or accepted new
   direction rather than assumed to be authoritative.
8. **Task pressure** — the task is not the latest of repeated workarounds or
   exceptions indicating that the decision's cost has materially changed.

## Return one verdict

### `ADR applicable`

Use when status and scope match, assumptions and drivers remain valid, and no
material review trigger is unresolved. Require the task to respect the ADR or
return the conflicting proposal to shaping.

### `ADR review required`

Use when credible evidence shows changed assumptions, new material risks,
changed boundaries, repeated exceptions, unacceptable consequences, or a fired
review trigger. Stop dependent specification or implementation until shaping
accepts either the existing or a replacement decision.

### `ADR not applicable`

Use when the task is outside the ADR's explicit scope or a linked replacement
clearly owns the decision. State the applicable source if one exists.

### `ADR applicability unclear`

Use when status, scope, authority, transition state, or code drift cannot be
resolved from current evidence. Ask only the question or request only the
bounded discovery needed to distinguish the cases.

## Avoid both failure modes

Do not weaken an applicable ADR because following it is inconvenient. Do not
force a task to conform when the ADR's premises may be obsolete. Treat code as
runtime evidence and ADR as decision evidence; neither silently overrides the
other when they conflict.
