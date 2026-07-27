---
name: maintain-project-context
description: Audit, consolidate, archive, and safely clean project memory and documentation through a manual two-phase workflow. Use only when the user explicitly requests a context health audit, invokes `--context-audit`, asks to review stale or duplicate project context, or separately approves an exact cleanup manifest. Do not invoke automatically from age, file count, task completion, ordinary context loading or recording, and never treat an audit request as permission to mutate files.
---

# Maintain Project Context

Keep active project context compact without erasing unique history. Separate discovery from mutation and require explicit user control at every destructive boundary.

## Preserve the safety boundary

- Run only after an explicit user request.
- Treat `--context-audit` as an exact plain-text alias for the read-only audit phase.
- Interpret text after `--context-audit` as an optional scope hint. With no hint, use the configured project-context roots.
- If the same message asks to audit and clean, perform only the audit and stop.
- Never transition from audit to cleanup automatically.
- Require a separately prepared exact manifest and a later explicit approval before changing files.
- Treat age, size, and count only as discovery metrics. Never use them alone to classify or delete an artifact.
- Do not commit, push, open a pull request, or mutate an external task system unless separately requested.

## Resolve project policy

Read the project workflow configuration and applicable project instructions. Resolve:

- project root and configured context roots;
- active, canonical, historical, archive, and protected locations;
- context map and source-of-truth ownership;
- active maintenance-manifest path, if configured;
- language and reporting policy.

If configuration is absent, infer the smallest safe scope from the explicit request and existing project instructions. Do not invent retention thresholds or a cleanup root.

## Choose the phase

### Run phase 1: read-only audit

Use this phase for `--context-audit`, health checks, stale-context review, duplicate discovery, and cleanup preparation.

1. Read [context-retention-policy.md](references/context-retention-policy.md).
2. Read [audit-project-context.md](references/audit-project-context.md).
3. Inspect metadata across the configured or requested scope.
4. Use `scripts/audit_project_context.py` when Python 3.9+ is available.
5. Read candidate contents only after the metadata pass, and only where semantic classification requires it.
6. Classify reviewed artifacts as:
   - `retain`;
   - `consolidate`;
   - `archive`;
   - `delete_candidate`;
   - `needs_human_decision`;
   - `broken_reference`.
7. Return a compact report with evidence, protected items, uncertain items, and a proposed next step.
8. State explicitly that no files were changed, then stop.

Do not save a report in the repository by default. If the user chooses to pursue cleanup, prepare one rolling exact manifest at the configured location; do not create per-audit reports.

### Prepare an exact cleanup manifest

Prepare a manifest only after the user selects cleanup candidates or explicitly asks to prepare cleanup.

For every proposed mutation include:

- exact project-relative path;
- exact action: `consolidate`, `archive`, `delete`, or `update_reference`;
- reason and evidence;
- canonical replacement or archive destination;
- incoming references that must change;
- Git state and recovery source;
- current SHA-256 fingerprint;
- validation required after the action.

Mark modified, untracked, protected, ambiguous, or unresolved items as excluded. Present the exact manifest and request separate approval. Approval to create the manifest is not approval to apply it.

### Run phase 2: approved cleanup

Enter this phase only when the user explicitly approves the exact current manifest.

1. Re-read [context-retention-policy.md](references/context-retention-policy.md).
2. Read [consolidate-project-context.md](references/consolidate-project-context.md) for any consolidation.
3. Read [apply-and-verify-context-cleanup.md](references/apply-and-verify-context-cleanup.md).
4. Revalidate paths, fingerprints, Git state, references, and replacement destinations.
5. Exclude any item that drifted after approval; do not broaden the manifest.
6. Apply only exact approved paths and actions.
7. Show the diff, rerun the same audit scope, and compare before/after results.
8. Stop and report any skipped or uncertain item instead of improvising.

## Use the audit script safely

Run the script directly without installing dependencies:

```bash
python3 scripts/audit_project_context.py \
  --root <workspace> \
  --scope <context-root> \
  --active-root <active-root> \
  --canonical <canonical-path> \
  --protected <protected-path> \
  --historical-root <historical-root> \
  --archive-root <archive-root> \
  --task-id-regex <configured-validation-regex> \
  --include-content-signals \
  --include-git-state \
  --format text
```

Repeat path flags as needed. Pass the project's configured Task ID validation regex when one exists; the script applies it to generic identifier tokens and otherwise uses neutral discovery. Use `--format json` when structured output is useful. The script accepts no mutation flags and prints no file contents.

If Python 3.9+ is unavailable, follow the bounded macOS/Linux fallback in [audit-project-context.md](references/audit-project-context.md). Do not install Python or packages automatically.

## Coordinate with adjacent skills

- Use `load-project-context` for ordinary task orientation, not this skill.
- Use `record-project-context` when consolidation must update canonical memory or a rolling manifest.
- Keep broad audit, retention judgment, archive selection, and cleanup ownership in this skill.
- Let task, ADR, incident, security, legal, and production workflows continue to own their substantive artifacts.
