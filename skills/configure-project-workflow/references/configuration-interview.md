# Configuration Interview

Use this staged catalog to obtain complete setup information without presenting one overwhelming questionnaire.

## Contents

1. Interview rules
2. Stage 1 — safety and authority
3. Stage 2 — project identity and repositories
4. Stage 3 — instructions and source-of-truth boundaries
5. Stage 4 — context and documentation
6. Stage 5 — shaping and specifications
7. Stage 6 — task management
8. Stage 7 — implementation
9. Stage 8 — review and delivery
10. Stage 9 — domain modules
11. Stage 10 — installation and customization
12. Final review

## Interview rules

- Treat each stage list as a coverage checklist, not a question quota.
- Apply documented safe defaults for ordinary paths and low-risk conventions,
  record them as assumptions or decisions, and summarize them for optional
  correction instead of asking.
- Ask only decision-changing questions and factual unknowns that bounded
  inspection cannot resolve. Prefer one to five numbered prompts in a round.
- Use a detected fact directly when ownership and confidence are clear; ask a
  confirm-or-correct question only when a wrong inference would be material.
- Skip an entire conditional stage only when the selected profile makes it genuinely inapplicable.
- Do not pad a stage with irrelevant questions; combine closely related decisions when needed.
- Ask factual unknowns directly.
- For material decisions, offer 2–3 mutually exclusive options with `А (Рекомендую)` first and a concise trade-off.
- Accept compact answers such as `1 - А` and free-form alternatives.
- Explain why a question matters when its consequence is not obvious.
- Update and validate the tracker after every stage.
- Preserve deferred questions and return to them before manifest approval.

## Stage 1 — safety and authority

Purpose: establish the setup protection layer before deeper inspection.

Resolve the following; ask only unresolved decision-changing items:

1. confirmation of the default forbidden reads;
2. additional forbidden paths or repositories;
3. additional forbidden commands, runtimes, containers, or tools;
4. network and external-service restrictions;
5. production, customer-data, tenant, billing, legal, or privacy boundaries;
6. whether any safe manifest or documentation class is still restricted;
7. global installation restrictions;
8. authority required for tracker, installation, and final project mutations;
9. required redaction or reporting behavior;
10. the person or workflow that resolves a safety blocker.

## Stage 2 — project identity and repositories

Purpose: define the target system and its ownership boundaries.

Resolve the following; ask only unresolved decision-changing items:

1. project name and concise purpose;
2. product, library, service, internal tool, content project, or another type;
3. single-repo, monorepo, multi-repo, or hybrid structure;
4. stable component keys, purposes, types, local paths, remote repositories,
   and deployable units;
5. supported versus legacy or frozen components and their ownership;
6. languages, frameworks, package managers, and compact entry points;
7. production status, environments, and independent deploy boundaries;
8. upstream, downstream, shared-contract, and cross-repository dependencies;
9. actors, roles, tenant or account model plus market, locale, regulatory,
   billing, or legal scope;
10. task-scope prefixes and component ownership not safely inferable.

## Stage 3 — instructions and source-of-truth boundaries

Purpose: prevent generated workflow rules from competing with existing project truth.

Resolve the following; ask only unresolved decision-changing items:

1. root and nested instruction ownership;
2. architectural source of truth;
3. product and business source of truth;
4. code, schema, API, and runtime configuration ownership;
5. tracker versus local documentation ownership;
6. always-on safety and engineering invariants;
7. conflict precedence among instructions, config, docs, tracker, and code;
8. managed `AGENTS.md` block policy;
9. documentation and interaction languages;
10. existing instructions that must never be generated or modified.

## Stage 4 — context and documentation

Purpose: choose a compact durable context model.

Resolve the following; ask only unresolved decision-changing items:

1. an explicit existing project-doc root, otherwise the automatic `docs_ai`
   default without a question;
2. an explicit existing internal-memory root, otherwise the automatic
   `local_memory_ai` default without a question;
3. project context, project-topology, and engineering-rules destinations;
4. context map and progressive-disclosure routing from topology to the owning
   component's instructions, architecture, memory, and runbooks;
5. active task note policy;
6. session-note and historical-context policy;
7. recording language and provenance requirements;
8. retention, archive, manual cleanup, and categories that must not be created;
9. human-facing report root and chat, file, handoff, incident, link, and
   path-only output policy;
10. whether `load`, `record`, and `maintain` modules are applicable.

## Stage 5 — shaping and specifications

Purpose: define how ideas become implementation-ready work.

Resolve the following; ask only unresolved decision-changing items:

1. work types that require shaping;
2. clarification-question format;
3. conflict and risk gate;
4. conceptual hierarchy and decomposition expectations, including a
   `--shape-roadmap` contract that receives a shaped outcome, discusses only
   its tracker representation in one coherent iteration, approves one semantic
   manifest, and creates no local roadmap or coordination artifact;
5. when full versus lightweight specifications apply;
6. explicit and configured specification handoffs, including whether a
   continuation command may resolve the next task from the active work graph;
7. canonical spec owner and root: reuse an explicit coherent owner, otherwise
   default to the project root repository and `docs_ai/tasks` without asking;
8. isolated planning/spec workspace and required publication before
   implementation for Git-tracked specifications;
9. independent spec-review policy, model/effort configuration, allowed
   supporting artifact classes, deterministic gates, PR target, merge authority,
   and canonical-revision evidence;
10. specification readiness verdicts and the separate implementation authority
    gate, including deterministic adoption evidence for specifications already
    ready on the canonical target before planning publication was enabled.

## Stage 6 — task management

Activate only when operational task tracking is selected.

Resolve the following; ask only unresolved decision-changing items:

1. provider and issue repository;
2. Project, board, or roadmap location;
3. Task identity strategy, format, and namespace: when the provider supplies an
   immutable human-visible Issue number, derive new Task IDs from that number
   plus configured semantic prefixes by default without asking; preserve a
   coherent existing custom allocator only when detected or explicitly
   requested;
4. hierarchy levels and parent rules;
5. allowed standalone task types;
6. fields, labels, milestones, or components;
7. lifecycle statuses and transitions;
8. Issue body and spec/PR linking;
9. mutation checkpoints owned by runtime workflows and authoritative
   read-only completion evidence used for task-sequence continuation;
10. operations requiring separate confirmation, including broad sync and schema changes.

## Stage 7 — implementation

Purpose: define safe local task execution.

Resolve the following; ask only unresolved decision-changing items:

1. readiness requirements;
2. implementation repository selection;
3. worktree or workspace isolation policy;
4. workspace root and branch naming;
5. single- versus multi-repo coordination;
6. parallel-task and unfamiliar-change protection;
7. required quality gates by repository;
8. migration, data, environment, and production restrictions;
9. operational status checkpoints;
10. exact boundary between implementation and delivery.

## Stage 8 — review and delivery

Purpose: define publication and completion authority.

Resolve the following; ask only unresolved decision-changing items:

1. distinct independent review requirements for specifications and
   implementation changes;
2. reviewer isolation, model/effort ownership, finding severity, scope guard,
   and bounded retry policy;
3. commit policy and message conventions;
4. push and force-push rules;
5. pull-request language, target, template, and non-closing linkage for spec
   publication versus closing linkage for implementation delivery;
6. automated reviewer integration and bounded waiting;
7. required CI/check policy;
8. merge authority and allowed methods;
9. post-merge canonical spec evidence and planning-workspace cleanup versus
   implementation Issue closure, sync, and task-workspace cleanup;
10. deployment and production boundaries excluded from normal delivery.

## Stage 9 — domain modules

Activate when frontend design, frontend QA, or product-reference analysis is selected.

Resolve the following for active modules; ask only unresolved
decision-changing items:

1. frontend repositories and architecture sources;
2. visual source of truth;
3. navigation, responsive, accessibility, and localization defaults;
4. backend contract and dependency ordering;
5. QA environments, roles, accounts, and test-data policy;
6. production QA and evidence-redaction restrictions;
7. defect classification, priority, and spec-depth policy;
8. reference-library root, domains, and artifact authority;
9. external access and capture restrictions;
10. routing from domain evidence to shaping, specification, and implementation.

## Stage 10 — installation and customization

Purpose: finalize distribution, commands, and extension boundaries.

Resolve the following; ask only unresolved decision-changing items:

1. workflow-kit source repository and exact release tag or full commit SHA;
2. centralized, vendored, or symlink installation;
3. active Codex skill directory;
4. behavior when an installed copy differs;
5. selected aliases and command catalog;
6. generated templates and managed files;
7. configuration-only versus project-runbook customization;
8. conditions for updating a central skill;
9. versioning, compatibility, migration, rollback, and future update policy;
10. final manifest approval and cleanup of setup state.

## Final review

Before manifest preview:

1. list all stages as complete, not applicable, deferred, or blocked;
2. resolve every material deferred question;
3. show detected facts that remain unconfirmed;
4. show assumptions and their consequences;
5. show selected and rejected modules;
6. show custom safety restrictions;
7. show external or global mutations;
8. stop when any required decision remains blocked.
