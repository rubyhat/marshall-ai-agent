# Setup State and Resume

Keep one machine-readable rolling state for initialize, resume, and reconfigure modes:

```text
.codex/project-workflow.setup.json
```

Audit mode must not create it.

## Contents

1. Required structure
2. Current-state rules
3. Resume behavior
4. Validation
5. Safe closure

## Required top-level structure

```json
{
  "schema_version": 1,
  "setup_id": "project-workflow-setup",
  "mode": "initialize",
  "phase": "inspection",
  "project_root": "/absolute/target/root",
  "workflow_kit": {},
  "protection": {},
  "facts": [],
  "decisions": [],
  "modules": {"profile": null, "selected": []},
  "questions": [],
  "assumptions": [],
  "conflicts": [],
  "deferred_topics": [],
  "manifest": [],
  "validation": {"status": "not_run", "checks": []}
}
```

Use absolute `project_root` only in temporary state. Generated reusable instructions and templates must not embed user-specific absolute paths unless project policy explicitly requires an operational workspace path.

## Track current state, not history

- Replace superseded answers.
- Keep one entry per stable question ID.
- Preserve the answer, status, source, confidence, and confirmation state.
- Do not copy conversation, command output, or intermediate drafts.
- Record a detour only as a current decision, conflict, deferred topic, or unresolved question.

Allowed question statuses:

- `pending`;
- `detected_needs_confirmation`;
- `answered`;
- `assumed`;
- `deferred`;
- `blocked`;
- `not_applicable`.

Allowed phases:

- `inspection`;
- `safety`;
- `module_selection`;
- `interview`;
- `manifest_preview`;
- `approved`;
- `applying`;
- `validation`;
- `blocked`;
- `complete`.

## Resume deterministically

On resume:

1. verify that the state file is inside the exact current project root;
2. validate it with `scripts/validate_setup_state.py`;
3. compare safe project metadata with recorded facts;
4. mark drift instead of silently accepting stale answers;
5. state mode, phase, completed stages, unresolved stages, blockers, and next question IDs;
6. resume from the first unresolved active stage.

Do not restart the interview or repeat confirmed answers unless relevant project evidence changed.

## Validate after material stages

From the skill directory:

```bash
python3 scripts/validate_setup_state.py \
  --state <project-root>/.codex/project-workflow.setup.json \
  --catalog assets/workflow-modules.json
```

Fix structural errors before continuing. Treat semantic conflicts as interview items rather than editing around them.

## Close safely

Delete the tracker only after:

- the approved manifest is fully applied;
- generated files are reread;
- setup validation passes;
- no answer, conflict, assumption, or deferred topic remains material;
- final values exist in canonical configuration or project docs.

Keep it for a paused or blocked setup. Do not archive completed setup history by default.
