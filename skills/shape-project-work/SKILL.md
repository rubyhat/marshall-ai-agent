---
name: shape-project-work
description: Shape a project idea, feature, problem, research initiative, epic, or oversized task into an agreed outcome, bounded scope, explicit decisions, and a risk-checked conceptual work breakdown. Use when the user wants to discuss or formalize new work, compare solution options, answer decision-changing questions, define an epic or feature, split work into implementation tasks, resolve cross-repository ownership and ordering, check shaping readiness, continue to the next planned specification, invokes `--planning-session`, `--shape-work`, `--shape-roadmap`, `--prepare-spec`, or `--next-spec`, or answers the current shaping questions with `--accept-recommended`. Challenge material conflicts with established rules, architecture, decisions, workflow order, or safety constraints before continuing. Do not itself write a full task specification, allocate Task IDs, mutate Issues or Projects, implement code, perform QA intake, or own broad external reference research.
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

- `planning session`: keep the current conversation focused on discussion,
  product and architecture shaping, roadmap work, and specification preparation;
- `discussion`: explore an idea and return a synthesis without writing files or creating tasks;
- `roadmap shaping`: define durable Epic, Feature/Story, or Implementation Task candidates and hand authorized operational work to `manage-project-work`;
- `specification requested`: finish shaping, then hand the agreed task to `write-task-spec`;
- `next specification requested`: verify the prior planning handoff, resolve the
  next eligible task from the same canonical work graph, and then run the
  specification-requested workflow;
- `shaping review`: inspect an existing proposal or work breakdown and report gaps without silently rewriting it.

A planning-session profile is a sticky conversation constraint, not a host
application mode. It remains active for the current conversation. It does not
authorize artifacts or tracker mutations by itself, and it blocks
implementation and delivery capabilities. Later planning, roadmap,
task-management, frontend-design, reference-analysis, architecture-decision,
or specification
requests may authorize only their bounded non-implementation workflows.
Implementation or delivery aliases and equivalent natural-language requests
never release the profile implicitly. Require a new conversation when project
policy defines `new_conversation_only` release semantics.

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

## Enforce workflow order

Resolve active conversation constraints before alias-specific authority, task
readiness, or mutation-capable tool calls. Treat an explicit current-session
no-code, no-implementation, no-delivery, read-only, or planning-only
instruction as sticky when its wording or project policy makes it persistent.
A later request may narrow the active boundary but must not silently expand it.

Before acting on a quick alias, resolve the strongest available workflow state:
current idea or task anchor, shaping verdict, tracker identity, specification
verdict, dependencies, implementation checkpoint, and delivery checkpoint.

If the alias is premature, stale, ambiguous, or belongs to another phase:

1. stop before mutations;
2. state the received alias and resolved current state;
3. name the unmet prerequisite or ordering conflict;
4. recommend the exact safest next alias or action;
5. explain what evidence will unblock the requested alias.

Do not require every preceding implementation task to be complete merely
because it appears earlier in a roadmap. Block downstream specification only
when an unfinished dependency leaves the outcome, contract, scope, ownership,
or acceptance behavior materially unstable.

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

Name the exact conflict or risk, its likely consequence, supporting source, and the safest correction or alternatives. Continue only after the user corrects the request or explicitly acknowledges and accepts the material trade-off. Route a challenged architecture decision through `record-architecture-decision`; use `record-project-context` to persist other superseded durable knowledge.

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

When a confirmed choice is a material architectural decision and
`record-architecture-decision` is configured, use it to test whether an ADR is
needed and to record the accepted rationale before dependent specifications
rely on it. If the module is unavailable, stop at the material decision
boundary and report the missing owner instead of improvising an ADR. If a
relevant accepted ADR may no longer apply, stop downstream shaping and request
an applicability review instead of forcing the new outcome to conform.

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
- Use `record-architecture-decision` for approved durable architectural
  decisions and `record-project-context` for their persistence, other durable
  decisions, research results, risks, or active handoffs. Prefer updating an
  existing canonical source.
- If a full specification was explicitly requested, resolve the project's required task anchors. When project policy says that request authorizes their creation, hand the exact shaped task to `manage-project-work`, verify the anchors, and then hand it to `write-task-spec` without asking for duplicate permission. Otherwise ask only for the missing anchor authority.
- If the specification workflow is unavailable, stop after shaping and report the missing dependency instead of writing an ad hoc specification.

## Interpret quick aliases

- `--planning-session [scope]`: establish the planning-session profile. Use the
  optional text only to bound the conversation. Do not create artifacts or
  require a task anchor merely to acknowledge the profile. Keep the profile
  active for the current conversation. Permit only separately authorized
  bounded planning and specification capabilities, and block implementation
  and delivery. When either is requested, stop before mutations, name the
  active profile and conflict, confirm that no mutation occurred, and require
  the configured release action.
- `--shape-work <idea or task anchor>`: start discussion or guided shaping. The
  alias does not authorize file creation, Issue/Project mutation, or a full
  task specification.
- `--shape-roadmap <idea or task anchor>`: run roadmap shaping and produce a
  conceptual work graph without full specifications. After questions are
  resolved, present the exact proposed tracker and optional durable-artifact
  mutations. Require a separate approval of that preview before handing
  operational changes to `manage-project-work` or durable recording to
  `record-project-context`.
- `--prepare-spec <Task ID or exact task anchor>`: treat this as an explicit
  request for one complete task specification. First validate workflow order,
  shape the exact task, explain the proposed bounded direction, and resolve all
  decision-changing questions. When no shaping blocker remains, establish any
  project-required task anchors through `manage-project-work` and hand the task
  to `write-task-spec` without asking again whether to create the specification.
  The alias does not authorize implementation or delivery.
- `--next-spec [Epic, previous Task, or exact plan anchor]`: treat this as an
  explicit request to select, discuss, and create the next complete
  specification in the active planning sequence. Resolve the last task prepared
  in the current conversation and its canonical work graph; use the optional
  anchor only to disambiguate that continuity. Do not scan the project for a
  merely recent task or guess when the active Epic or prior task is ambiguous.
  Ask `manage-project-work` to verify prior completion and linkage read-only;
  never repair the previous task's status through this alias. Select the next
  unfinished and unblocked task from dependency edges, not Task ID ordering.
  Automatically continue when one candidate is uniquely eligible; when
  multiple materially equivalent parallel candidates remain, present them,
  recommend one, and wait for the user's choice. An unfinished predecessor
  blocks continuation only when it leaves the next outcome, contract, scope,
  ownership, or acceptance behavior materially unstable. Once the exact next
  task is resolved, follow the same shaping, clarification, task-anchor, and
  `write-task-spec` handoff as `--prepare-spec` without asking again whether to
  create the specification. The alias does not authorize implementation,
  delivery, or mutation of completion evidence.

Ask for a missing required argument. An absent optional `--next-spec` anchor is
valid only when the current planning continuity is unambiguous. Treat trailing
text as bounded input, not broader authority.
