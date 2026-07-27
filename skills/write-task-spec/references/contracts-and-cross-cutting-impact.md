# Specify contracts and cross-cutting impacts

Read only the applicable parts of this reference. Use project-specific policies for exact classifications and gates.

## Interface contracts

For an API, event, command, file, schema, or inter-module interface, define:

- owner and consumers;
- operation or message identity;
- inputs, outputs, and invariants;
- validation;
- errors and recovery;
- authentication and authorization;
- idempotency, ordering, concurrency, or retry behavior;
- versioning and compatibility;
- examples only where they remove ambiguity.

Do not assume HTTP or JSON when another contract type is used.

## Data and lifecycle

Define:

- source of truth;
- entities and relationships;
- state transitions and forbidden transitions;
- retention, deletion, and audit behavior;
- consistency and transaction boundary;
- migration, backfill, and compatibility needs;
- failure and reconciliation behavior.

## Security and privacy

Check:

- actors and permission matrix;
- tenant or account isolation;
- sensitive fields and redaction;
- public/private serialization;
- input validation and abuse controls;
- secrets and credential handling;
- auditability;
- production-data restrictions.

Never include secret values in a spec.

## Delivery and operations

Check:

- deploy and release order;
- feature flag or staged rollout;
- rollback versus forward-fix;
- background work and retries;
- observability, logs, metrics, alerts, and runbooks;
- support and incident recovery;
- external dependencies and failure modes.

## User-facing quality

Check:

- localization and source-language policy;
- content semantics and promises;
- accessibility;
- responsive or platform-specific behavior;
- loading, empty, success, error, and recovery states;
- analytics and consent;
- documentation and help impact.

## Record applicability

Use project-configured impact fields or a compact impact table. Describe affected dimensions and required gates.

Use an explicit `none` or `not applicable` only when project policy requires the classification or omission could be mistaken for oversight. Add a short reason.

Move detailed contract, rollout, migration, or test matrices to an annex only when the core document would otherwise become hard to scan.
