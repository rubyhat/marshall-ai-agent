---
name: load-project-context
description: Load the minimum repository-specific context needed to start or resume a substantive project task. Use when beginning implementation, diagnosis, planning, review, QA, architecture, issue/spec work, or another project task; when resuming previous work; when the task, repository, or domain changes; or when resolving a referenced task ID, issue, PR, spec, or prior decision. Reuse an already sufficient orientation for follow-up messages in the same scope. Do not use for writing memory, creating project artifacts, auditing context health, cleanup, or generic self-contained questions.
---

# Load Project Context

Orient to the current task with progressive disclosure. Load enough evidence for the next justified action, not every potentially related project artifact.

## Preserve the read-only boundary

- Treat loading as read-only.
- Do not create or update memory, task notes, reports, maps, configuration, or specs.
- Do not archive, move, consolidate, or delete files.
- Do not change GitHub issues, pull requests, projects, or fields.
- Hand later recording to the project's recording workflow or skill.
- Hand audit and cleanup to the project's maintenance workflow or skill.

## Follow the loading workflow

### 1. Frame the task from existing signals

Collect the strongest available anchors before opening project documentation:

- the user's requested outcome;
- an explicit task ID, issue, pull request, spec, path, or decision;
- the current repository or worktree;
- the current branch or changed paths, only when they help identify scope;
- the task type, owning repository, and product or technical domain.

Reuse the current orientation when the conversation remains in the same scope. Restart orientation when the task anchor, repository, domain, or work type materially changes.

### 2. Resolve project routing

Respect already loaded instructions and do not reread them without a concrete need.

1. Locate the project workflow configuration named by project instructions.
2. Locate the context map referenced by that configuration.
3. Inspect the map's headings or index before reading a matching section.
4. Resolve the owning repository and then read any applicable nested instruction file.
5. Keep project-specific paths, domains, and required workflows in project configuration or the context map, not in this reusable skill.

If configuration or a context map is absent, use explicit task anchors and a shallow filesystem inspection. Do not compensate with a broad repository or documentation scan. Report the missing routing source only when it creates material uncertainty.

Read [context-loading-model.md](references/context-loading-model.md) when source ownership, priority, or freshness is ambiguous.

### 3. Select sources by relevance

Prefer sources in this order:

1. Direct task anchors: the named spec, issue, pull request, file, or active task pointer.
2. Applicable constraints: project instructions, safety rules, repository instructions, and required workflows.
3. Canonical domain context: the relevant architecture, engineering rule, repository memory, or known issue section.
4. Operational context: a runbook, template, environment note, or test/deploy instruction required by the next action.
5. Cold history: completed specs, reports, session notes, progress logs, and archives.

Treat cold history as conditional. Do not load it merely because it is recent or adjacent to the task.

Read GitHub issue or pull-request state only when the task is explicitly linked to it and local sources do not establish the current state. Keep this access read-only.

### 4. Preflight before reading

Inspect candidate context documents before opening them:

- check their shape and size;
- inspect headings;
- search exact identifiers, paths, symbols, domains, and decision terms;
- select relevant ranges;
- keep command output bounded to the evidence needed.

Use semantic sufficiency rather than numeric read or output limits. Expand reading only to answer an identified question. Read [context-budget-and-search.md](references/context-budget-and-search.md) for the detailed runbook.

### 5. Recover previous work only when necessary

Use task ID, issue, spec path, branch, or active-task pointer before chronology. Never assume the latest session note belongs to the current task.

Read [recover-previous-task-context.md](references/recover-previous-task-context.md) only when resuming work or when canonical sources do not explain the current state.

### 6. Stop at sufficient orientation

Stop loading when all of the following are known well enough for the next action:

- the task anchor and expected outcome;
- the owning repository and affected domain;
- the current source of truth;
- the applicable hard constraints and safety gates;
- the next action;
- any remaining uncertainty that could change that action.

Do not continue reading for completeness. If sources conflict, identify the conflict, prefer the current canonical source when ownership and freshness are clear, and ask only when the unresolved choice materially changes the work.

## Communicate compactly

Do not create a context report or manifest file. Keep a compact working orientation containing:

- task anchor;
- scope;
- sources used;
- applicable constraints;
- material unknowns.

Mention the orientation to the user only when it clarifies scope, exposes a conflict, or explains a blocking question.
