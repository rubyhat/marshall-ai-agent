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
configuration schema v4. Treat every other project-configuration version as
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
  project configuration, scope guards, a positive `max_correction_rounds`
  value that defaults to `5`, and an explicit process working directory bound
  to the exact planning worktree rather than the checkout from which the
  publication alias was invoked. Count correction packages rather than
  findings, review the final allowed corrected head, and fail closed instead of
  resetting or resuming automatically when the exact counter and round history
  cannot be proven. Materialize the required `committed_correction_review`
  strategy as `local_checkpoint_committed_base_diff`: explicitly allow one
  local checkpoint commit, require deterministic checks first, restrict it to
  the exact publication manifest, and set push-before-clean-review to false. Do
  materialize this dormant policy for every configured project so a later
  correction does not require a mid-publication configuration mutation;
  activate it only when a correction package after a non-clean review changes a
  manifest that already has an in-scope planning-branch commit or when a mixed
  committed-plus-uncommitted candidate must be checkpointed before its first
  review. Preserve the
  separately bound uncommitted-review path only when the manifest has no
  in-scope commit relative to the canonical base. Reject a mixed
  committed-plus-uncommitted candidate before model invocation; create an
  explicitly authorized clean checkpoint and review the complete candidate with
  the committed-base selector. Materialize the provisional implementation-ready
  target verdict before the first review manifest and preserve it across bounded
  content corrections. Require every changed semantic manifest to receive one
  review, and
  stop before checkpoint creation when an excluded dirty path would prevent a
  clean worktree; do not absorb, stash, or delete that path. Do not generate
  persistent state, locks, archives, migrations, or crash-recovery machinery
  for this counter;
- the canonical authoritative-session review runner, required command-template
  placeholders including every configured settlement value and the bounded
  reviewer invocation timeout, strict native
  terminal-result schema, exact parent/child/cwd/
  target binding, two stable settlement scans, final rescan, cumulative usage,
  and one technical retry only after settled absence of any authoritative
  terminal result. Materialize settlement intervals as whole seconds and
  require settlement timeout strictly greater than interval. Reject a direct `codex review`
  command template;
- deterministic validation, commit, push, PR, checks, merge, canonical-revision,
  specification-owner ancestry, exact-task publication evidence, sync, and
  cleanup gates; require an ordinary publication record with evidence kind,
  Task ID, owner repository, canonical spec path, PR URL, merged revision/tree,
  bound reviewed-head revision/tree, full package path/mode/blob-OID manifest,
  reviewer run identity and clean-verdict metadata, review base/target/binding
  method, capture-contract revision, publication-attempt ID, normalized-result
  hash, complete matched reviewer session set, and explicit reviewed-versus-
  merged manifest equality. Reread every field before cleanup, and never
  require a component repository with a separate Git history to contain that
  commit;
- when `execute-project-task` is also selected,
  `legacy_ready_adoption.enabled: false` and ordinary reviewed publication as
  the only implementation-readiness path. Keep historical baseline tuples as
  audit input only. Generate the typed `publication_upgrade_required` stop,
  stale-published-ready correction entry, complete ready-spec inventory,
  status-preserving reconciliation, mandatory post-merge rescan, and zero-old-
  evidence-ready completion predicate;
- `planning_artifact_publication` as a separately allowed planning-session
  capability that does not release implementation or delivery locks;
- a `--publish-spec` handoff after `Spec ready` and a hard implementation gate
  until the reviewed spec is merged into the canonical target.

When `execute-project-task` is selected, generate:

- the implementation-start tracker checkpoint after readiness succeeds and
  before implementation worktree or feature-branch creation.
- when `publish-planning-change` is not selected, keep the required
  `implementation` section empty and omit publication evidence, publication
  ancestry and manifest gates, `publication_upgrade_required`, and every
  `--publish-spec` alias or handoff. Resolve readiness only from the remaining
  selected modules and project policy; do not route execution to an unavailable
  publisher.

When both `execute-project-task` and `publish-planning-change` are selected,
also generate a hard rule that any task-owned specification or annex correction
during implementation invalidates the selected publication evidence, stops
  task-code edits, returns the correction through `write-task-spec` and
  `publish-planning-change`, and reruns the complete readiness gate against the
  new persisted publication record before implementation resumes. Require the
  readiness gate to rebuild the complete task-owned package manifest at the
  current specification-owner authority base and compare every path/mode/blob OID
  with the selected record.

When `deliver-reviewed-change` is selected, generate:

- one immutable delivery baseline bound to the exact task, specification or
  equivalent contract, acceptance criteria, non-goals, initial complete diff
  manifest, and initial diff statistics;
- separate positive `max_correction_rounds` values for local independent review
  and GitHub pull-request review, each materialized as `5` and forbidden from
  exceeding `5`;
- one correction round as one coherent review-driven correction package, with
  multiple findings from one result grouped together and technical retries or
  unchanged-head contextual re-reviews consuming no round;
- a fresh review of the candidate produced by the final allowed round, followed
  by fail-closed stop before mutations when another package would be required;
- ordered local and GitHub correction histories retained across resume, with a
  new PR head resetting only technical request attempts and lost history
  stopping delivery instead of resetting either counter;
- one independent GitHub correction counter and ordered history per pull
  request: each PR starts at zero, later heads of the same PR preserve it, and
  different PRs never share or synchronize correction state;
- a compact machine-readable pre-PR state block owned by the retained current
  Codex task, containing the baseline and local correction state only, updated
  and read back after every local transition, then copied into each new PR
  heartbeat before that PR initializes its GitHub counter and history to zero;
- authoritative local correction state refreshed and read back from that task
  block into the exact PR heartbeat before every GitHub generation after proving
  the same baseline, while preserving all PR-owned GitHub state unchanged;
- one single exact-PR heartbeat for active and paused GitHub state: pause it for
  every review-terminal outcome while the PR remains open, reactivate that same
  heartbeat only for an authorized later head of the same PR, and delete it only
  after provider evidence proves that exact PR merged or closed; never copy its
  terminal state into retained current-task state or another PR; before every
  workflow-owned push that changes the PR head, require that heartbeat to persist
  and read back a paused finding state, then reactivate it only after the pushed
  head is proven;
  store the PR head observed at terminal transition as `terminal_head_sha`,
  distinct from the generation `head_sha`, and compare resume with the observed
  terminal head, including after `head_mismatch`; require pause without deletion
  when exact PR identity or required state cannot be proven, updated, or read
  back;
- a provisional exact-PR heartbeat created and read back before any remote
  review request, then updated and read back with the proven request identity;
  require the same addressable-heartbeat and request-identity transition for
  every initial, retry, and contextual request;
  require an unchanged terminal head from a paused heartbeat to return its
  recorded outcome without posting another review request, and require a later
  authorized head of the same PR to reuse and reactivate that heartbeat;
- one centralized `finalize_codex_review_state` procedure with an exhaustive
  terminal-reason matrix; require every terminal branch to call it and forbid
  duplicated pause, reactivation, or deletion rules in branch runbooks;
- bounded cycle analysis on exhaustion and scope-drift gates that reject
  generalized hardening, unsubstantiated edge cases, unrelated defects, and
  unexplained material cumulative diff growth.

Require the local reviewer and reviewer-visible pull-request context to receive
the exact task contract, acceptance criteria, non-goals, and complete current
diff without implementation discussion or an intended verdict. Require every
actionable finding to name a concrete current-task failure or credible mandatory
risk before it may authorize a correction package.

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
