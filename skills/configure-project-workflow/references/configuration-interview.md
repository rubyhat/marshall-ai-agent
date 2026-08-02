# Configuration Interview

Use this staged catalog to obtain complete setup information without presenting one overwhelming questionnaire.

## Contents

1. Interview rules
2. Stage 1 — safety and authority
3. Stage 2 — project identity and repositories
4. Stage 3 — instructions and source-of-truth boundaries
5. Stage 4 — context and documentation
6. Stage 5 — architecture decisions
7. Stage 6 — shaping and specifications
8. Stage 7 — task management
9. Stage 8 — implementation
10. Stage 9 — review and delivery
11. Stage 10 — domain modules
12. Stage 11 — installation and customization
13. Final review

## Interview rules

- Present 7–10 numbered prompts in each active stage.
- Use a detected fact as a confirm-or-correct prompt instead of asking it from scratch.
- Skip an entire conditional stage only when the selected profile makes it genuinely inapplicable.
- Do not pad a stage with irrelevant questions; combine closely related confirmations into one prompt when needed.
- Ask factual unknowns directly.
- For material decisions, offer 2–3 mutually exclusive options with `А (Рекомендую)` first and a concise trade-off.
- Accept compact answers such as `1 - А` and free-form alternatives.
- Explain why a question matters when its consequence is not obvious.
- Update and validate the tracker after every stage.
- Preserve deferred questions and return to them before manifest approval.

## Stage 1 — safety and authority

Purpose: establish the setup protection layer before deeper inspection.

Ask 7–10 prompts covering:

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

Ask 7–10 prompts covering:

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

Ask 7–10 prompts covering:

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

Ask 7–10 prompts covering:

1. existing or default project-doc root;
2. existing or default internal-memory root;
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

## Stage 5 — architecture decisions

Activate only when `record-architecture-decision` is selected.

Ask 7–10 prompts covering:

1. canonical ADR root and index path;
2. the bounded fixed-width decimal ADR identifier convention and exact
   `<ID>.md` filename pattern;
3. semantic lifecycle states and their project-specific labels;
4. required sections, relative-link policy, and index-entry contract;
5. materiality threshold and when applicability review gates downstream work;
6. decision authority and acceptable evidence for proposal, acceptance,
   rejection, clarification, deprecation, and supersession;
7. preview and separate-confirmation requirements for lifecycle mutations;
8. the boundary between non-material clarification and mandatory
   supersession;
9. links to architecture, tasks, specifications, and supporting evidence;
10. existing ADRs or status vocabularies that must be preserved or reconciled.

Reject a requested convention that cannot preserve project containment,
artifact identity, distinct lifecycle labels, or non-blank authority. Route a
project that requires another ID or filename format to an explicit workflow-kit
contract change instead of expanding the setup interview into a generic pattern
validator.

## Stage 6 — shaping and specifications

Purpose: define how ideas become implementation-ready work.

Ask 7–10 prompts covering:

1. work types that require shaping;
2. clarification-question format;
3. conflict and risk gate;
4. conceptual hierarchy and decomposition expectations;
5. when full versus lightweight specifications apply;
6. explicit and configured specification handoffs, including whether a
   continuation command may resolve the next task from the active work graph;
7. project-local templates and bundled fallback policy;
8. required impact gates such as migration, localization, security, privacy, rollout, or accessibility;
9. specification readiness verdicts;
10. when implementation authority must be requested separately.

## Stage 7 — task management

Activate only when operational task tracking is selected.

Ask 7–10 prompts covering:

1. provider and issue repository;
2. Project, board, or roadmap location;
3. Task ID format and uniqueness scope;
4. hierarchy levels and parent rules;
5. allowed standalone task types;
6. fields, labels, milestones, or components;
7. lifecycle statuses and transitions;
8. Issue body and spec/PR linking;
9. mutation checkpoints owned by runtime workflows and authoritative
   read-only completion evidence used for task-sequence continuation;
10. operations requiring separate confirmation, including broad sync and schema changes.

## Stage 8 — implementation

Purpose: define safe local task execution.

Ask 7–10 prompts covering:

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

## Stage 9 — review and delivery

Purpose: define publication and completion authority.

Ask 7–10 prompts covering:

1. independent local review requirement;
2. reviewer isolation and finding severity;
3. commit policy and message conventions;
4. push and force-push rules;
5. pull-request language, target, template, and linkage;
6. automated reviewer integration and bounded waiting;
7. required CI/check policy;
8. merge authority and allowed methods;
9. post-merge closure, sync, and workspace cleanup;
10. deployment and production boundaries excluded from normal delivery.

## Stage 10 — domain modules

Activate when frontend design, frontend QA, or product-reference analysis is selected.

Present 7–10 prompts tailored to active modules, covering:

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

## Stage 11 — installation and customization

Purpose: finalize distribution, commands, and extension boundaries.

Ask 7–10 prompts covering:

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
