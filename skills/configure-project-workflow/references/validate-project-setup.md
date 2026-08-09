# Validate Project Setup

Validate the configured workflow without executing ordinary project work.

## Structure

- Parse the setup tracker and generated configuration with an available safe parser.
- Require project configuration schema v4. Treat every other project schema as
  unsupported and report setup drift; do not apply compatibility defaults or
  treat any selected workflow as configured until an approved reconfiguration
  produces one complete schema-v4 configuration.
- Verify required generic fields and selected module sections.
- Verify unique module names, aliases, paths, and managed markers.
- Verify every alias has a resolvable owning workflow, authority boundary,
  prerequisites, and sequence-mismatch behavior.
- Verify every alias maps to a capability when session profiles are enabled.
- Verify sticky negative session constraints are evaluated before
  alias-specific authority and task readiness.
- Verify each session profile has explicit lifetime, precedence, allowed or
  blocked capabilities, and release semantics.
- Verify natural-language requests use the same capability gate as aliases.
- Verify every enabled conditional alias has all modules declared by its
  catalog `requires` list, and that ineligible conditional aliases are absent
  from configuration, routing, and the project command catalog.
- For a next-specification continuation alias, verify unambiguous continuity
  resolution, read-only prior-completion checks, dependency-graph selection,
  parallel-candidate handling, explicit specification authority, and no
  previous-task status mutation.
- For a roadmap-shaping alias, verify a shaped-outcome prerequisite, one
  coherent semantic manifest preview, a single approved task-management
  handoff, semantic reapproval rules, no predicted Issue numbers or Task IDs,
  and no local roadmap or coordination artifact.
- When provider-number-derived task identity is configured, verify that new
  tasks are recovered by a deterministic semantic marker, created before Task
  ID derivation, use a cross-repository-safe namespace, and preserve existing
  legacy IDs. For multi-node manifests, verify combined dependency and
  parent-to-child precedence with cycle detection.
- When planning publication is selected, verify `--publish-spec` maps only to
  `planning_artifact_publication`, is allowed without releasing the planning
  profile, requires one exact task/spec anchor, and cannot authorize
  implementation, implementation delivery, Issue closure, release, deploy, or
  production mutation. Verify the independent reviewer process runs with the
  exact planning worktree as its working directory so an uncommitted review
  cannot accidentally inspect the clean main checkout. Require the reviewer
  worktree, placeholder, branch-readback, bound-review evidence, and publication
  completion fields to be materialized in the current configuration. A missing
  field must fail validation and must not fall back to the invoking checkout.
- Verify no unresolved template placeholders.
- Verify every generated relative link.
- Verify no configured path escapes its intended root.
- When no explicit coherent project convention overrides it, verify project
  docs, task specs, and internal memory use `docs_ai`, `docs_ai/tasks`, and
  `local_memory_ai` without an unresolved path-selection question.
- Verify `paths.project_topology` resolves to exactly one canonical topology
  artifact.
- Verify every configured repository or deployable unit has one topology entry
  with a stable key, purpose, type, lifecycle, local or explicitly external
  path, remote repository or explicit `not_applicable`, task scope, owner, and
  deploy boundary.
- Verify topology routing resolves applicable instructions, architecture,
  context or memory, and runbooks without embedding their detailed content.
- Verify directional dependency edges use known component keys or explicitly
  named external systems and that the map does not compete with architecture,
  task, or operational sources of truth.
- Verify persistent report types have a configured destination and that
  file/link/path-only output rules do not conflict.

Do not install a parser or dependency automatically. If no YAML parser is safely available, validate the approved setup state, generated text structure, and a full agent readback, then report the parser limitation.

## Module graph

- Validate required dependencies from `assets/workflow-modules.json`.
- Confirm selected modules match configuration and `AGENTS.md` routing.
- Confirm disabled or removed modules have no active alias or generated routing.
- Confirm domain handoffs target installed modules.
- When `publish-planning-change` is selected, confirm `write-task-spec` hands
  file-backed specs to it before implementation. When
  `execute-project-task` is also selected, confirm execution has a
  canonical-publication gate.
- Confirm `execute-project-task` establishes its implementation-start status
  after readiness and before workspace creation.
- When `publish-planning-change` is selected, require the canonical runner
  command template rather than direct `codex review`, all runtime placeholders,
  including every configured settlement value and the bounded reviewer
  invocation timeout,
  exact parent/child/cwd/target binding, strict native terminal JSON, one
  technical retry only after settled absence, at least two stable scans,
  bounded whole-second interval values, settlement timeout strictly greater
  than interval, final rescan, cumulative token capture, and
  the full current provenance tuple in publication evidence.
- When `execute-project-task` is selected without `publish-planning-change`,
  require an empty implementation section; reject publication readiness,
  evidence, ancestry and manifest gates, `publication_upgrade_required`, and
  the unavailable `--publish-spec` alias or handoff. Confirm the installed
  execution skill skips those gates when publication is not configured.
- When `deliver-reviewed-change` is selected, confirm that local and GitHub
  review have separate positive correction-round limits set to five and unable
  to exceed five,
  share one immutable exact-task delivery baseline, retain independent ordered
  histories across resume, and stop before a correction beyond either limit.
  Confirm a new PR head resets only technical request attempts, the final
  allowed correction still receives review, lost history fails closed, and a
  bounded cycle analysis is required on exhaustion or material scope drift.
  Require one machine-readable pre-PR state block in the retained current Codex
  task, update/readback after every local transition, and exact transfer into
  the first GitHub heartbeat. A different conversation without proven state
  must not reset or resume the counters automatically.
  Confirm every later GitHub generation refreshes and reads back authoritative
  local correction state from that task block into the exact PR heartbeat after
  baseline verification, without replacing the heartbeat's PR-owned GitHub
  state.
  For multi-repository delivery, require one independent GitHub correction
  counter per PR: a new PR starts at zero, a new head preserves the same PR's
  counter, and different PRs do not share or synchronize counters, histories,
  dismissed-finding fingerprints, heartbeat state, or terminal state. Require
  one exact-PR heartbeat to own both active and paused GitHub state. Confirm
  every review-terminal outcome pauses that heartbeat while the PR remains
  open, an authorized later head of the same PR reactivates that heartbeat, and
  only provider-proven merge or close permits deletion. Require every
  workflow-owned push that changes the PR head to begin only after that heartbeat
  persists and reads back a paused finding state, so its monitor cannot classify
  the controlled push as an external `head_mismatch`. Confirm it stores the PR
  head observed at terminal transition as `terminal_head_sha`, separate from the
  generation `head_sha`, and uses the observed terminal head for resume,
  including `head_mismatch`. If exact PR identity or required state is not
  provable, require pause without heartbeat deletion or fabricated state.
  Confirm a provisional exact-PR heartbeat is persisted and read back before a
  remote review request, then updated and reread with proven request identity.
  Confirm every retry and contextual request uses the same heartbeat and
  request-identity transition before monitoring.
  Confirm an unchanged terminal head in a paused heartbeat returns its recorded
  outcome without another review request and a later authorized same-PR head
  reuses that heartbeat instead of creating a replacement.
  Confirm one `finalize_codex_review_state` procedure owns the exhaustive
  terminal-reason matrix and every terminal branch delegates to it without
  duplicating mutation rules.
- Confirm reviewer context is bound to the exact task contract, acceptance
  criteria, non-goals, initial diff manifest and statistics. Generalized
  hardening, unsubstantiated edge cases, unrelated defects, and unexplained
  material cumulative diff growth must not silently expand delivery scope.
- When `publish-planning-change` is also selected, confirm that a later
  task-owned specification-package correction invalidates the selected
  evidence, requires a new canonical publication record, and reruns readiness
  before task-code edits resume. Require current-authority-base package
  path/mode/blob-OID equality with the selected record; checking only the record's
  older merged revision is insufficient. Do not route a selective installation
  to an unselected publication module.
- When `publish-planning-change` is selected, confirm publication ancestry is
  required only in the repository that owns
  the specification revision. For implementation repositories with separate
  Git histories, require the same resolvable exact-task reviewed-publication
  record without impossible shared ancestry. Verify it binds the clean reviewer
  run, capture-contract revision, publication-attempt ID, normalized-result
  hash, complete matched-session set, and package manifest to the reviewed head
  and merged revision, is persisted and reread before cleanup, and does not
  rely on PR prose.
- When `publish-planning-change` is selected, verify legacy-ready adoption is
  materialized as disabled and ordinary current capture-contract publication is
  the only accepted implementation evidence path, including workspace creation
  in a separate repository. Old or incomplete records must return typed
  `publication_upgrade_required` before workspace mutation, preserve historical
  evidence for audit, downgrade only exact implementation-ready operational
  status, keep every other configured status audit-only, and require a
  post-merge rescan plus zero-old-evidence-ready completion readback.

## Installation

- Run system `quick_validate.py` for each installed skill when available.
- Compare active copies with the approved source.
- Verify `agents/openai.yaml` default prompts name the correct skill.
- Verify all selected modules came from the same recorded revision.
- Require an exact release tag or full commit SHA for reproducible centralized
  or vendored installation.
- Treat a floating branch or dirty symlink source as explicitly
  non-reproducible and report it in the verdict.
- Report modified or unavailable active copies.

## Safety and preservation

- Confirm project-specific protection additions are recorded.
- Confirm default protection was not weakened.
- Confirm content outside managed `AGENTS.md` markers remains intact.
- Confirm setup did not touch Git state, external services, project code, production, or unapproved paths.
- Confirm no secret, credential, token, or sensitive value entered generated files.

## Dry-run routing

Evaluate representative prompts without performing their mutations:

- start a planning-only conversation -> planning-session profile;
- start a substantive task -> context loading;
- discuss a new idea -> shaping;
- request roadmap decomposition from a shaped outcome -> one semantic preview
  before tracker mutations, followed by Issue-first identity establishment only
  after approval;
- request a full spec -> configured task/spec handoff;
- when planning publication is selected, finish a file-backed spec -> stop at
  `Spec ready` and recommend `--publish-spec` rather than implementation;
- when planning publication is selected, publish a spec in a planning session
  -> allow only the exact planning
  publication manifest, require independent review, and preserve the
  implementation and delivery locks;
- when planning publication is selected, request implementation with a local or
  PR-only unmerged spec -> stop before task lookup or workspace mutation and
  recommend `--publish-spec`;
- when planning publication is selected, request implementation with a reviewed
  merged spec -> require the canonical
  revision in the specification-owner authority base and, for a separate
  component repository, require the exact-task publication tuple without
  shared ancestry;
- when planning publication is selected, request implementation for an old or
  pre-adoption ready spec -> return typed `publication_upgrade_required` with
  `workspace_created: false` and recommend exact `--publish-spec <Task ID>` even
  when a historical baseline matches;
- when `execute-project-task` is selected without planning publication, request
  implementation with all remaining configured readiness gates satisfied ->
  continue without publication evidence or a `--publish-spec` handoff;
- request the next spec with one active work graph -> verify the previous task
  read-only, select the unique next eligible task by dependencies, and enter
  the configured specification workflow;
- request the next spec with ambiguous continuity or equivalent parallel
  candidates -> stop before mutations and ask for the exact anchor or choice;
- accept current recommendations -> only the latest recommended question set;
- request implementation -> readiness and explicit authority gate;
- request delivery -> exact endpoint gate;
- planning session then request implementation -> stop before task lookup or
  mutations and require the configured release action;
- planning session then request delivery -> stop before review or delivery
  mutations and require the configured release action;
- planning session then request a specification -> permit only the bounded
  specification workflow;
- natural-language current-session no-code constraint then request
  implementation -> stop as for the equivalent alias;
- request a transferable handoff report -> use the configured persistent
  destination;
- request a path-only report response -> return only the verified path;
- start a task naming one component -> resolve its topology entry before its
  nested instructions and context route;
- start a cross-component task -> load only the named dependency edges and the
  owning sources for affected components;
- report a frontend defect when QA is selected;
- request external reference analysis when selected;
- run `--workflow-check` -> read-only audit.

For `--workflow-check`, compare the bounded inspector's component candidates
with configuration and the topology map. Report an unclassified active
component, a missing configured component, an unresolved route, or a
repository/topology mismatch as drift. Do not repair it in audit mode. A
candidate alone is not proof of a deployable service; preserve it as an
explicit question when classification is uncertain.

## Verdict

Return exactly one:

- `Setup ready`;
- `Setup incomplete`;
- `Setup blocked`;
- `Setup drift detected`.

Delete the tracker only for `Setup ready` with no unresolved material state.
