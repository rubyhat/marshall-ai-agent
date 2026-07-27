# Assess Frontend Flow Readiness

Check domain completeness without claiming specification or implementation readiness.

## Use the lightweight path when safe

Keep the result short when:

- the change reuses an established pattern;
- one surface and one owner are involved;
- no new lifecycle, permission, data, navigation, or recovery behavior exists;
- responsive, accessibility, and content behavior are already determined by the pattern.

Do not force a full state matrix for a trivial bounded change.

## Check the agreed-flow gate

Require enough clarity about:

- actor, goal, entry, and successful outcome;
- surface and route ownership;
- happy, alternative, error, cancel, and recovery paths;
- applicable states and actions;
- permission, tenant, privacy, and destructive-action boundaries;
- mobile, desktop, and accessibility behavior;
- content and localization impact;
- data, API, and companion dependencies;
- backend/frontend order;
- non-goals, assumptions, and unresolved decisions.

## Return one domain result

### `needs frontend clarification`

Use when a frontend-specific decision remains open and changes navigation, state, action, recovery, responsive behavior, accessibility, content, or contract needs.

### `frontend flow agreed`

Use when the interaction contract is coherent enough to return to `shape-project-work`. This does not authorize a specification or implementation.

### `blocked by product or contract decision`

Use when the missing decision belongs to product scope, backend or data ownership, permissions, legal behavior, or another workflow. Name the owner and exact decision.

## Hand off without creating artifacts

Return the compact flow packet in chat. Let `shape-project-work` produce the overall shaping verdict and decomposition. Let `manage-project-work` establish required task identity and tracker anchors. Let `write-task-spec` record that identity and add verified implementation detail, module map, acceptance criteria, and tests only after explicit specification authority.

Persist a separate artifact only on explicit request or when `record-project-context` identifies a real session-boundary need.
