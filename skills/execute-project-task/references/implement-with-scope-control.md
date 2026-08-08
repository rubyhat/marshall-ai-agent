# Implement with Scope Control

Use the agreed task contract to distinguish routine implementation judgment from a scope change.

## Map the contract to work

Before substantial editing, map:

- requirements and acceptance criteria to affected surfaces;
- contract owners and consumers;
- required tests and quality gates;
- migration, rollout, localization, security, privacy, accessibility, observability, and documentation impacts;
- explicit non-goals.

Keep this mapping compact. Do not create a second specification.

## Stay within local implementation authority

Routine authority includes task-scoped:

- source, test, configuration, migration, documentation, and generated-file edits;
- local dependency installation using project-approved tooling;
- code generation, formatting, linting, building, testing, and local runtime verification;
- creation of disposable local or configured test data;
- implementation-start and local-review task checkpoints through the owning workflow.

Routine authority excludes:

- commit, push, pull-request creation, merge, release, or deployment;
- production credentials, production data, or destructive shared-environment operations;
- global machine configuration or unapproved global dependency installation;
- unrelated refactors, cleanup, upgrades, or task mutations;
- weakening security, tenant boundaries, tests, or required gates to make the change pass.

## Classify discoveries

### Level 1: technical adaptation

Proceed when the change:

- preserves the agreed outcome and observable behavior;
- stays inside scope and architecture;
- does not change a durable external contract;
- is reversible and covered by the planned verification.

Examples include using an actual current helper name or placing code in the project-native layer instead of an outdated speculative path.

### Level 2: durable contract correction

Pause implementation long enough to update the task specification through `write-task-spec` when the discovery changes:

- an API, event, schema, state, permission, error, data, migration, or rollout contract;
- an acceptance criterion or required gate;
- a dependency or compatibility assumption;
- a durable implementation constraint needed by later work or review.

Stop task-code edits while the correction is unresolved. Route the exact
contract change through `write-task-spec` and its configured planning workspace
instead of casually editing the canonical specification from the implementation
worktree.

When canonical planning publication is configured:

1. treat the selected readiness evidence as invalid when any task-owned
   specification or annex changes;
2. publish the complete corrected package through `publish-planning-change`;
3. require the new canonical merge and persisted publication record;
4. rerun the complete implementation-readiness gate against that record.

Resume only after the updated contract is coherent and the new readiness path
is complete. `Spec ready`, a local specification edit, or an unbound merged PR
does not authorize implementation to continue.

### Level 3: material work change

Stop and return to `shape-project-work` when the discovery changes:

- user or business outcome;
- in-scope versus out-of-scope behavior;
- task decomposition or repository ownership;
- architecture or dependency direction;
- security, privacy, tenant isolation, billing, legal, or operational risk;
- task size enough to require sibling implementation work.

Present the concrete risk and options before continuing.

## Keep evidence current

Update implementation and tests together. Do not defer required error, permission, localization, migration, or compatibility behavior merely because the happy path works.

When current code contradicts the specification, treat code as evidence of current behavior and the specification as the promised task contract. Resolve the contradiction through the owning workflow rather than silently choosing either source.
