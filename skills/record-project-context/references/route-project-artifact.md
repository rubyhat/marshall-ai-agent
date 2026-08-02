# Route a project artifact

Use this reference to decide whether to skip, link, update, or create and to select the logical owner of project information.

## Identify the candidate

State the candidate as one concise fact or artifact purpose. Separate mixed candidates before routing them.

Determine:

- lifetime: ephemeral, active, durable, or historical;
- audience: agent, human, project tooling, or external task system;
- scope: task, repository, cross-repository, project, or operations;
- owner: the source that must remain authoritative;
- recovery cost: how difficult and risky rediscovery would be.

## Use the action order

### Skip

Skip when the candidate is:

- routine tool output;
- an intermediate attempt;
- ordinary success status;
- already obvious from code or configuration;
- already recorded with no meaningful change;
- too uncertain to present as a fact;
- unlikely to help a later task or handoff.

### Link

Link when another source owns the detail:

- code or schema owns implementation truth;
- task spec owns scope and acceptance criteria;
- ADR owns architectural rationale;
- report owns detailed analysis or evidence;
- issue or project owns operational status and priority;
- pull request owns review and merge history;
- external documentation owns third-party behavior.

Store only the non-obvious implication or relationship when a link alone is insufficient.

### Update

Update when a current canonical artifact already owns the candidate. Search for the exact task ID, domain, concept, command, or decision before adding a section.

Prefer replacing current state over adding a dated duplicate.

### Create

Create only when:

- no existing artifact has the same responsibility;
- the information has a unique active or durable purpose;
- another agent or person must discover it later;
- the configured project structure defines or permits the destination.

Do not create a document merely to prove that work occurred.

## Select the logical destination

- Active objective, blocker, open question, next action: rolling active task note.
- Stable product fact: project context.
- Stable component, repository, lifecycle, ownership, dependency, routing, or
  deploy-boundary fact: project topology map.
- Stable engineering convention: engineering rules.
- Repository-specific fact: repository memory.
- Verified repeatable procedure: runbook.
- Cross-repository invariant: shared architecture.
- Important decision rationale: ADR.
- Current unresolved risk or discrepancy: known-issues registry.
- Planned task scope and acceptance criteria: task spec.
- Human-facing analysis, report, or guide: project documentation.
- Transferable handoff or incident report: the configured report destination
  when one exists; otherwise the owning project-documentation route.
- Project workflow value: project workflow configuration.
- Status, priority, roadmap, or pull-request lifecycle: external task system.

Use project configuration, the project topology, and the context map to
translate these roles into paths.
An existing directory is evidence, not authority. Do not call it canonical
unless configuration, project instructions, or the context map assigns that
role.

## Respect the requested output form

- Chat-only analysis does not create a project artifact unless the user or
  owning workflow requests persistence.
- A report intended for transfer to another agent or person uses the configured
  persistent destination when project policy marks that report type as
  file-backed.
- An explicit file request requires a verified file.
- An explicit path-only request requires a final response containing only the
  verified path.
- Do not repeat a complete persistent report in chat unless the user explicitly
  requests both surfaces.

## Respect content ownership

Let the owning domain workflow decide what a spec, report, or plan should say.
Require `record-architecture-decision` to establish ADR content and lifecycle.
Apply this skill to routing, duplication control, persistence, and consistency.

Ask only when two plausible destinations would create competing sources of truth. Otherwise choose the configured owner and proceed.

The project topology map is a compact routing index. Link architecture,
runbooks, task state, and implementation detail rather than copying them into
the map. If project configuration owns the repository registry, keep its
machine-readable values consistent with the human-readable topology entry.
