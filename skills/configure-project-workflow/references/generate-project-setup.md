# Generate Project Setup

Generate only the files and sections listed in the approved manifest.

## Preserve existing structure

- Reuse coherent docs, memory, task, template, and workflow roots.
- Recommend `docs_ai` and `local_memory_ai` only when the project has no suitable convention.
- Update canonical files rather than creating parallel sources of truth.
- Do not create empty module directories without an immediate tracked artifact.
- Do not rewrite completed historical specifications or reports.

## Manage root instructions

When creating or updating `AGENTS.md`, own only:

```markdown
<!-- marshall-ai-agent:start -->
...generated workflow routing...
<!-- marshall-ai-agent:end -->
```

Preserve all content outside the markers byte-for-byte when practical. If markers are malformed, duplicated, nested, or ambiguous, stop rather than guessing.

The managed section should contain:

- exact active skill names and triggers;
- exact resolvable paths;
- project configuration path;
- plain-text alias catalog path;
- always-on project safety and engineering invariants;
- minimal routing and authority boundaries.

Keep detailed procedures in skills and project runbooks.

## Generate compact configuration

Use `assets/project-workflow.schema.json` as the generic contract and `assets/templates/project-workflow.yaml` as a starting shape.

Include only selected modules. Record:

- workflow-kit source, revision, and installation mode;
- project identity and repositories;
- language and interaction policy;
- paths and source-of-truth ownership;
- protection additions;
- selected skills and active paths;
- aliases;
- applicable task, spec, implementation, delivery, context, and domain sections.

Do not copy project-specific values from an example project.

## Create project docs conditionally

Use bundled templates only when the project lacks an existing owner:

- `project-context.md`;
- `engineering-rules.md`;
- `local-memory-map.md`;
- `agent-commands.md`.

Use assets from owning skills for task-spec or reference templates. Do not duplicate those assets in this skill.

## Reread and verify

After every write:

1. reread the generated file;
2. confirm placeholders are resolved;
3. confirm links and paths;
4. confirm user content is preserved;
5. confirm one source owns each durable fact;
6. update the manifest result.
