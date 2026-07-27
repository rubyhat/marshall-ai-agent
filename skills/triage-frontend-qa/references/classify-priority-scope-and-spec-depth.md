# Classify Priority, Scope, and Specification Depth

Classify what the evidence supports, not what the symptom initially suggested.

## Choose one primary result

### `confirmed actionable defect`

Use when the behavior is reproduced or otherwise directly verified, conflicts with the expected contract, and has enough ownership and scope for a task handoff.

### `confirmed but ownership unresolved`

Use when the defect is verified but the owning repository, contract boundary, or safe task split is still uncertain. Resolve the ownership decision before automatic task/spec creation.

### `not reproduced`

Use when faithful bounded attempts do not show the reported symptom and no equivalent direct evidence confirms it.

### `expected behavior`

Use when current behavior matches the agreed product contract or explicit scope. A desired change is an enhancement and belongs to shaping or frontend-flow design after user agreement.

### `environment or test-data issue`

Use when the observed symptom is explained by configuration, deployment, fixtures, stale state, unsupported data, or setup rather than a confirmed product defect.

### `blocked by access or environment`

Use when no safe faithful reproduction is possible because required access, service, data, build, or environment is unavailable and fallback would not answer the question.

### `security or privacy escalation`

Use when ordinary evidence handling or continued reproduction could expose sensitive data or worsen a credible authorization, tenant, privacy, credential, or payment risk.

## Classify problem type

Use project-defined types where available. Common types include:

- functional defect;
- UI or UX defect;
- regression;
- error-handling defect;
- frontend/backend contract mismatch;
- accessibility defect;
- content or localization defect;
- environment or test-data defect;
- scope clarification or enhancement.

Do not label a behavior as regression without a verified earlier working contract or version.

## Determine ownership and order

Identify:

- user-visible surface;
- smallest likely owning boundary;
- affected repositories or services;
- shared contract, role, permission, tenant, privacy, legal, billing, or lifecycle impact;
- producer-before-consumer dependency;
- whether one task is coherent or project-configured multi-repository tasks are required.

Do not use a cross-repository label merely because multiple systems were inspected.

## Assign priority and risk

Use configured definitions. Consider:

- user and business impact;
- frequency and reach;
- blocked versus degraded outcome;
- data integrity and recoverability;
- auth, tenant, privacy, security, payment, order, legal, or billing exposure;
- regression and production reach;
- workaround quality;
- implementation and rollout uncertainty.

Keep priority separate from confidence. A potentially severe but unconfirmed report remains unconfirmed and may require escalation or further evidence.

## Select specification depth

Apply project configuration rather than hardcoding a universal matrix. Typical policy may require:

- full specification for critical or high-impact defects;
- full specification for API, auth, tenant, privacy, security, cross-repository, migration, data, or lifecycle risk;
- lightweight specification for a confirmed low-risk local frontend defect;
- grouped lightweight handling for related polish findings on one screen or flow.

Never use a lightweight template to hide unresolved contract or safety questions. Never create a heavy standalone task for each minor polish observation when configured grouping is more useful.
