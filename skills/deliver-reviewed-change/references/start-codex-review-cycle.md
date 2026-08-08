# Start a Codex Review Cycle

Bind every review generation to one exact pull request head.

## Contents

- [Initialize the generation](#initialize-the-generation)
- [Initialize and verify provisional heartbeat state](#initialize-and-verify-provisional-heartbeat-state)
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

For the first generation of a new PR, copy the exact delivery baseline and local
correction state from the current Codex task, then initialize this PR's GitHub
counter to zero with an empty history. To resume an existing PR, read its exact
active heartbeat or verified terminal per-PR snapshot. Never initialize or
reconstruct one PR's GitHub counter from another PR, a task-wide counter,
commits, or PR prose.

When the source is a terminal snapshot, compare its terminal reason and distinct
`terminal_head_sha` with the current PR head before creating a heartbeat or
posting a request. Do not use the generation's `head_sha` for this comparison:
on `head_mismatch` it is the superseded head. A current head equal to
`terminal_head_sha` does not start another review cycle: `clean`
returns to the already proven merge-ready checkpoint, while every other reason
returns its recorded terminal outcome. Only a later head of the same PR may
start a new generation from that snapshot.

Verify which repository instructions and code-review rules are visible to the remote reviewer. Do not assume that a local reusable skill outside the target repository is available to GitHub Codex; keep essential repository-specific review rules in an applicable `AGENTS.md` or another configured reviewer-visible source.

If the reviewer cannot access the task specification or root project rules, put a bounded task-specific summary, acceptance criteria, and non-goals in the PR description or another reviewer-visible context message. Keep the actual trigger comment in its configured exact form.

## Initialize and verify provisional heartbeat state

Before posting a remote review trigger, create or update one current-thread
heartbeat for this PR. Use the configured cadence and verify the saved
automation. Until a request exists, set `request_comment_id`,
`request_created_at`, request author, and request URL to null and set state to
`request_not_created`.

Its prompt must contain a compact machine-readable state block with:

```yaml
task_id:
repository:
pr_url:
authorized_endpoint:
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
history. Preserve the copied local state, complete delivery baseline, and its
fingerprint exactly. Keep state at `request_not_created` until the request is
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

Read back the provisional automation and confirm:

- destination is the current thread;
- cadence matches project policy;
- it is recurring without an accidental finite occurrence limit;
- repository, immutable PR identity, and head SHA are correct;
- GitHub counter scope is the exact pull request;
- baseline, counters, histories, and terminal rules are present;
- state is `request_not_created` and no request identity is fabricated.

If provisional state cannot be created and read back, stop before posting the
trigger and report that no remote review became active. Do not monitor from
informal memory.

## Create one request attempt

For every initial, retry, or contextual request attempt, first read back an
addressable current heartbeat for the exact PR and head. The initial attempt
uses the verified provisional heartbeat; later attempts use the verified active
heartbeat from the prior request. Only then post the configured exact review
trigger. Read back the created comment and capture:

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
