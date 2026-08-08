# Bound Review Correction Cycles

Keep local-review corrections and GitHub pull-request review corrections
bounded independently while preserving one exact task contract.

## Contents

- [Bind the delivery baseline](#bind-the-delivery-baseline)
- [Keep two independent correction budgets](#keep-two-independent-correction-budgets)
- [Enforce the local-review budget](#enforce-the-local-review-budget)
- [Enforce the GitHub-review budget](#enforce-the-github-review-budget)
- [Scope GitHub state per pull request](#scope-github-state-per-pull-request)
- [Finalize terminal per-PR state centrally](#finalize-terminal-per-pr-state-centrally)
- [Stop scope drift before editing](#stop-scope-drift-before-editing)
- [Stop fail-closed and report the cycle](#stop-fail-closed-and-report-the-cycle)

## Bind the delivery baseline

Before the first independent local review, capture one delivery baseline with:

- exact Task ID, Issue, specification or equivalent approved contract, and its
  revision when one exists;
- acceptance criteria, explicit non-goals, repositories, worktrees, branches,
  and target branches;
- the complete initial task diff manifest with path, status, and content hash;
- initial diff statistics, including changed files, additions, and deletions.

Give every reviewer only neutral bounded context: the exact task contract,
acceptance criteria, non-goals, complete current diff, applicable instructions,
and required gates. Require each actionable finding to identify a concrete
current-task failure or credible mandatory risk and its relationship to the
reviewed diff. Do not include implementation discussion, the desired verdict,
or a defense of the current implementation.

Keep the same baseline for the whole delivery attempt. A new review run,
commit, push, pull-request head, heartbeat, or resumed turn must not redefine
the original task or initial diff.

## Keep two independent correction budgets

Read the configured positive limits for:

- local independent-review correction rounds; and
- GitHub pull-request review correction rounds.

Initialize `local_correction_rounds_used` to zero at the beginning of one new
delivery attempt. Before the first local review, persist the baseline, the local
counter, and its ordered history as one compact machine-readable delivery-state
block in the retained state of the current Codex task. Update and read back that
block after initialization and after every local review or correction
transition. Do not rely on unrecorded working memory.

Initialize a separate `github_correction_rounds_used` counter and ordered
history to zero in the first heartbeat for each new pull request. Do not create
one task-wide GitHub correction counter.

The state block must retain the complete baseline rather than only its
fingerprint. Include Task ID, Issue, specification or equivalent contract and
revision, acceptance criteria, non-goals, repositories, worktrees, branches,
target branches, the initial diff manifest, and initial diff statistics. Keep a
fingerprint as an integrity check, not as a substitute for those fields.

One correction round is one coherent package of code, tests, configuration, or
documentation changes made in response to one non-clean review result.
Multiple findings corrected together consume one round. Do not split one
review result into artificial packages to evade the limit. Follow-on edits
needed to make that same package pass its affected gates remain in the same
round.

These events do not consume a correction round by themselves:

- a finding without a code change;
- a clean review;
- a request retry caused by silence, acknowledgment without a result, or an
  explicit reviewer error;
- an evidence-based reply to a false or intentionally out-of-scope finding;
- a contextual re-review of an unchanged head.

Attribute a package to the reviewer whose non-clean result caused it. A GitHub
finding fixed locally consumes one GitHub round. A local verification review of
that package consumes no local round when clean; any additional code package
required by a new local finding consumes one local round.

## Enforce the local-review budget

Before applying a package requested by local review:

1. verify the finding is real and in scope;
2. compare `local_correction_rounds_used` with the configured limit;
3. stop before editing when another package would exceed the limit;
4. otherwise apply the smallest coherent package, increment the counter once,
   record its evidence, rerun affected gates, and review the complete new
   candidate.

The candidate produced by the final allowed local round still receives an
independent local review. If that review is non-clean and another real package
is required, do not start it, commit, push, or continue to pull-request
creation.

## Enforce the GitHub-review budget

Before changing code for a GitHub review finding, apply the same sequence to
that exact pull request's `github_correction_rounds_used`. Record the finding
fingerprints, package, before/after head SHAs and diff statistics, gates, and
resulting request generation in that PR's ordered history.

A pushed head in the same PR resets only the configured technical
request-attempt and waiting counters for the new generation. It never resets
that PR's GitHub correction counter or history.

The head produced by the final allowed GitHub round still receives review. If
it receives another real actionable finding, stop before another edit, commit,
push, review request, or heartbeat wait. Apply
[finalize-codex-review-state.md](finalize-codex-review-state.md) with
`github_correction_budget_exhausted`.

## Scope GitHub state per pull request

Each pull request independently owns up to the configured five GitHub
correction packages. Its first review generation starts at zero with an empty
history. Every later head and generation of that same PR preserves its counter
and history, while another PR starts its own counter at zero.

While review is active, persist GitHub counters, histories, dismissed
fingerprints, heads, generations, and technical request state only in the exact
PR heartbeat. Never copy or synchronize them between PRs. A clean verdict
completes only that PR's review; it cannot complete another PR or change another
PR's budget.

## Finalize terminal per-PR state centrally

Use [finalize-codex-review-state.md](finalize-codex-review-state.md) as the only
owner of terminal snapshot, readback, heartbeat deletion, and pause behavior.
Every terminal branch must select one matrix reason and apply that procedure.
Do not duplicate its mutation rules in another runbook.

## Stop scope drift before editing

Treat a finding as non-actionable for the current delivery when it asks only
for generalized hardening, stylistic cleanup, a speculative edge case without
a credible current-task path, a pre-existing unrelated defect, future scaling,
or work assigned to another task.

Before every correction package, compare the proposed change with the delivery
baseline and current task contract. Stop for analysis instead of editing when
the proposed package:

- changes outcome, acceptance criteria, non-goals, architecture, permissions,
  security posture, data contract, dependency direction, or repository
  ownership;
- introduces a new repository, subsystem, migration, or durable contract not
  required by the approved task;
- causes material cumulative diff growth that cannot be explained directly by
  concrete in-scope findings;
- repeats a semantic defect category that was already fixed or dismissed and
  indicates moving review boundaries.

Return a contract or scope change to its owning shaping or specification
workflow. Do not let reviewer preference silently redefine the task.

## Stop fail-closed and report the cycle

When either next correction would exceed its configured limit, return a bounded
cycle analysis containing:

- the delivery baseline and current diff manifest and statistics;
- every reviewed head or uncommitted candidate;
- ordered finding fingerprints and classifications;
- every local and GitHub correction package with its counter value;
- files and behavior introduced only by review corrections;
- open findings, repeated semantic categories, and signs of scope drift;
- the recommended owning workflow or explicit user decision.

Resume local review only when the baseline, local counter, and local ordered
history are provable from retained task state. Resume GitHub review only when
the exact PR's active heartbeat or verified terminal snapshot proves that PR's
counter and ordered history. A different PR is not a resume and starts its own
GitHub counter at zero. Do not invent repository-local runtime files, locks, or
archives.

If interruption or resume makes the state uncertain, fail closed. A different
conversation is not an automatic continuation unless it can prove the exact
retained state. Do not reset either counter or start a nominally new attempt
automatically. Require an explicit user decision after presenting the known
history and uncertainty. If an active heartbeat exists, apply the terminal
procedure with `lost_or_contradictory_state` or `pr_identity_ambiguous`.
