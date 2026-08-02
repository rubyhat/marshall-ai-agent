---
name: record-architecture-decision
description: Create, review, clarify, accept, reject, deprecate, or supersede one material Architecture Decision Record (ADR) under project-configured authority. Use when the user asks to create or update an ADR, invokes `--adr-review` or `--record-adr`, or when shaping, specification, implementation, or context work encounters a durable architecture choice, a conflict with an accepted ADR, or evidence that an ADR may no longer apply. Do not use for routine implementation choices, architecture overviews, task status, broad documentation cleanup, or silent acceptance of an unapproved decision.
---

# Record Architecture Decision

Own the substantive lifecycle of one material architecture decision without
turning ADRs into immutable dogma or task history.

## Keep the responsibility narrow

- Decide whether one architecture choice merits an ADR.
- Review whether an existing ADR still applies before downstream work conforms
  to it.
- Compose one bounded ADR lifecycle mutation: proposal, decision, clarification,
  rejection, deprecation, or supersession.
- Let project configuration define paths, identifiers, status labels, required
  sections, decision authority, and mutation policy.
- Use `record-project-context` to route and persist the exact ADR/index mutation
  after this skill establishes its content and authority.
- Do not own current architecture documentation, task specifications, issue
  status, implementation progress, broad context cleanup, or release history.

## Resolve mode and authority

Choose one mode:

- `review`: read-only necessity or applicability assessment;
- `propose`: create a reviewable decision without accepting it;
- `decide`: accept or reject a proposed decision under configured authority;
- `clarify`: correct or expand an ADR without changing its material meaning;
- `deprecate`: retire an accepted decision without naming a replacement;
- `supersede`: replace an accepted decision with a new decision and preserve
  both records.

Treat `--adr-review <ADR or task anchor>` as read-only authority. Treat
`--record-adr <decision anchor>` as authority to run the guided bounded workflow,
not as authority to accept an unresolved decision.

Before any mutation, resolve:

- the exact decision or ADR;
- project ADR root and index;
- ID and filename convention;
- semantic lifecycle states and their project-specific labels;
- decision authority and approval evidence;
- required sections and link policy;
- whether the requested mutation needs a preview or separate confirmation;
- configured writer-coordination strategy and its exact project protocol.

If ownership, identity, status meaning, decision authority, or writer
coordination is ambiguous, stop before writing.

Read [validate-adr-configuration.md](references/validate-adr-configuration.md)
before every ADR mutation. Stop when the configured convention or the concrete
rendered paths fail its bounded safety checks.

## Run the ADR workflow

### 1. Test materiality

Read [decide-whether-adr-is-needed.md](references/decide-whether-adr-is-needed.md).

Create an ADR only for a durable choice whose rationale and consequences will
matter across tasks or over time. Return `ADR not needed` for routine,
reversible, task-local implementation choices and route their constraints to
the owning specification, code, or runbook.

### 2. Review applicability

When an existing ADR may govern the work, read
[review-adr-applicability.md](references/review-adr-applicability.md).

Check semantic status, scope, assumptions, decision drivers, review triggers,
current architecture, and new evidence. Do not force a task to conform when
applicability is uncertain or the decision's premises may have changed.

Return one result:

- `applicable`;
- `not applicable`;
- `review required`;
- `unclear`.

Only `applicable` permits downstream work to rely on the ADR as an active
constraint. The other results must carry a concise reason and next owner.

### 3. Build the decision record

Capture only information needed to understand and revisit the decision:

- context and exact scope;
- decision drivers and material constraints;
- considered options and meaningful trade-offs;
- decision and rationale;
- positive and negative consequences;
- assumptions and review triggers;
- related ADRs, architecture, tasks, specs, and evidence;
- semantic state, project label, authority, and decision date.

Use [ADR template](assets/adr-template.md) and the project's configured
adaptation. Do not copy implementation plans, status logs, or large source
documents into the ADR.

### 4. Apply the lifecycle gate

- A proposed ADR may be edited while the decision remains unresolved.
- Acceptance or rejection requires configured decision authority and explicit
  evidence of the decision.
- An accepted ADR may receive non-material corrections, clearer scope, links,
  evidence, or review metadata.
- A material change to an accepted ADR requires supersession; never rewrite its
  historical rationale to make the old decision appear different.
- Deprecation requires an explicit reason and resulting downstream guidance.
- Project-specific labels may differ, but semantic states must remain distinct.

Read [supersede-architecture-decision.md](references/supersede-architecture-decision.md)
before changing the material meaning of an accepted ADR.

### 5. Preview and persist the exact mutation

Show the bounded mutation set before writing when project policy requires it:

- create: new ADR and its index entry;
- decide or clarify: exact ADR fields plus its index entry when affected;
- deprecate: lifecycle metadata, reason, and index entry;
- supersede: replacement ADR, old ADR status/backlink, and both index entries.

Do not broaden the mutation to unrelated ADRs, architecture documents, specs,
or memory. Hand the approved content, complete artifact set, and configured
whole-mutation coordination, cleanup, and partial-failure policy to
`record-project-context`. Reread every written file, verify links and semantic
states, and confirm that one source owns the rationale.

## Coordinate with downstream work

- `shape-project-work` hands off a confirmed material architecture choice
  before dependent scope or decomposition treats it as settled.
- `write-task-spec` links applicable accepted ADRs and returns uncertain or
  challenged decisions to this workflow.
- `execute-project-task` stops when implementation evidence may invalidate an
  ADR instead of silently adapting code or the decision.
- `load-project-context` loads only ADRs relevant to the exact task and treats
  status and applicability as part of relevance.
- `record-project-context` routes and persists ADR content but does not invent
  its rationale or lifecycle transition.
- `maintain-project-context` may verify links and lifecycle consistency but
  never rewrites ADR rationale during cleanup.

After a lifecycle mutation, report the ADR identity, semantic state, authority
evidence, affected files, applicability result, and any blocked downstream work.
