# Shape outcome, scope, and risks

Use this reference to convert a request or proposed solution into a stable problem definition and to challenge material conflicts before work is committed.

## Separate outcome from implementation

Capture:

- actor and affected stakeholder;
- current behavior or problem;
- desired observable outcome;
- reason the outcome matters now;
- evidence, source, or user report;
- success signal;
- constraints and non-goals;
- proposed implementation, clearly marked as a proposal rather than a requirement.

Do not let a suggested implementation silently define the problem. Offer a simpler or more native path when it achieves the same outcome with lower cost or risk.

## Establish boundaries

State:

- `in scope`;
- `out of scope`;
- assumptions;
- dependencies;
- follow-ups needed to preserve the complete intended outcome.

Decomposition must not become silent scope reduction. When work is deferred, name where and how it remains tracked.

## Check established sources

Compare the proposal with the minimum relevant:

- active user decisions;
- project instructions and workflow configuration;
- architecture and domain contracts;
- source code or runtime truth when applicable;
- existing roadmap hierarchy and related specifications;
- security, privacy, data, legal, billing, localization, and operational policies.

Prefer current canonical evidence over an older summary. Cite the exact conflict source when stopping.

## Apply a proportional stop gate

Stop before endorsing or persisting work when there is:

- a direct contradiction with an active rule, decision, architecture boundary, or required workflow;
- credible risk of unauthorized access, tenant leakage, privacy exposure, data loss, unsafe migration, incorrect billing or legal behavior;
- a likely reliability, scalability, compatibility, or supportability failure with meaningful impact;
- an irreversible or expensive commitment based on unresolved authority, scope, or ownership;
- a decomposition that omits a required part of the promised outcome.

State:

1. what conflicts or is risky;
2. the likely impact and affected actors;
3. the supporting source or reasoning;
4. the recommended correction;
5. viable alternatives and their trade-offs;
6. what explicit decision is required to continue.

Do not soften a material objection into a footnote after the plan.

## Avoid risk theatre

Do not block on:

- purely theoretical harm without a credible path;
- minor style preferences;
- cheaply reversible local choices;
- already mitigated risk;
- ordinary uncertainty that can be recorded as a low-impact assumption.

Mention non-blocking trade-offs in the shaping summary and proceed within the user's authority.

## Continue after resolution

Continue only when:

- the proposal is corrected; or
- the user explicitly accepts the described material trade-off and has authority to do so.

If the new decision supersedes durable project truth, update the canonical decision through `record-project-context` before downstream work relies on it.

Explicit acceptance cannot override higher-priority instructions, permissions, legal constraints, or non-waivable safety requirements.
