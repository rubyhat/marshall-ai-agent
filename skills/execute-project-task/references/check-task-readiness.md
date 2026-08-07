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
- when file-backed planning publication is configured, exactly one complete
  evidence path passes: either ordinary independent review plus canonical merge
  and its recorded revision, or the explicitly enabled and fully verified
  `legacy_ready_baseline` path below;
- the specification-owner authority base contains or descends from the
  selected path's ordinary merged revision or legacy derived revision;
- when implementation occurs in a different repository, the component resolves
  the matching exact-task record — ordinary Task ID, owner repository,
  canonical spec path, and merged revision, or the legacy tuple with its full
  package manifest, derived revision, and adoption baseline — without requiring
  cross-repository Git ancestry;
- outcome, in-scope behavior, non-goals, acceptance criteria, and ownership are stable;
- blocking questions and product decisions are resolved;
- affected repositories and dependency order are known;
- required API, event, schema, permission, state, migration, rollout, localization, security, and data contracts are explicit when applicable;
- quality gates and verification paths are actionable;
- the task is small enough to execute safely;
- current project instructions and architecture do not contradict the intended work.

Inspect only enough current code to verify that named surfaces and critical assumptions still exist. Do not begin broad implementation during readiness checking.

## Resolve pre-adoption ready specifications

If the ordinary publication tuple is missing, inspect the configured
legacy-ready adoption policy before declaring the task blocked. Use this path
only when it is explicitly enabled for an existing project and supplies one
immutable full baseline revision captured from the canonical target before
planning-publication adoption.

First build candidate evidence and require all of the following:

1. the baseline revision is an ancestor of the current specification-owner
   authority base, and the exact canonical spec package paths exist at both;
2. project policy or the exact task package resolves every task-owned primary
   spec and required annex path. For both revisions, build the same sorted
   manifest of project-relative path and Git blob OID; require byte-for-byte
   manifest equality so no post-baseline package change is grandfathered. Use a
   Git tree OID only when the whole tree is exactly the owned package;
3. the baseline spec contains the exact Task ID, tracker link, and configured
   implementation-ready verdict, and current tracker identity still agrees;
4. the evidence revision is the last revision that changed any manifest path at
   or before the baseline, contains the same package manifest, and is an
   ancestor of both the baseline and current authority base.

Only after those candidate checks pass, ask `manage-project-work` to record
Task ID, owner repository, canonical spec entrypoint, the complete sorted
baseline package manifest with every path and blob OID, derived revision,
baseline revision, and evidence kind `legacy_ready_baseline` as one exact-task
record. Then reread the tracker record, require the same complete manifest and
verify every persisted value against the candidate, including the exact path
set and each blob OID. Verify it explicitly states that independent review is
not claimed. The persisted and verified tuple is the final readiness evidence;
it is not a prerequisite for constructing the candidate.

This is deterministic migration evidence for work accepted by the previous
workflow, not permission to weaken the new publication gate. Do not mass-mark
tasks ready, choose a newer baseline, compare only the entrypoint when annexes
exist, accept approximate content equality, or use a user assertion in place of
Git and tracker evidence. If any check or persisted readback fails, route the
task to `publish-planning-change`.

## Classify gaps

Use these routes:

- missing or inconsistent specification detail: `write-task-spec`;
- neither complete ordinary publication evidence nor complete configured
  legacy-ready baseline evidence: `publish-planning-change`;
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
- `Ready by configured migration evidence`: the exact legacy baseline tuple is
  recorded without claiming independent review.
- `Ready by configured exception`: another allowed exception and risk are explicit.
- `Not ready`: name the blocking gate and owning workflow.
