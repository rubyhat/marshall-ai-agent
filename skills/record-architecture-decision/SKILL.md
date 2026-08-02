---
name: record-architecture-decision
description: Create, review, accept, reject, clarify, deprecate, or supersede one material architectural decision without treating an accepted ADR as permanent dogma. Use when the user asks to document or revisit an architectural choice, invokes `--adr-review` or `--record-adr`, when shaping approves a durable cross-cutting decision, when a persisted proposal is resolved, when a task or implementation conflicts with an applicable ADR, or when new evidence may invalidate an ADR's assumptions, scope, trade-offs, or consequences. Perform applicability review before forcing work to conform. Do not use for ordinary implementation preferences, current architecture summaries, task specifications, task logs, or silent scope changes.
---

# Record Architecture Decision

Preserve why one material architecture choice was made while keeping the
decision explicitly reviewable as the project changes.

## Keep the responsibility narrow

- Own ADR necessity, applicability review, content, lifecycle, and
  supersession.
- Let `shape-project-work` establish the intended outcome, compare material
  options, resolve product scope, and obtain the decision authority.
- Let `record-project-context` route and persist the approved project-local
  artifact without creating a competing source of truth.
- Keep current system structure in the owning architecture documentation and
  implementation truth in code, schema, and runtime configuration.
- Keep implementation scope and acceptance criteria in task specifications,
  and operational progress in the configured task system.
- Do not use an ADR to legitimize an accidental code drift, temporary shortcut,
  ordinary library preference, or decision that has not been accepted.

## Choose one mode

- `review`: inspect one exact ADR or one task against its relevant ADRs without
  changing project artifacts.
- `record`: create one proposed ADR after its materiality, scope, decision
  question, and the user's request to persist the unresolved proposal are
  explicit, or one accepted ADR after the decision authority accepts it.
- `accept`: transition one persisted proposal in place to the configured
  accepted state after the configured authority explicitly accepts it.
- `clarify`: correct wording, provenance, metadata, or links without changing
  the accepted decision's meaning.
- `supersede`: record a new accepted decision and link the replaced ADR without
  rewriting its historical rationale.
- `deprecate`: mark a decision no longer recommended when no replacement has
  yet become authoritative.
- `reject`: transition one persisted proposal to the configured rejected state
  after the configured authority explicitly rejects it, preserving the
  rejection rationale.

Treat exact `--adr-review <ADR or task anchor>` as read-only review authority.
Treat exact `--record-adr <decision anchor>` as authority to run the guided ADR
workflow. Creation, acceptance, rejection, clarification, and deprecation may
mutate only the one exact target ADR and its index entry. Supersession may
mutate only the exact replacement ADR, the replaced ADR's lifecycle status and
backlink, and their index entries. Persist a
proposed ADR only when that state is configured, the request explicitly asks
to retain the unresolved proposal, and the record clearly states that no
decision was accepted. Persist an accepted ADR only after the configured
decision authority accepts it. Persist a rejected transition only after that
authority explicitly rejects the recorded proposal. The alias does not accept
or reject a decision by itself and does not authorize code, task, tracker,
deployment, or production mutations.

## Resolve project policy

Use project configuration and instructions to resolve:

- whether the ADR module is enabled;
- ADR root, index, ID and filename convention;
- configured `<slug>` UTF-8 byte budget, defaulting to 96 when omitted;
- configured labels for the semantic lifecycle states and decision authority;
- project or domain triggers that require an ADR;
- architecture sources and relationship to code and task specifications;
- template, documentation language, and required metadata;
- applicability and supersession rules plus configured review triggers;
- whether the optional proposed state, bounded exceptions, and retrospective
  recording are permitted.

The workflow names semantic states as `proposed`, `accepted`, `superseded`,
`deprecated`, and `rejected`. Write the project-configured label mapped to that
state; do not assume the literal English label. If `proposed` maps to `null`,
resolve the decision before persisting an ADR.

Do not invent a path or approval authority merely because an ADR-like folder
exists. If policy is missing, reuse one coherent existing convention or ask
only for the choice that would create a competing source of truth.

## Run the ADR workflow

### 1. Resolve one exact decision

State the decision question, affected scope, current behavior, desired outcome,
known constraints, and source of the request. Separate the architectural choice
from the task that exposed it.

Read [decide-whether-adr-is-needed.md](references/decide-whether-adr-is-needed.md).
Do not create an ADR when another artifact already owns the information or when
the choice is cheap, local, reversible, and unsurprising.

### 2. Review applicability before enforcing an ADR

When an ADR may constrain current work, read
[review-adr-applicability.md](references/review-adr-applicability.md).

Check status, scope, assumptions, decision drivers, review triggers, current
architecture, code evidence, and new constraints before requiring the task to
conform. Return one verdict:

- `ADR applicable`;
- `ADR review required`;
- `ADR not applicable`;
- `ADR applicability unclear`.

Do not adapt a task or implementation to an ADR while the verdict is `ADR
review required` or `ADR applicability unclear`. Stop before downstream specs
or code rely on the disputed decision and return the decision to shaping.

### 3. Establish the decision and authority

For a new or reconsidered decision, require:

- explicit outcome and scope;
- verified decision drivers and assumptions;
- viable options and material trade-offs;
- consequences, including costs and risks;
- review triggers;
- configured acceptance authority.

Use `shape-project-work` when any of those would change product meaning,
architecture direction, dependency ownership, security posture, or task
decomposition. Do not hide an unresolved choice inside confident ADR prose.

### 4. Choose the lifecycle action

Read [supersede-architecture-decision.md](references/supersede-architecture-decision.md).

- Create `proposed` only for a material decision that must survive an extended
  unresolved discussion.
- Create `accepted` only after the configured authority accepts the decision.
- Use `accept` to transition an existing proposal in place after that
  authority accepts it. Preserve its ADR identity, update its decision date,
  authority, status, and index entry, and do not create a duplicate accepted
  ADR for the same decision.
- Use `clarify` only when the decision's meaning remains unchanged.
- Use `supersede` for a material change to an accepted decision.
- Use `deprecate` when the decision should no longer guide new work but no
  replacement is accepted.
- Use `reject` to transition a durable proposal to the configured `rejected`
  state only when its rejection rationale will prevent costly reopening.

### 5. Write one compact ADR

Use the configured project template. Fall back to
[adr-template.md](assets/adr-template.md) only when no project template exists.
Treat `<ID>` as the complete project-configured ADR identifier; never add a
second fixed prefix to it in the title, filename, index, or links.
Before writing, require the configured ADR root and index to be project-root
relative and contained on both POSIX and Windows path semantics. Require the
concrete ID to match both the configured pattern and the portable
`[A-Za-z0-9_-]+` boundary. Render every filename placeholder to a concrete
relative path, then reject an absolute path, Windows drive, parent component,
or any lexical/resolved escape from the configured ADR root or project root,
including a symlink boundary. Normalize a generated slug to a single safe
`[a-z0-9_-]+` filename segment, truncate it to the configured
`slug_max_bytes` UTF-8 budget (96 when omitted), and revalidate the fully
rendered component against the 255-byte portability limit. Reject Windows
reserved device components such as
`CON`, `NUL`, `COM0`–`COM9`, `LPT0`–`LPT9`, their ISO-8859-1 superscript
`1`–`3` aliases, `CONIN$`, or `CONOUT$` even when they have an extension;
never interpolate raw user text into the path.

Include only applicable content:

- ID, title, status, decision date, authority, and scope;
- context and decision question;
- decision drivers and assumptions;
- considered options and their material trade-offs;
- accepted decision, or explicit rejected outcome and rejection rationale;
- positive and negative consequences;
- explicit review triggers;
- supersession and canonical links.

Do not include task chronology, implementation progress, meeting narration,
full code detail, or copied specifications. Status describes the decision
lifecycle, not whether implementation or rollout is complete.

Use `record-project-context` to persist only the exact ADR artifact set
authorized for the selected lifecycle action and update the configured ADR
index. Link architecture, specs, Issues, and pull requests instead of
duplicating their contents.

### 6. Verify and hand off

Verify:

1. one ADR owns the exact rationale;
2. status, scope, authority, and supersession links agree;
3. the old accepted rationale was not rewritten during supersession;
4. architecture documentation is not falsely describing a future state as
   current;
5. dependent task specs link the decision rather than restating it;
6. a `proposed → accepted` or `proposed → rejected` transition preserved the
   ADR identity and updated the index;
7. a rejected ADR contains the explicit rejection outcome and durable
   rationale;
8. no downstream implementation proceeds while applicability is unresolved.

Then hand an accepted direction or a rejected outcome back to
`shape-project-work` or `write-task-spec` as applicable. When implementation
later reveals material contrary evidence, repeat applicability review instead
of silently bending the code or the task around the ADR.

## Coordinate with adjacent skills

- Use `load-project-context` to locate only the relevant architecture and ADRs.
- Receive material decisions and conflict resolution from `shape-project-work`.
- Use `record-project-context` for persistence and source-of-truth routing.
- Let `write-task-spec` consume accepted ADRs as linked constraints.
- Require `execute-project-task` to stop on a credible ADR invalidation signal.
- Let `maintain-project-context` audit links and retention without owning ADR
  meaning or supersession.
