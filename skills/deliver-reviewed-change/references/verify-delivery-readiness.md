# Verify Delivery Readiness

Run this gate before independent review or external delivery mutations.

## Resolve one exact delivery

Confirm:

- exact Task ID, Issue, specification, repository, worktree, and feature branch;
- current authorized endpoint;
- whether the work is one repository or an ordered set of repo-specific tasks;
- expected target branch and pull-request ownership;
- task status and the handoff from implementation.

Do not infer another open pull request from repository proximity. If multiple tasks, branches, or pull requests plausibly match, stop and resolve the identity.

## Verify local state

For every repository:

- confirm the worktree and branch belong to the task;
- inspect status, complete diff, untracked files, and base relationship;
- confirm no unrelated or unfamiliar changes are included;
- confirm implementation quality gates correspond to the final diff;
- confirm required task files, generated artifacts, migrations, localization, and documentation are present;
- confirm secrets, local environment files, debug output, and temporary artifacts are absent.

Do not discard or move unfamiliar changes to make delivery easier.

## Verify review inputs

Resolve:

- task specification and acceptance criteria;
- applicable project and repository instructions;
- local-review rubric and configured command;
- architecture and domain gates;
- accepted implementation exceptions or blockers;
- required CI and merge checks.

Before the first review, capture the immutable delivery baseline: exact task
and contract anchors, acceptance criteria, non-goals, repositories and branches,
plus a complete initial diff path/status/content-hash manifest and diff
statistics. Initialize separate local and GitHub correction counters and retain
their ordered histories. Persist and read back one compact machine-readable
delivery-state block in the retained state of the current Codex task before
launching review. On resume, require the same baseline and provable counters
before any mutation.

If implementation is incomplete or a required implementation gate fails, return to `execute-project-task`. If the promised contract or scope changed, return to the owning shaping or specification workflow.

## Verify authority

Confirm the user-authorized endpoint:

- local review only;
- commit and push;
- pull-request creation;
- clean external review;
- full delivery through merge and cleanup.

The exact `--deliver-task` alias authorizes the configured full lifecycle only for the current exact task. It never authorizes force-push, unrelated PRs, production operations, destructive recovery, or bypassing gates.

Return one result:

- `Ready for local review`;
- `Ready to resume at <exact phase>`;
- `Not ready`, with the exact owning workflow or blocker.
