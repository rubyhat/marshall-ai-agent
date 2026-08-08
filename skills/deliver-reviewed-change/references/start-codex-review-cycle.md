# Start a Codex Review Cycle

Bind every review generation to one exact pull request head.

## Contents

- [Initialize the generation](#initialize-the-generation)
- [Initialize or reactivate heartbeat state](#initialize-or-reactivate-heartbeat-state)
- [Create one request attempt](#create-one-request-attempt)
- [Attach and verify the request identity](#attach-and-verify-the-request-identity)

## Initialize the generation

Before requesting review, capture:

- Task ID and Issue;
- repository and PR URL/number;
- authorized endpoint;
- current PR state;
- current head SHA;
- review-generation number;
- immutable delivery-baseline fingerprint;
- local correction state and this PR's GitHub correction counter and history;
- required checks to rerun after code changes;
- configured reviewer matching and response patterns.

A push that changes head SHA invalidates the previous generation. Start a new
generation with fresh technical request and waiting counters, but preserve the
local correction state and this PR's GitHub correction counter and history.

Before a workflow-owned push that will change the PR head, persist and read back
the same exact PR heartbeat in paused finding state. Keep it paused until the
push and new head readback finish, then reactivate that same automation for the
new generation. If the old heartbeat was active during the push or ownership of
the transition is not provable, apply `head_mismatch` fail-closed. Do not treat an
unknown external head change as an authorized transition.

Before every initial or later GitHub generation, read the retained current-task
block and the exact PR state independently. Prove that their complete delivery
baseline and fingerprint match. Copy the authoritative local correction counter
and ordered history from the task block into this PR's heartbeat, then read back
the combined state while preserving this PR's GitHub counter, history, dismissed
fingerprints, and technical state. Never copy PR-owned GitHub state back to the
task block or into another PR. If either source or the combined readback is not
provable, apply `lost_or_contradictory_state` before posting a review request.

For the first generation of a new PR, copy the exact delivery baseline and local
correction state from the current Codex task, then initialize this PR's GitHub
counter to zero with an empty history. To resume an existing PR, read its exact
heartbeat, whether active or paused. Never initialize or reconstruct one PR's
GitHub counter from another PR, a task-wide counter, commits, or PR prose.

For a paused heartbeat, compare its terminal reason and distinct
`terminal_head_sha` with the current PR head before reactivation or a request.
Do not use the generation's `head_sha` for this comparison: on `head_mismatch`
it is the superseded head. A current head equal to `terminal_head_sha` does not
start another review cycle: `clean` returns to the already proven merge-ready
checkpoint, while every other reason returns its recorded terminal outcome.
Keep the heartbeat paused. Only an authorized later head of the same open PR may
reactivate that same heartbeat and start a new generation. If the provider shows
the PR merged or closed, apply the terminal procedure with `pr_terminal` instead
of reactivating it.

Verify which repository instructions and code-review rules are visible to the remote reviewer. Do not assume that a local reusable skill outside the target repository is available to GitHub Codex; keep essential repository-specific review rules in an applicable `AGENTS.md` or another configured reviewer-visible source.

If the reviewer cannot access the task specification or root project rules, put a bounded task-specific summary, acceptance criteria, and non-goals in the PR description or another reviewer-visible context message. Keep the actual trigger comment in its configured exact form.

## Initialize or reactivate heartbeat state

Before posting a remote review trigger, create one current-thread heartbeat for
a new PR or reactivate the existing paused heartbeat for the same PR. Never
replace a paused same-PR heartbeat with a new automation. Use the configured
cadence and verify the saved automation. Until a request exists, set
`request_comment_id`,
`request_created_at`, request author, and request URL to null and set state to
`request_not_created`.

Its prompt must contain a compact machine-readable state block with:

```yaml
task_id:
repository:
pr_url:
authorized_endpoint:
heartbeat_status:
head_sha:
review_generation:
request_attempt:
request_comment_id:
request_created_at:
request_author:
request_url:
silent_heartbeat_count:
in_progress_heartbeat_count:
explicit_error_count:
github_counter_scope: pull_request
delivery_baseline:
  task_id:
  issue:
  specification_or_equivalent_contract:
  specification_revision_or_not_applicable:
  acceptance_criteria:
  non_goals:
  repositories:
  worktrees:
  branches:
  target_branches:
  initial_diff_manifest:
  initial_diff_stats:
delivery_baseline_fingerprint:
local_correction_rounds_used:
local_correction_history:
github_correction_rounds_used:
github_correction_history:
dismissed_finding_fingerprints:
last_seen_event_ids:
state:
terminal_reason:
terminal_head_sha:
```

Initialize technical request, waiting, and explicit-error counters to zero. For
a new PR, also initialize its GitHub correction counter to zero and history to
empty. For a new head of the same PR, preserve that PR's GitHub counter and
history. When reactivating, clear the prior terminal reason and observed terminal
head only as part of the verified new-generation transition. Preserve the copied
local state, complete delivery baseline, and its fingerprint exactly. Keep state
at `request_not_created` and heartbeat status active until the request is
attached and read back.

The prompt must also state:

- inspect only the exact PR and current request;
- read every configured review channel after `request_created_at`;
- follow the state-machine evaluation order;
- update the prompt after each transition;
- apply [finalize-codex-review-state.md](finalize-codex-review-state.md) at every
  terminal state;
- report once on success or stop;
- never broaden the authorized endpoint.

Read back the created or reactivated automation and confirm:

- destination is the current thread;
- cadence matches project policy;
- it is recurring without an accidental finite occurrence limit;
- repository, immutable PR identity, and head SHA are correct;
- GitHub counter scope is the exact pull request;
- baseline, counters, histories, and terminal rules are present;
- state is `request_not_created`, status is active, and no request identity is
  fabricated;
- reactivation reused the same automation identity and preserved the same PR's
  GitHub counter, history, and dismissed fingerprints.

If created or reactivated state cannot be read back, stop before posting the
trigger, preserve any addressable same-PR heartbeat, and report that no remote
review became active. Do not monitor from informal memory.

## Create one request attempt

For every initial, retry, or contextual request attempt, first read back an
addressable current heartbeat for the exact PR and head. The initial attempt
uses the verified created or reactivated heartbeat; later attempts use the
verified active heartbeat from the prior request. Only then post the configured
exact review trigger. Read back the created comment and capture:

- request attempt number;
- request comment ID;
- request timestamp;
- head SHA at request time;
- request author and URL.

Do not assume a successful API response means the reviewer started. Do not reuse
an earlier request comment as the current attempt. If posting may have succeeded
but exact request readback fails, apply the terminal procedure with
`lost_or_contradictory_state` to the already addressable current heartbeat.

## Attach and verify the request identity

Update that exact heartbeat with the proven request identity, change state to
`request_pending`, reset only the applicable per-request technical counters,
and read it back before monitoring.

Confirm:

- destination is the current thread;
- cadence matches project policy;
- it is recurring without an accidental finite occurrence limit;
- PR identity and head SHA are correct;
- GitHub counter scope is the exact pull request;
- counters and request identity match the created comment;
- terminal rules are present.

If the state cannot be saved or reread, apply the terminal procedure with
`lost_or_contradictory_state`. Do not monitor from informal memory.
