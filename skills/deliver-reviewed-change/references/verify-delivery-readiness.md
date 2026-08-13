# Verify Delivery Readiness

Run this gate before independent review or external delivery mutations.

## Resolve one exact delivery

For ordinary task delivery, confirm:

- exact Task ID, Issue, specification, repository, worktree, and feature branch;
- current authorized endpoint;
- whether the work is one repository or an ordered set of repo-specific tasks;
- expected target branch and pull-request ownership;
- the execution handoff's intended base and target still match current policy;
- the handoff identifies the routing source and verified base-creation source
  branch or explicit not-applicable value;
- task status and the handoff from implementation.

For aggregate promotion, confirm instead:

- the exact aggregate result or Epic anchor and its equivalent contract;
- the project-defined source integration branch and destination branch for each
  repository;
- project-owned readiness evidence for the aggregate result, without inventing
  an automatic scan of every child task;
- any allowed direct-delivery evidence that already satisfies part or all of
  the aggregate outcome;
- the required checks chosen from the actual aggregate risk;
- that this is a standalone aggregate delivery, not a second delivery of a
  completed child task.

Do not infer another open pull request from repository proximity. If multiple tasks, branches, or pull requests plausibly match, stop and resolve the identity.

## Verify local state

For every repository in ordinary task mode:

- confirm the worktree and branch belong to the task;
- inspect status, complete diff, untracked files, and base relationship;
- confirm no unrelated or unfamiliar changes are included;
- confirm implementation quality gates correspond to the final diff;
- confirm required task files, generated artifacts, migrations, localization, and documentation are present;
- confirm secrets, local environment files, debug output, and temporary artifacts are absent.

For aggregate promotion:

1. resolve and read back the configured runtime routing record for the exact
   aggregate anchor and its selected repositories. Require exactly one concrete
   source, destination, and routing-source tuple per selected repository from
   its typed values collection. Stop when any route is missing, duplicated,
   empty, mismatched, ambiguous, or belongs to an unrelated repository;
2. fetch or otherwise verify the current destination ref and the source ref
   when it exists. Stop if the destination is missing or either existing ref's
   ownership is ambiguous. Capture the exact destination revision for every
   selected repository in delivery state before synchronization, and carry it
   through the immutable review input and GitHub review state so it can be
   revalidated immediately before merge;
3. when the source is absent, evaluate the project-approved direct-delivery
   evidence first. If it proves that the complete aggregate outcome is already
   present in the destination, return `Already integrated` before any source
   comparison and do not create a branch or pull request. Otherwise return
   `Not ready` and fail closed before branch, review, or pull-request creation;
4. with an existing source, establish safe ancestry and determine whether it
   contains a meaningful result not already in the destination. When approved
   evidence proves the complete result is already present, return `Already
   integrated` and do not create an empty pull request. When no meaningful
   destination-to-source diff remains and the evidence is incomplete, return
   `Not ready` and fail closed before review or pull-request creation;
5. create or reuse and validate a delivery-owned worktree for the source branch
   or a safe helper. When the source exists only as a remote ref, first fetch
   and verify it, then materialize the local branch/worktree without rewriting
   history. Do not reuse a completed child task's worktree for promotion review
   or corrections;
6. integrate the current destination into the source branch or a safe
   delivery-owned helper branch before review. Resolve conflicts and required
   corrections there, never by committing directly to the destination;
7. never force, reset, or rewrite an existing shared source branch; if it moved,
   reconcile the new history and rerun the gate;
8. inspect the delivery worktree's branch, registration, ownership, status,
   complete destination-to-source candidate diff, untracked files, and
   delivery-owned corrections before independent review.

Do not discard or move unfamiliar changes to make delivery easier.

## Verify review inputs

Resolve:

- task specification or aggregate result contract and acceptance criteria;
- applicable project and repository instructions;
- local-review rubric and configured command;
- architecture and domain gates;
- accepted implementation exceptions or blockers;
- required CI and merge checks.

Before the first review, capture the immutable delivery baseline: exact task or
aggregate anchor and contract, acceptance criteria, non-goals, repositories,
source branches, target branches, plus a complete initial candidate diff
path/status/content-hash manifest and diff statistics. For promotion, compute
that manifest from the destination-to-source candidate after synchronization
and include aggregate readiness, direct-delivery evidence, and the exact
pre-review destination revision for every selected repository.

Initialize only the local correction counter and retain its ordered history.
Persist and read back one compact machine-readable delivery-state block containing
the baseline and local state in the retained state of the current Codex task before launching
review. Initialize GitHub correction state only
after the exact pull request
exists. On resume, require the same baseline and provable state owned by the
applicable local block or exact PR before any mutation.

If implementation is incomplete or a required implementation gate fails, return to `execute-project-task`. If the promised contract or scope changed, return to the owning shaping or specification workflow.

## Verify authority

Confirm the user-authorized endpoint:

- local review only;
- commit and push;
- pull-request creation;
- clean external review;
- full delivery through merge and cleanup.

The exact `--deliver-task` alias authorizes the configured full lifecycle only
for the current exact task or configured aggregate promotion anchor. It never
authorizes force-push, unrelated PRs, production operations, destructive
recovery, or bypassing gates.

Return one result:

- `Ready for local review`;
- `Already integrated`, with the exact evidence and no empty pull request;
- `Ready to resume at <exact phase>`;
- `Not ready`, with the exact owning workflow or blocker.
