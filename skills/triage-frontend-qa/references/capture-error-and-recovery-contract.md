# Capture the Error and Recovery Contract

Describe how failure behaves for the user and the system, not only the visible message.

## Capture backend and transport semantics

Record when applicable:

- request or action that failed;
- HTTP status or transport failure;
- stable backend error key or typed result;
- safe redacted response shape;
- retryability and idempotency;
- partial success, asynchronous acceptance, or stale-conflict behavior;
- whether frontend mapping preserves the backend meaning.

Do not expose sensitive payloads or invent undocumented keys.

## Capture visible behavior

State:

- message meaning and placement;
- affected field, form, section, page, or global state;
- loading and disabled-state behavior;
- primary recovery action;
- secondary escape or support path;
- whether the user can understand what happened and what to do next;
- mobile, keyboard, screen-reader, and focus behavior when relevant.

A generic toast, blank screen, infinite loader, or raw server message is evidence only after its relationship to the failed action is established.

## Check preservation and duplicate safety

Verify applicable behavior for:

- entered form data and drafts;
- uploads and progress;
- cart, checkout, order, payment, or legal state;
- optimistic updates and rollback;
- duplicate submit, retry, and refresh;
- navigation away and later resume;
- already-completed or concurrently changed resources.

## Check auth, permission, and tenant boundaries

Distinguish:

- unauthenticated or expired session;
- authenticated but unauthorized role;
- missing or inaccessible resource;
- another tenant or account;
- business-rule denial;
- temporary service failure.

Verify that the UI does not reveal resource existence, personal data, tenant data, internal diagnostics, or misleading recovery options.

## Produce a compact contract

For each material failure class, capture:

| Failure class | Backend or transport signal | Visible behavior | Preserved state | Recovery | Safety concern |
| --- | --- | --- | --- | --- | --- |

Include only rows relevant to the reported defect. Pass this contract to the specification workflow for confirmed actionable work.
