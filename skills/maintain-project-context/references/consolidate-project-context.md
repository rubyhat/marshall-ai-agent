# Consolidate project context

Use this runbook when reviewed artifacts contain durable facts that must be promoted before archival or deletion.

## Resolve ownership

For each fact, identify one owner:

- code, schema, or runtime configuration for implementation truth;
- Issue or Project for operational task state;
- task spec for detailed implementation scope;
- ADR through `record-architecture-decision` for an architectural decision;
- incident, security, legal, migration, backup, or restore artifact for governed evidence;
- canonical memory or runbook for compact reusable current knowledge;
- rolling active note for unresolved task-local state.

Link to the owner instead of copying its detail into several artifacts.

## Consolidate

1. Read only the candidate, its proposed canonical owner, and direct references needed to verify the move.
2. Separate current facts from historical narrative, hypotheses, and obsolete status.
3. Use `record-project-context` before updating project memory or documentation.
4. Update existing canonical current state; create a new artifact only when no owner exists.
5. Preserve provenance or a verification date when staleness or evidence matters.
6. Replace stale wording and update exact incoming links in the approved manifest.
7. Re-read the source and canonical owner to confirm no unique durable fact was lost.
8. Reclassify the source using the retention policy.

Do not turn canonical memory into a chronology. Do not move task progress out of its Issue or Project merely to make local files self-contained.

## Handle mixed artifacts

When a file contains both durable and transient material:

- promote durable facts;
- retain unresolved task state in the rolling note;
- preserve unique governed evidence in its owning artifact or exceptional archive;
- discard only transient or duplicated wording after exact approval.

If ownership remains ambiguous, classify the artifact as `needs_human_decision` and stop.
