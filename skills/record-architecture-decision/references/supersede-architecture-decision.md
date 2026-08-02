# Supersede an Architecture Decision

Supersede an accepted ADR when new circumstances materially change the decision,
its rationale, its scope, or its accepted consequences.

## Distinguish clarification from replacement

A clarification may correct wording, add evidence or links, narrow an already
intended scope, or record a review without changing the choice.

Create a replacement ADR when the update changes:

- the selected option or dependency direction;
- a material architectural boundary or invariant;
- the reasons the option was accepted;
- important consequences or accepted risks;
- the population, domain, or system for which the decision is authoritative.

When uncertain, treat the change as material and request decision-owner review.

## Apply the bounded transition

1. Create a new ADR containing current context, options, decision, rationale,
   consequences, assumptions, and review triggers.
2. Link the replacement to every ADR it supersedes.
3. After configured acceptance, change each replaced ADR to the semantic
   `superseded` state and add a backlink to the replacement.
4. Update the affected old and new index entries.
5. Preserve the old rationale and consequences verbatim except for clearly
   identified non-material corrections.
6. Verify that downstream architecture and task artifacts point to the active
   decision where appropriate.

Do not mark the old ADR superseded while the replacement is only proposed
unless project policy explicitly models that transition. Do not use
supersession to hide architecture drift or an incomplete migration.
