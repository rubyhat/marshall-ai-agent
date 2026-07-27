# Define acceptance and testability

Use acceptance criteria to state observable completion, not implementation activity.

## Write strong acceptance criteria

Each criterion should be:

- attributable to a requirement or risk;
- observable by a user, API consumer, operator, test, or reviewer;
- specific about the relevant actor, precondition, action, and outcome;
- bounded enough to pass or fail;
- independent of an unverified implementation detail.

Use Given/When/Then only when it improves clarity. A concise declarative checklist is acceptable.

## Cover applicable behavior

Include:

- primary success path;
- role and permission boundaries;
- validation and negative cases;
- lifecycle and state transitions;
- error visibility and recovery;
- retry, idempotency, or duplicate handling;
- data integrity and compatibility;
- accessibility, localization, responsive behavior, or content semantics;
- observability and operational outcome;
- migration, rollout, and rollback gates.

Do not add irrelevant categories merely to make the list look complete.

## Trace requirements to verification

For every material requirement:

1. identify at least one acceptance criterion;
2. identify the best verification layer;
3. name any required manual or external verification;
4. explain why a critical requirement cannot be automated, if applicable.

Useful verification layers include:

- unit;
- component;
- contract;
- request/API;
- integration;
- end-to-end;
- migration;
- security/privacy;
- performance;
- static analysis;
- manual/browser/operational smoke.

## Avoid weak criteria

Reject criteria such as:

- "code is clean";
- "works correctly";
- "tests are added";
- "UI is improved";
- "API is updated";
- "handle errors".

Replace them with the exact observable result and boundary.

## Check the test plan

Confirm:

- critical criteria have direct verification;
- tests are placed at the lowest useful reliable layer;
- integration boundaries are exercised;
- negative and recovery paths are represented;
- commands are project-verified rather than guessed;
- manual checks include actor, environment, data, and expected evidence;
- the plan does not require unrelated full-suite work without reason.
