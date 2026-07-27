# Clarify the Frontend Business Flow

Define the behavioral frame before discussing screens in detail.

## Reuse upstream shaping

Start from confirmed:

- problem and intended outcome;
- actor and role;
- in-scope and out-of-scope behavior;
- existing product decisions;
- repository or product ownership;
- accepted risks and dependencies.

Do not repeat questions already answered. If these inputs conflict or remain materially unstable, return the gap to `shape-project-work`.

## Define the flow boundary

Identify:

- entry trigger and prerequisite state;
- user goal and successful end state;
- system state changed by success;
- cancel, abandon, and resume behavior;
- actors or systems participating in the flow;
- data, role, permission, tenant, privacy, legal, or billing constraints;
- explicit non-goals and follow-up behavior.

Separate desired behavior from a proposed UI mechanism. A drawer, wizard, modal, or page is an option until its behavioral trade-off is understood.

## Cover paths that change the design

Describe only meaningful paths:

- happy path;
- allowed alternative path;
- validation or permission failure;
- asynchronous pending or partial completion;
- recoverable service or network error;
- irreversible or destructive action;
- cancellation, navigation away, refresh, and later resume;
- conflicting or stale data when applicable.

Do not enumerate imaginary edge cases. Include a path when it changes the surface, state, action, contract, safety boundary, or acceptance behavior.

## Produce a bounded flow statement

Return:

- actor and goal;
- entry and exit;
- primary steps;
- material alternative and recovery paths;
- constraints and non-goals;
- unresolved decisions that block surface modeling.
