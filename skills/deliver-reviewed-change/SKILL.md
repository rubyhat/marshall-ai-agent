---
name: deliver-reviewed-change
description: Deliver an exact current task from a verified local handoff through commit, push, pull-request creation, authorized merge, synchronization, and cleanup. Use independent local and GitHub review for ordinary changes; use a configured documentation-only fast path when the complete diff satisfies its exact path and file-type allowlist. Use when the user explicitly asks to review, publish, deliver, finish, or merge the current task; invokes `--deliver-task`; receives an authorized ready-spec delivery handoff from `write-task-spec`; resumes the exact task pull request; or continues its configured review cycle. Verify active conversation authority, reported checks, provider-enforced merge rules, merge ownership, and exact-diff gates according to the configured delivery mode.
---

# Deliver Reviewed Change

Move one exact implementation task through review and delivery without losing task identity, scope, review-cycle state, or merge authority.

## Keep the responsibility narrow

- Receive verified uncommitted changes from `execute-project-task`, or one exact
  content-ready specification package from an authorized `write-task-spec`
  handoff when project policy enables automatic specification delivery.
- Own independent local review, finding assessment, commit, push, pull-request creation, review monitoring, authorized merge, operational closure, sync, and task-workspace cleanup.
- Preserve the agreed specification and non-goals while addressing findings.
- Do not perform initial feature implementation, silently expand scope, select an unrelated pull request, force-push, deploy, mutate production, or bypass required gates.
- Use `manage-project-work` for lifecycle mutations and `record-project-context` for durable findings or closing state.

## Resolve active conversation authority first

Before task or pull-request reconciliation, review fixes, status changes,
commit, push, pull-request comments, heartbeat creation, merge, or cleanup,
inspect already loaded conversation state and project policy for:

- an active planning-session profile;
- an explicit current-session no-code, no-delivery, read-only, or
  discussion-only constraint;
- another sticky negative constraint that excludes review or delivery
  mutations.

Treat a conflicting alias or natural-language delivery request as a conflict,
not as an implicit override. Stop before mutations, state the received request,
active constraint, conflict, and exact configured release action, and confirm
that no task, Git, pull-request, heartbeat, or file state changed.

A heartbeat may resume only an already authorized delivery cycle. It cannot
release or broaden a later sticky conversation constraint.

A project may define one narrow `specification_documentation_delivery`
capability that `--prepare-spec` is allowed to inherit inside a planning
session. This exception authorizes only the exact ready specification package,
task branch, commit, push, pull request, merge, and readiness-status handoff.
It does not release the planning lock for implementation, ordinary task
delivery, workflow/configuration files, or any additional path.

## Establish mode and endpoint

Choose one mode:

- `start`: begin from verified uncommitted changes;
- `resume`: continue an exact existing branch or pull request;
- `monitor`: execute one heartbeat decision for an exact persisted review cycle;
- `complete`: resume an exact clean and authorized delivery through merge and cleanup.

Resolve the authorized endpoint from the user's request:

- a narrow request such as “open a PR” stops at that endpoint;
- after the active-conversation gate passes, `--deliver-task` authorizes the
  configured full lifecycle for the exact current task, including merge and
  cleanup when all gates and merge-ownership rules pass;
- a heartbeat inherits the existing endpoint and cannot broaden it;
- ambiguity about task, pull request, repository, or merge target blocks mutations.

Neither an alias nor the documentation fast path authorizes force-push,
unrelated pull requests, Project schema changes, deployment, production data
access, destructive recovery, bypassing provider-enforced rules, merging with
pending or failing reported checks, or weakening the configured file allowlist.

## Resolve project policy

Read project instructions and workflow configuration. Resolve:

- task, Issue, specification, branch, worktree, and repository mapping;
- required local-review command, model, fallback, rubric, and architecture gates;
- commit, push, PR description, target branch, linkage, and status policy;
- GitHub review trigger, reviewer actor matching, acknowledgment reactions, channels, verdict and error patterns;
- heartbeat cadence, persistent state, retry budgets, and stop conditions;
- CI and merge gates, merge authorization, dependency order, and multi-repository policy;
- post-merge synchronization, task closure, recording, and cleanup rules.
- documentation-only fast-path roots, excluded subtrees, allowed file types,
  deterministic validation, and mode-specific post-merge task status.

Keep project names, paths, models, commands, languages, status labels, bot identities, intervals, and retry counts out of this reusable skill.

## Run the delivery workflow

### 1. Verify the exact handoff

Read [verify-delivery-readiness.md](references/verify-delivery-readiness.md).

Confirm the exact task, authorized endpoint, repository/worktree/branch mapping, current diff, specification, gate evidence, task status, and ownership. Do not absorb unrelated dirty changes.

Classify the complete change set before review. Use the documentation-only fast
path only when every changed and untracked file intended for Git satisfies the
configured roots, file types, and exclusions. One ineligible, unfamiliar,
generated, executable, configuration, workflow, schema, or symlinked path
returns the whole delivery to the ordinary reviewed flow.

Record the exact head and base SHAs used for classification and deterministic
validation. Reclassify and rerun those gates if either SHA changes before
merge.

### 2. Run independent local review

Read [run-independent-local-review.md](references/run-independent-local-review.md).

For the ordinary flow, use a fresh configured reviewer without implementation
discussion history. Evaluate every finding against code, tests, architecture,
specification, and scope. Fix real findings locally, rerun affected gates, and
repeat review as required. Do not commit until the local-review gate passes or
an allowed blocker is explicit.

For a verified documentation-only fast path whose authorized endpoint includes
delivery mutations, skip independent local review. Still require the exact-diff
check, specification/document structure checks, link and identity validation,
secret/temporary-file rejection, and every configured deterministic gate before
commit. When the authorized endpoint is local review only, run the configured
independent reviewer even if the diff would otherwise qualify for the fast
path, then stop after reporting that review result.

### 3. Commit, push, and open or reconcile the pull request

Read [commit-push-and-open-pr.md](references/commit-push-and-open-pr.md).

Create intentional task-scoped commits, push without force, create or reuse the
exact pull request, verify target and head branches, and link the task through
`manage-project-work`. Apply the configured PR-review status only for ordinary
reviewed delivery. An automatic ready-spec fast path uses reference-only Issue
linkage and does not enter a review status. An ordinary documentation task uses
the project's configured close/reference linkage while still skipping review
statuses on the fast path. Read back external mutations.

Stop here when the authorized endpoint is only pull-request creation.

For a verified documentation-only fast path, skip steps 4–8: do not request
GitHub Codex review, create a review heartbeat, or require a clean-review
status. Continue directly to exact-head, reported-check, mergeability, and
authority verification for the same pull request. Absence of reported checks
or branch-protection evidence is not a blocker in this mode.

### 4. Start one GitHub review generation

Read [start-codex-review-cycle.md](references/start-codex-review-cycle.md).

Bind the generation to the exact pull request and current head SHA. Post the configured review request, capture its comment ID and timestamp, initialize attempt and heartbeat counters, and create or update one thread heartbeat with durable state and explicit stop conditions.

A new pushed head starts a new generation and resets its request budget. Old events cannot complete the new generation.

### 5. Monitor through the state machine

Read [monitor-codex-review-state-machine.md](references/monitor-codex-review-state-machine.md).

On each heartbeat, inspect the exact request comment, reactions, pull-request head, state, and all configured response channels after the current request timestamp. Use the prescribed evaluation order. Never interpret silence as `in_progress`, and never continue monitoring after a terminal state.

Use the bundled read-only inspector when `gh` is available:

```text
python3 scripts/inspect_codex_review_cycle.py \
  --repo OWNER/REPOSITORY \
  --pr NUMBER \
  --request-comment-id COMMENT_ID \
  --requested-at TIMESTAMP \
  --head-sha SHA \
  --reviewer-login-contains codex
```

Pass configured reviewer and pattern arguments. Treat script classifications as mechanical evidence; the agent still decides whether a finding is actionable.

### 6. Handle findings without scope drift

Read [classify-and-handle-review-findings.md](references/classify-and-handle-review-findings.md).

- Fix a real in-scope finding, rerun gates and local review as required, commit and push, then start a new head-bound generation.
- Answer an evidenced false or intentionally out-of-scope finding without changing code, request a contextual re-review, and persist its semantic fingerprint.
- Stop and inform the user when the same dismissed finding returns once.
- Stop on uncertainty that could change scope, architecture, security, or task outcome.

Do not delegate branch changes to a remote reviewer by default. Keep fixes in the controlled local task worktree.

### 7. Recover or stop deterministically

Read [recover-stalled-or-failed-review.md](references/recover-stalled-or-failed-review.md).

Apply the configured request and waiting budgets exactly. For the project policy agreed for this workflow:

- count silence per exact request;
- retry only after the configured number of silent heartbeats;
- allow no more than the configured total request attempts per head;
- treat an allowed reviewer acknowledgment on the exact request as non-terminal `in_progress`;
- stop after the configured acknowledged-without-result budget;
- let an explicit start error consume the current request attempt;
- delete the heartbeat and report once when any budget is exhausted.

### 8. Treat clean review as terminal

When the current generation has a clean verdict and no new actionable findings:

1. set review state to `clean`;
2. delete the review heartbeat immediately;
3. never request another review for that unchanged head;
4. ask `manage-project-work` to apply the configured merge-ready status;
5. report review success once.

Do not keep the review heartbeat alive for CI, merge, or closure. Continue through a separate CI/merge state only when the authorized endpoint permits it.

### 9. Merge, close, sync, and clean

Read [merge-close-and-clean.md](references/merge-close-and-clean.md).

For ordinary delivery, verify clean review, required checks, current head,
dependency order, and merge authority immediately before merge. For the
documentation-only fast path, replace the review requirement with the verified
fast-path classification and current deterministic-gate evidence. Require all
reported checks for the exact head to be terminal and non-failing, but do not
require checks or branch-protection evidence to exist. Always merge only the
exact current task pull request and never bypass provider-enforced rules. If
the base SHA differs from the validated base, rerun fast-path classification
and deterministic validation against the current head/base pair before merge.

After an automatic ready-spec merge, keep the implementation or research Issue
open and apply only the configured execution-ready status. After delivery of a
completed documentation task, use the ordinary completion lifecycle. Then
synchronize configured local branches and clean only proven task-owned state.

Report any dirty workspace, unavailable tracker, failed sync, or cleanup blocker without destroying unfamiliar work.

## Maintain heartbeat state

Persist at least:

- task and pull-request identity;
- authorized endpoint;
- current head SHA and generation;
- request attempt, comment ID, and timestamp;
- silent, acknowledged-wait, and explicit-error counters;
- dismissed-finding fingerprints;
- last-seen event IDs;
- current state and terminal reason.

Update the automation prompt after every state transition. If durable state cannot be updated or reread, stop the monitor rather than continuing statelessly.

## Coordinate with adjacent skills

- Receive the local-review handoff from `execute-project-task`.
- Receive an exact automatic ready-spec delivery handoff from
  `write-task-spec` only when project policy enables it.
- Use `manage-project-work` for PR, merge-readiness, done, and closure checkpoints.
- Use `record-project-context` for durable findings, active handoff, and the closing cycle.
- Return material scope or contract changes to `shape-project-work` or `write-task-spec`.
- Use provider-specific GitHub workflows for thread-level review operations when available, without changing this skill's authority boundary.
