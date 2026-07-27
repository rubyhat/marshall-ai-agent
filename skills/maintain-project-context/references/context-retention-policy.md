# Context retention policy

Use this policy to make semantic retention decisions after the metadata audit. A script may surface evidence, but the agent owns the classification.

## Artifact states

- `active`: unresolved work, blockers, open questions, current next actions, and unpromoted durable facts.
- `canonical`: compact current truth owned by a map, configuration, memory, runbook, ADR, or other designated source.
- `historical`: completed specs, reports, decisions, incidents, and implementation evidence read only by exact link or explicit historical need.
- `archive`: exceptional superseded material preserved outside default loading because it contains unique evidence.

History may grow. Active and canonical context must remain compact.

## Classification vocabulary

- `retain`: keep in place; the artifact is active, canonical, protected, or uniquely valuable.
- `consolidate`: promote durable facts to the canonical owner, update links, then reassess the source.
- `archive`: preserve unique historical evidence outside default loading when the original location is no longer appropriate.
- `delete_candidate`: all deletion criteria are satisfied, subject to an exact manifest and separate approval.
- `needs_human_decision`: ownership, replacement, evidence value, or risk remains ambiguous.
- `broken_reference`: a link, map, or configured route is missing or would become invalid.

Do not treat a tool-generated classification hint as a final classification.

## Protected by default

Retain or exclude from cleanup unless the user explicitly resolves the risk:

- active task notes and unresolved coordination state;
- current configuration, context maps, root instructions, and skill sources;
- canonical memory and runbooks;
- ADRs, incidents, postmortems, security/privacy/legal decisions;
- production-change, migration, backup, restore, or manual-production evidence;
- task specifications referenced by an active GitHub Issue or Project field;
- the only known source of a fact, decision, blocker, or recovery procedure;
- files with modified or untracked Git state;
- artifacts with no unambiguous replacement;
- symlinks, secret-like files, binary files, and paths outside the approved root.

## Deletion gate

Classify a file as `delete_candidate` only when every applicable statement is verified:

1. Its work is completed, cancelled, or explicitly superseded.
2. It contains no active blocker, open question, required next action, or pending promotion.
3. It is not a canonical or protected source.
4. Every durable fact is already present in its canonical owner.
5. Relevant implementation history remains accessible through a spec, Issue, PR, Git, or approved archive.
6. It contains no unique production, security, privacy, legal, incident, migration, backup, restore, or manual-action evidence.
7. Incoming links are absent or included in the same manifest as exact reference updates.
8. Removing it does not break a context map, workflow, configuration path, or external task-system spec path.
9. A recovery source exists:
   - committed tracked files may use Git history;
   - modified or untracked files require an explicit backup/archive decision or exclusion.
10. One unambiguous current source of truth remains after deletion.

Age, file count, directory size, naming style, or a closed task is never sufficient by itself.

## Typical review candidates

Review, but do not automatically delete:

- a legacy session note duplicated by a task spec and merged PR;
- a status-only completion or merge note;
- an intermediate note fully superseded by a later canonical decision;
- an exact duplicate report;
- a reproducible generated inventory;
- an empty placeholder;
- a superseded draft after the final decision is verified;
- a closed rolling note after durable-fact promotion.

Consolidate before considering deletion when several notes contain partially current facts, repeated repository gotchas, dated entries inside canonical memory, or a sequence of architecture findings.

## Archive policy

Archive only exceptional unique evidence that should not remain in default loading and should not be deleted. Preserve:

- the artifact's project-relative relationship or a clear source-path record;
- a short archive reason;
- the canonical replacement, if one exists;
- enough provenance to understand the evidence later.

Do not use archive as a routine destination for every completed rolling note or task spec.
