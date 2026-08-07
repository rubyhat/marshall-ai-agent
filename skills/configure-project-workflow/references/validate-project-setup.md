# Validate Project Setup

Validate the configured workflow without executing ordinary project work.

## Structure

- Parse the setup tracker and generated configuration with an available safe parser.
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
  production mutation.
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
- Confirm `write-task-spec` hands file-backed specs to
  `publish-planning-change` before implementation and that
  `execute-project-task` has a canonical-publication gate when the module is
  selected.
- Confirm publication ancestry is required only in the repository that owns
  the specification revision. For implementation repositories with separate
  Git histories, require a resolvable exact-task publication tuple containing
  Task ID, owner repository, canonical spec path, and merged revision instead
  of impossible shared ancestry.

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
- finish a file-backed spec -> stop at `Spec ready` and recommend
  `--publish-spec` rather than implementation;
- publish a spec in a planning session -> allow only the exact planning
  publication manifest, require independent review, and preserve the
  implementation and delivery locks;
- request implementation with a local or PR-only unmerged spec -> stop before
  task lookup or workspace mutation and recommend `--publish-spec`;
- request implementation with a reviewed merged spec -> require the canonical
  revision in the specification-owner authority base and, for a separate
  component repository, require the exact-task publication tuple without
  shared ancestry;
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
