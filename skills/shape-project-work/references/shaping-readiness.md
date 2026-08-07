# Assess shaping readiness

Use this reference before handing work to task management or a task-spec writer.

## Return one shaping verdict

### `needs clarification`

Use when a blocking question, unresolved conflict, unknown owner, unsafe assumption, or material unaccepted risk could change the work meaning or decomposition.

### `shaped for roadmap`

Use when the outcome, scope, work units, owners, dependencies, and major risks are clear enough to create or update roadmap tasks. Detailed implementation contracts may still require later specification work.

Before starting `--shape-roadmap`, require this verdict or equivalent evidence
that the outcome, scope, decisions, non-goals, and material risks are already
stable. Return a raw or materially changed idea to `--shape-work`; roadmap
shaping owns representation and decomposition, not renewed product discovery.

### `ready for specification`

Use when the selected implementation slice has stable product and lifecycle decisions, bounded scope, known ownership and dependencies, and enough verified context for a task-spec writer to investigate technical details without reopening the basic outcome.

These are shaping verdicts, not Project status values.

## Check the shaped result

Confirm:

- problem and observable outcome are explicit;
- actors and affected boundaries are known;
- current and desired behavior are distinguishable;
- in-scope and out-of-scope work are explicit;
- decisions are separated from assumptions;
- material conflicts and risks are corrected or explicitly accepted;
- the complete intended outcome survives decomposition;
- every proposed task has a bounded outcome and owner;
- dependencies, ordering, and integration gates are visible;
- blocking open questions are not hidden;
- the result does not contain invented implementation precision.

For cross-repository work, also confirm a stable shared contract direction and end-to-end proof owner.

## Distinguish shaping from specification

Shaping does not need:

- final endpoint schemas;
- exact file lists;
- complete test matrices;
- migration command sequences;
- localization key inventories;
- implementation module maps.

Those belong to a full task specification when applicable. Shaping must still identify that each area is impacted and assign ownership.

Do not use `Spec ready` or `Ready for implementation` merely because the roadmap breakdown looks plausible.

## Decide the next action

- `needs clarification`: ask only the blocking questions or propose bounded discovery.
- `shaped for roadmap`: hand authorized work to `manage-project-work`.
- `ready for specification`: obtain or reuse explicit specification authority, establish stable task anchors, then hand off to `write-task-spec`.

If the user explicitly deferred a specification, stop after roadmap shaping. If the user was silent, ask one separate next-step question after presenting the shaping result.
