# Example: EXPORT-ACTIVITY-01 — export filtered activity

This abbreviated example demonstrates a coherent generic full spec. It is not a universal product or architecture pattern.

## Contents

- Metadata
- Summary and outcome
- Current and desired behavior
- Scope
- Decisions and assumptions
- Requirements
- Solution boundaries
- Contract and error behavior
- Cross-cutting impacts
- Acceptance criteria
- Test plan
- Dependencies and risks
- Links

## Metadata

- Task ID: `EXPORT-ACTIVITY-01`
- Owner: `web-app`
- Tracker: `https://tracker.example/issues/142`
- Parent: `ACCOUNT-AUDIT-01`
- Verdict: `Ready for implementation`

## Summary and outcome

Account administrators can export the activity currently selected by date and event filters as a CSV file. The export helps them perform offline review without exposing activity from another account.

## Current and desired behavior

Current: administrators can view and filter activity in the application, but cannot export it.

Desired: an authorized administrator can request an export for the active filters, receive a UTF-8 CSV, and see a recoverable error when generation fails.

## Scope

In scope:

- export of the currently supported date and event filters;
- account-scoped authorization;
- stable column order and timestamps in ISO 8601;
- empty-result export with headers;
- audit event for successful export.

Out of scope:

- scheduled exports;
- email delivery;
- new activity filters;
- cross-account reporting.

## Decisions and assumptions

- Decision: generate the first version synchronously because the verified upper bound is small.
- Decision: use the same query policy as the activity list.
- Assumption: the configured response-size limit supports the verified maximum export.
- Follow-up trigger: move generation to background work if measured size or latency exceeds the configured threshold.

## Requirements

- R1: only account administrators can export activity.
- R2: exported rows must use the active filters and current account scope.
- R3: CSV columns must remain in the documented order.
- R4: failure must not navigate away from or clear the current filters.
- R5: successful exports must produce an audit event without storing CSV contents.

## Solution boundaries

- Reuse the verified activity-query policy rather than duplicating filter logic.
- Add one export operation owned by the activity module.
- Keep CSV formatting separate from authorization and query selection.
- Do not expose internal identifiers not present in the documented export contract.

## Contract and error behavior

Input:

- current account context;
- supported date range;
- zero or more supported event filters.

Output:

- `text/csv`;
- UTF-8;
- header row even when no events match.

Errors:

- unauthorized actor: access denied without export data;
- invalid filters: existing validation semantics;
- generation failure: visible retryable error; filters remain intact.

## Cross-cutting impacts

| Dimension | Impact |
| --- | --- |
| Security/privacy | Reuse account scope and administrator policy; no cross-account rows |
| Data/migration | None; no schema change |
| Compatibility | Additive operation |
| Localization | Exported event labels use configured product policy |
| Accessibility | Export control has an accessible name and progress state |
| Observability | Count success/failure and duration without exported content |

## Acceptance criteria

- AC1: an account administrator exporting filtered activity receives only matching rows from the current account.
- AC2: a non-administrator cannot obtain an export.
- AC3: an empty result produces a valid CSV containing headers only.
- AC4: output columns and timestamp format match the documented contract.
- AC5: a generation failure leaves filters unchanged and offers retry.
- AC6: a successful export writes an audit event without CSV contents.

## Test plan

- Policy tests for administrator and non-administrator actors.
- Query/contract tests for account boundary, filters, column order, timestamp format, and empty results.
- Failure-path test confirming filter preservation and retry state.
- Observability test confirming the audit event excludes file contents.
- Manual smoke with a bounded fixture containing two accounts.

## Dependencies and risks

- Dependency: verified activity-query policy remains the source of truth.
- Risk: synchronous generation may exceed latency limits if the data bound changes.
- Mitigation: measure duration and size; use the documented follow-up trigger.

## Links

- Parent outcome: `ACCOUNT-AUDIT-01`
- Tracker: `https://tracker.example/issues/142`
