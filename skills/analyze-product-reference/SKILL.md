---
name: analyze-product-reference
description: Analyze an external product, competitor, live URL, screenshot, recording, document, or existing reference pack as bounded product evidence. Use when the user asks to research, benchmark, compare, revisit, or add a product reference; investigate how other products handle a flow, surface, state, product mechanic, onboarding, pricing presentation, positioning, or marketing pattern; compare one pattern across products; adapt findings to the current project; or invokes `--reference-analysis` with a product, URL, artifact, or question. Select the lowest sufficient depth, distinguish observation from documentation and inference, grade freshness and confidence, and persist artifacts only with explicit authority. Do not use for generic factual lookup, market sizing, broad due diligence, confidential intelligence, designing the target flow, final copywriting, task specifications, implementation, target-product QA, or literal copying.
---

# Analyze Product Reference

Turn one bounded external reference question into evidence-backed product implications without treating the reference as a source of truth.

## Keep the responsibility narrow

- Own the research question, evidence boundary, analysis depth, confidence, comparison method, and adaptation classification.
- Support UI/UX, product mechanics, onboarding, pricing presentation, positioning, and marketing evidence while keeping one declared primary domain per analysis.
- Separate what was directly observed, officially documented, inferred, and left unknown.
- Let project-specific design, shaping, pricing, marketing, copy, specification, and implementation workflows own their resulting decisions and artifacts.
- Do not convert a competitor pattern directly into a target-product requirement, visual source of truth, task, specification, or code.
- Do not inventory an entire product when a focused question is sufficient.

## Establish mode and authority

Choose the lowest sufficient mode:

- `quick scan`: answer one narrow question in chat;
- `flow level`: analyze one bounded user journey and identify candidate surfaces for deeper study;
- `surface level`: analyze one page, screen, modal, drawer, step, or other coherent surface;
- `focused follow-up`: deepen one predefined dimension such as states, mobile behavior, trust, pricing, content, or adaptation;
- `cross-reference comparison`: compare the same bounded question across multiple products with one rubric.

Treat `--reference-analysis <product, URL, artifact, or question>` as authority for bounded external research and a chat-first result. It does not authorize project files, stored captures, task artifacts, product decisions, or implementation.

An explicit request to add, save, document, refresh, or update the reference authorizes exact project-configured reference artifacts, minimum reusable evidence assets, and required map updates. Apply `record-project-context` and update existing canonical artifacts before creating new ones.

When a broad request combines a flow and unspecified deep dives, complete the flow-level result first and stop for surface selection. Continue in the same request only when the user already named the exact surfaces or focused dimensions.

## Respect external-access and content boundaries

- Prefer public, current, direct sources.
- Use public navigation and reversible anonymous UI state only when needed for the research question.
- Treat this as authority only for transient, non-submitted interaction state, not for durable, account-level, transactional, or submitted external mutations.
- Use an authenticated user-provided session only with explicit authority and without changing account or production data outside the exact request.
- Do not create accounts, submit real leads or messages, upload data, place orders, enter payment details, make purchases, or change external account settings.
- Do not bypass authentication, paywalls, CAPTCHA, anti-bot controls, geographic restrictions, or access controls.
- Treat access blocks as evidence limitations; use permitted official or secondary sources and lower confidence.
- Do not collect confidential, personal, cross-tenant, credential, or unnecessary account data.
- Keep quotations minimal and never reuse external copy, code, images, or visual assets as target-product production material.

## Resolve project policy

Use an already sufficient orientation or `load-project-context`. Resolve only what the analysis needs:

- target product, decision, actor, market, maturity, and source-of-truth boundaries;
- configured reference root, maps, domains, naming, templates, and artifact language;
- existing reference packs and freshness metadata;
- visual, product, content, legal, privacy, tenant, accessibility, localization, and mobile constraints;
- allowed browser, web, authenticated-session, capture, and asset-storage behavior;
- domain-specific handoffs and persistence authority.

Keep project names, paths, products, locales, repositories, templates, and adaptation criteria in project configuration or project docs, not in this reusable skill.

## Run the reference-analysis workflow

### 1. Frame one research question

Read [frame-reference-question-and-scope.md](references/frame-reference-question-and-scope.md).

Define the decision this evidence should inform, target audience, primary domain, reference subject, included and excluded scope, required freshness, intended consumer, and result mode. Ask only when a missing answer changes the evidence plan or analysis boundary.

### 2. Check existing knowledge before research

Inspect the configured root map, exact project map, relevant domain map, and matching analysis artifacts through progressive disclosure. Do not load an entire reference library.

Reuse an existing pack when it already owns the subject. Distinguish a refresh of stale evidence from a new question. Do not create a parallel document merely because the source is being revisited.

### 3. Collect and grade evidence

Read [collect-and-grade-reference-evidence.md](references/collect-and-grade-reference-evidence.md).

Use the minimum source set that can answer the question. Capture provenance, observation date, source type, locale, viewport or device, authentication state, accessible scope, limitations, and confidence when relevant.

Label claims as:

- `observed`;
- `documented`;
- `inferred`;
- `unknown`.

Do not upgrade inference into observation through repetition.

### 4. Analyze at the selected depth

- For a journey, read [analyze-product-flow.md](references/analyze-product-flow.md).
- For one coherent surface, read [analyze-product-surface.md](references/analyze-product-surface.md).
- For a focused dimension or comparison, read [run-focused-or-cross-reference-analysis.md](references/run-focused-or-cross-reference-analysis.md).

For a quick scan, apply only the relevant subset and stop when the exact question is answered.

Keep observations, interpretation, strengths, weaknesses, and unresolved gaps separate. Do not fabricate hidden states, business rules, implementation details, conversion performance, or causal outcomes.

### 5. Adapt findings to the target product

Read [adapt-findings-to-target-product.md](references/adapt-findings-to-target-product.md).

Classify each material pattern:

- `adopt`;
- `adapt`;
- `experiment`;
- `reject`;
- `unknown`.

Explain the target-product constraint or evidence behind the classification. Translate visual or product inspiration into principles and testable implications, not copied layouts, content, assets, or technical instructions.

### 6. Report or persist the result

Read [persist-and-handoff-reference-findings.md](references/persist-and-handoff-reference-findings.md).

Return the result in chat by default. With explicit persistence authority:

1. update the existing canonical pack or create only the exact missing artifact;
2. use project-local templates before bundled fallbacks in `assets/templates/`;
3. store only decisive, reusable, permitted evidence assets;
4. update applicable root, project, and domain maps;
5. preserve provenance and freshness;
6. avoid duplicating target-product decisions owned elsewhere.

## Present the result

Include only applicable sections:

- research question, mode, scope, and intended consumer;
- sources, observation date, environment, limitations, and confidence;
- observed or documented behavior;
- interpretation and unknowns;
- strengths, weaknesses, and relevant patterns;
- cross-reference matrix when comparing products;
- `adopt`, `adapt`, `experiment`, `reject`, and `unknown` implications;
- evidence or artifact links;
- exact next owner and open questions.

Do not claim that a pattern is proven by the market merely because a competitor uses it. Do not infer business performance, accessibility, security, or user satisfaction from appearance alone.

## Coordinate with adjacent workflows

- Hand product outcome, scope, prioritization, and backlog decisions to `shape-project-work`.
- Hand target frontend interaction design to `design-frontend-flow`.
- Hand own-channel content performance, campaign execution, and content creation to the configured marketing or copy workflow.
- Hand exact Task ID, Issue, Project, and status changes to `manage-project-work` only after separate backlog authority.
- Hand a requested implementation specification to `write-task-spec` only after shaping and specification authority.
- Never hand directly to implementation from reference evidence alone.
