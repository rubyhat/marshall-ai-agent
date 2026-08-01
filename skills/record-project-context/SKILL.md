---
name: record-project-context
description: Route and persist durable project knowledge without duplicating sources of truth. Use when Codex is about to create or update project memory or documentation; when a durable decision, risk, gotcha, runbook, handoff state, or expensive-to-recover fact should survive the current session; when active task state materially changes; or when closing a task's recording lifecycle. Apply a skip, link, update, then create decision order. Do not use for loading context, defining the substantive content of specs or ADRs, routine transient status, broad context audits, bulk cleanup, or GitHub lifecycle changes.
---

# Record Project Context

Apply a recording gate before writing project context. Preserve only information whose loss would make future work materially slower, ambiguous, or risky.

## Keep the responsibility narrow

- Route and persist knowledge supplied by the current task or an owning workflow.
- Let domain workflows define the substantive content of specs, reports, and
  product decisions. Let `record-architecture-decision` own ADR necessity,
  applicability, content, and lifecycle.
- Keep operational task status in the configured issue or project system.
- Keep implementation truth in code, schema, and runtime configuration.
- Do not perform broad discovery, health audits, historical consolidation, or bulk deletion.
- Delete only the active task note being closed when its bounded closure checks pass.
- Do not modify GitHub issues, pull requests, projects, or fields.

## Run the recording workflow

### 1. Confirm a recording checkpoint

Record only at one of these checkpoints:

- an explicit request to save or document information;
- a write to project memory or project documentation;
- a durable decision, risk, gotcha, or verified repeatable procedure;
- a verified structural change to a component, repository, ownership,
  lifecycle, dependency, context route, or deploy boundary;
- a blocker, open question, or next action that would be expensive to reconstruct;
- a handoff, pause, scope transition, or task completion.

Do not record routine command output, ordinary successful checks, duplicated task or pull-request status, intermediate attempts, or facts that are obvious and cheaply rediscovered from their canonical source.

### 2. Resolve project policy

Read the project workflow configuration for:

- logical destination paths;
- active task note location;
- documentation and memory languages;
- source-of-truth ownership;
- project-topology location and repository-registry ownership;
- context map location;
- exceptional recording requirements.

Keep project-specific names and paths out of this reusable skill. If recording configuration is absent, use project instructions and existing canonical artifacts. Avoid inventing a new folder structure unless the user's request requires project setup.

### 3. Classify the candidate

Classify its lifetime:

- `ephemeral`: useful only in the current reasoning;
- `active`: needed until the current task is complete;
- `durable`: reusable current project knowledge;
- `historical`: evidence of a completed event.

Classify its audience:

- agent;
- human;
- project tooling;
- external task system.

Read [route-project-artifact.md](references/route-project-artifact.md) when the destination or source-of-truth owner is not immediately clear.

### 4. Resolve the output contract

Before writing an artifact or composing the final response, determine:

- whether the requested result is chat-only or persistent;
- whether another agent or person must consume it later;
- the configured logical destination and format;
- whether the user requested a file, link, path, path-only response, or another
  exact output surface.

Give an explicit user-requested form precedence within applicable project and
safety policy. Treat a handoff or incident report as a persistent
human-facing artifact when project policy defines such reports as file-backed.
Do not infer a file destination merely from an existing directory; resolve it
from configuration, project instructions, or an owning documentation route.

When the user explicitly requests only a path, verify the artifact first and
return only that path. When the user requests a transferable file without a
path-only response, return a compact link or path instead of duplicating the
full artifact in chat.

### 5. Choose the least duplicative action

Use this order:

1. `skip` when the candidate is transient, redundant, or cheaply rediscovered.
2. `link` when another source already owns the detail.
3. `update` when an existing canonical artifact owns the fact.
4. `create` only when no suitable artifact exists and the candidate has a unique durable or active role.

Search the likely canonical destination before creating a file or section. Do not create a new artifact merely because the current session is significant.

### 6. Write current state

- Replace superseded current-state wording instead of appending a task changelog.
- Keep explanations compact and decision-oriented.
- Distinguish verified facts, decisions, hypotheses, risks, and unresolved questions.
- Add a source or verification date only when provenance or staleness matters.
- Link to detailed specs, ADRs, reports, issues, pull requests, code, or external documentation instead of copying them.
- Follow the configured language policy.

Before recording architectural rationale, hand the exact decision to
`record-architecture-decision`. Do not treat a generic recording request as
authority to accept, reject, rewrite, deprecate, or supersede an ADR.
If that module is not configured, report the missing decision owner and do not
improvise an ADR lifecycle inside this skill.

Read [update-canonical-context.md](references/update-canonical-context.md) when changing stable memory, runbooks, configuration, architecture, known issues, or a context map.

For a verified structural topology change, update the canonical topology map
instead of appending the fact to general memory. When project configuration
owns a machine-readable repository registry, update both owners in one bounded
mutation and verify they agree. Do not rewrite topology for ordinary code,
dependency-version, task-status, or deployment-event changes.

### 7. Manage active task state

Use one rolling note per stable active Task ID. Use a stable slug only when a multi-session initiative has no Task ID.

- Update the same note across sessions.
- Keep only current objective, canonical links, confirmed decisions, blockers, open questions, next action, and pending promotion.
- Do not create a note for a short self-contained discussion.
- Do not create per-session notes by default.
- Use separate implementation-task notes for independently active Task IDs.
- Create a parent coordination note only when coordination has its own unresolved state.

Read [manage-active-task-note.md](references/manage-active-task-note.md) when creating, updating, handing off, or closing a rolling note.

### 8. Verify the mutation

After writing:

1. Confirm that one canonical source owns each recorded fact.
2. Confirm that obsolete wording in the edited scope was replaced or clearly superseded.
3. Confirm that links and paths resolve.
4. Update the context map only when a canonical route was added or changed.
5. Update the project topology only when a structural component or route fact
   changed, and reconcile it with the configured repository registry.
6. Confirm that the active note does not duplicate its linked spec, issue, or pull request.
7. Confirm that the final response matches the resolved output contract.
8. Report only material recording choices, conflicts, or assumptions.

## Close a task recording cycle

At task completion:

1. Resolve every pending-promotion item.
2. Promote durable knowledge to its canonical owner.
3. Remove promoted and transient content from the rolling note.
4. Verify canonical links and the completed task identity.
5. Delete that rolling note when no unique information remains.
6. Keep the note only when unresolved task state remains; do not retain it as a completion log.

Treat legacy session notes and unrelated context as out of scope. Hand their audit and cleanup to the maintenance workflow.

## Coordinate with architecture decisions

- Route important architectural rationale to `record-architecture-decision`.
- Persist only the ADR action that workflow authorized and verified.
- Keep current architecture in its owning current-state source and cross-link
  the ADR instead of duplicating rationale.
- Never append task completion or implementation progress to an ADR.
