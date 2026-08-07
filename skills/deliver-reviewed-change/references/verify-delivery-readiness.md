# Verify Delivery Readiness

Run this gate before independent review or external delivery mutations.

## Resolve one exact delivery

Confirm:

- exact Task ID, Issue, specification, repository, worktree, and feature branch;
- current authorized endpoint;
- whether the work is one repository or an ordered set of repo-specific tasks;
- expected target branch and pull-request ownership;
- task status and the handoff from implementation.
- whether the handoff is completed task work or an automatic ready-spec
  delivery that must keep the task open after merge.

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

## Classify a documentation-only fast path

When project policy enables it, inspect the complete intended Git change set
before any review decision. Require every path to:

- remain beneath one configured documentation root;
- use an allowed non-executable documentation file type;
- avoid every configured workflow, skill, runbook, configuration, schema,
  script, generated, temporary, secret, and symlink exclusion;
- belong to the exact task or ready-spec package.

Require exact task identity, diff, structure, links, content verdict when
applicable, deterministic validation, target branch, and merge authority. If
any path or gate is uncertain or ineligible, classify the entire handoff as
ordinary reviewed delivery. Never split an ineligible mixed PR to obtain the
fast path implicitly.

Classification does not override a narrower endpoint. A local-review-only
request still runs the configured independent reviewer and stops with its
result; fast-path review skipping applies only when delivery mutations are
authorized.

Record the exact head and base SHAs covered by classification and deterministic
validation. Treat any later change to either SHA as stale evidence that must be
recomputed before merge.

## Verify review inputs

Resolve:

- task specification and acceptance criteria;
- applicable project and repository instructions;
- local-review rubric and configured command;
- architecture and domain gates;
- accepted implementation exceptions or blockers;
- mode-specific reported-check and merge requirements.

If implementation is incomplete or a required implementation gate fails, return to `execute-project-task`. If the promised contract or scope changed, return to the owning shaping or specification workflow.

## Verify authority

Confirm the user-authorized endpoint:

- local review only;
- commit and push;
- pull-request creation;
- clean external review;
- full delivery through merge and cleanup.

The exact `--deliver-task` alias authorizes the configured full lifecycle only
for the current exact task. A configured `--prepare-spec` handoff may authorize
only automatic delivery of its exact ready-spec package. Neither authorizes
force-push, unrelated PRs, production operations, destructive recovery, or
bypassing provider-enforced rules, merging with pending or failing reported
checks, or bypassing deterministic validation or path gates. A configured
documentation-only fast path may explicitly allow no reported checks and no
branch-protection evidence.

Return one result:

- `Ready for local review`;
- `Ready for documentation fast path`;
- `Ready to resume at <exact phase>`;
- `Not ready`, with the exact owning workflow or blocker.
