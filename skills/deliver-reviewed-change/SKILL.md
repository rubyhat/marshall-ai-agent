---
name: deliver-reviewed-change
description: Deliver an exact current implementation task from an uncommitted local-review handoff through independent local review, intentional commit and push, pull-request creation, review-feedback handling, GitHub Codex review monitoring, authorized merge, tracker closure, synchronization, and workspace cleanup. Use when the user explicitly asks to review, publish, deliver, finish, or merge the current task; invokes `--deliver-task` with a Task ID, Issue URL, PR URL, spec path, or current task anchor; asks to resume or address feedback on that exact task's pull request; or when a configured heartbeat resumes its active review cycle. Verify active conversation authority before review or delivery mutations and respect narrower requested endpoints. Do not use for initial implementation, unrelated pull requests, generic GitHub orientation, force-push, deployment, production mutations, or broad repository cleanup.
---

# Deliver Reviewed Change

Move one exact implementation task through review and delivery without losing task identity, scope, review-cycle state, or merge authority.

## Keep the responsibility narrow

- Receive verified uncommitted changes from `execute-project-task` or an equivalent configured local-review handoff.
- Own independent local review, finding assessment, commit, push, pull-request creation, review monitoring, authorized merge, operational closure, sync, and task-workspace cleanup.
- Preserve the agreed specification and non-goals while addressing findings.
- Do not perform initial feature implementation, silently expand scope, select an unrelated pull request, force-push, deploy, mutate production, or bypass required gates.
- Do not absorb a planning/specification publication pull request; route it to
  `publish-planning-change` and preserve the implementation Issue as open.
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

The alias does not authorize force-push, unrelated pull requests, Project schema changes, deployment, production data access, destructive recovery, or bypassing review and CI.

## Resolve project policy

Read project instructions and workflow configuration. Resolve:

- task, Issue, specification, branch, worktree, and repository mapping;
- required local-review command, model, fallback, rubric, and architecture gates;
- commit, push, PR description, target branch, linkage, and status policy;
- GitHub review trigger, reviewer actor matching, acknowledgment reactions, channels, verdict and error patterns;
- heartbeat cadence, persistent state, retry budgets, and stop conditions;
- separate local and GitHub correction-round budgets, delivery-baseline
  binding, retained histories, and scope-drift stop conditions;
- CI and merge gates, merge authorization, dependency order, and multi-repository policy;
- post-merge synchronization, task closure, recording, and cleanup rules.

Keep project names, paths, models, commands, languages, status labels, bot identities, intervals, and retry counts out of this reusable skill.

## Run the delivery workflow

### 1. Verify the exact handoff

Read [verify-delivery-readiness.md](references/verify-delivery-readiness.md).

Confirm the exact task, authorized endpoint, repository/worktree/branch mapping, current diff, specification, gate evidence, task status, and ownership. Do not absorb unrelated dirty changes.

### 2. Run independent local review

Read [run-independent-local-review.md](references/run-independent-local-review.md).
Read [bound-review-correction-cycles.md](references/bound-review-correction-cycles.md).

Use a fresh configured reviewer without implementation discussion history. Evaluate every finding against code, tests, architecture, specification, and scope. Fix real findings locally, rerun affected gates, and repeat review as required. Do not commit until the local-review gate passes or an allowed blocker is explicit.

### 3. Commit, push, and open or reconcile the pull request

Read [commit-push-and-open-pr.md](references/commit-push-and-open-pr.md).

Create intentional task-scoped commits, push without force, create or reuse the exact pull request, verify target and head branches, link the task, and apply the configured PR-review status through `manage-project-work`. Read back external mutations.

Stop here when the authorized endpoint is only pull-request creation.

### 4. Start one GitHub review generation

Read [start-codex-review-cycle.md](references/start-codex-review-cycle.md).

Bind the generation to the exact pull request and current head SHA. Create and
read back its durable heartbeat before the first review request. For every
initial, retry, or contextual request, post only from an addressable exact-PR
heartbeat, then attach and read back the new request identity before monitoring.
Before each generation, refresh and read back authoritative local correction
state from the retained task block without changing this PR's GitHub state.

A new pushed head starts a new generation and resets only its technical request
budget. It does not reset the GitHub correction-round budget, delivery baseline,
or correction history. Old events cannot complete the new generation.

### 5. Monitor through the state machine

Read [monitor-codex-review-state-machine.md](references/monitor-codex-review-state-machine.md).
Read [finalize-codex-review-state.md](references/finalize-codex-review-state.md)
before any terminal review transition.

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
- Stop before mutations and return a bounded cycle analysis when the next local
  or GitHub correction package would exceed its configured independent limit.
- Stop on uncertainty that could change scope, architecture, security, or task outcome.

For every terminal finding outcome, select its terminal reason and apply
[finalize-codex-review-state.md](references/finalize-codex-review-state.md).

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
- apply [finalize-codex-review-state.md](references/finalize-codex-review-state.md)
  with the exact exhausted-budget terminal reason.

### 8. Treat clean review as terminal

When the current generation has a clean verdict and no new actionable findings:

1. apply [finalize-codex-review-state.md](references/finalize-codex-review-state.md)
   with `clean`;
2. continue only after it returns `pause_merge_ready`;
3. never request another review for that unchanged head;
4. ask `manage-project-work` to apply the configured merge-ready status;
5. report review success once.

Keep the exact PR heartbeat paused during CI and merge. After provider evidence
proves that the PR is merged or closed, apply the terminal procedure with
`pr_terminal` and delete only that exact heartbeat. Continue through a separate
CI/merge state only when the authorized endpoint permits it.

### 9. Merge, close, sync, and clean

Read [merge-close-and-clean.md](references/merge-close-and-clean.md).

Verify clean review, required checks, current head, dependency order, and merge authority immediately before merge. Merge only the exact current task pull request. Then close/reconcile the task, synchronize configured local branches, run the recording closing cycle, and remove task worktrees/branches only after merge and safety checks.

Report any dirty workspace, unavailable tracker, failed sync, or cleanup blocker without destroying unfamiliar work.

## Maintain heartbeat state

Persist at least:

- task and pull-request identity;
- authorized endpoint;
- heartbeat automation status;
- current head SHA and generation;
- terminal-observed head SHA when the state is terminal;
- request attempt, comment ID, and timestamp;
- silent, acknowledged-wait, and explicit-error counters;
- the immutable delivery-baseline fingerprint;
- local correction-round state and the exact PR's independent GitHub correction
  counter and compact ordered history;
- dismissed-finding fingerprints;
- last-seen event IDs;
- current state and terminal reason.

Update and read back only the exact PR heartbeat after every active or terminal
GitHub review transition. Preserve it in paused state while its PR remains open,
and reactivate it only for an authorized later head of the same PR. Apply
[finalize-codex-review-state.md](references/finalize-codex-review-state.md) for
every terminal transition. Never synchronize, copy, or derive one PR's GitHub
counter or history from another PR, and never delete a heartbeat before its
exact PR is proven merged or closed.

## Coordinate with adjacent skills

- Receive the local-review handoff from `execute-project-task`.
- Use `manage-project-work` for PR, merge-readiness, done, and closure checkpoints.
- Use `record-project-context` for durable findings, active handoff, and the closing cycle.
- Return material scope or contract changes to `shape-project-work` or `write-task-spec`.
- Use provider-specific GitHub workflows for thread-level review operations when available, without changing this skill's authority boundary.
