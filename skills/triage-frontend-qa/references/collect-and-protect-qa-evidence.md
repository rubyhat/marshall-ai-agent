# Collect and Protect QA Evidence

Keep enough evidence to support the verdict while minimizing sensitive data and context volume.

## Prefer strong evidence

Use the most direct applicable evidence:

- exact steps with expected and actual behavior;
- screenshot or short recording of the relevant state;
- console error with surrounding action;
- request method and path, response status, stable error key, and redacted payload shape;
- correlated server log event or request identifier;
- current documented behavior or established product pattern;
- narrow code location that explains already reproduced behavior;
- existing focused test result.

Do not paste full logs, whole network archives, database dumps, or unrelated source files into chat or project artifacts.

## Preserve provenance

For each decisive item, state:

- source and environment;
- observation time or revision when staleness matters;
- whether the user or agent observed it;
- any fallback or substitution;
- confidence and unresolved alternative explanation.

Use links or project-relative paths for durable evidence when a canonical artifact already owns it.

## Redact by default

Remove or avoid:

- passwords, tokens, cookies, authorization headers, session identifiers, and secret URLs;
- personal data not required to identify the failure;
- full payment, order, customer, or legal records;
- data belonging to another tenant or account;
- internal stack details that should not enter a public Issue.

Use stable redacted identifiers such as `tenant A`, a truncated request ID, or a safely configured test entity.

## Escalate sensitive findings

If evidence suggests cross-tenant exposure, unauthorized access, privacy leakage, credential disclosure, payment risk, or exploitable behavior:

1. Stop broadening the reproduction or copying exposed data.
2. Preserve only minimal non-sensitive evidence.
3. Mark the primary result as `security or privacy escalation`.
4. Use the configured restricted reporting path; if none exists, stop and give the user a minimal redacted summary.
5. Do not create an ordinary public bug Issue unless project policy explicitly defines it as safe.

## Avoid redundant reports

Return evidence in the chat triage packet and pass it to the Issue/spec owners. Do not create a standalone QA report file unless the user explicitly requests one or project policy requires a durable evidence artifact.
