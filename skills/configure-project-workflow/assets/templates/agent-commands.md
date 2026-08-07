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
A configured `specification_documentation_delivery` exception may be inherited
only by the project-designated specification command; it does not release the
constraint for implementation or ordinary delivery.

{{COMMAND_CATALOG}}
