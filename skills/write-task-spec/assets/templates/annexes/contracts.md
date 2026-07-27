# Contracts annex — <TASK-ID>

Use this annex only when contract detail is too large or independently consumed.

## Ownership and consumers

- Contract owner:
- Consumers:
- Source of truth:
- Compatibility policy:

## Operations, messages, or interfaces

### <INTERFACE NAME>

- Purpose:
- Actor / caller:
- Authentication / authorization:
- Idempotency / ordering / retry:

Input:

```text
<schema or structured example>
```

Output:

```text
<schema or structured example>
```

Errors:

| Condition | Stable error / outcome | Recovery |
| --- | --- | --- |
| <condition> | <error or state> | <caller action> |

## Data and lifecycle invariants

- <Invariant or allowed transition.>
- <Forbidden transition or disclosure.>

## Versioning and rollout

- Backward compatibility:
- Deprecation:
- Producer / consumer order:

## Contract verification

- <Contract, schema, consumer, or integration test.>
