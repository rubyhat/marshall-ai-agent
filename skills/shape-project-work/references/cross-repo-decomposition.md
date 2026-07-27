# Decompose cross-repository work

Use this reference when a result crosses repositories, services, clients, teams, or independently deployed units.

## Start from one shared outcome

Define the end-to-end actor outcome before splitting by repository. Identify:

- shared business rule;
- source of truth;
- contract producer and consumers;
- state or lifecycle owner;
- security and permission owner;
- data and migration owner;
- user-facing integration point;
- end-to-end proof.

A repository list is not yet a valid decomposition.

## Stabilize the contract first

Use `contract-first`, not unconditional backend-first.

1. Agree on the minimum contract needed by every consumer.
2. Make the producer implementation precede any integration that depends on unavailable runtime truth.
3. Allow independent UI, documentation, fixtures, or adapter preparation in parallel only when the contract is stable enough to prevent divergent assumptions.
4. Define the integration gate that proves producer and consumers agree.

Do not let frontend mocks become an unreviewed replacement for the real contract.

## Create repository-owned slices

Give each implementation slice:

- one primary owner;
- exact contract responsibility;
- inputs and outputs;
- dependency position;
- independently testable result;
- compatibility and rollout constraints;
- link to the shared feature outcome.

Use sibling repository-owned implementation tasks under a shared feature when project hierarchy requires it.

## Order by dependency and risk

Express relationships explicitly:

- `blocks`;
- `blocked by`;
- `can run in parallel after contract approval`;
- `integration gate`;
- `release or migration order`;
- `end-to-end verification`.

Separate a high-risk migration, permission change, or public contract when it needs an independent review or rollback boundary.

## Check completeness

Before calling the decomposition shaped, confirm:

- every promised part has an owner;
- no shared contract has two conflicting owners;
- tenant, auth, privacy, and error behavior are consistent across boundaries;
- data migration and compatibility are assigned;
- documentation and observability are included when required;
- an integration or QA slice proves the full outcome;
- deferred work remains explicit rather than disappearing from scope.
