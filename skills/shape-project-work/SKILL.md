---
name: shape-project-work
description: Shape a project idea, feature, problem, research initiative, epic, or oversized task into an agreed outcome, bounded scope, explicit decisions, and a risk-checked conceptual work breakdown. Use when the user wants to discuss or formalize new work, compare solution options, answer decision-changing questions, define an epic or feature, split work into implementation tasks, resolve cross-repository ownership and ordering, check shaping readiness, or invokes `--shape-work`. Challenge material conflicts with established rules, architecture, decisions, or safety constraints before continuing. Do not write a full task specification, allocate Task IDs, mutate Issues or Projects, implement code, perform QA intake, or own broad external reference research.
---

# Shape Project Work

Turn unclear project intent into an agreed and traceable work definition. Preserve the complete intended outcome while reducing ambiguity, risk, and implementation size.

## Keep the responsibility narrow

- Own problem framing, option analysis, clarification, decisions, scope, conceptual hierarchy, repository ownership, dependencies, and shaping readiness.
- Perform only bounded research needed to make a shaping decision. Route a substantial research deliverable to the relevant research or analysis workflow.
- Let `manage-project-work` allocate Task IDs, validate operational hierarchy, and mutate Issues or Projects.
- Let `write-task-spec` create, update, or audit full task specifications when that workflow is available.
- Let domain workflows own detailed frontend flow design, QA reproduction, legal analysis, migrations, or external product-reference analysis.
- Do not create a local planning document by default. Preserve durable decisions or research only through `record-project-context`.

## Resolve the user's intent

Classify the request before shaping:

- `discussion`: explore an idea and return a synthesis without writing files or creating tasks;
- `roadmap shaping`: define durable Epic, Feature/Story, or Implementation Task candidates and hand authorized operational work to `manage-project-work`;
- `specification requested`: finish shaping, then hand the agreed task to `write-task-spec`;
- `shaping review`: inspect an existing proposal or work breakdown and report gaps without silently rewriting it.

Do not treat silence as authorization to create a full task specification.

- If the user explicitly requested a full specification, do not ask for the same permission again after shaping.
- If the user explicitly deferred or rejected a full specification, stop after the agreed shaping result and do not ask again in that workflow.
- If the user did not state an intention, finish the shaping result and ask one separate question about whether to create a full specification next.

## Resolve project policy and context

Use an already sufficient project orientation or invoke `load-project-context` for the minimum relevant context. Resolve:

- product and architecture sources of truth;
- existing decisions, constraints, and task hierarchy;
- repository ownership and configured task types;
- project dialogue and clarification policy;
- roadmap commitment and artifact-recording rules;
- domain workflows and sizing gates;
- whether a task-spec writer and templates are configured.

Do not load unrelated memory, specifications, or repositories.

## Run the shaping workflow

### 1. Restate the problem and intended outcome

Read [shape-outcome-scope-and-risks.md](references/shape-outcome-scope-and-risks.md).

Separate the user's desired outcome from the proposed implementation. Identify actors, current behavior, desired behavior, evidence, constraints, success signals, and explicit non-goals.

### 2. Run the conflict and risk gate

Before endorsing an option or committing work, compare the request with established decisions, project rules, architecture, workflow boundaries, permissions, and material risks.

Stop and state the objection before continuing when:

- the current request directly contradicts a still-active agreement, rule, architecture boundary, or workflow;
- the proposal introduces a credible material risk to security, privacy, tenant isolation, data integrity, legal or billing behavior, reliability, scalability, supportability, or scope integrity;
- continuing would make a durable mutation based on unresolved ownership or authority.

Name the exact conflict or risk, its likely consequence, supporting source, and the safest correction or alternatives. Continue only after the user corrects the request or explicitly acknowledges and accepts the material trade-off. Update a superseded durable decision through `record-project-context`.

Do not use speculative, remote, or trivial risks to block routine reversible choices. User acknowledgement never overrides higher-priority instructions, access boundaries, or non-waivable safety requirements.

### 3. Ask decision-changing questions

Read [clarifying-questions.md](references/clarifying-questions.md).

Ask only questions whose answers change the outcome, scope, lifecycle, contract, UX, safety, decomposition, ownership, or ordering. Offer recommended alternatives for decisions; ask factual questions directly when the answer cannot be inferred safely.

Wait for answers when unresolved questions are material. Accept the user's compact configured answer format and do not repeat settled questions.

### 4. Maintain the decision model

Distinguish:

- confirmed decisions;
- verified facts;
- assumptions;
- open questions;
- blockers;
- explicit out-of-scope items;
- follow-ups that preserve excluded parts of the intended outcome;
- accepted material risks and superseded decisions.

Never hide uncertainty inside confident task wording.

### 5. Decompose the work

Read [work-decomposition.md](references/work-decomposition.md) whenever the result may need more than one task, spans multiple outcomes, or has significant risk.

Read [cross-repo-decomposition.md](references/cross-repo-decomposition.md) when more than one repository, service, client, team, or deployable unit is involved.

Produce a conceptual work graph rather than operational Issue IDs. Give each proposed unit a bounded outcome, owner, dependency position, acceptance outline, and major risks.

### 6. Assess shaping readiness

Read [shaping-readiness.md](references/shaping-readiness.md).

Return one verdict:

- `needs clarification`;
- `shaped for roadmap`;
- `ready for specification`.

Do not call work `Spec ready` or `Ready for implementation`; those verdicts belong to the task-spec workflow.

### 7. Present the final shaping result

Include only applicable sections:

- problem and intended outcome;
- actors and value;
- current and desired behavior;
- in scope and out of scope;
- decisions and rationale;
- assumptions, open questions, and blockers;
- material risks and accepted trade-offs;
- proposed Epic/Feature/Implementation breakdown;
- repository ownership, dependencies, and ordering;
- shaping readiness verdict;
- recommended next action.

Keep the result usable as input to task management without pretending it is a full specification.

## Persist and hand off deliberately

- For discussion-only work, do not create files, Issues, or Project items.
- When the user commits the result to backlog or roadmap, pass the agreed work graph to `manage-project-work`; do not perform its mutations inside this skill.
- Do not create a separate local planning artifact unless the analysis has unique durable value beyond the Issue and future specification.
- Use `record-project-context` for an approved durable decision, research result, risk, or active handoff; prefer updating an existing canonical source.
- If a full specification was explicitly requested, resolve the project's required task anchors. When project policy says that request authorizes their creation, hand the exact shaped task to `manage-project-work`, verify the anchors, and then hand it to `write-task-spec` without asking for duplicate permission. Otherwise ask only for the missing anchor authority.
- If the specification workflow is unavailable, stop after shaping and report the missing dependency instead of writing an ad hoc specification.

## Interpret the quick alias

Treat exact `--shape-work <idea or task anchor>` as a request to start this workflow. The alias does not by itself authorize file creation, Issue/Project mutation, or a full task specification. Text after the alias supplies the shaping input.
