# Link and close a project task

Use this reference to connect specs and pull requests, close an implementation task after verified merge, and reconcile parent work.

## Link a task spec

1. Verify the spec belongs to the exact Task ID and Issue.
2. Add the configured project-relative spec path to the Issue and Project field.
3. Add the canonical Issue URL and Task ID to the spec metadata.
4. Use `record-project-context` before modifying local documentation.
5. Do not copy the full spec into the Issue.

When file-backed planning publication is configured, distinguish a local
pre-publication link from the canonical link. Apply the configured
implementation-ready status only after `publish-planning-change` verifies the
spec is independently reviewed and merged into the canonical branch. Record
the resolvable merged revision when project policy requires it. Do not close
the implementation Issue for a spec-publication pull request.

For ordinary reviewed publication, accept the handoff only with one complete
`reviewed_canonical_publication` record: Task ID, owner repository, canonical
spec entrypoint, pull request URL, merged revision/tree OID, bound reviewed-head
revision/tree OID, complete sorted reviewed package path/mode/blob-OID manifest,
reviewer run/evidence identifier, model, effort, completion time, terminal
clean verdict, review target kind, canonical base revision, binding method, and
explicit reviewed-versus-merged package-manifest equality. Also require the
current capture-contract revision, publication-attempt ID, normalized-result SHA-256,
and complete matched reviewer session/event set. Persist the record on
the exact task, reread it, and require exact equality of every field. Do not
infer clean review from PR prose, status, model selection, or merge alone.

For old or incomplete ordinary evidence, record the deterministic audit
classification `publication_upgrade_required`, observed evidence revision,
canonical Task ID/spec path, required capture-contract revision, observed
operational status, and exact next action `--publish-spec <Task ID>`. Historical
legacy baseline records may remain linked as audit history but never become
implementation authority and never receive synthetic review sessions or result
hashes.

During the configured schema cutover, inventory every current task selected by
implementation-ready content or operational status before mutation, then run a
full authoritative post-merge rescan. Change status only when the observed
operational value is exact implementation-ready; map it to spec-ready. Preserve
every other configured lifecycle or exceptional status as `audit_only`,
including earlier states, active work, review/merge readiness, done, blocked,
paused, and not-planned. Reconciliation must be idempotent, and completion
requires zero old-evidence items still in implementation-ready status.

If either side points to another Task ID, stop and resolve the identity conflict before writing.

## Link pull requests

Use the project-configured close/reference pattern:

- use closing linkage only when the pull request completes the exact implementation Issue;
- use reference-only linkage when it contributes to a parent or only part of the task;
- create separate repository-owned implementation Issues and pull requests for multi-repository work when policy requires them.

This skill may verify or add task linkage after the owning delivery workflow creates the pull request. It does not open, review, approve, or merge the pull request.

## Close after merge

Act only after the delivery workflow verifies the exact pull request was merged and required gates passed.

1. Reread the Issue; closing linkage may already have closed it.
2. Close the exact implementation Issue if it remains open and the configured policy requires closure.
3. Set its Project status to the configured done value.
4. Verify all repository-specific parts and linked pull requests relevant to that Issue.
5. Inspect the parent without assuming it is complete.

Reference-only linkage does not prove the task is complete.

## Reconcile the parent

Do not close a feature or epic from child count alone. Confirm:

- all relevant children are complete or explicitly removed from scope;
- the parent acceptance outcome is achieved;
- no untracked implementation or unresolved dependency remains;
- its Issue body and Project fields still describe current scope.

Update or close the parent only when those checks pass. Ask when scope or outcome is ambiguous.

## Verify final linkage

Confirm:

- Issue ↔ spec identity;
- Issue ↔ Project item;
- parent ↔ child relationship;
- pull request ↔ exact implementation Issue;
- Issue open/closed state;
- task and parent statuses.

Report any link that could not be verified rather than creating a replacement by inference.
