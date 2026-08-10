# Run the Planning GitHub Review Cycle

Use this procedure for every initial or corrected planning pull-request head.
Read all trigger, reviewer, channel, verdict, retry, cadence, counter, and state
values from `planning_publication.post_pr_correction_review.github_review_cycle`.
Do not borrow runtime state or procedural references from implementation
delivery.

## Initialize the exact pull request

Before the first remote request, prove the exact task, repository, pull request,
authorized endpoint, current open state, head SHA, complete publication manifest,
and passed pre-PR independent-review evidence. Create one current-thread
heartbeat for this exact planning pull request and read it back before posting
the configured request comment.

The heartbeat must persist at least:

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
acknowledged_heartbeat_count:
explicit_error_count:
publication_manifest:
pre_pr_review_evidence:
github_correction_rounds_used:
github_correction_history:
last_seen_event_ids:
stale_or_unbound_event_ids:
response_binding_evidence:
state:
terminal_reason:
terminal_head_sha:
```

For a new pull request, initialize `github_correction_rounds_used: 0`, an empty
ordered GitHub history, zero technical counters, null request identity, and
`state: request_not_created`. The configured maximum is five packages for this
exact pull request. Never reconstruct its counter from another PR, task prose,
commit count, or informal memory.

On resume, reuse and read back only the addressable heartbeat for the same pull
request. Preserve its counter and ordered history. A new authorized head resets
only request and waiting counters; it does not reset the GitHub correction
counter. Lost, ambiguous, or contradictory state stops before a request, edit,
push, final evidence review, or merge.

## Create and bind one request attempt

From the verified active heartbeat, post the configured exact request comment.
Read the created comment back and capture its ID, timestamp, author, URL,
attempt number, and head SHA. Attach that identity to the same heartbeat, set
`state: request_pending`, reset only the applicable per-request technical
counters, and read back the update before monitoring.

If posting may have succeeded but request identity cannot be proved, pause the
heartbeat with `lost_or_contradictory_state`. Do not post a speculative duplicate
or monitor from conversation memory.

## Monitor one deterministic transition

At each configured heartbeat, take one atomic snapshot:

1. current PR state and head SHA;
2. configured acknowledgment reactions on the exact request comment;
3. every configured response channel after `request_created_at`;
4. events matching a configured reviewer login or login substring;
5. each event's provider-reviewed commit SHA, when exposed, and active
   request-generation correlation;
6. event IDs not already present in `last_seen_event_ids`.

Before state evaluation, bind each possible response to the persisted generation
head. Accept it when the provider exposes that exact reviewed commit SHA. A
matched-reviewer issue comment that omits commit metadata may instead bind to
the active request generation only when all of these facts are proven from one
atomic snapshot: it belongs to the exact PR, is a new event created after the
persisted request, the request is still the sole active attempt for this
generation, no later generation or request supersedes it, and the current PR
head still equals the generation head. This binding comes from the exact
head-bound request lifecycle, not from issue-comment metadata. A timestamp,
reviewer identity, current head, reaction, or issue comment without that
complete active-generation correlation is not sufficient. Record an old-head
or unbound event in `stale_or_unbound_event_ids` and ignore it for the current
generation; it cannot produce findings, CLEAN, progress, or an error.

Apply the first matching configured state in this strict order:

1. `pr_terminal` when the provider proves merged or closed;
2. `head_mismatch` when the observed head is not the persisted generation head;
3. `findings_received` for possible findings from the matched reviewer;
4. `clean` for a configured current-generation clean verdict with no findings;
5. `transient_error` for a configured explicit error pattern;
6. `in_progress` for an allowed acknowledgment on the exact request;
7. `not_started` only after every response channel is empty;
8. `unclassified_response` for any remaining matched reviewer response.

Acknowledgment is never terminal and never overrides findings or CLEAN.
Silence is never `in_progress`.

For `not_started`, increment the silent count. When the configured per-attempt
threshold is reached, create another bound request attempt only if the total
per-head attempt budget permits; otherwise pause with
`request_budget_exhausted`. For `in_progress`, reset the silent count and
increment the acknowledged-without-result count; exhausting that limit pauses
with `acknowledged_wait_budget_exhausted`.

For `transient_error`, persist the state, matched event ID, error evidence, and
incremented explicit-error count before deciding the next transition. The error
consumes the current request attempt. If another configured per-head attempt
remains, immediately use the complete `Create and bind one request attempt`
transition, attach and read back the new request identity, and return to
`request_pending`. If no attempt remains, pause and read back the heartbeat with
`request_budget_exhausted`. Never leave `transient_error` as an ambiguous active
state or create a separate hidden error-retry loop.

Persist and read back the exact heartbeat after every transition. A failed
write or readback stops the monitor; it never creates a stateless retry loop.

## Route findings through the bounded package gate

On `findings_received`, persist the reviewed head, exact finding identities,
counter, and ordered history, then pause and read back the heartbeat before any
edit. Apply
[verify-post-pr-planning-correction.md](verify-post-pr-planning-correction.md).

For a `real_in_scope` finding, if `github_correction_rounds_used` is already
five, stop before edits, counter increment, commit, push, or another request and
report the bounded cycle. A non-actionable classification still follows its
configured unchanged-head no-edit path because it consumes no correction
package. For one allowed routine package, increment the exact PR counter once
after the package is applied, append its finding IDs, changed paths, behavior
mapping, before/after statistics, and verification evidence, then read back the
paused state. Follow-on deterministic gate fixes remain part of that same
package.

The fifth package still passes every deterministic gate, pushes, and receives a
fresh full-head GitHub generation. A sixth package never starts. Material or
uncertain findings stop before edits and do not increment the counter.

After the package gates pass, create the intentional exact-manifest correction
commit. Prove its local head SHA, tree, complete manifest, and correction delta
before rereading the paused heartbeat. Push that commit without force, prove the
remote PR now has the same new head and complete manifest, reset only technical
request state, reactivate the same heartbeat, and create the next head-bound
generation. Events from an older or unbound head cannot complete it.

## Finalize review state

`clean` is absorbing for the unchanged head. Persist `terminal_head_sha`, pause
and read back the heartbeat while the pull request remains open, and continue to
the zero-or-one final evidence gate. Do not request another review for that head.

Every other review-terminal result also records its reason and observed terminal
head, then pauses the same heartbeat while the PR is open. An unchanged terminal
head returns its recorded outcome. Only a proven later authorized head of the
same PR may reactivate it. Delete the heartbeat only after the provider proves
that exact pull request merged or closed; inability to prove terminal PR state
leaves it paused and addressable.
