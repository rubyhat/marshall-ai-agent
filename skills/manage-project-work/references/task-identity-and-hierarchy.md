# Task identity and hierarchy

Use this reference before creating an Issue, assigning a Task ID, changing a parent, or validating a multi-repository task tree.

## Establish a Task ID

Resolve the owning repository, configured scope prefix, stable semantic domain,
task type, and identity strategy. Do not encode the full hierarchy in the ID.

### Provider-number-derived identity

Prefer this strategy when the tracker supplies an immutable, human-visible
Issue number and no coherent project convention requires an independent
sequence.

1. Validate that configured scope/domain prefixes keep IDs unambiguous across
   every Issue repository. Stop on a cross-repository namespace collision.
2. Apply the configured ID pattern for ordinary tasks, epics, sibling
   subdivisions, and direct fixes without predicting the numeric part.
3. Resolve one deterministic semantic correlation key supplied by the owning
   workflow or derived from the exact authorized task anchor. It must remain
   identical across retries; stop before creation when no stable key exists.
4. Recover an already created Issue through that configured correlation marker
   before every create retry.
5. If no correlated Issue exists, create the Issue first and read its immutable
   provider number.
6. Derive the final Task ID from the configured semantic prefix and that
   number. Examples of pattern shapes are
   `<SCOPE>-<DOMAIN>-<ISSUE_NUMBER>` and
   `<SCOPE>-<DOMAIN>-EPIC-<ISSUE_NUMBER>`; project configuration owns the
   actual format.
7. Update the Issue title and body with the final Task ID in the same operation,
   then complete hierarchy, Project fields, and links.

Do not search for the “next free” custom number under this strategy. The
provider assigns and reserves the number atomically; the semantic marker makes
partial creation recoverable.

### Explicit custom allocator

Use an independent sequence only when project configuration explicitly
preserves an existing convention or the provider lacks a suitable immutable
number.

1. Apply the configured format.
2. Search the exact candidate ID in open Issues, closed Issues, configured
   task-spec roots, and every additional uniqueness source named by policy.
3. Select the next free number in the configured line.
4. Recheck uniqueness immediately before Issue creation and create promptly so
   the Issue becomes the durable reservation.

If a parallel actor claims a custom ID, do not overwrite or repurpose its
Issue. Recompute the next ID and update only artifacts created by the current
operation.

When the user supplies an existing ID, validate its syntax and resolve it as an
anchor. An exact match means reconcile the existing task, not reuse the ID for
new work. Never recycle a closed or not-planned ID. Under a
provider-number-derived strategy, do not accept a guessed future Task ID for a
new Issue; establish it from the assigned number.

Keep Task ID uppercase in operational systems. Use the configured lowercase form only for filesystem slugs. Preserve existing legacy IDs unless the user requests a migration; do not rename history merely to fit current conventions.

If a newly created Issue is left in provisional identity state after partial
failure, recover it by semantic marker and finish the configured title/body
update before creating any local spec. If a task with implementation or
external history needs an identity change, treat it as a migration and request
confirmation instead of silently rewriting identity.

## Validate hierarchy

Treat the configured parent/sub-issue relationship as hierarchy source of truth.

1. Confirm the proposed type and parent come from the owning shaping or intake workflow.
2. Reject a parent that would exceed configured depth.
3. Do not make an implementation task the parent of another implementation layer.
4. Split additional implementation scope into sibling tasks under the same feature, or return the scope to shaping when the feature itself is too large.
5. For multi-repository work, use a shared feature/story and sibling repository-owned implementation tasks.
6. Keep business-area grouping in the configured Project field when policy says it is not an Issue level.

Require a parent for features and implementation tasks when an applicable hierarchy exists. Allow a standalone bug, infrastructure, documentation, maintenance, or similarly bounded task only when project policy permits it and record a short reason in the Issue.

Do not infer a different product decomposition merely to make an Issue fit. Return invalid or ambiguous hierarchy to the owning workflow.

## Reparent safely

Reparenting changes roadmap meaning and requires explicit confirmation.

Before reparenting:

- verify the exact current and proposed parents;
- check depth and task type;
- check cross-repository ownership and dependencies;
- show the resulting hierarchy;
- confirm that spec and Issue wording remain accurate.

After reparenting, reread both parents and the child. Do not rewrite Task IDs to mirror the new ancestry.
