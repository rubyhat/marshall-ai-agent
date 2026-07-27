# Accept and Normalize a Frontend Report

Turn an informal observation into a bounded reproduction hypothesis without making the user complete a form.

## Extract what is already known

Capture:

- affected product, frontend, screen, route, or entry point;
- actor, role, account or tenant context;
- action sequence;
- expected and observed behavior;
- environment, URL, browser, viewport, locale, and timing when relevant;
- affected entity or state;
- frequency and last known good behavior;
- screenshot, recording, console message, network response, or error key;
- stated impact and whether the user asked only to investigate or also to fix.

Mark each item as user-observed, agent-verified, inferred, or unknown. Do not turn a user interpretation such as “the API is broken” into a verified cause.

## Define one triage boundary

Express the report as:

```text
Given <role, environment, and prerequisite state>,
when <exact action>,
the frontend shows or does <actual behavior>
instead of <expected behavior>.
```

Split multiple independent symptoms only when they require different reproduction paths or owners. Keep related visual and behavioral symptoms together when they describe one failure.

## Decide whether to attempt reproduction

Proceed when a safe first attempt is possible. Ask before proceeding only when a missing fact changes:

- the target environment or product;
- the actor, tenant, or permission boundary;
- the route or action being tested;
- the required data state;
- whether production mutation would be required;
- which of several materially different symptoms the user means.

Use the configured clarification format for decisions. Ask missing facts directly when artificial options would not help.

## Preserve authority

Record whether the user explicitly requested implementation. Do not infer it from urgency, severity, obviousness, or phrases that only ask to inspect, reproduce, diagnose, or explain.

Treat an explicit request to create a Discovery item after a no-repro result as separate artifact authority. Otherwise leave that decision for the result handoff.
