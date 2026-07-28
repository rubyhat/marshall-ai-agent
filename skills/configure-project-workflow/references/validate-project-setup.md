# Validate Project Setup

Validate the configured workflow without executing ordinary project work.

## Structure

- Parse the setup tracker and generated configuration with an available safe parser.
- Verify required generic fields and selected module sections.
- Verify unique module names, aliases, paths, and managed markers.
- Verify every alias has a resolvable owning workflow, authority boundary,
  prerequisites, and sequence-mismatch behavior.
- Verify every enabled conditional alias has all modules declared by its
  catalog `requires` list, and that ineligible conditional aliases are absent
  from configuration, routing, and the project command catalog.
- Verify no unresolved template placeholders.
- Verify every generated relative link.
- Verify no configured path escapes its intended root.

Do not install a parser or dependency automatically. If no YAML parser is safely available, validate the approved setup state, generated text structure, and a full agent readback, then report the parser limitation.

## Module graph

- Validate required dependencies from `assets/workflow-modules.json`.
- Confirm selected modules match configuration and `AGENTS.md` routing.
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
- accept current recommendations -> only the latest recommended question set;
- request implementation -> readiness and explicit authority gate;
- request delivery -> exact endpoint gate;
- report a frontend defect when QA is selected;
- request external reference analysis when selected;
- run `--workflow-check` -> read-only audit.

## Verdict

Return exactly one:

- `Setup ready`;
- `Setup incomplete`;
- `Setup blocked`;
- `Setup drift detected`.

Delete the tracker only for `Setup ready` with no unresolved material state.
