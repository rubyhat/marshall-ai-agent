# Context loading model

Use this reference when deciding which project source owns a fact, which source to read first, or how to handle conflicting context.

## Separate reusable policy from project routing

Keep the loading method in the reusable skill. Read project-specific values from project instructions, workflow configuration, and the context map:

- repository names and ownership;
- paths to memory, specs, runbooks, and architecture;
- domain-to-source routes;
- required safety or workflow documents;
- historical and archive locations;
- issue and pull-request conventions.

Do not hardcode one project's paths into the reusable skill.

## Build a task frame

Determine:

- requested outcome;
- task identity;
- work type;
- owning repository;
- product or technical domain;
- explicit source links;
- current versus historical intent.

Treat an explicit path, task ID, issue, pull request, or decision name as a stronger anchor than a general keyword match. Use the current branch or changed paths only as supporting evidence.

## Use source layers

### Direct

Use the artifact explicitly attached to the work:

- active task spec;
- issue or pull request;
- named file;
- active task pointer;
- user-provided material.

### Constraint

Load only constraints applicable to the framed task:

- project and repository instructions;
- security, privacy, tenancy, migration, or production gates;
- required product or engineering workflow.

### Canonical

Use current-state sources for reusable facts:

- architecture;
- engineering rules;
- repository or domain memory;
- current known-issues registry;
- current API or data contract.

Search for the relevant section instead of reading a multi-domain document in full.

### Operational

Load a runbook, template, or environment guide only when the next action requires it. Do not load test, deploy, migration, or review procedures during unrelated orientation.

### Historical

Treat completed specs, progress logs, reports, session notes, and archives as cold sources. Load them only through an exact link or a stated historical gap.

## Resolve conflicts

Evaluate:

1. ownership: which source is designated as canonical;
2. status: active, current, superseded, completed, or archived;
3. freshness: whether the fact can become stale;
4. evidence: source file, code, issue, pull request, command output, or external documentation;
5. scope: whether both statements apply to different repositories, tenants, versions, or lifecycle stages.

Do not silently merge incompatible statements. Prefer a clearly owned current source; otherwise surface the conflict before taking an action that depends on it.

## Handle missing routing

When no project configuration or context map exists:

1. Start from explicit user anchors.
2. Inspect the workspace only shallowly for instructions and obvious canonical documents.
3. Read the smallest plausible source set.
4. State an assumption only when it affects the task.
5. Avoid creating configuration or documentation from this read-only skill.
