# Decompose project work

Use this reference when shaping produces an epic, multiple outcomes, an oversized task, or work with independent risk and delivery boundaries.

## Decompose by outcome

Use the configured conceptual levels. A common model is:

- `Epic`: a large but finite product or operational outcome;
- `Feature/Story`: an independently meaningful capability or user/system result;
- `Implementation Task`: a bounded, reviewable delivery slice owned by one repository, service, team, or deployable unit.

Treat these as conceptual units. Let the task-management workflow validate operational hierarchy and assign identifiers.

## Define each unit

For every proposed unit, state:

- stable semantic manifest key;
- bounded outcome;
- actor or consumer;
- why it is independently valuable or necessary;
- owner;
- in-scope and excluded work;
- acceptance outline;
- dependencies and blocked-by relationships;
- major risks;
- whether it is discovery, delivery, documentation, migration, QA, or another project-configured type.

Do not invent implementation files, classes, endpoints, or schemas before they are verified.

Use a short stable kebab-case semantic key such as `profile-change-epic` or
`profile-request-api`. Keep the key stable through preview, approval, task
creation, and retry. It correlates one approved manifest node with one tracker
Issue and must not contain a predicted Issue number or Task ID.

## Prefer vertical and risk-aware slices

Prefer a slice that produces a testable outcome over a purely horizontal layer. Separate work when it has:

- a distinct repository or deployment owner;
- an independent contract or lifecycle;
- a sensitive security, privacy, migration, or billing boundary;
- an independently reviewable result;
- a dependency that must be stabilized before downstream integration;
- a size or uncertainty that would make one review unsafe.

Do not split work merely to create more Issues. Keep tightly coupled changes together when separating them would produce unusable intermediate states or duplicated coordination.

## Preserve the full outcome

When work is divided or deferred:

1. show the complete roadmap of slices;
2. show which slice delivers each required part;
3. keep deferred scope as an explicit follow-up;
4. state ordering and integration gates;
5. identify the slice that proves the end-to-end outcome.

Never present a reduced first slice as if it completes the original promise.

## Detect oversized work

Recommend decomposition when one task combines several of:

- multiple user outcomes;
- multiple repositories or deployables;
- broad API surface;
- complex lifecycle or permission changes;
- sensitive data or direct uploads;
- schema migration plus backfill;
- compatibility or rollout work;
- extensive documentation or contract generation;
- end-to-end QA across independent flows.

Read project-specific sizing gates when configured. If the user chooses an unusually large task after seeing the risk, record the accepted trade-off and keep review and rollout boundaries explicit.

## Avoid hierarchy abuse

- Do not encode ancestry in names or IDs.
- Do not add hierarchy levels beyond project policy.
- Do not make an implementation task the parent of another implementation layer.
- Use sibling implementation tasks under the same feature when further separation is needed.
- Return a still-oversized feature to shaping instead of hiding depth in nested identifiers.

## Shape research work

When research is itself the deliverable, define:

- the decision it must enable;
- bounded questions;
- evidence sources;
- expected report or recommendation;
- stop condition;
- how the result affects later roadmap or specification work.

Do not write a full implementation specification for a discovery task whose solution is intentionally unknown.
