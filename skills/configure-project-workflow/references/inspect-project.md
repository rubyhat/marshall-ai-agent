# Inspect Project

Use read-only inspection to replace unnecessary questions with sourced facts.

## Start with the bundled inspector

From the skill directory:

```bash
python3 scripts/inspect_project.py \
  --root <project-root> \
  --format json
```

The script uses Python 3.9+ standard library only, does not follow external symlinks, skips sensitive and generated paths, captures bounded Git metadata without a shell, never reads remote URLs, and never runs project code.

If Python 3.9+ is unavailable, inspect the same categories manually under the setup safety boundary. Do not install Python or another dependency automatically.

## Inventory in this order

1. Exact project root and Git topology.
2. Root and nested `AGENTS.md`.
3. Existing `.codex` workflow files and active setup tracker.
4. Safe package and workspace manifests.
5. README, architecture, documentation, and memory maps.
6. CI definitions, CODEOWNERS, and Issue templates.
7. Existing task, reference, template, and workflow directories.
8. Active skill installation only when installation reconciliation is in scope.

Do not recursively read the documents discovered by inventory. Open a file or section only to resolve a concrete setup field.

## Normalize facts

For each material fact record:

- key;
- normalized value;
- status: `detected`, `conflict`, `unknown`, or `not_applicable`;
- source path or read-only command;
- confidence: `high`, `medium`, or `low`;
- whether user confirmation is required.

Examples:

- repository roots and ownership;
- detected language and framework;
- existing docs and memory conventions;
- CI provider and configured quality-gate names;
- existing Task ID or Issue conventions;
- production or deployment signals that require a question rather than an assumption.

Do not infer product roles, production safety, merge authority, tracker policy, or legal constraints from framework files alone.

## Bound output

- Prefer grouped paths and counts over full directory listings.
- Report skipped protected categories without content.
- Stop at configured depth and file count.
- Treat an incomplete inventory as a limitation, not a reason for a broader scan.
- Store normalized facts in the setup tracker, not raw tool output.
