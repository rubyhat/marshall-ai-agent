# Create or reconcile a project task

Use this reference for GitHub Issue and Project mutations. Keep the operation idempotent so retrying after a partial failure cannot create duplicate tasks.

## Build an exact mutation plan

Resolve:

- canonical Issue repository;
- existing Task ID or new stable semantic key and identity strategy;
- title and complete concise Issue body;
- task type and parent;
- target Project;
- field names and configured values;
- existing labels;
- initial or target status;
- spec, dependency, report, and pull-request links.

For every new provider-number-derived task, resolve the configured
correlation-marker format and one deterministic semantic creation key supplied
by the owning workflow or derived from the exact authorized task anchor. The
key must remain identical across retries. Use a project-neutral default when
the project does not override it, for example:

```text
<!-- project-task-key: <operation-key>/<semantic-task-key> -->
```

For an approved roadmap manifest, use its stable roadmap-operation key as the
operation namespace and resolve the complete ordered node set. If no stable
correlation key can be established, stop before creating an Issue.

Do not begin writes while the Issue, parent, repository, existing identity, or
semantic key is ambiguous.

## Reconcile before creating

For an existing task, search the exact Task ID in open and closed Issues and
configured local specs. For every new provider-number-derived task, search open
and closed Issues for its exact correlation marker, then run a bounded semantic
duplicate search using its approved title, outcome, and parent context.

- One canonical Issue: update it.
- No Issue and creation is authorized: create according to the configured
  identity strategy.
- Multiple marker, ID, or plausible semantic matches: stop and report the
  conflict.
- Closed Issue for the same work: reopen only when project policy and user
  scope allow; otherwise create a distinct new task.

The duplicate search prevents duplicate work; it is not a search for a free
future ID. If it changes an approved roadmap node from `create` to `reuse` or
`update`, return the changed semantic manifest for new approval before writing.

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

Process a multi-node manifest in a combined hierarchy-and-dependency
topological order. Add a parent-to-child precedence edge for every hierarchy
relationship and a predecessor-to-dependent edge for every dependency. Stop
before mutations when the combined graph contains a cycle. This guarantees
that every child can use its canonical parent Issue.

For a new provider-number-derived node:

1. Search its exact correlation marker again.
2. Create one provisional Issue with the approved semantic title/body and the
   marker, or reuse the correlated Issue after a partial create.
3. Read the immutable Issue number and derive the configured final Task ID.
4. Update the Issue title and body with the final Task ID while preserving the
   marker.

For an existing node or an explicitly configured custom allocator, reconcile
or allocate using the configured identity policy. Then, for every node:

1. Establish the parent relationship once.
2. Add the Issue to the configured Project only if it is not already an item.
3. Resolve current field and option IDs, then set configured values.
4. Apply only labels that already exist and are allowed by policy.
5. Add exact artifact links without duplicating body sections.
6. Reread the Issue and Project item.

Do not create or rename labels, fields, options, workflows, views, or Projects during ordinary task management.

## Recover partial success

Keep the semantic key, canonical Issue URL/number, derived Task ID, and Project
item ID as soon as they exist.

If a later mutation fails:

- preserve completed writes;
- reread actual state;
- retry only missing mutations;
- do not create a second Issue or Project item;
- report authentication, permission, missing field/option, or provider capability errors precisely.

If local spec metadata must be updated, use `record-project-context` and change only identity/link fields owned by this workflow. Do not rewrite substantive scope.

## Verify

Confirm the exact Issue title and ID, parent, Project membership, fields, labels, status, and links. Return partial completion explicitly when any expected state could not be verified.

For a roadmap manifest, return a complete readback table mapping every semantic
key to its final Task ID, Issue URL, parent, and Project state.
