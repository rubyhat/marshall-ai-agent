# Prepare the Local Review Handoff

Prepare an exact uncommitted state for independent review. Do not perform that review here.

## Inspect the final state

For every modified repository:

- confirm the expected worktree, branch, and task identity;
- inspect status, diff summary, full diff, and whitespace/error checks;
- identify staged changes if any, without staging merely for handoff;
- verify that no unrelated, temporary, secret, debug, editor, local-environment, or accidental generated files are present;
- confirm required generated artifacts and lockfiles are present when they belong to the task.

Trace material acceptance criteria to the implementation and current gate evidence. Check applicable contracts, errors, permissions, migrations, localization, accessibility, documentation, observability, and compatibility.

## Distinguish self-check from review

Executor self-check confirms completeness and obvious hygiene. It must not:

- claim independent-review coverage;
- resolve review findings that have not been produced;
- commit, push, create a pull request, merge, deploy, or clean the workspace;
- mark delivery or merge readiness.

The next workflow must inspect the uncommitted diff independently.

## Establish the checkpoint

Only when the final state is ready:

1. ask `manage-project-work` to apply the configured local-review status;
2. read back the mutation when the provider is available;
3. if unavailable, report the pending status and follow degraded-mode recording policy;
4. use `record-project-context` only when the task needs a rolling multi-session handoff or produced a durable discovery.

Do not duplicate the specification, Issue, or full command log in memory.

## Report the handoff

Provide:

- exact task anchor and readiness result;
- repository, worktree, task branch, intended base, intended pull-request
  target, routing source, verified base- and target-creation source branches or
  not-applicable values, target revision or explicit absence, and base-revision
  mapping;
- concise implemented outcome;
- relevant gate results, including blocked or accepted exceptions;
- material assumptions, risks, and known limitations;
- specification changes made during implementation;
- explicit statement that changes are uncommitted;
- next owner: `deliver-reviewed-change`.

If any required item is missing, keep the task in implementation or blocked state instead of presenting it as ready for local review.
