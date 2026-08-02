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

When context modules are selected, create `memory` and include only the exact
child policy owned by each selected module:

- `load-project-context` -> large or mixed artifact preflight,
  section-targeted loading, and full reads only for an identified semantic need
  that bounded reads cannot answer;
- `record-project-context` -> canonical current-state-only recording,
  update-before-create behavior, and exclusion of task chronology, completion
  logs, and duplicated tracker state from canonical memory;
- `maintain-project-context` -> manual-only maintenance,
  audit-before-cleanup, exact manifest approval, section-level compaction for
  mixed canonical artifacts, diagnostic-only size or chronology metrics, and
  explicit reference roots used to count incoming links without expanding a
  bounded candidate scope.

Removing a context module removes its child policy from generated
configuration after the approved reconfiguration manifest; it does not remove
other selected context policies or historical project artifacts.

When `record-architecture-decision` is selected, generate one
`architecture_decisions` section containing:

- canonical ADR root and index;
- ID and filename convention, including a bounded `<slug>` byte budget;
- distinct semantic lifecycle-status mapping and decision authority;
- project-specific materiality and review triggers;
- mandatory applicability review before forcing task conformance;
- new-ADR supersession policy that preserves old accepted rationale;
- bounded-exception and retrospective-recording policy.

Reuse a coherent existing decision library. When none exists, create the ADR
index from the owning skill's `assets/adr-index-template.md`; do not create an
empty folder or a speculative ADR. Add the ADR index as a conditional route in
the context map without making the complete decision library part of default
loading.

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
When the ADR module is selected, allow its read-only applicability review and
its exact lifecycle artifact set and index persistence inside planning. Do not
let that bounded document mutation expand into task, code, delivery,
deployment, or production authority.

Use assets from owning skills for task-spec or reference templates. Do not duplicate those assets in this skill.
Use the owning `record-architecture-decision` assets for ADR and index
templates. Do not copy their contents into setup references.

## Reread and verify

After every write:

1. reread the generated file;
2. confirm placeholders are resolved;
3. confirm links and paths;
4. confirm user content is preserved;
5. confirm one source owns each durable fact;
6. update the manifest result.
