# Update canonical context

Use this reference when changing stable memory, runbooks, project configuration, architecture, known issues, or the context map.

## Preserve current truth

Treat canonical context as a description of the current project, not a chronological record of tasks.

1. Find the existing owning section.
2. Verify the candidate against its source.
3. Replace outdated wording in the affected scope.
4. Merge duplicate statements.
5. Keep only rationale that affects future decisions.
6. Link to detailed historical evidence.

Do not append a dated task or merge entry when the durable result can be expressed as current state.

Before adding a new section, check whether the candidate can replace or merge
into an existing owning section. Treat repeated task-ID headings, dated
completion entries, merge reports, and resolved status summaries as a
canonical-growth warning. Record the resulting current fact or link, not the
event narrative.

## Type the statement

Make the status explicit when ambiguity matters:

- `fact`: verified current behavior;
- `decision`: accepted direction or invariant;
- `hypothesis`: unverified interpretation;
- `risk`: possible harmful outcome;
- `gotcha`: non-obvious implementation or operational trap;
- `runbook`: verified repeatable procedure;
- `todo`: unresolved action that does not belong in an issue system.

Keep operational task status in its configured task system.

## Use provenance selectively

Add a source when the statement is disputed, external, surprising, or expensive to verify:

- code or configuration path;
- command and relevant result;
- task spec, ADR, issue, pull request, or report;
- official external documentation.

Add a verification date when the fact can become stale. Do not date every stable statement.

## Update by destination

### Stable memory

Keep concise current-state facts and non-obvious relationships. Avoid copying implementation detail that code search reveals cheaply.

### Runbook

Record only commands and sequences that were verified or whose unverified status is explicit. Include prerequisites, safety boundaries, expected result, and recovery guidance when relevant.

### Architecture or ADR

Keep current invariants in architecture. Keep alternatives, reasoning,
assumptions, consequences, and review triggers in an ADR. Use
`record-architecture-decision` for ADR applicability and lifecycle. Cross-link
rather than duplicate.

### Known issues

Keep actionable unresolved risks. When an issue is resolved, update the current state and link to durable evidence; do not grow an indefinite resolved-task archive.

### Project configuration

Update only when the owning workflow explicitly changes a project-specific setting. Do not use configuration as free-form memory.

### Context map

Update only when a canonical route is added, removed, renamed, or materially reclassified. Do not add ordinary task specs, reports, or rolling notes individually.

### Project topology map

Update only when a component or repository is added, removed, renamed, changes
lifecycle or ownership, moves locally, changes its canonical context route,
changes a material dependency edge, or crosses a deploy boundary. Keep stable
keys when display names change. Reconcile the configured repository registry
in the same bounded change when it owns machine-readable routing. Do not record
routine releases, dependency upgrades, task status, or deployment history.

## Verify the result

- Ensure that the edited section does not contain both old and new truth.
- Ensure that another artifact does not now compete as canonical.
- Ensure that links resolve.
- Ensure that project language policy is respected.
- Ensure that the edited canonical artifact did not gain task chronology that
  belongs to a spec, Issue, pull request, report, or archive.
- Keep cleanup outside the directly edited scope for the maintenance workflow.
