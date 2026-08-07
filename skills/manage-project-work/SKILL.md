---
name: manage-project-work
description: Manage the operational lifecycle of configured GitHub Issues and Projects. Use when the user explicitly asks to create, find, reconcile, reparent, link, close, or update a backlog/roadmap task; invokes `--task-check` or `--task-status`; or when an authorized shaping, QA, specification, implementation, review, or delivery workflow reaches a configured task checkpoint. Handle Task ID uniqueness, hierarchy, Issue/Project state, fields, existing labels, spec/PR links, status transitions, and post-merge closure. Do not use for product discovery, substantive spec writing, implementation workspaces or code, deciding review/merge readiness, broad roadmap synchronization, or Project schema/view changes.
---

# Manage Project Work

Keep each project task operationally consistent across its configured Issue, Project item, hierarchy, spec, and pull requests. Make mutations idempotent and verify external state after every write sequence.

## Keep the responsibility narrow

- Accept the task meaning and decomposition from the owning shaping or QA workflow.
- Own task identity, hierarchy validation, Issue/Project mutations, lifecycle status, and artifact linkage.
- Do not decide product scope, write substantive task-spec content, create worktrees, implement code, review changes, open or merge pull requests, or infer that review gates passed.
- Let owning workflows establish a lifecycle checkpoint; apply its configured operational mutation.
- Support GitHub Issues and GitHub Projects in this version. If another provider is configured without a project adapter, stop with the exact unsupported dependency.
- Never delete an Issue. Close or mark it according to configured policy only within the authorized task scope.

## Resolve project policy

Read project instructions and the project workflow configuration. Resolve:

- task-tracking enablement and provider;
- Issue repository and Project owner/number;
- hierarchy levels, maximum depth, parent policy, and standalone exceptions;
- Task ID formats, scope prefixes, uniqueness sources, and spec roots;
- configured fields, field values, statuses, transition order, and existing-label policy;
- Issue body requirements and source-of-truth boundaries;
- spec and pull-request linkage patterns;
- tool and authentication fallback instructions.

Do not embed project names, repository owners, field IDs, option IDs, status labels, prefixes, or filesystem paths in this reusable skill.

## Interpret exact quick aliases

- `--task-check <Task ID or Issue URL>`: perform a read-only consistency check and stop. Report missing or conflicting state without repairing it.
- `--task-status <Task ID or Issue URL> <target status>`: mutate only the status of that exact task after validating the configured transition and checkpoint evidence. Do not repair unrelated fields in the same command.

Ask for the missing task anchor or target status when an alias is incomplete. Text after the exact alias is input, not broader authority.

## Establish mutation authority

Proceed without an extra confirmation for routine mutations that are:

- part of the user-authorized current task;
- required by a configured lifecycle checkpoint;
- supplied by an owning workflow whose configured handoff explicitly authorizes the required task anchors;
- limited to the exact resolved Issue and Project item.

Request confirmation before:

- broad or multi-task synchronization;
- reparenting an existing task;
- marking work `not planned`, cancelling, or closing a task outside the current workflow;
- mutating an unrelated task;
- changing Project fields, options, workflows, views, labels, or other schema;
- resolving an ambiguity that could select a different Issue, parent, repository, or Task ID.

## Run the management workflow

### 1. Resolve one exact task

Use the strongest available anchor: Issue URL/number, exact Task ID, spec path, or current authorized task. Search open and closed Issues plus configured local spec roots before creating anything.

If zero matches exist and creation is authorized, continue to allocation. If one match exists, reconcile it. If multiple plausible matches exist, stop and ask which task is canonical.

### 2. Validate identity and hierarchy

Read [task-identity-and-hierarchy.md](references/task-identity-and-hierarchy.md).

Confirm the owning repository, task type, Task ID, semantic domain, parent, hierarchy depth, and standalone exception if applicable. Treat the conceptual work breakdown as input; reject invalid operational hierarchy without reshaping the product scope inside this skill.

### 3. Prepare the intended state

Before writing, summarize the exact intended:

- Issue repository, Task ID, title, and body scope;
- task type and parent;
- Project and field values;
- existing labels to apply;
- status;
- spec and pull-request links.

This summary is an internal mutation plan, not a mandatory confirmation for routine authorized work.

### 4. Create or reconcile idempotently

Read [create-or-reconcile-project-task.md](references/create-or-reconcile-project-task.md).

Recheck Task ID availability immediately before Issue creation. Create or update one Issue, add it to the configured Project once, set configured fields, apply only existing labels, and establish the parent relationship. Recover from partial success by reusing the created Issue and Project item.

### 5. Transition status

Read [transition-project-task-state.md](references/transition-project-task-state.md) whenever the operation changes status, blocked/paused state, readiness, or lifecycle position.

Validate the target against configured transitions and evidence supplied by the owning workflow. Allow a skipped intermediate state only when the reason is explicit and required gates are already satisfied.

### 6. Link and close

Read [link-and-close-project-task.md](references/link-and-close-project-task.md) when a spec or pull request is linked, an implementation Issue is closed, or a parent may need reconciliation.

Use configured close/reference semantics. After merge, reread both Issue and Project state. Do not close a parent from child count alone.

### 7. Verify read-back

After mutations, reread the exact task and confirm:

- canonical Issue URL and Task ID;
- Issue open/closed state;
- parent and type;
- Project membership and field values;
- spec and pull-request links;
- status;
- any missing, skipped, or failed mutation.

Never report a mutation as successful from a command exit alone.

## Use GitHub tools safely

- Prefer a purpose-built GitHub connector for supported semantic reads and writes.
- Use authenticated `gh` or GitHub API/GraphQL for Project fields or hierarchy operations not covered by the connector, following project fallback instructions.
- Resolve mutable node IDs and field-option IDs at runtime instead of storing them in the skill.
- Do not scrape the GitHub web UI for operational mutations.
- Do not create missing Project schema, views, fields, options, workflows, or labels as a side effect of task management.

## Coordinate with adjacent skills

- Receive scope and hierarchy proposals from `shape-project-work` or a domain intake skill.
- Establish required Task ID and tracker anchors for `write-task-spec` only when project policy makes that handoff explicit.
- Apply canonical spec linkage and the implementation-ready status only from a
  verified `publish-planning-change` handoff when that workflow is configured.
- Let `execute-project-task` establish implementation start and local-review checkpoints.
- Let `deliver-reviewed-change` establish PR, review, merge-readiness, and merge checkpoints.
- Use `record-project-context` before changing local project documentation or rolling task context; do not copy GitHub operational state into memory.
- Use the general GitHub workflow only for broad orientation that is outside this task-management contract.
