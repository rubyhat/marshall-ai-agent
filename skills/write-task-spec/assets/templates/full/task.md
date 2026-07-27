# <TASK-ID>: <TASK TITLE>

## Metadata

- Task ID: `<TASK-ID or project equivalent>`
- Owner: `<repository, service, team, or deployable unit>`
- Tracker: `<issue or task URL when configured>`
- Parent: `<parent task or shared outcome when applicable>`
- Spec path: `<project-relative path>`
- Priority / risk: `<when kept in the spec>`
- Content verdict: `Draft spec | Spec ready | Ready for implementation`

## 1. Summary and outcome

<Describe the intended observable result and why it matters in one to three paragraphs.>

## 2. Current and desired behavior

Current:

- <Verified current behavior or gap.>

Desired:

- <Observable behavior after completion.>

## 3. Scope

In scope:

- <Bounded outcome or change.>

Out of scope:

- <Explicit exclusion or separately tracked follow-up.>

## 4. Actors and scenarios

- Actor / role: `<goal, permissions, primary scenario>`
- Happy path: `<ordered behavior>`
- Relevant edge or recovery paths: `<only applicable cases>`

## 5. Decisions, assumptions, and open questions

Confirmed decisions:

- <Decision and short rationale.>

Assumptions:

- <Non-blocking assumption and how it will be verified.>

Open questions / blockers:

- `<None>` or <explicit blocker, owner, and next action>

## 6. Requirements

Functional:

- R1: <Observable required behavior.>

Non-functional:

- NFR1: <Applicable reliability, performance, usability, or operational constraint.>

## 7. Solution boundaries and implementation plan

Verified architecture and ownership:

- <Current module, component, service, data owner, or integration boundary.>

Implementation sequence:

1. <Bounded step and result.>
2. <Bounded step and result.>

Investigation gates:

- `<None>` or <unknown that can be resolved safely during implementation without changing scope>

## 8. Contracts, data, errors, and recovery

Contracts:

- `<Interface, input/output, invariant, or link to contracts annex.>`

Data and lifecycle:

- `<Source of truth, state transition, migration, retention, or none with reason when required.>`

Errors and recovery:

- `<Failure visibility, retry/recovery, draft safety, and forbidden behavior.>`

## 9. Dependencies, compatibility, and rollout

- Blocked by: `<task, contract, or none>`
- Blocks: `<task or none>`
- Parallel work: `<safe parallel boundary or none>`
- Compatibility / rollout: `<order, flag, migration, rollback, or link to annex>`

## 10. Cross-cutting impacts

| Dimension | Impact and required gate |
| --- | --- |
| Security / privacy / permissions | <impact or configured explicit none> |
| Data / migration | <impact or configured explicit none> |
| Compatibility / rollout | <impact or configured explicit none> |
| Localization / content | <impact or configured explicit none> |
| UX / accessibility | <impact or configured explicit none> |
| Performance / scalability | <impact or configured explicit none> |
| Observability / operations | <impact or configured explicit none> |
| Documentation / analytics | <impact or configured explicit none> |

## 11. Acceptance criteria

- AC1: <Observable pass/fail result linked to a requirement.>
- AC2: <Negative, permission, error, recovery, or compatibility result when applicable.>

## 12. Test and verification plan

- Unit / component: <scope or not applicable>
- Contract / API: <scope or not applicable>
- Integration / end-to-end: <scope or not applicable>
- Migration / security / performance: <applicable gates>
- Manual / browser / operational smoke: <actor, environment, data, and expected evidence>
- Project quality gates: <verified commands or configured checks>

## 13. Risks and trade-offs

- Risk: <credible risk, consequence, and mitigation.>
- Accepted trade-off: `<None>` or <explicitly accepted decision and source>

## 14. Links

- Shaping result:
- Tracker:
- Parent / related tasks:
- Decisions / architecture:
- Research / references:
- Annexes:
