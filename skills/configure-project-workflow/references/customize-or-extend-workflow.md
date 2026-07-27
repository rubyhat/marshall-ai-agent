# Customize or Extend Workflow

Choose the narrowest extension layer that owns the requested behavior.

## Routing order

### 1. Project configuration

Use for values and switches such as repositories, paths, statuses, languages, providers, aliases, quality gates, and approval policy.

### 2. Always-on project instruction

Use for a project invariant that must apply without a skill trigger, such as tenant isolation, protected directories, or a mandatory safety rule.

### 3. Project runbook

Use for a project-specific sequence, command set, provider detail, or operational procedure.

### 4. Project template

Use when only the shape of a local artifact differs.

### 5. Existing reusable skill

Update the central skill through the system `skill-creator` when the behavior is broadly reusable, belongs to that skill's ownership, and should apply across projects.

### 6. New reusable skill

Create a separate skill when the behavior has its own user trigger, responsibility, authority boundary, and reusable workflow.

## Do not create hidden forks

- Do not edit `~/.codex/skills` as canonical source.
- Do not patch the central workflow-kit repository during project setup.
- Do not put project names or local absolute paths into reusable skills.
- Do not copy an entire reusable skill into a project for one configuration difference.
- Do not expand `configure-project-workflow` into runtime ownership.

When a central change is needed, record a bounded proposal and stop setup only if the project cannot be configured safely without it.

Create a dedicated library-maintenance skill later only if versioning, releases, synchronization, migrations, and compatibility management become a frequent independent workflow.
