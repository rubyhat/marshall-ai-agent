# Generate Project Setup

Generate only the files and sections listed in the approved manifest.

## Preserve existing structure

- Reuse explicit coherent docs, memory, task, template, and workflow roots.
- When no explicit coherent convention exists, create `docs_ai` for project
  documentation, `docs_ai/tasks` for task specifications, and
  `local_memory_ai` for internal memory without asking the user to choose path
  names. Record the defaults in the manifest and allow an explicit user
  override.
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

Use `assets/project-workflow.schema.json` as the generic contract and
`assets/templates/project-workflow.yaml` as a starting shape. Generate project
configuration schema v3. Treat every other project-configuration version as
unsupported and regenerate it only through an approved reconfiguration manifest
that materializes every current required field. Do not apply compatibility
defaults from an older project schema. The setup-state tracker has its own
schema version and is not changed by this rule.

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
- applicable task, spec, planning-publication, implementation, delivery,
  context, and domain sections.

Generate only aliases listed in the approved
`modules.enabled_aliases` setup-state field. For every ordinary alias, require
its owning module to be selected. For every conditional alias, additionally
require every module in its catalog `requires` list. Never advertise an alias
excluded from the approved enabled set or an ineligible conditional alias in
configuration, `AGENTS.md`, or the project command catalog.
Add alias-specific interaction settings such as the bounded
`--accept-recommended` scope only when the owning module and alias are enabled.
For a roadmap-shaping alias, generate:

- a required shaped-outcome or exact-anchor input and an explicit route back to
  ordinary shaping when product meaning remains unstable;
- one coherent Epic/Feature/Task iteration with only
  decomposition-changing questions;
- one exact semantic mutation preview whose stable node keys do not promise
  provider numbers or final Task IDs;
- a single post-approval handoff to task management, with a fresh preview when
  reconciliation changes semantics but not when identity is mechanically
  derived from a provider number;
- no local roadmap, memory, coordination, or documentation artifact.

When task management is enabled and the provider supplies an immutable,
human-visible Issue number, generate provider-number-derived Task IDs as the
safe default. Record semantic prefixes and a cross-repository-safe namespace,
record a project-neutral correlation-marker format such as
`project-task-key` for every new task, create or recover the Issue by that
deterministic semantic marker before deriving the ID, and preserve existing
legacy IDs. For roadmap manifests, namespace each task key with the stable
roadmap-operation key. Generate a separate
custom allocator only when an explicit coherent project convention requires
it or the provider lacks a suitable immutable number.

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

When `publish-planning-change` is selected, generate:

- canonical spec owner and default `docs_ai/tasks` root unless an explicit
  coherent project convention overrides it;
- an isolated planning worktree and task-scoped branch policy;
- exact primary/supporting artifact classes and forbidden implementation,
  release, deployment, production, secret, and unrelated paths;
- fresh independent spec-review configuration with model and effort owned by
  project configuration, scope guards, a positive explicit
  `max_correction_rounds` value defaulting to five, separate bounded request
  attempts, a non-tracked atomic review-cycle record under the specification
  owner's Git common directory that uses a per-attempt atomic-`mkdir` lock and
  monotonic state revision, reserves rounds before correction, stops rather
  than resets on missing or ambiguous resume state, and archives complete
  consumed-round history before a user-accepted material reshaping can start a
  replacement attempt; plus an explicit process working directory bound to the
  exact planning worktree rather than the checkout from which the publication
  alias was invoked;
- deterministic validation, commit, push, PR, checks, merge, canonical-revision,
  specification-owner ancestry, exact-task publication evidence, sync, and
  cleanup gates; require an ordinary publication record with evidence kind,
  Task ID, owner repository, canonical spec path, PR URL, merged revision/tree,
  bound reviewed-head revision/tree, full package path/blob-OID manifest,
  reviewer run identity and clean-verdict metadata, review base/target/binding
  method, and explicit reviewed-versus-merged manifest equality. Reread every
  field before cleanup, and never require a component repository with a
  separate Git history to contain that commit;
- for an existing project with specifications already marked implementation-ready
  on the canonical target, capture its exact full Git object ID before workflow
  mutations as an adoption baseline without asking the user to choose one.
  Accept full 40-hex SHA-1 and 64-hex SHA-256 object IDs. Require that baseline
  to be an ancestor of the current specification-
  owner authority base. Enable legacy-ready adoption only when the deterministic
  current package manifest of every task-owned spec path and Git blob OID must
  equal its baseline manifest, the ready verdict existed at that baseline, the
  evidence revision is derived from the last package change at or before the
  baseline, the complete sorted baseline manifest is persisted and compared on
  every readback, and the record is explicitly classified as
  `legacy_ready_baseline` rather than an independent review. Disable this path
  for a new project or when no pre-adoption ready specifications exist;
- `planning_artifact_publication` as a separately allowed planning-session
  capability that does not release implementation or delivery locks;
- a `--publish-spec` handoff after `Spec ready` and a hard implementation gate
  until the reviewed spec is merged into the canonical target.

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
boundary before implementation and implementation delivery. A configured
`--publish-spec` may publish only one exact reviewed planning manifest inside
the planning session. Do not describe it, an implementation alias, or a
delivery alias as an implicit release of the sticky planning profile.

Use assets from owning skills for task-spec or reference templates. Do not duplicate those assets in this skill.

## Reread and verify

After every write:

1. reread the generated file;
2. confirm placeholders are resolved;
3. confirm links and paths;
4. confirm user content is preserved;
5. confirm one source owns each durable fact;
6. update the manifest result.
