# Recover previous task context

Use this runbook only when the user resumes previous work or canonical sources do not explain the current task state.

## Resolve identity before chronology

Search in this order:

1. explicit task ID or issue number;
2. explicit spec or report path;
3. current branch or worktree;
4. active-task pointer or rolling note;
5. repository and domain;
6. recent filenames as candidate hints.

Do not select a session note only because it is the newest file.

## Recover the current state

1. Read the active task spec or issue when available.
2. Read the rolling task note matching the same identity.
3. Verify current repository or branch state when needed.
4. Read a historical session note only for a concrete missing decision, blocker, or handoff detail.
5. Read linked pull-request state only when local sources cannot establish whether the work changed.

Keep GitHub access read-only. Do not update task status or lifecycle fields from this skill.

## Handle ambiguous continuation

When several tasks plausibly match:

1. List candidate names or identifiers without opening every body.
2. Use repository, branch, date, and explicit user wording as supporting evidence.
3. Prefer an active canonical task artifact over a session note.
4. Ask the user only if choosing the wrong candidate would materially change the work.

## Stop recovery

Stop when the task identity, current state, unresolved blockers, and next action are established. Do not reconstruct the full chronological history.
