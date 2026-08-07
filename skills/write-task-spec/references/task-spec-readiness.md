# Assess task-spec readiness

Return a content verdict only after checking the written or audited specification.

## `Draft spec`

Use only when draft persistence was explicitly authorized and at least one blocker remains.

The spec must name:

- unresolved decisions;
- missing evidence or technical discovery;
- affected sections;
- owner or next action;
- why implementation must not start.

Do not use placeholders to imply completeness.

## `Spec ready`

Use when:

- outcome, scope, and requirements are coherent;
- shaping decisions are stable;
- acceptance criteria are testable;
- applicable impacts are classified;
- dependencies and ownership are explicit;
- no blocking product question remains.

Technical discovery or an upstream contract may still need completion before implementation.

## `Ready for implementation`

Use when all `Spec ready` conditions pass and:

- the exact implementation task and owner are stable;
- relevant current code and architecture were inspected;
- required contracts are defined or available;
- dependencies and prerequisite tasks are satisfied or sequenced;
- implementation boundaries are verified without false precision;
- test and quality gates are actionable;
- rollout, migration, compatibility, and recovery are defined when applicable;
- no blocking open question remains.

When project policy requires independent planning publication, do not assign
this verdict from the author's self-check. Require a clean independent review
for the exact current spec head. The publication workflow may then hand the
review evidence back to `write-task-spec` for the verdict update before Git
publication. Operational implementation readiness still requires the merged
canonical revision and belongs to the configured publication and task-management
gates.

## Downgrade conditions

Do not claim readiness when:

- identity or scope conflicts across artifacts;
- a requirement lacks acceptance coverage;
- critical behavior lacks verification;
- a contract, permission, state, or data rule is ambiguous;
- the plan violates architecture or exceeds the shaped scope;
- a material risk is unaccepted;
- the task should be decomposed further;
- named technical details were not verified.

## Read-only audit

For `--spec-check`:

1. identify the exact spec and configured template/policy;
2. report missing, contradictory, stale, or unverifiable content;
3. distinguish blockers from improvements;
4. return the highest supported verdict;
5. recommend the smallest next action;
6. stop without editing files, tracker state, or project status.

Do not mark operational status directly. Hand an authorized verdict to `manage-project-work`.
When invoked as a fresh reviewer by `publish-planning-change`, return the
highest supported content verdict and findings for the exact reviewed head;
do not publish or edit the specification yourself.
