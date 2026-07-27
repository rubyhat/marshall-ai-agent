# Start a Codex Review Cycle

Bind every review generation to one exact pull request head.

## Initialize the generation

Before requesting review, capture:

- Task ID and Issue;
- repository and PR URL/number;
- authorized endpoint;
- current PR state;
- current head SHA;
- review-generation number;
- required checks to rerun after code changes;
- configured reviewer matching and response patterns.

A push that changes head SHA invalidates the previous generation. Start a new generation with fresh request counters.

Verify which repository instructions and code-review rules are visible to the remote reviewer. Do not assume that a local reusable skill outside the target repository is available to GitHub Codex; keep essential repository-specific review rules in an applicable `AGENTS.md` or another configured reviewer-visible source.

If the reviewer cannot access the task specification or root project rules, put a bounded task-specific summary, acceptance criteria, and non-goals in the PR description or another reviewer-visible context message. Keep the actual trigger comment in its configured exact form.

## Create one request attempt

Post the configured exact review trigger. Read back the created comment and save:

- request attempt number;
- request comment ID;
- request timestamp;
- head SHA at request time;
- request author and URL.

Do not assume a successful API response means the reviewer started. Do not reuse an earlier request comment as the current attempt.

## Initialize durable heartbeat state

Create or update one current-thread heartbeat for this PR. Use the configured cadence and verify the saved automation.

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
silent_heartbeat_count:
in_progress_heartbeat_count:
explicit_error_count:
dismissed_finding_fingerprints:
last_seen_event_ids:
state:
terminal_reason:
```

Initialize counters to zero and state to `request_pending`.

The prompt must also state:

- inspect only the exact PR and current request;
- read every configured review channel after `request_created_at`;
- follow the state-machine evaluation order;
- update the prompt after each transition;
- delete the heartbeat at every terminal state;
- report once on success or stop;
- never broaden the authorized endpoint.

## Verify the heartbeat

Read back the automation and confirm:

- destination is the current thread;
- cadence matches project policy;
- it is recurring without an accidental finite occurrence limit;
- PR identity and head SHA are correct;
- counters and request identity match the created comment;
- terminal rules are present.

If the state cannot be saved or reread, delete or pause the incomplete heartbeat and stop. Do not monitor from informal memory.
