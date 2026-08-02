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
- a compact alias-sequence guard that routes detailed behavior to configuration
  and the command catalog;
- always-on project safety and engineering invariants;
- minimal routing and authority boundaries.

Keep detailed procedures in skills and project runbooks.

## Generate compact configuration

Use `assets/project-workflow.schema.json` as the generic contract and `assets/templates/project-workflow.yaml` as a starting shape.

Include only selected modules. Record:

- workflow-kit source, revision, and installation mode;
- project identity and repositories;
- canonical project-topology path and its relationship to the machine-readable
  repository registry;
- language and interaction policy;
- paths and source-of-truth ownership;
- protection additions;
- selected skills and active paths;
- aliases;
- alias prerequisites, workflow-phase checks, and mismatch behavior;
- sticky session profiles, capability allow/block rules, precedence, lifetime,
  and release semantics;
- persistent artifact destinations and exact output-form precedence;
- applicable task, spec, implementation, delivery, context, and domain sections.

When `record-architecture-decision` is selected, generate an
`architecture_decisions` section containing:

- project-relative ADR root and index paths;
- ADR identifier and filename patterns;
- a mapping from the semantic `proposed`, `accepted`, `rejected`, `deprecated`,
  and `superseded` states to project labels;
- the approved `materiality_policy` used to distinguish an ADR from a
  task-local choice;
- an `applicability_policy` containing the evidence or review triggers that
  require read-only reassessment and the blocking `review required` and
  `unclear` results;
- required ADR sections and relative-link/index policy;
- decision authority and acceptable approval evidence for every lifecycle
  transition;
- mutation-preview and separate-confirmation policy;
- the invariant that a material change to an accepted ADR requires
  supersession.

Do not enable either ADR alias or generate ADR routing without the owning
module and its required `record-project-context` dependency. Do not create an
ADR directory, index, or placeholder record during setup unless that exact
artifact is part of the approved manifest.

Generate only aliases listed in the approved
`modules.enabled_aliases` setup-state field. For every ordinary alias, require
its owning module to be selected. For every conditional alias, additionally
require every module in its catalog `requires` list. Never advertise an alias
excluded from the approved enabled set or an ineligible conditional alias in
configuration, `AGENTS.md`, or the project command catalog.
Add alias-specific interaction settings such as the bounded
`--accept-recommended` scope only when the owning module and alias are enabled.
For a next-specification continuation alias, generate:

- current-conversation continuity first and an optional exact anchor fallback;
- read-only verification of the prior task through the configured task
  workflow, without automatic status repair;
- next-task selection from the canonical dependency graph rather than Task ID
  ordering;
- automatic continuation only for one uniquely eligible task;
- explicit user choice after a recommendation when parallel candidates are
  materially equivalent;
- the same explicit specification authority and implementation exclusion as
  the ordinary specification-preparation alias.

Do not copy project-specific values from an example project.

## Create project docs conditionally

Establish exactly one canonical project topology. Reuse an existing document
only when it already provides a compact, current index with the required
ownership and routing fields. Otherwise create `project-topology.md` from the
bundled template at the approved project-memory or documentation destination.
New projects should use a standalone topology file even for a single
repository so future components can be added without growing the general
project context.

The topology must remain an index, not an architecture document or task log.
Include:

- a stable component key, purpose, type, lifecycle, local path, remote
  repository, stack/package manager, compact entry point, task scope, owner,
  and deploy boundary for each component;
- direct paths to applicable instructions, architecture, context or memory,
  and operational runbooks;
- compact directional dependency or shared-contract edges;
- explicit `unknown` or `not_applicable` values instead of invented facts.

Keep detailed architecture, operational commands, task state, and historical
events in their owning sources and link to them. Keep the machine-readable
repository registry and topology map consistent, but do not duplicate the
whole topology into configuration.

Use bundled templates only when the project lacks an existing owner:

- `project-topology.md`;
- `project-context.md`;
- `engineering-rules.md`;
- `local-memory-map.md`;
- `agent-commands.md`.

The command catalog must explain each enabled alias, arguments, owning workflow,
authority boundary, prerequisites, terminal result, and recommended
sequences. Do not generate expanded prompt copies that duplicate `SKILL.md`;
the owning skill remains the procedural source of truth.

When planning-session behavior is enabled, show an explicit new-conversation
boundary before implementation and delivery. Do not describe a later
implementation or delivery alias as an implicit release of a sticky planning
profile.

Use assets from owning skills for task-spec or reference templates. Do not duplicate those assets in this skill.

## Reread and verify

After every write:

1. reread the generated file;
2. confirm placeholders are resolved;
3. confirm links and paths;
4. confirm user content is preserved;
5. confirm one source owns each durable fact;
6. update the manifest result.
