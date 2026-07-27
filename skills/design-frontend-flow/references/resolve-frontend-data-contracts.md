# Resolve Frontend Data Contracts

Identify the contract needed to make the flow truthful and recoverable.

## Define data needs

For every surface and transition, determine:

- data required before rendering;
- data that can load progressively;
- query ownership and refresh behavior;
- mutations and idempotency expectations;
- server-owned statuses and allowed transitions;
- permission and tenant checks;
- filtering, sorting, pagination, and search semantics;
- freshness, concurrency, and stale-update behavior;
- sensitive fields that must not reach the client or another tenant.

Do not invent endpoint names, schemas, enum values, or error keys. Mark missing contract detail for verification in the specification workflow.

## Define error and recovery semantics

Distinguish:

- validation error;
- authentication or session expiry;
- authorization denial;
- missing or already-changed resource;
- business-rule conflict;
- rate limit or temporary unavailability;
- network failure;
- partial success;
- asynchronous acceptance versus completion.

For each applicable class, define the visible message intent, preserved user state, retry or recovery action, and safe destination.

## Decide optimistic and persistent behavior

Use optimistic UI only when failure can be reversed or reconciled without misleading the user. Define:

- source of truth during pending state;
- duplicate action protection;
- rollback or reconciliation;
- behavior across refresh or another client;
- draft or cache lifetime and ownership.

## Establish dependency direction

Classify the frontend dependency:

- existing contract is sufficient;
- contract clarification is required;
- new producer contract is required;
- companion client or shared design-system change is required;
- work can proceed independently after a stable contract;
- dependent integration must wait for producer implementation.

Stabilize the contract before dependent integration. Allow parallel frontend foundation only when it does not fabricate backend truth or create throwaway behavior.

## Preserve the implementation boundary

Define route and interaction ownership, required capabilities, and dependency order. Let `write-task-spec` verify concrete modules, files, component boundaries, hooks, model logic, API adapters, tests, and rollout details.
