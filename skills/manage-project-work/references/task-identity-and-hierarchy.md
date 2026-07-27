# Task identity and hierarchy

Use this reference before creating an Issue, assigning a Task ID, changing a parent, or validating a multi-repository task tree.

## Allocate a Task ID

1. Resolve the owning repository and configured scope prefix.
2. Choose the stable semantic domain supplied by the owning workflow. Do not encode the full ancestry in the ID.
3. Apply the configured format for ordinary tasks, epics, sibling subdivisions, and direct fixes.
4. Search the exact candidate ID in:
   - open Issues;
   - closed Issues;
   - configured task-spec roots;
   - any additional uniqueness source named by project policy.
5. Select the next free number within the exact configured prefix/domain line.
6. Recheck remote and local uniqueness immediately before Issue creation.
7. Create the Issue promptly after allocation so the Issue becomes the durable reservation.

If a parallel actor claims the same ID, do not overwrite or repurpose its Issue. Recompute the next ID and update only artifacts created by the current operation.

When the user supplies an ID, validate both syntax and uniqueness. An existing exact match means reconcile the existing task, not reuse the ID for new work. Never recycle a closed or not-planned ID.

Keep Task ID uppercase in operational systems. Use the configured lowercase form only for filesystem slugs. Preserve existing legacy IDs unless the user requests a migration; do not rename history merely to fit current conventions.

If a newly created Issue accidentally lacks its required Task ID and implementation has not begun, repair the identity consistently in the same operation: Issue title, filesystem slug/spec path, configured Project spec-path field, spec metadata, and durable local links. Once implementation or external history exists, treat the rename as a migration and request confirmation instead of silently rewriting identity.

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
