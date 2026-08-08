# Bound Review Correction Cycles

Keep local-review corrections and GitHub pull-request review corrections
bounded independently while preserving one exact task contract.

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

Initialize `local_correction_rounds_used` and
`github_correction_rounds_used` to zero at the beginning of one new delivery
attempt. Retain an ordered history for each counter.

Before the first local review, persist the baseline, both counters, and both
ordered histories as one compact machine-readable delivery-state block in the
retained state of the current Codex task. Update and read back that block after
initialization and after every local review or correction transition. Do not
rely on unrecorded working memory.

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
`github_correction_rounds_used`. Record the finding fingerprints, package,
before/after head SHAs and diff statistics, gates, and resulting request
generation.

A pushed head resets only the configured technical request-attempt and waiting
counters for the new generation. It never resets the GitHub correction counter,
the delivery baseline, or either correction history.

The head produced by the final allowed GitHub round still receives review. If
it receives another real actionable finding, stop before another edit, commit,
push, review request, or heartbeat wait. Delete the review heartbeat before
reporting the stop.

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

Resume an existing delivery attempt only when both counters, the baseline, and
the ordered histories are provable from retained delivery state. Before PR
creation, the current Codex task is the required state owner. At GitHub review
initialization, copy that exact pre-PR state into the heartbeat prompt, read it
back, and keep both copies consistent until the local state is no longer needed.
Do not invent repository-local runtime files, locks, or archives.

If interruption or resume makes the state uncertain, fail closed. A different
conversation is not an automatic continuation unless it can prove the exact
retained state. Do not reset either counter or start a nominally new attempt
automatically. Require an explicit user decision after presenting the known
history and uncertainty.
