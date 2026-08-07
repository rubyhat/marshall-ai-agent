---
name: configure-project-workflow
description: Safely initialize, resume, audit, or reconfigure a project to use a selected set of reusable Codex workflow skills. Use when the user asks to set up the workflow kit in a new or existing repository, invokes `--workflow-setup` or `--workflow-check`, wants to add or remove workflow modules, needs a resumable configuration interview, or wants project-specific `AGENTS.md`, `.codex/project-workflow.yaml`, project topology, memory, documentation, templates, aliases, and active skill installation generated and validated. Inspect read-only first, ask staged questions, track current setup state, preview an exact mutation manifest, and require approval before applying it. Do not use for ordinary project work, implementation, broad repository execution, production access, or directly editing the reusable skill library.
---

# Configure Project Workflow

Bootstrap or reconcile one project workflow without copying another project's assumptions, losing existing instructions, or turning setup into implementation work.

## Keep the responsibility bounded

- Own safe project inspection, workflow-module selection, staged configuration interview, setup-state tracking, mutation preview, approved generation, installation reconciliation, and setup validation.
- Configure selected reusable skills; do not execute their ordinary product, task, QA, review, or delivery workflows during setup.
- Treat the central workflow-kit repository as reusable source, the active Codex skill directory as installation, and the target repository as owner of project-specific configuration and documentation.
- Preserve existing project conventions when they are coherent. Recommend `docs_ai` and `local_memory_ai` only when no better project structure exists.
- Route changes to reusable skill behavior through the system `skill-creator`; never silently edit the central library or an installed copy.

## Choose one mode

- `initialize`: configure a project that has no established workflow-kit configuration.
- `resume`: continue from the exact current setup tracker.
- `reconfigure`: add, remove, or change configured modules and policies through a bounded diff.
- `audit`: inspect the current setup read-only and report inconsistencies without repairing them.

Treat `$configure-project-workflow` and `--workflow-setup` as initialize, resume, or reconfigure authority according to discovered state. Treat `--workflow-check` as read-only audit authority.

## Establish authority

An initialize, resume, or reconfigure request authorizes:

- bounded read-only inspection within the exact target project root;
- creation or update of only `.codex/project-workflow.setup.json`;
- staged questions and a proposed exact mutation manifest.

It does not authorize installing skills, overwriting project files, changing Git state, contacting external services, running project code, or creating the final structure. Apply those mutations only after the user approves the exact current manifest.

Audit mode authorizes no file mutation, including no setup tracker.

## Enforce the setup safety gate

Read [setup-safety-boundary.md](references/setup-safety-boundary.md) before inspecting the project.

Present the non-negotiable default protection boundary and ask whether the user wants to add project-specific restrictions. User additions may tighten the boundary but cannot weaken higher-priority safety, privacy, access, or production rules.

Stop when safe inspection would require a forbidden read, execution, network action, credential, production access, or scope expansion.

## Run the setup workflow

### 1. Inspect without executing

Read [inspect-project.md](references/inspect-project.md). Use `scripts/inspect_project.py` when Python 3.9+ is available.

Determine existing repositories, candidate components, manifests, frameworks, instructions, architecture sources, documentation, CI metadata, workflow artifacts, and conflicts. Use this evidence to prepare a provisional project-topology model without inventing ownership or deployment boundaries. Record each fact as `detected`, `conflict`, `unknown`, or `not_applicable` with provenance and confidence. Do not infer sensitive or production state from filenames alone.

### 2. Create or resume one tracker

Read [setup-state-and-resume.md](references/setup-state-and-resume.md).

For non-audit modes, create or update only:

```text
.codex/project-workflow.setup.json
```

Keep current state rather than a session transcript. Validate it with `scripts/validate_setup_state.py` after each material stage and before presenting a manifest.

### 3. Select a provisional profile

Read [select-workflow-modules.md](references/select-workflow-modules.md) and `assets/workflow-modules.json`.

Recommend the smallest profile that covers the project's actual work. Resolve required dependencies, explain optional modules, and let the user adjust the selection. Do not install every skill merely because it exists.

### 4. Conduct the staged interview

Read [configuration-interview.md](references/configuration-interview.md).

Apply documented safe defaults for ordinary paths and low-risk conventions.
Ask only questions whose answers materially change safety, ownership,
capabilities, external mutations, lifecycle, or workflow behavior, plus factual
unknowns that inspection cannot resolve. Present small numbered rounds with
2–3 mutually exclusive options for material decisions and the recommended
option first. Summarize applied defaults so the user can override them; do not
turn every covered field into a question or use a question quota. Skip an
entire conditional stage when it is genuinely not applicable.

After each stage:

1. normalize the answers;
2. update decisions, assumptions, conflicts, and deferred topics;
3. validate the tracker;
4. state the completed stage and remaining stages;
5. resume at the first unresolved stage after any detour.

### 5. Preview the exact setup

Read [generate-project-setup.md](references/generate-project-setup.md).

Present:

- selected modules and dependencies;
- installation source, revision, and mode;
- exact create, update, install, and cleanup operations;
- managed `AGENTS.md` section;
- configuration, project-topology, and project-document destinations;
- preserved existing files and instructions;
- skipped modules and reasons;
- unresolved assumptions and blockers;
- validation plan.

Do not apply the manifest until the user explicitly approves this exact version. Rebuild and reapprove it after any material change.

### 6. Apply only the approved manifest

Read [install-and-sync-skills.md](references/install-and-sync-skills.md) before changing active skill installation.

Apply operations idempotently:

- preserve content outside generated managed sections;
- update existing canonical files instead of creating parallel copies;
- create only selected module structures and templates;
- never overwrite modified installed skills without a reviewed diff and approval;
- never delete project data when disabling a module;
- reread every generated or updated artifact.

### 7. Validate the resulting setup

Read [validate-project-setup.md](references/validate-project-setup.md).

Validate configuration structure, module dependencies, skill paths, active-copy identity, managed instruction routing, project-topology coverage and routing, aliases, sticky session constraints, capability gates, artifact output contracts, links, placeholders, safety policy, preservation of user content, and representative dry-run routes. Do not run project builds, tests, migrations, services, or network workflows as setup validation unless separately requested and authorized.

### 8. Close or preserve setup state

When validation passes and no setup decision remains unresolved:

1. promote final values to canonical configuration and docs;
2. report installed modules, generated artifacts, preserved files, and validation results;
3. delete `.codex/project-workflow.setup.json`;
4. stop without beginning ordinary project work.

Keep the tracker only when setup is incomplete, blocked, or intentionally paused.

## Handle customization without forking by default

Read [customize-or-extend-workflow.md](references/customize-or-extend-workflow.md) when the user requests behavior that the selected modules do not directly provide.

Prefer, in order:

1. project configuration;
2. an always-on project instruction;
3. a project runbook;
4. a project template;
5. a central reusable skill update through system `skill-creator`;
6. a new reusable skill with its own trigger and ownership.

Do not edit the central workflow kit during project setup.

## Coordinate with adjacent workflows

- Use the system skill installer or an equivalent configured installer only during an approved installation phase.
- Use `record-project-context` for durable project documentation produced by the approved setup.
- Use `maintain-project-context` only for a separately requested audit or cleanup of pre-existing context.
- Hand ordinary work to the configured runtime skills only after setup closes.
