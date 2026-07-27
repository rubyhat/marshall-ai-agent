# Select specification depth and template

Use project policy first. Select the shallowest format that still makes implementation and review safe.

## Template priority

1. Use the project-local configured template when one applies.
2. Use the bundled generic template when no project template exists.
3. Stop only when project policy requires a missing specialized template or gate that cannot be reconstructed safely.

Do not edit installed skill assets to customize a project. Copy and adapt them into the project, then record the project-local path in configuration.

## Choose a full spec

Prefer a full specification when work includes one or more material complexity signals:

- a new feature or user-visible lifecycle;
- API, event, schema, integration, or public contract;
- authorization, roles, privacy, tenant, or sensitive-data behavior;
- data migration, backfill, compatibility, rollout, or rollback;
- billing, payment, legal, consent, or compliance behavior;
- multiple repositories, services, clients, or deployment units;
- state transitions, asynchronous work, or complex recovery;
- significant UX flow, localization, accessibility, or analytics impact;
- high-risk performance, reliability, or operational behavior;
- acceptance that cannot be expressed safely in a short bounded document.

Project policy may make a full spec mandatory for configured priorities, risks, domains, or task types.

## Choose a lightweight spec

Use a lightweight specification only when the task is bounded and low risk, for example:

- a local bug with verified cause and no new contract;
- small UI, content, or documentation work;
- maintenance confined to one owner and one behavior;
- a reversible change with simple acceptance and regression coverage.

Escalate to full when investigation reveals auth, privacy, data, migration, contract, cross-unit, or lifecycle impact.

## Select annexes

Add `contracts.md` when interface detail has independent value or multiple consumers.

Add `rollout-and-migration.md` when deploy order, compatibility, data change, backfill, rollback, or forward-fix needs more than a compact core section.

Add `test-matrix.md` when roles, states, platforms, locales, or failure modes create a matrix too large for the core file.

Do not create empty annexes.

## Decide without unnecessary questions

Infer depth from verified scope and configured rules. State:

- chosen depth;
- applicable template source;
- selected annexes;
- short reason.

Ask only when two valid depths would materially change cost, assurance, or user intent.
