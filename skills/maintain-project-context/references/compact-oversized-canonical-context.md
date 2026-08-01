# Compact oversized canonical context

Use this runbook when one canonical artifact mixes current truth with task
chronology, completed work, superseded decisions, reports, or several unrelated
domains. Treat the file as protected and work one bounded section or domain at
a time.

## Keep the operation staged

Do not full-read, rewrite, split, archive, or delete the artifact in one pass.
Do not classify the whole file from size alone.

Use this sequence:

1. inventory file metadata and headings without printing the body;
2. identify one exact section, domain, or heading range;
3. inspect only that range and the minimum owning sources needed to verify it;
4. classify the range semantically;
5. propose exact promotions, replacements, links, archival, or removal;
6. add the proposal to the cleanup manifest;
7. wait for separate approval before mutation;
8. apply and validate only that approved range or exact artifact set;
9. rerun targeted audit before choosing the next range.

Keep the original artifact recoverable until every retained fact and incoming
reference in the approved scope is verified.

## Classify content by owner

Route each reviewed statement to one owner:

| Content | Owner |
| --- | --- |
| Verified current system structure or invariant | Architecture documentation |
| Architectural rationale, options, assumptions, and consequences | ADR through `record-architecture-decision` |
| Compact current project or repository fact | Canonical memory |
| Verified repeatable operational sequence | Runbook |
| Current unresolved risk | Known-issues registry |
| Task scope and acceptance behavior | Task specification |
| Priority, status, and dependency progress | Issue or Project |
| Review, merge, and implementation evidence | Pull request, Git, or approved historical artifact |
| Unique incident, migration, security, legal, backup, or production evidence | Its governed artifact or exceptional archive |

Do not preserve task narration in canonical memory merely because it contains
one durable fact. Promote the fact, link its evidence when useful, and reassess
the remaining narrative.

## Detect mixed-era risk

Treat these as review signals, not automatic cleanup authority:

- many task-ID or dated headings;
- accepted and superseded statements in the same owning section;
- completed or merged status mixed with current instructions;
- resolved and unresolved issues sharing one undifferentiated list;
- repeated architecture findings without a decision owner;
- one section too large to load safely for a normal task;
- several components or deploy boundaries with no section routing;
- duplicated current facts with conflicting verification dates.

Prefer adding or repairing a context-map route before moving content when the
information is already well owned but difficult to target.

## Build the section manifest

For every proposed range record:

- source path and stable heading anchor;
- current fingerprint of the whole source;
- semantic classification;
- exact destination and action;
- durable facts to retain;
- history or duplicated wording to exclude;
- incoming references affected;
- validation and recovery evidence;
- whether the action changes an ADR, architecture, runbook, known issue, or
  context map and therefore requires its owning workflow.

Line numbers may assist review but are not stable manifest identity. Use the
heading and fingerprint, then re-resolve the range immediately before applying
an approved change.

## Stop safely

Stop and request a human decision when:

- current and superseded truth cannot be separated reliably;
- an architectural decision lacks enough evidence for retrospective ADR;
- a unique fact has no configured owner;
- incoming references cannot be reconciled in the same bounded change;
- the source changed after manifest approval;
- the range contains modified, untracked, governed, or production-sensitive
  evidence not explicitly approved.

Never create retrospective ADRs in bulk. Create one only when the decision is
still relevant, materially affects future work, and has verifiable rationale.
