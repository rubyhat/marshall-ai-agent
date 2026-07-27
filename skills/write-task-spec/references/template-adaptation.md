# Adapt default templates to a project

Bundled templates are generic source material, not a replacement for project policy.

## Keep sources separate

- Treat `assets/templates/` as immutable reusable defaults.
- Copy selected templates into the project's configured template location.
- Adapt only the project-local copies.
- Record project-local paths and required modules in project configuration.
- Do not rewrite existing completed specs when a template changes.

## Adapt project metadata

Configure:

- document language;
- task identity and tracker fields;
- owner or repository fields;
- parent and dependency references;
- status or readiness vocabulary;
- spec destination and naming;
- required links.

Remove fields the project does not use.

## Adapt content modules

Add or specialize only applicable policies, such as:

- architecture and repository boundaries;
- migration classifications and commands;
- localization languages and parity gates;
- security, privacy, tenant, or production-data rules;
- legal, billing, or consent review;
- accessibility and UX requirements;
- observability, deployment, or release checks;
- QA depth by priority and risk.

Keep project-specific commands, paths, framework details, and status labels in project configuration, workflows, or project-local templates.

## Preserve the fallback

When no project-local template exists, use the generic defaults:

- `assets/templates/full/task.md`;
- `assets/templates/lightweight/task.md`;
- optional annexes under `assets/templates/annexes/`.

Write the generated spec in the configured project language even when the fallback template headings are English.

## Evolve templates safely

- Update templates prospectively.
- Do not mass-migrate historical specs for consistency alone.
- Validate project-local changes against at least one realistic full and lightweight task.
- Keep core information scannable and move only conditionally large detail to annexes.
- Avoid adding a mandatory section when a configured impact field or linked workflow already owns the same information.
