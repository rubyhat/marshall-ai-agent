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
- Verify no unresolved template placeholders.
- Verify every generated relative link.
- Verify no configured path escapes its intended root.
- Verify the ADR ID regex can emit only non-empty portable identifier
  characters and that every concrete rendered ADR filename remains inside the
  configured ADR root on both POSIX and Windows path semantics.
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
- When architecture decisions are selected, verify one canonical ADR root and
  index, a complete semantic mapping for required lifecycle states, explicit
  filename convention, decision authority, materiality triggers,
  material-change supersession, review triggers, applicability review before
  task conformance, bounded-exception policy, and retrospective-recording
  policy.
- Run `scripts/validate_project_workflow_config.py --config <path>` when the
  generated config can be parsed safely. It supplements JSON Schema with
  cross-field checks for module dependencies, conditional policy ownership,
  and distinct project labels for ADR lifecycle states.

Do not install a parser or dependency automatically. If no YAML parser is safely available, validate the approved setup state, generated text structure, and a full agent readback, then report the parser limitation.

## Module graph

- Validate required dependencies from `assets/workflow-modules.json`.
- Confirm selected modules match configuration and `AGENTS.md` routing.
- Confirm each `memory.context_*` policy exists only when its catalog owner is
  selected and contains every required safety invariant.
- Confirm disabled or removed modules have no active alias or generated routing.
- Confirm domain handoffs target installed modules.

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
- request roadmap decomposition -> read-only preview before tracker mutations;
- request a full spec -> configured task/spec handoff;
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
- planning session then record an ADR -> permit only the exact lifecycle
  artifacts owned by `record-architecture-decision`; keep implementation and
  delivery blocked;
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
- review an ADR against a conflicting task -> read-only applicability verdict
  before any task or ADR mutation;
- record an accepted architecture decision -> one indexed ADR with no task
  chronology and no implementation authority;
- accept or reject a persisted proposal -> preserve its ADR ID, update its
  status and index entry, and require configured authority;
- supersede an accepted decision -> mutate only the replacement ADR, the
  replaced ADR's lifecycle status and backlink, and both index entries;
- challenge an ADR during implementation -> stop and return to shaping until
  applicability or replacement is resolved;
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
