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
