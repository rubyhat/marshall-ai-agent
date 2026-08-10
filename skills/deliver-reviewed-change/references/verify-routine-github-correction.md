# Verify a Routine GitHub Correction

Apply this gate to a correction package requested by GitHub review after the
exact pull request exists. Do not use it for the pre-PR local-review phase.

## Require the pre-PR gate

Before classifying or editing a GitHub finding, prove that the pull request was
created from a candidate with bound passed pre-PR local-review evidence. If the
evidence is missing, return `pre_pr_local_gate_missing` before correction,
review request, or merge. An accepted blocker or owner override cannot bypass
this gate.

The pull request closes the active pre-PR local-review phase. Retain its counter
and ordered history as provenance, but do not reopen that phase for a routine
GitHub correction or because the local correction counter is exhausted.

## Classify before every edit

For every proposed correction and every follow-on edit needed to make its gates
pass:

1. bind the finding to the immutable delivery baseline, acceptance criteria,
   non-goals, and reviewed head;
2. classify it as `real_in_scope`, `false`, `intentional_out_of_scope`,
   `duplicate`, or `uncertain`;
3. stop with `scope_or_contract_stop` before edits, counter increment, commit,
   push, or another request when the correction is `uncertain` or changes the
   outcome, scope, acceptance criteria, architecture, permissions, security or
   tenant boundary, data contract, migration or backfill, repository ownership,
   dependency direction, or causes unexplained cumulative diff growth;
4. continue only for a routine `real_in_scope` correction.

Do not use a targeted or full local model review to decide or bypass this gate.

## Persist the exact package

Consume one GitHub correction round for one coherent package, even when it
addresses several findings. Preserve in the exact PR history:

- reviewed head SHA and GitHub round;
- finding IDs or semantic fingerprints and classifications;
- bounded changed-behavior mapping and exact changed paths;
- base head and candidate commit or tree identity;
- before/after changed-file, addition, and deletion statistics;
- affected tests and deterministic verification evidence.

Follow-on gate-fix edits remain in the same round after they pass the
classification gate again.

## Run deterministic verification

Before commit or push, require all of:

- affected tests;
- every configured deterministic gate applicable to the changed paths;
- `git diff --check`;
- exact correction-delta review from the prior reviewed head to the candidate;
- exact path/scope verification with no unexplained path or drift;
- finding-by-finding readback naming the fixed behavior, changed paths, and
  verification evidence.

Any failed or missing item blocks commit, push, and the next generation. A
routine package records `local_model_invocations: 0`; do not run `codex review`,
another local model reviewer, or a hidden reviewer subprocess.

## Continue with GitHub review

After deterministic verification passes, commit intentionally, reread the
paused exact-PR heartbeat, push without force, and prove the new head. Start a
new head-bound GitHub generation that reviews the complete pull-request head.
Reset only technical request and waiting counters. Preserve the immutable
delivery baseline, local audit history, GitHub correction counter, and GitHub
ordered history.
