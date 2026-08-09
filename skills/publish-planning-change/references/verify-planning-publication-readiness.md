# Verify planning publication readiness

Resolve the exact planning change before review or Git publication.

## Confirm identity and ownership

Verify:

- one exact Task ID or configured equivalent;
- the matching Issue and parent when the project requires them;
- the specification entrypoint and every required annex;
- the shaped outcome, scope, non-goals, owner, and dependency position;
- the repository that owns the canonical specification;
- the configured spec root and target branch;
- the current content verdict and authorized publication endpoint.

Stop when identifiers or links disagree. Do not infer ownership from the
current directory alone.

## Verify the planning workspace

For a new file-backed spec, establish the configured planning worktree before
the first write. Base it on a fetched canonical target when network access is
authorized. If only an offline base is available, report staleness and keep
remote verification pending before publication.

Before review, confirm:

- the worktree and branch belong to the exact task;
- the main checkout was not switched for planning work;
- the base and target are known;
- no unfamiliar dirty changes predate the task;
- the complete diff can be explained by the exact publication manifest.

If an existing spec is dirty in a main checkout, preserve it. Prepare a
path-by-path recovery proposal; do not stash, reset, copy, or delete files
silently.

## Classify changed paths

Classify every changed path:

- `primary`: the task-spec entrypoint and required annexes;
- `supporting`: directly required tracked project documentation, durable
  context, task links, or configuration allowed by project policy;
- `unrelated`: a valid user change outside this planning handoff;
- `forbidden`: implementation source, migration, build output, dependency
  lockfile change, secret, credential, release, deployment, or production
  mutation.

An unrelated or forbidden path blocks broad publication. Exclude unrelated
paths only when the remaining manifest is independently coherent and no shared
file contains mixed ownership.

## Require a stable pre-review state

Require:

- either normal `Spec ready` author content or the configured
  `stale_published_ready_spec` entry with existing canonical publication,
  exact `Ready for implementation`, typed `publication_upgrade_required`, and
  implementation authority closed before review;
- no unresolved product decision hidden in prose;
- stable shaped scope and dependency direction;
- resolvable links and verified technical references;
- configured deterministic checks available or an explicit blocker;
- no implementation work started from this unpublished spec.

Do not promote operational readiness merely because the local file exists.
Before computing the review manifest, let `write-task-spec` materialize or
preserve provisional `Ready for implementation` in the isolated candidate.
That provisional verdict does not unlock implementation before merge and full
publication-evidence readback.
