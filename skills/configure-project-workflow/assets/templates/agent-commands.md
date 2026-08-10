# Agent commands

These are plain-text project conventions, not built-in slash commands. An alias never expands the authority of its owning skill.

Before running an alias, validate its configured prerequisites and current
workflow phase. If it is premature, stale, ambiguous, or out of order, stop
before mutations, explain the mismatch, and recommend the exact safest next
alias or action.

Resolve sticky current-conversation constraints before alias-specific
authority. A later alias may narrow authority but cannot implicitly release a
planning, no-code, no-implementation, no-delivery, or read-only constraint.
Apply the same capability gate to equivalent natural-language requests.

When configured, `--publish-spec` may use only the bounded
`planning_artifact_publication` capability for one exact reviewed
specification. It does not release the planning profile or authorize
implementation, ordinary delivery, release, or deployment.

For configured planning publication, routine GitHub correction packages use
deterministic verification and no local model review. The initial pull-request
head and every corrected head use the configured trigger, reviewer matching,
response channels, bounded request attempts, and exact-PR heartbeat, and require
a clean GitHub generation for the exact complete current head before final
evidence or merge. The exact PR starts its five-package GitHub counter at zero;
the fifth package receives review and a sixth stops before mutation. False,
out-of-scope, and duplicate findings use one fingerprinted no-edit contextual
re-review; explicit errors retry only through the persisted request budget.
Every verdict event must bind to the requested exact head, and an applied
package must become a proved intentional commit before push. Then reuse
exact current evidence or run at most one final canonical evidence review; a
non-clean, invalid, or timed-out final result stops without automatic
corrections.

For configured implementation delivery, pull-request creation closes the
passed pre-PR local-review phase. Routine GitHub corrections run affected tests,
deterministic gates, `git diff --check`, exact delta/scope verification, and
finding readback with zero local model invocations. Material or uncertain
corrections stop before edits.

{{COMMAND_CATALOG}}
