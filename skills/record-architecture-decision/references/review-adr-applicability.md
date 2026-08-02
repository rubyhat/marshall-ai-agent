# Review ADR Applicability

Use this review before requiring shaping, specification, or implementation to
conform to an existing ADR.

## Check the decision

1. Resolve the exact ADR and its semantic lifecycle state.
2. Confirm that it covers the affected product, repository, component, domain,
   actor, and change type.
3. Compare its assumptions and decision drivers with current evidence.
4. Inspect its explicit review triggers.
5. Check whether architecture or code drifted from the recorded decision.
6. Identify new security, privacy, tenancy, legal, scale, reliability, cost, or
   operational constraints.
7. Distinguish inconvenience from evidence that the decision no longer fits.

## Interpret the result

- `applicable`: accepted, in scope, and no material premise changed;
- `not applicable`: an accepted decision is outside the current work's scope,
  or the ADR is rejected, deprecated, or superseded and therefore is not an
  active constraint;
- `review required`: an in-scope proposed ADR leaves a decision unresolved, or
  an accepted ADR's premise, driver, consequence, or trigger materially changed
  and the decision owner must reconsider it;
- `unclear`: identity, status, scope, evidence, or current architecture cannot
  be reconciled safely.

For a superseded ADR, follow its replacement and review that active record
instead of treating the old decision as a constraint. For a deprecated ADR,
follow its recorded downstream guidance; if that guidance or status is
irreconcilable, return `unclear`. Keep rejected ADRs only as historical
rationale.

An accepted status alone never proves applicability. A conflicting task never
proves that the ADR is obsolete. For `review required` or `unclear`, stop the
dependent decision boundary and state whether the likely issue is an unresolved
proposal, task conflict, architecture drift, incomplete migration, or outdated
ADR.
