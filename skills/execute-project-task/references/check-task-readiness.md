# Check Task Readiness

Use this gate before creating or resuming an implementation workspace.

## Resolve the implementation unit

Prefer anchors in this order:

1. exact Task ID or Issue;
2. exact specification path;
3. an already established current task whose identity is unambiguous.

Confirm that the anchor resolves to an implementation task or the project-configured equivalent. Do not implement an Epic or Feature directly when project policy requires child implementation tasks.

For multi-repository work, determine whether policy uses:

- one implementation task that owns several repositories; or
- one coordination item plus exact repo-specific sibling implementation tasks.

Resolve and authorize every implementation task that will be mutated.

## Require explicit implementation authority

Accept an explicit request to implement, build, fix, start, continue, or resume the exact task. A ready specification, tracker status, shaping outcome, or workspace that already exists does not by itself authorize implementation.

The exact `--execute-task <anchor>` alias supplies local implementation authority within the skill boundary.

## Verify readiness evidence

Check the configured requirements:

- required Task ID, Issue, Project item, parent, and specification links agree;
- the specification has the configured implementation-ready content verdict;
- when file-backed planning publication is configured, require ordinary
  independent review plus canonical merge and its complete current-schema
  `reviewed_canonical_publication` evidence;
- the specification-owner authority base contains or descends from the
  ordinary merged revision;
- when implementation occurs in a different repository, the component resolves
  the matching exact-task ordinary reviewed-publication record without
  requiring cross-repository Git ancestry;
- outcome, in-scope behavior, non-goals, acceptance criteria, and ownership are stable;
- blocking questions and product decisions are resolved;
- affected repositories and dependency order are known;
- required API, event, schema, permission, state, migration, rollout, localization, security, and data contracts are explicit when applicable;
- quality gates and verification paths are actionable;
- the task is small enough to execute safely;
- current project instructions and architecture do not contradict the intended work.

Inspect only enough current code to verify that named surfaces and critical assumptions still exist. Do not begin broad implementation during readiness checking.

Only when file-backed planning publication is configured, require one persisted
and reread ordinary record with evidence kind `reviewed_canonical_publication`,
Task ID, owner repository, canonical spec
entrypoint, PR URL, merged revision/tree OID, bound reviewed-head revision/tree
OID, complete sorted reviewed package path/mode/blob-OID manifest, reviewer run or
evidence identifier, model, effort, completion time, terminal clean verdict,
review target kind, canonical base revision, binding method, and explicit
reviewed-versus-merged package-manifest equality. Also require current review
capture-contract revision, publication-attempt ID, normalized-result SHA-256,
and the complete matched reviewer session/event set. Resolve all revisions and
tree OIDs, require the current specification-owner authority base to contain
the merged revision, and rebuild the canonical package manifest at that revision.
It must equal the persisted reviewed manifest exactly. PR prose, an open or
merged PR, a status field, or a model/effort pair without the bound clean record
is insufficient.

Also rebuild the same complete sorted package manifest from the current
specification-owner authority base, not only from the record's older merged
revision. Require exact path, mode, and blob-OID equality with the selected persisted
manifest before returning a ready result. A missing, added, or changed
task-owned specification or annex invalidates the selected path even when the
old merged revision remains in ancestry.

If implementation discovery causes any package change, invalidate the selected
path immediately. Require the corrected package to pass its configured
planning-publication workflow and rerun this complete readiness gate against
the new persisted record before resuming task-code edits. Do not reuse the
earlier record as implementation authority. A configured stale-publication
correction may preserve the content target verdict only as provisional while
the implementation gate remains closed and a new complete record is pending.

## Stop for publication evidence upgrade

Apply this section only when file-backed planning publication is configured.
Historical baseline evidence and an ordinary record without the current
capture-contract provenance are audit inputs only. They cannot satisfy
implementation readiness, even when their old manifest still matches the
current package.

For missing, old, incomplete, or ambiguous ordinary evidence, return a typed
stop before status, branch, worktree, dependency, or file mutation:

```yaml
status: publication_upgrade_required
task_id: <TASK-ID>
canonical_spec_path: <PROJECT-RELATIVE-PATH>
observed_evidence_revision: <REVISION-OR-NULL>
required_capture_contract_revision: 1
observed_operational_status: <CONFIGURED-STATUS>
reconciliation_action: downgrade_to_spec_ready | audit_only
next_action: --publish-spec <TASK-ID>
workspace_created: false
```

Only exact operational `Ready for implementation` maps to the configured
`downgrade_to_spec_ready` migration action. Every other configured lifecycle or
exceptional status is `audit_only` and remains unchanged. The migration owns an
authoritative post-cutover rescan and is complete only when no old-evidence item
still has implementation-ready operational status. It must not synthesize
session IDs, result hashes, or independent-review claims.

When `publish-planning-change` is not selected, skip this stop entirely. Do not
require publication evidence, return `publication_upgrade_required`, or emit a
`--publish-spec` next action. Evaluate only the remaining configured readiness
gates.

## Classify gaps

Use these routes:

- missing or inconsistent specification detail: `write-task-spec`;
- missing, old, or incomplete ordinary publication evidence when publication is
  configured: `publish-planning-change` with typed
  `publication_upgrade_required`;
- changed outcome, scope, task decomposition, architecture, or dependency direction: `shape-project-work`;
- missing or inconsistent task identity or tracker state: `manage-project-work`;
- missing domain-specific evidence: the configured domain workflow;
- unsupported tool, unavailable repository, or external dependency: blocker or configured degraded mode.

Do not hide a readiness gap in an implementation assumption.

## Handle overrides

Apply an explicit user override only when project policy allows that exact gate to be overridden. Before continuing:

1. state the missing evidence or failed gate;
2. explain the concrete implementation risk;
3. record the accepted exception where project policy requires it;
4. preserve all non-overridable higher-priority constraints.

User acceptance cannot override safety restrictions, repository policy, access controls, or missing authority for production and external mutations.

## Return one result

- `Ready to execute`: every required gate is satisfied.
- `Ready by configured exception`: another allowed exception and risk are explicit.
- `Not ready`: name the blocking gate and owning workflow.
