---
name: design-frontend-flow
description: Design or review a frontend interaction flow from a shaped product outcome or an explicit UI/UX request. Use when the user asks to plan, clarify, compare, or validate a new or changed screen, navigation or information architecture, state-and-action lifecycle, complex form, responsive or mobile behavior, or a frontend experience that depends on API, permission, role, or data contracts; when `shape-project-work` hands off meaningful frontend behavior; or when the user invokes `--design-flow` with an idea or task anchor. Produce a chat-first frontend-flow packet and return overall shaping readiness to `shape-project-work`. Do not use for trivial copy or style edits, technical refactoring without UX change, implementation from an already ready specification, manual QA defect intake, broad competitor research, visual-artifact generation, or code implementation.
---

# Design Frontend Flow

Define how one bounded frontend experience should behave for its users before specification or implementation.

## Keep the responsibility narrow

- Own frontend-specific user flow, surfaces, navigation, states, actions, feedback, recovery, responsive behavior, accessibility implications, content and localization impact, data needs, and dependency direction.
- Receive the product outcome and scope from `shape-project-work`, or accept a direct explicit frontend-flow request when the outcome is already clear enough.
- Return the agreed frontend-flow packet to `shape-project-work` for overall decomposition and readiness.
- Let `manage-project-work` own Task ID, task identity, tracker anchors, and operational state.
- Let `write-task-spec` own implementation detail, the verified file or module map, acceptance criteria, test plan, and specification verdict.
- Let project-configured QA, external-reference, legal-document, visual-design, and implementation workflows own their specialized work.
- Do not create a Figma file, wireframe, HTML prototype, specification, Issue, code change, or project document merely because a flow was discussed.

## Establish mode and authority

Choose one mode:

- `discover`: define a new or materially changed frontend experience;
- `review`: inspect an existing flow proposal, specification section, screenshot set, or design reference and report behavioral gaps;
- `lightweight`: resolve a bounded change that reuses an established interaction pattern.

Treat `--design-flow <idea or task anchor>` as discussion and read-only analysis authority. It does not authorize files, design-tool mutations, a full specification, tracker changes, or implementation.

Use a direct request only for frontend-specific decisions. Return broad product ambiguity, material scope changes, or conceptual task decomposition to `shape-project-work`.

## Resolve project policy

Use an already sufficient orientation or `load-project-context`. Resolve only what the flow needs:

- applicable frontend repositories, routes, architecture, and visual sources of truth;
- actors, roles, permissions, tenant and privacy constraints;
- mobile-first, responsive, accessibility, localization, and content policies;
- existing UI patterns and legacy boundaries;
- data and API ownership;
- artifact, specification, and backend-first policies;
- project clarification format and adjacent domain workflows.

Keep repository names, frameworks, routes, locales, design systems, commands, and directory structures in project configuration or project docs, not in this reusable skill.

## Run the frontend-flow workflow

### 1. Confirm the frontend outcome

Read [clarify-frontend-business-flow.md](references/clarify-frontend-business-flow.md).

Establish the actor, goal, entry point, successful end state, current behavior, desired behavior, boundaries, and material constraints. Reuse decisions already settled by shaping. Do not ask the user to repeat them.

If the product outcome, owner, or scope is unstable, stop and return the exact gap to `shape-project-work`.

### 2. Inspect the current experience

Perform bounded read-only reconnaissance:

- find the owning route or nearest analogous flow;
- inspect applicable architecture and design-system guidance;
- identify existing navigation, state, error, form, responsive, and accessibility patterns;
- verify relevant data contracts and repository boundaries;
- distinguish current source of truth from legacy behavior or optional references.

Do not scan every frontend repository or create a design artifact for orientation.

### 3. Model surfaces, states, actions, and recovery

Read [model-surfaces-states-and-actions.md](references/model-surfaces-states-and-actions.md).

Define the minimum coherent surface inventory. For each surface, describe its responsibility, entry and exit, states, available actions, feedback, validation, failure handling, recovery, and preservation behavior.

Use the lightweight path when an established pattern already answers these questions.

### 4. Resolve navigation and experience quality

Read [resolve-navigation-responsive-and-accessibility.md](references/resolve-navigation-responsive-and-accessibility.md).

Resolve route or surface ownership, deep linking, back and cancel behavior, page versus modal or drawer choice, mobile and desktop differences, focus and keyboard behavior, semantic structure, and visual intent relative to the configured source of truth.

Treat screenshots, Figma, prototypes, and external examples as optional evidence. Hand deep comparison research or artifact creation to its owning workflow.

### 5. Resolve data, permissions, and delivery order

Read [resolve-frontend-data-contracts.md](references/resolve-frontend-data-contracts.md).

Identify data required at entry, queries, mutations, permissions, status transitions, error semantics, pagination or filtering, concurrency, recovery, and any backend or companion-client dependency.

Define interaction-level ownership and contract needs without inventing endpoints, schemas, filenames, components, hooks, or tests. Let `write-task-spec` verify and record the technical module map.

### 6. Assess content and localization

Read [assess-localization-and-content-impact.md](references/assess-localization-and-content-impact.md).

Identify user-facing copy, locale impact, semantic constraints, content expansion, layout sensitivity, validation and recovery wording, accessibility labels, and elevated legal, billing, verification, privacy, or support review needs.

Apply configured project locales and translation rules. Never hardcode a language set as a reusable default.

### 7. Ask only decision-changing questions

Use the configured clarification policy from `shape-project-work`. Ask only when the answer changes navigation, lifecycle, state behavior, data contract, permissions, recovery, responsive UX, accessibility, content semantics, scope, or dependency order.

Prefer evidence from the current product and its patterns. Offer mutually exclusive options with one recommendation for actual decisions. Ask missing facts directly. Do not reopen confirmed product decisions or ask about implementation details owned by the specification.

### 8. Check domain readiness

Read [assess-frontend-flow-readiness.md](references/assess-frontend-flow-readiness.md).

Return one domain result:

- `needs frontend clarification`;
- `frontend flow agreed`;
- `blocked by product or contract decision`.

Do not return `ready for specification`, `Spec ready`, or `Ready for implementation`. Overall shaping readiness belongs to `shape-project-work`; specification readiness belongs to `write-task-spec`.

## Present the frontend-flow packet

Include only applicable sections:

- actor, goal, entry point, and successful outcome;
- happy, alternative, error, cancel, and recovery paths;
- surface and route inventory;
- state, action, feedback, and preservation model;
- responsive and accessibility behavior;
- content and localization impact;
- data, permission, API, and companion dependencies;
- backend/frontend delivery direction;
- accepted decisions, assumptions, non-goals, risks, and open questions;
- domain readiness result and owning next step.

Keep it compact enough to remain part of the shaping conversation. Create or update a durable artifact only when the user explicitly requests one or `record-project-context` determines that the agreed flow must survive a session boundary. Do not create a separate flow document by default.

## Coordinate with adjacent workflows

- Use `shape-project-work` before or after this workflow for product scope, decomposition, and overall readiness.
- Hand an explicitly requested full specification to `write-task-spec` after overall shaping is ready.
- Hand manual defect reproduction to the configured frontend QA workflow.
- Hand broad competitor or reference analysis to the configured product-reference workflow.
- Hand visual artifact creation or editing to the explicitly requested design-tool workflow.
- Hand implementation to `execute-project-task` only after an implementation-ready specification exists.
