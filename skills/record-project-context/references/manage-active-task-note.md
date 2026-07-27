# Manage an active task note

Use this reference for task handoff state that must survive sessions without becoming permanent session history.

## Resolve note identity

Use the stable Task ID as the filename identity. Use a stable lowercase slug only for a multi-session initiative without a Task ID.

Read the configured active-task directory. Do not place new rolling notes in a legacy session-history directory.

Before creating a note:

1. Search for the exact Task ID or stable slug.
2. Reuse the existing active note.
3. Confirm that the work cannot be resumed cheaply from its spec, issue, and repository state alone.
4. Skip note creation for a short self-contained task or discussion.

## Keep a current-state structure

Use only applicable sections:

```markdown
# <Task ID or stable initiative>

## Current objective

## Canonical links

## Confirmed decisions

## Blockers and open questions

## Next action

## Pending promotion
```

Do not append a session-by-session diary. Replace obsolete objectives, completed blockers, and old next actions.

## Keep the note narrow

- Link to the task spec instead of copying scope and acceptance criteria.
- Link to the issue instead of copying status and priority.
- Link to the pull request instead of copying checks and review history.
- Keep only decisions not yet promoted or a concise link after promotion.
- Keep evidence only when it explains an unresolved blocker.
- Remove routine completion details.

## Handle related tasks

Use one note per independently active implementation Task ID.

For multi-repository work:

- keep repository-specific state in each active implementation-task note;
- create a parent coordination note only when the parent has its own ordering, dependency, or cross-task blocker;
- do not mirror every child status in the parent note.

## Update at meaningful transitions

Update the note when:

- the objective materially changes;
- a decision changes the next implementation step;
- a blocker appears or is resolved;
- a handoff or pause begins;
- the next action changes;
- a durable fact awaits promotion.

Do not update after every command, check, or conversation message.

## Close the note

At task completion:

1. Verify the task identity and completion state.
2. Process every pending-promotion item.
3. Move durable knowledge to the canonical destination.
4. Replace duplicated detail with canonical links.
5. Remove transient status, resolved blockers, and obsolete next actions.
6. Check whether any unique unresolved information remains.
7. Delete this specific note when none remains.

Do not scan or delete other active notes. Do not archive the note merely to retain proof of completion; use the issue, pull request, task spec, ADR, or report as historical evidence.

If unresolved work remains, keep the note active and state the exact blocker and next action.
