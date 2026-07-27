# Adapt Findings to the Target Product

Translate evidence into project-relevant implications without importing the reference product's assumptions.

## Resolve adaptation criteria

Use configured target-product context:

- business and revenue model;
- actors, roles, permissions, and tenant boundaries;
- market, locale, regulation, and cultural context;
- product maturity and current shipped truth;
- device, responsive, and accessibility policy;
- data, lifecycle, integration, and operational constraints;
- visual and content sources of truth;
- legal, privacy, billing, trust, and support responsibilities.

Do not hardcode one product model into the reusable workflow.

## Classify each material pattern

### `adopt`

Use when the underlying principle fits current constraints with no meaningful behavioral change.

### `adapt`

Use when the principle is useful but the target roles, scope, lifecycle, market, content, or interaction requires modification.

### `experiment`

Use when the pattern is plausible but benefit, demand, usability, or operational fit is unproven. State the hypothesis and evidence needed.

### `reject`

Use when the pattern conflicts with product truth, safety, accessibility, privacy, business model, source of truth, or current scope.

### `unknown`

Use when either the reference evidence or target constraint is insufficient.

## Express implications at the right level

Prefer:

- user or business principle;
- interaction or information requirement;
- risk or constraint;
- question for shaping;
- hypothesis for validation;
- anti-reference.

Avoid:

- copied layout or wording;
- invented routes, APIs, schemas, modules, or components;
- claims that a competitor pattern is automatically best practice;
- requirements that bypass product shaping or domain review.

## Route the result

Name the owning next workflow: product shaping, frontend-flow design, pricing decision, marketing strategy, copywriting, specification, or no action. Reference evidence alone never authorizes a task or implementation.
