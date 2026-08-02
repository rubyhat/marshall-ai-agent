# Decide Whether an ADR Is Needed

Use an ADR when future work needs to recover why a material architecture choice
was made, not merely what a current task will implement.

## Strong ADR signals

- ownership or dependency boundaries between components or repositories;
- durable API, event, data, security, privacy, tenancy, deployment, or
  compatibility direction;
- selection between credible alternatives with lasting trade-offs;
- a constraint that will govern multiple tasks or teams;
- acceptance of meaningful operational cost, risk, or limitation;
- replacement of an existing accepted architecture decision.

## Usually not an ADR

- a routine framework-native implementation detail;
- a local refactor or easily reversible choice;
- task scope, acceptance criteria, priority, or delivery status;
- current architecture description without a decision to explain;
- a runbook, incident record, research report, or temporary workaround;
- an unverified idea that has not reached a real decision boundary.

## Return a bounded result

Return one of:

- `ADR required`: name the material decision, scope, drivers, authority, and
  downstream work that must wait;
- `ADR optional`: explain why a short rationale may help but is not a gate;
- `ADR not needed`: name the correct owner of the information;
- `insufficient evidence`: name the smallest question or discovery needed.

Do not create an ADR merely because the implementation is large. Do not avoid
an ADR merely because the resulting code change is small.
