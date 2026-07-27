# Ask decision-changing questions

Use this reference when shaping cannot proceed safely from verified context and low-risk assumptions.

## Decide whether to ask

Ask only when the answer can materially change:

- intended outcome or scope;
- actor, role, permission, or lifecycle;
- product or technical contract;
- UX behavior or recovery path;
- security, privacy, legal, billing, or tenant boundary;
- repository ownership, decomposition, dependency, or ordering;
- acceptance outcome or durable trade-off.

First inspect the minimum relevant source of truth. Do not ask the user to repeat information that is available and current.

Use a reversible explicit assumption for a low-impact unknown when project policy permits it. Ask before making an assumption that would change product meaning, create durable work, or introduce material risk.

## Ask decision questions with alternatives

For a real choice:

1. Number each question.
2. Offer two or three mutually exclusive options by default.
3. Add a fourth option only when it represents a materially distinct path.
4. Put the recommended option first and mark it with the configured equivalent of `A (Recommended)`.
5. Explain the recommendation in one short paragraph, including the main trade-off.
6. Let the user provide a different free-form answer.

Do not create fake alternatives merely to reach a target count. Do not label two semantically identical variants as different choices.

## Ask factual questions directly

Do not invent alternatives for an unknown fact such as:

- an existing contractual obligation;
- a required external identifier or URL;
- a decision already made by another authority;
- an actual production constraint;
- a factual business rule only the user can supply.

State why the fact is needed and what remains blocked by it.

## Keep rounds small

Prefer one to five high-impact questions in one round. Group related decisions and ask the smallest batch that can unblock the next meaningful shaping step.

Do not front-load implementation details before product and lifecycle decisions are stable. Ask a follow-up round only when answers expose a new material ambiguity or conflict.

## Interpret answers robustly

Accept compact configured forms such as:

```text
1 - A
2 - B
```

or:

```text
1. A
2. B
```

Also accept full-sentence answers, mixed formats, and a user-defined alternative. Map answers by question number, not by position alone.

If one answer is ambiguous, clarify only that answer. Preserve every settled decision and do not ask it again.

## Close the clarification cycle

After the final answers:

1. restate the decisions in compact form;
2. identify any remaining assumption or blocker;
3. rerun the conflict and risk gate;
4. continue to decomposition only when material contradictions are resolved or explicitly accepted.
