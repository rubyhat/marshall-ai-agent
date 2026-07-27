# Resolve Navigation, Responsive Behavior, and Accessibility

Make the flow usable across entry paths, viewport sizes, and interaction methods.

## Resolve route and navigation behavior

Determine:

- route or parent-surface owner;
- direct-link and refresh behavior;
- browser back and in-product back behavior;
- cancel destination;
- post-success destination;
- preserved query, filter, tab, or scroll context;
- authorization redirect or denial behavior;
- whether the experience belongs in a page, modal, drawer, inline region, or step sequence.

Prefer existing navigation patterns unless the new flow has a concrete reason to diverge.

## Design mobile first

Start with the smallest supported viewport and decide:

- information priority;
- action placement and reachability;
- sticky or persistent controls;
- progressive disclosure;
- long-list, table, form, and keyboard behavior;
- overflow and content expansion;
- whether modal or drawer patterns remain usable.

Then define meaningful desktop enhancements. Do not treat desktop as a stretched mobile layout or mobile as a collapsed desktop table.

## Include accessibility in the flow

Resolve applicable:

- heading and landmark structure;
- logical focus order and focus movement after transitions;
- keyboard access and escape behavior;
- accessible names, descriptions, errors, and status announcements;
- contrast-independent status communication;
- touch-target size and action separation;
- reduced-motion behavior;
- screen-reader handling for loading, validation, asynchronous completion, and dynamic updates.

Accessibility findings that change navigation, state, or action behavior belong in the flow, not as a later cosmetic checklist.

## Clarify visual intent

Use the configured design system and current product UI as the visual source of truth. Capture:

- desired visual character;
- patterns to preserve;
- references and anti-references;
- hierarchy and density expectations;
- visual behaviors explicitly rejected.

Treat external references as inputs, not requirements. Route substantial comparison research or creation of a visual artifact to its owning workflow.
