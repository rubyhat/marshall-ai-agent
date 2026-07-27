# Create or reconcile a project task

Use this reference for GitHub Issue and Project mutations. Keep the operation idempotent so retrying after a partial failure cannot create duplicate tasks.

## Build an exact mutation plan

Resolve:

- canonical Issue repository;
- Task ID and title;
- concise Issue body;
- task type and parent;
- target Project;
- field names and configured values;
- existing labels;
- initial or target status;
- spec, dependency, report, and pull-request links.

Do not begin writes while the Issue, parent, repository, or Task ID is ambiguous.

## Reconcile before creating

Search the exact Task ID in open and closed Issues and configured local specs.

- One canonical Issue: update it.
- No Issue and creation is authorized: recheck the ID, then create.
- Multiple Issues using the ID: stop and report the conflict.
- Closed Issue for the same work: reopen only when project policy and user scope allow; otherwise create a distinct new Task ID.

Never assume a failed create request means nothing was created. Search again before retrying.

## Keep the Issue concise

Write only the configured operational sections, typically:

- goal;
- bounded scope;
- acceptance checklist;
- dependencies and order;
- links.

Link to the detailed spec rather than copying it. Keep roadmap status, priority, risk, repository, release, size, and similar operational values in Project fields when configured there.

## Apply mutations idempotently

1. Create or update the Issue.
2. Establish the parent relationship once.
3. Add the Issue to the configured Project only if it is not already an item.
4. Resolve current field and option IDs, then set configured values.
5. Apply only labels that already exist and are allowed by policy.
6. Add exact artifact links without duplicating body sections.
7. Reread the Issue and Project item.

Do not create or rename labels, fields, options, workflows, views, or Projects during ordinary task management.

## Recover partial success

Keep the canonical Issue URL/number and Project item ID as soon as they exist.

If a later mutation fails:

- preserve completed writes;
- reread actual state;
- retry only missing mutations;
- do not create a second Issue or Project item;
- report authentication, permission, missing field/option, or provider capability errors precisely.

If local spec metadata must be updated, use `record-project-context` and change only identity/link fields owned by this workflow. Do not rewrite substantive scope.

## Verify

Confirm the exact Issue title and ID, parent, Project membership, fields, labels, status, and links. Return partial completion explicitly when any expected state could not be verified.
