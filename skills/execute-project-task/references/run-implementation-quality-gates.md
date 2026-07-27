# Run Implementation Quality Gates

Select gates from project configuration, repository instructions, the task specification, and applicable domain workflows.

## Build the gate set

Include only checks relevant to the changed surface, such as:

- focused unit, integration, request, component, or end-to-end tests;
- lint, formatting, static analysis, and type checking;
- build or compile checks;
- schema, migration, rollback, data, or compatibility checks;
- security, authorization, tenant isolation, privacy, or dependency checks;
- localization, accessibility, visual, browser, or mobile-flow checks;
- API, event, generated-client, or multi-repository contract checks;
- documentation or configuration validation.

Start with targeted feedback. Run broader suites when project policy, risk, shared surface area, or the specification requires them. Do not substitute a narrow passing test for a configured required gate.

## Run against the final change

- Use the task worktree and project-approved commands.
- Record command, relevant environment, result, and meaningful limitation.
- Rerun affected gates after fixes.
- Ensure the reported result corresponds to the final diff, not an earlier intermediate state.
- Do not expose secrets or persist sensitive command output.

## Classify failures

### Caused by the task

Fix the failure within scope and rerun the gate.

### Suspected pre-existing or unrelated

Verify with bounded evidence, such as:

- the same command or focused reproduction on the verified base;
- an existing tracked issue or current known-problem source;
- a clearly unrelated failing file, service, or environment dependency.

Do not label a failure pre-existing merely because the changed code looks unrelated.

### External blocker

Identify the unavailable service, credential, environment, remote, or tool. Follow project degraded-mode policy. Preserve the exact unverified gate for review or delivery.

## Decide implementation readiness

Mark each required gate as:

- `passed`;
- `failed`;
- `not run` with reason;
- `blocked` with evidence.

The task is ready for local review only when:

- every required gate passed; or
- project policy explicitly allows the exact verified external or pre-existing blocker and the limitation is visible in the handoff.

Do not fix unrelated failures by silently widening scope. Do not weaken or delete a valid gate to obtain a passing result.
