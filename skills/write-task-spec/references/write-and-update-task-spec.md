# Write and update a task specification

Build one coherent implementation contract from the shaped task and verified technical context.

## Preserve source-of-truth boundaries

- Keep roadmap priority and operational status in the configured task system.
- Keep detailed intended behavior and implementation constraints in the spec.
- Keep runtime truth in code, schemas, and configuration.
- Keep durable architecture decisions in their canonical decision artifact.
- Link rather than copy large research reports, parent specs, or external contracts.

The specification may summarize those sources only to make the exact task executable.

## Establish metadata

Use configured fields such as:

- task identifier;
- title and slug;
- owner or repository;
- tracker URL;
- parent or shared feature;
- spec path;
- priority and risk when the project keeps them in specs;
- content verdict.

Do not invent metadata that project policy does not use. Verify every link and identifier.

## Write the core contract

Describe:

1. outcome and why it matters;
2. current and desired behavior;
3. in-scope and out-of-scope work;
4. actors, roles, and key scenarios;
5. confirmed decisions, assumptions, and open questions;
6. functional and non-functional requirements;
7. verified solution boundaries and implementation sequence;
8. contracts, data, errors, and recovery;
9. dependencies, ordering, compatibility, and rollout;
10. cross-cutting impacts;
11. acceptance criteria and test strategy;
12. risks and links.

Remove unused optional sections when project templates permit it. Do not fill them with generic prose such as "not applicable" unless project policy requires an explicit classification.

## Use verified technical detail

- Name a module, file, class, endpoint, table, event, or command only after verification.
- Distinguish an architectural requirement from a suggested implementation.
- Preserve framework-native and project-native patterns.
- Explain why a non-obvious constraint exists.
- Mark a bounded investigation gate when exact implementation detail cannot be known before work starts.

Do not turn a spec into pseudocode for every function.

## Keep the document concise

- State each rule once in its canonical section.
- Reference requirements from acceptance criteria rather than restating long prose.
- Use tables for state, role, permission, compatibility, or test matrices.
- Move only large conditionally needed material to annexes.
- Avoid history logs, session narration, and duplicated Issue content.

## Update an existing spec

Before editing:

1. identify the current approved outcome and scope;
2. compare requested changes with the tracker, parent, decisions, and code;
3. separate clarification from material scope change;
4. route material reshaping to `shape-project-work`.

When authorized:

- replace superseded current-state wording;
- keep task identity stable;
- update all affected requirements, contracts, criteria, tests, and links together;
- remove contradictions introduced by the change;
- preserve completed historical specs unless the user explicitly requests correction or migration.

## Handle incomplete information

Do not manufacture content to make the template look complete.

- Blocking product decision: return to shaping.
- Large unknown technical boundary: propose discovery.
- Non-blocking verified assumption: label it and define validation.
- Explicit draft request: retain clear blockers and do not claim readiness.
