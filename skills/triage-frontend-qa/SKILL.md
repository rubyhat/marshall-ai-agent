---
name: triage-frontend-qa
description: Triage one exact frontend defect reported through manual testing or an explicit reproduction request. Use when the user reports an incomplete or detailed UI bug, UX defect, regression, frontend error-handling failure, or frontend/backend contract mismatch; asks to reproduce or localize specific observed frontend behavior; resumes a specific QA triage; or invokes `--qa-triage` with a report, URL, or task anchor. Collect bounded browser, network, API, log, code, and focused-test evidence; classify the result, ownership, priority, and specification depth; and hand a sufficiently confirmed actionable defect to the configured task and specification workflows. Do not use for broad exploratory QA, design of new frontend behavior, general product shaping, backend-only diagnosis without a frontend symptom, implementation, code review, or delivery.
---

# Triage Frontend QA

Turn one reported frontend symptom into a defensible triage result without silently expanding diagnosis into implementation.

## Keep the responsibility narrow

- Accept and normalize an exact report even when the user does not follow a template.
- Reproduce the reported behavior, localize the likely owning boundary, and gather only evidence needed for the verdict.
- Distinguish a product defect from expected behavior, an environment or test-data problem, and an unresolved observation.
- Define defect type, priority, risk, ownership, and required specification depth from project policy.
- Let `manage-project-work` own Task ID, Issue, hierarchy, Project, and operational state.
- Let `write-task-spec` own the detailed implementation specification and readiness verdict.
- Let `execute-project-task` own implementation only when the user has explicitly asked to fix or implement the defect.
- Do not perform broad exploratory testing or opportunistic cleanup around the reported flow.

## Establish authority before acting

Treat an ordinary defect report and `--qa-triage <report, URL, or task anchor>` as authority for bounded diagnosis. This may include:

- read-only inspection of browser state, network traffic, API responses, logs, code, configuration, and existing tests;
- starting configured local development services and running focused diagnostic checks;
- using configured seeded or development accounts;
- creating the minimum required test entities only in project-approved non-production accounts or environments.

Do not treat diagnosis as implementation authority. A defect being small, obvious, or local does not authorize a code change.

When the original or a later user request explicitly says to fix or implement the exact defect, preserve that authority across the triage handoff. After a required Issue and implementation-ready specification exist, hand the exact task to `execute-project-task` without asking the same permission again.

Never mutate production data merely to reproduce a problem. Require explicit user permission and applicable project policy before any production mutation; prefer a safer non-production reproduction. Do not expose credentials, tokens, personal data, tenant data, or sensitive payloads in artifacts or chat.

## Resolve project policy

Use an already sufficient orientation or `load-project-context`. Resolve only the policy needed for this report:

- supported frontend repositories and excluded or frozen clients;
- environment, authentication, test-account, and test-data rules;
- production safety and evidence-redaction requirements;
- priority, risk, grouping, Issue, Project, and specification-depth rules;
- templates and required error/recovery fields;
- repository ownership, tenant, role, privacy, legal, billing, and security constraints;
- routing to task, specification, implementation, design, incident, or discovery workflows.

Keep project names, repositories, URLs, accounts, status labels, locales, templates, commands, and paths in project configuration or project docs, not in this reusable skill.

## Run the triage workflow

### 1. Normalize the reported observation

Read [accept-and-normalize-frontend-report.md](references/accept-and-normalize-frontend-report.md).

Extract known facts, separate observation from interpretation, identify the exact flow boundary, and ask only questions that block a safe reproduction attempt. Do not require the user to rewrite the report in a template.

### 2. Preflight environment and safety

Identify the target environment, frontend, route, role, tenant or account, data prerequisites, viewport, browser, and backend/API profile when applicable.

Prefer the reported environment for read-only observation. If authentication or access blocks it, use the configured local or test fallback instead of stopping immediately. Record the fallback and any created non-production entities in the triage result.

If reproduction would require unsafe production mutation, cross-tenant access, secret disclosure, destructive data changes, or authority not supplied by the user, stop that path and report the exact blocker.

### 3. Reproduce and localize

Read [reproduce-and-localize-frontend-defect.md](references/reproduce-and-localize-frontend-defect.md).

Start with the shortest faithful reproduction path. Expand through browser state, network, API, logs, code, and focused tests only when each next layer resolves a concrete uncertainty.

Establish reproducibility, the smallest failing boundary, relevant data and lifecycle state, likely owner, cross-repository dependencies, and whether current evidence supports causation or only correlation.

### 4. Collect sufficient and safe evidence

Read [collect-and-protect-qa-evidence.md](references/collect-and-protect-qa-evidence.md).

Preserve the minimum evidence needed to support reproduction, expected versus actual behavior, environment identity, ownership, and severity. Redact or avoid sensitive data. Do not create a standalone QA report file by default.

If a tenant-isolation, privacy, authorization, payment, or security risk appears credible, minimize further exposure, classify it as an escalation, and follow the configured safe reporting path before ordinary artifact creation. If no restricted path is configured, stop and give the user only the minimum redacted summary needed to choose the next step.

### 5. Classify the result

Return exactly one primary triage result:

- `confirmed actionable defect`;
- `confirmed but ownership unresolved`;
- `not reproduced`;
- `expected behavior`;
- `environment or test-data issue`;
- `blocked by access or environment`;
- `security or privacy escalation`.

Read [classify-priority-scope-and-spec-depth.md](references/classify-priority-scope-and-spec-depth.md) to assign the problem type, priority, risk, owning scope, dependency order, grouping policy, and specification depth without overstating confidence.

### 6. Capture error and recovery behavior

For error handling, auth, form, mutation, asynchronous, cart, checkout, order, legal, billing, or other lifecycle-sensitive defects, read [capture-error-and-recovery-contract.md](references/capture-error-and-recovery-contract.md).

Record the applicable backend response semantics, visible user message, recovery action, input or draft preservation, auth/session behavior, duplicate-action safety, tenant/privacy boundary, and responsive state.

### 7. Hand off only the justified result

Read [handoff-and-report-qa-triage.md](references/handoff-and-report-qa-triage.md).

For a `confirmed actionable defect` that is sufficiently localized:

1. Hand exact task identity and operational artifact creation or reconciliation to `manage-project-work`.
2. Hand the confirmed behavior, evidence, scope, risk, dependencies, and configured depth to `write-task-spec`.
3. Do not request repeated user permission for these configured mandatory artifacts.
4. If explicit implementation authority already exists, continue only after the specification reaches the configured implementation-ready verdict and then hand the exact task to `execute-project-task`.
5. Otherwise stop after the triage and artifact handoff.

For all other results, do not create a confirmed bug Issue or task-spec automatically. A no-repro Discovery item, enhancement proposal, or unresolved ownership task requires explicit user agreement or another configured workflow authority.

## Present the triage result

Include only applicable sections:

- primary result and confidence;
- normalized symptom, expected behavior, and actual behavior;
- reproduction steps and reproducibility;
- environment, role, route, viewport, backend/API profile, and relevant data state;
- concise evidence and localization;
- problem type, owner, priority, risk, dependency order, and specification depth;
- error and recovery contract;
- production access blocker, fallback environment, test user role, and created test entities;
- artifacts created or reconciled by the owning workflows;
- implementation authority status;
- blocking questions or exact next owner.

Keep the report concise and evidence-backed. Do not claim confirmation from code plausibility alone, and do not continue investigating after the result and next owner are sufficiently established.

## Coordinate with adjacent workflows

- Use `design-frontend-flow` when the behavior is an enhancement or requires a new interaction contract rather than defect triage.
- Use `shape-project-work` when the desired outcome, scope, or conceptual ownership must be decided.
- Use `manage-project-work` and `write-task-spec` only through the authority boundary above.
- Use `execute-project-task` only with explicit implementation authority and an implementation-ready specification.
- Use the configured security, privacy, incident, or production workflow when ordinary QA handling would expose or mutate sensitive state.
