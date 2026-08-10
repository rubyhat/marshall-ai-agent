# Verify Post-PR Planning Corrections

Use this procedure only after the exact planning pull request exists. The
bounded pre-PR independent review remains required, but a routine GitHub
correction package does not re-enter that correction loop.

## Require the GitHub generation gate

Read the exact-PR counter from the planning GitHub heartbeat. A new planning
pull request starts at zero with an empty ordered history and a configured
maximum of five packages. A new head preserves that counter and history while
resetting only technical request state. If they cannot be proved on resume,
stop before edits or a new request instead of reinitializing them.

After creating the pull request, start or reconcile the configured head-bound
GitHub review generation for its exact complete initial head. Before final
evidence selection or merge, require a clean generation bound to the exact
current full head. An absent, stale, non-clean, or unbound generation blocks
both gates. A corrected head always requires its own new generation; an event
from an older head cannot satisfy this requirement.

## Verify a routine package deterministically

Before every correction edit and every follow-on gate-fix edit:

1. bind the finding to the exact task, publication manifest, reviewed head,
   shaped scope, acceptance criteria, and non-goals;
2. classify it as `real_in_scope`, `false`, `intentional_out_of_scope`,
   `duplicate`, or `uncertain`;
3. treat only `real_in_scope` as an actionable routine package, and only when
   it directly fixes a proven current-task defect without changing outcome,
   scope, contract, architecture, permissions, security or tenant boundary,
   data or migration behavior, repository ownership, or dependency direction;
4. stop before edits, counter increment, commit, push, or a new request when the
   finding is material or `uncertain`, and return it to the owning planning
   workflow;
5. preserve the prior independent evidence as invalidated history when bytes or
   head identity change; never use it as current readiness evidence.

For `false`, `intentional_out_of_scope`, or `duplicate`, make no planning edit
and consume no correction round. Persist a semantic fingerprint and evidence,
reply with the bounded explanation, then create and bind one contextual
re-review request for the unchanged head through the configured request budget.
The contextual generation must still reach CLEAN before final evidence or
merge. If the same semantic finding appears again after that response, pause
with `repeated_dismissed_finding` instead of replying or requesting again.

For a routine package require affected tests, every configured deterministic
gate, `git diff --check`, exact correction delta and scope verification, and a
finding-by-finding readback. Record exact paths, behavior mapping, before/after
statistics, and `local_model_invocations: 0`. Do not run the canonical review
runner, `codex review`, or another model between GitHub correction packages.

After applying one allowed package, increment the exact PR's GitHub correction
counter once, append its evidence to the ordered history, and read back the
paused heartbeat. After the gates pass, stage only the exact correction
manifest, create an intentional commit, and prove its local head SHA, tree,
complete manifest, and exact delta. Reread the still-paused heartbeat, then push
that commit without force and prove the remote PR head and manifest match it
before starting the next GitHub generation. Preserve the exact PR's GitHub
correction counter and history. The fifth and final allowed package still
receives GitHub review; when five packages are already used, stop before a
sixth package's edits, counter increment, commit, push, or request.

## Run zero or one final evidence review

Wait for the required clean GitHub generation bound to the exact current full
head. GitHub clean is a gate to evidence selection, not authoritative planning
evidence.

- Reuse the last independent evidence with zero invocations only when it is
  already valid for the exact current head revision, tree, and complete sorted
  path/mode/blob-OID manifest.
- Otherwise invoke the canonical authoritative runner exactly once against the
  exact current committed head and canonical base. A new commit requires this
  review even when it restores the same manifest blob OIDs as an older commit,
  because its head/tree binding differs.

This final evidence invocation consumes neither a local correction round nor a
GitHub correction round. Its technical retry behavior remains owned by the
canonical runner.

## Handle the terminal result

- `CLEAN`: bind the complete current-schema evidence to the exact head, tree,
  manifest, publication attempt, result hash, and matched session/event set,
  then continue to checks and merge.
- `NON_CLEAN`: preserve exact findings and return them to spec preparation;
  stop the current publication attempt before edits, push, merge, another
  GitHub request, or a second final evidence invocation.
- invalid, unbound, changed-target, settlement-timeout, invocation-timeout, or
  exhausted technical-retry result: preserve bounded evidence and stop with the
  same no-automatic-correction rule.

Any mutation after CLEAN final evidence invalidates it. Resume only through a
new explicit publication attempt; do not append an automatic correction loop.
