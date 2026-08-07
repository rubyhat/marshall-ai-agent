# Transition project task state

Use this reference for status changes, including blocked, paused, not-planned, readiness, review, and completion states.

## Use the configured state machine

Resolve logical checkpoints and their configured display values. A typical configured sequence may contain:

```text
inbox
→ discovery
→ draft_spec
→ spec_ready
→ ready_for_implementation
→ implementation
→ local_review
→ pull_request_review
→ ready_to_merge
→ done
```

Treat this sequence as configuration-driven, not universal. Use only statuses present in the current project.

## Require checkpoint evidence

The owning workflow decides whether a gate passed:

- shaping or intake establishes discovery/spec readiness;
- implementation establishes work start and local-review readiness;
- delivery establishes PR creation, clean review, merge readiness, and merge completion.

This skill applies the corresponding status but does not invent gate evidence. For `--task-status`, treat the target as explicit intent while still reporting a missing configured prerequisite before applying a misleading readiness or completion status.

Allow a reasoned skip only when required gates are already satisfied or the project policy permits a lightweight path. Record the reason in the Issue only when future operators need it.

## Handle exceptional states

- `blocked`: record the concrete blocker, owner or dependency, and recovery condition.
- `paused`: record why work stopped and the next decision needed.
- `not_planned`: require explicit confirmation and preserve the reason.
- resume: restore the verified previous actionable state or an explicit configured target.

Do not use an exceptional status to hide a failed mutation or incomplete gate.

## Restrict mutation scope

`--task-status` changes only the exact task's status. It does not repair hierarchy, fields, links, parent state, or related tasks.

Routine checkpoint transitions inside the current authorized workflow need no extra confirmation. Ask before changing an unrelated task, using `not_planned`, closing outside the current workflow, or applying a broad multi-task transition.

## Verify

Reread the Project item and Issue state after the mutation. Report the configured display status, task identity, and any mismatch. Do not infer success from a mutation response alone.
