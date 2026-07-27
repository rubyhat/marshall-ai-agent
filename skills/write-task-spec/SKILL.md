---
name: write-task-spec
description: Create, update, and audit full or lightweight project task specifications from an agreed shaped task or another configured authorized specification handoff. Use when the user explicitly asks for a complete task spec, approves specification as the next step after shaping, asks to revise an existing spec, invokes `--spec-check` for a read-only completeness and readiness audit, or when an authorized domain workflow such as confirmed QA hands off an exact sufficiently scoped task for specification. Select project-configured templates first and use bundled generic defaults as fallback; verify relevant code, contracts, dependencies, acceptance criteria, tests, and cross-cutting impacts. Do not trigger merely from an initial idea, roadmap commitment, or Issue creation, and do not allocate Task IDs, mutate task trackers, implement code, or silently resolve product-scope conflicts.
---

# Write Task Spec

Produce a coherent implementation specification without reopening settled shaping decisions or inventing technical precision.

## Keep the responsibility narrow

- Own specification depth, content, internal consistency, and readiness.
- Receive outcome, scope, decisions, and decomposition from `shape-project-work`, or an equivalent evidence and scope packet from a configured authorized domain handoff.
- Let `manage-project-work` establish required task identity, tracker anchors, links, and operational status.
- Use `record-project-context` to create or update project-local specification files.
- Let domain workflows define specialized requirements for frontend design, migrations, QA, legal behavior, or other configured impacts.
- Do not implement code, create worktrees, open pull requests, or write implementation reports.
- Do not create a full implementation spec for an Epic or Feature by default. Use a shared coordination or contract artifact only when project policy explicitly calls for one.

## Establish authority and mode

Choose one mode:

- `create`: create a new specification only after an explicit user request or an explicit specification handoff;
- `update`: revise an existing specification within the authorized task scope;
- `audit`: inspect a specification read-only and report gaps;
- `draft`: persist incomplete work only when the user explicitly requests a draft.

Silence, backlog commitment, Issue creation, `--shape-work`, or a shaping-readiness verdict does not authorize specification files.

Treat exact `--spec-check <Task ID or spec path>` as read-only audit authority. Do not repair files, tracker links, or status during that command.

## Resolve project policy

Read the project workflow configuration and resolve:

- specification root and language;
- required task identity, tracker, parent, and metadata;
- project-local full and lightweight templates;
- bundled-template fallback policy;
- selection rules for spec depth and annexes;
- required impacts and domain workflows;
- readiness labels and operational status mapping;
- recording and task-management handoffs.

Keep repository names, framework assumptions, languages, status labels, commands, and directory layouts out of this reusable skill.

## Run the specification workflow

### 1. Resolve the exact task

Identify one implementation task, its shaped outcome, scope, owning unit, dependencies, and current specification if any.

When project policy requires a stable Task ID or tracker item, use `manage-project-work` before creating the specification. If the configured policy says an explicit specification request authorizes those required anchors, treat it as an exact handoff rather than asking for duplicate permission. If anchor creation is not authorized, stop and request only that authority. If multiple tasks or specs plausibly match, stop and resolve the identity conflict.

### 2. Check shaping readiness

Require stable outcome, scope, decisions, ownership, and dependency direction. If a new product decision, material scope change, or conflict is discovered, return it to `shape-project-work` rather than deciding silently inside the spec.

Do not hide a blocker in placeholder prose. Create an incomplete draft only with explicit draft authority.

### 3. Select depth and template

Read [select-spec-depth-and-template.md](references/select-spec-depth-and-template.md).

Choose the configured project-local template first. Use the bundled defaults only when no project template applies:

- [full task template](assets/templates/full/task.md);
- [lightweight task template](assets/templates/lightweight/task.md);
- optional [contracts annex](assets/templates/annexes/contracts.md);
- optional [rollout and migration annex](assets/templates/annexes/rollout-and-migration.md);
- optional [test matrix annex](assets/templates/annexes/test-matrix.md).

Do not ask the user to choose full versus lightweight when project policy and risk make the answer clear. State the selected depth and reason before writing.

### 4. Load bounded technical context

Use an already sufficient orientation or `load-project-context`. Inspect only the repositories, modules, current behavior, contracts, tests, and domain policies needed for the exact task.

For an implementation-ready plan, verify named modules, interfaces, and constraints against current sources. Mark uncertainty or propose bounded technical discovery instead of inventing files, classes, endpoints, or schemas.

For a multi-file project spec, start with its configured entrypoint and follow only the files required by the selected write or audit scope. A full readiness verdict may require every canonical spec file, but never unrelated sibling tasks, historical reports, or broad memory.

### 5. Write or update coherently

Read [write-and-update-task-spec.md](references/write-and-update-task-spec.md).

Populate only applicable sections while preserving required project metadata and impact gates. Use the configured document language. Keep identifiers, code, schema, and protocol examples in their natural technical form.

Follow the selected project template when it defines a multi-file structure. With the bundled default, use the core file for the complete task contract and add an annex only when its detail would materially obscure the core spec or should be loaded conditionally.

### 6. Define contracts and impacts

Read [contracts-and-cross-cutting-impact.md](references/contracts-and-cross-cutting-impact.md) when the task affects an API, event, schema, state machine, permissions, data, migration, rollout, localization, accessibility, privacy, performance, observability, operations, documentation, or analytics.

Use project-specific workflows for the actual required classifications, commands, locales, and gates.

### 7. Make acceptance testable

Read [acceptance-and-testability.md](references/acceptance-and-testability.md).

Trace every material requirement to observable acceptance criteria and an appropriate verification method. Cover negative, permission, error, recovery, compatibility, and lifecycle behavior when applicable.

### 8. Verify internal consistency

Check that:

- task identity, title, owner, tracker, parent, and path agree;
- current and desired behavior do not conflict;
- plan stays within scope and respects architecture;
- every requirement has acceptance coverage;
- every critical criterion has a test or verification path;
- contracts, errors, permissions, states, and data semantics agree across sections;
- dependencies and rollout order are explicit;
- no secret, fabricated fact, or unresolved blocker is hidden;
- the task remains appropriately sized.

Return oversized or materially changed work to `shape-project-work`.

### 9. Assign a readiness verdict

Read [task-spec-readiness.md](references/task-spec-readiness.md).

Return exactly one content verdict:

- `Draft spec`;
- `Spec ready`;
- `Ready for implementation`.

The verdict describes specification content. Let `manage-project-work` apply the configured operational status after the write is verified.

### 10. Record, link, and read back

For create or update mode:

1. use `record-project-context` to write the project-local files;
2. reread the written spec and every created annex;
3. verify relative links and task identity;
4. ask `manage-project-work` to link the spec and apply the authorized status;
5. report the selected depth, files, verdict, blockers, assumptions, and handoff.

Do not start implementation automatically when the user requested only a specification.

## Update existing specifications safely

- Preserve confirmed requirements and decisions unless the user authorizes a scope change.
- Replace superseded current-state wording instead of appending a session changelog.
- Do not rewrite completed historical specs solely to match a newer template.
- Treat post-implementation behavior found in code as evidence, not automatic permission to rewrite the promised contract.
- Route a material outcome or decomposition change back through shaping.

## Adapt templates without coupling the skill

Read [template-adaptation.md](references/template-adaptation.md) when configuring a new project or comparing a project-local template with the bundled defaults.

Use [example-complete-spec.md](references/example-complete-spec.md) only when a concrete filled example is needed for calibration.
