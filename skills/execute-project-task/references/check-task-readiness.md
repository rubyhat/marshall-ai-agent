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
- outcome, in-scope behavior, non-goals, acceptance criteria, and ownership are stable;
- blocking questions and product decisions are resolved;
- affected repositories and dependency order are known;
- required API, event, schema, permission, state, migration, rollout, localization, security, and data contracts are explicit when applicable;
- quality gates and verification paths are actionable;
- the task is small enough to execute safely;
- current project instructions and architecture do not contradict the intended work.

Inspect only enough current code to verify that named surfaces and critical assumptions still exist. Do not begin broad implementation during readiness checking.

## Classify gaps

Use these routes:

- missing or inconsistent specification detail: `write-task-spec`;
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
- `Ready by configured exception`: the allowed exception and risk are explicit.
- `Not ready`: name the blocking gate and owning workflow.
