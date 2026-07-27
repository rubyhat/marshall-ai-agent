# Install and Sync Skills

Run only after the exact manifest is approved.

## Prefer the central-source model

Default ownership:

```text
workflow-kit repository -> canonical reusable source
~/.codex/skills          -> active Codex installation
target project           -> project config, instructions, docs, and templates
```

Record source repository, exact revision, installation mode, and selected modules
in project configuration.

Use one source revision for every selected module:

- prefer an exact release tag such as `v0.3.1` for stable installation;
- use a full commit SHA only for reviewed unreleased testing;
- do not record a floating branch such as `main` as the final revision;
- for `symlink` mode, record the current commit when available and mark the
  installation as non-reproducible while the working tree is dirty.

Support alternatives only when selected:

- `vendored`: keep a project-local reviewed source copy and install its active copy;
- `symlink`: local development mode with an explicit portability warning.

## Reconcile before writing

For each selected skill:

1. locate the canonical source;
2. locate the active destination;
3. validate both skill structures when they exist;
4. compare source and destination recursively;
5. classify destination as missing, identical, stale, locally modified, or conflicting;
6. include the exact action in the approved manifest.

Do not overwrite a locally modified active copy automatically. Show the diff and require a revised approval.

## Reconcile an update

Before moving an existing project to another workflow-kit revision:

1. identify the current recorded revision;
2. identify the exact target tag or commit;
3. read compatibility and migration notes between those revisions;
4. compare every selected source skill with its active copy;
5. identify configuration schema, generated artifact, alias, authority, and
   handoff changes;
6. include config migrations, skill replacements, validation, and rollback in
   one exact manifest;
7. require approval before changing the recorded revision or active copies.

Do not combine modules from different release tags unless the user explicitly
accepts a documented non-standard compatibility risk.

## Avoid hidden external actions

- Do not clone, fetch, pull, authenticate, or contact GitHub during inspection.
- Use a local source when available.
- Hand a GitHub installation to the system skill installer only after the manifest explicitly authorizes network access and the exact source.
- Do not install packages or plugins as a side effect.
- Do not use global installation when the user's protection layer forbids it.

## Verify installation

After installation:

- run the system skill validator for each installed module when available;
- compare installed contents with the approved source;
- verify `agents/openai.yaml`;
- verify every configured active path;
- verify the recorded revision is an exact tag or full commit SHA except for an
  explicitly non-reproducible symlink installation;
- report source revision and any skipped conflict.

Installing a skill does not authorize running its workflow.
