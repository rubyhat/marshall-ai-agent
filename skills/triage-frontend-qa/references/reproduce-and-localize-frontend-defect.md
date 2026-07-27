# Reproduce and Localize a Frontend Defect

Use the shortest evidence path that can confirm the symptom and its likely owning boundary.

## Build a faithful test setup

Record the applicable setup:

- frontend and build or revision;
- environment, URL, route, and backend/API profile;
- actor, role, account, tenant, store, or organization;
- prerequisite entity and lifecycle state;
- browser, device, viewport, and locale;
- feature flags, cached state, session state, and connectivity;
- user-provided timing or recurrence conditions.

Change one material variable at a time. Do not silently substitute a different role, tenant, API profile, or lifecycle state.

## Use an evidence ladder

Escalate only as needed:

1. Observe the exact UI path and visible state.
2. Inspect browser console, requests, responses, redirects, and client state.
3. Verify the corresponding API behavior and server logs.
4. Trace the smallest relevant route, component, state owner, API wrapper, serializer, policy, or error mapping.
5. Do not add or modify test code during triage; run only existing focused tests or commands when they can confirm the boundary quickly.

Code that looks suspicious is not reproduction. Runtime evidence without a stable failing path may be correlation rather than a localized cause.

## Use safe access fallback

If the reported production or test route is blocked by authentication:

- preserve the access blocker as evidence;
- use a configured local or non-production equivalent with a seeded or development account;
- create only the minimum test entities allowed by project policy;
- record the substituted environment, user role, entities, backend/API profile, and differences from the original report;
- avoid claiming production confirmation when only local or test behavior was observed.

Never create or mutate production state merely to reproduce a defect.

## Establish reproducibility

State:

- whether the symptom reproduces always, intermittently, once, or not at all;
- number and conditions of meaningful attempts without turning triage into a stress test;
- exact last successful step and first failing step;
- whether refresh, retry, another viewport, another role, or another allowed environment changes the result;
- whether expected behavior is documented, inferred from an established pattern, or still disputed.

## Localize ownership

Classify the smallest defensible owner:

- frontend presentation, navigation, or state management;
- frontend API mapping or error handling;
- backend contract, validation, authorization, or lifecycle;
- shared contract or multi-repository sequence;
- environment, configuration, test data, or deployment;
- unresolved.

Distinguish the owning cause from the surface where the user sees it. Do not invent a technical fix or module map; leave verified implementation detail to the specification workflow.

Stop when further investigation would not change the primary result, owner, priority, safety response, or next workflow.
