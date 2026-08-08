# Run Independent Local Review

Use a fresh configured reviewer before commit, push, or pull-request creation.

## Prepare neutral context

Give the reviewer only what is needed:

- applicable project and repository instructions;
- exact task specification;
- complete uncommitted diff;
- immutable delivery baseline with initial manifest and diff statistics;
- configured review rubric and domain gates;
- root project context access when review runs from a nested worktree.

Do not leak the implementation discussion, intended verdict, suspected findings, or previous defense of the code.
Require actionable output to name a concrete current-task failure or credible
mandatory risk, the affected path or behavior, and its relationship to the
reviewed diff. General hardening, speculative edge cases without a credible
task path, unrelated pre-existing defects, and stylistic refactors are not
actionable findings for this delivery.

## Run the configured command

Use the project-defined:

- reviewer command and sandbox;
- default model and reasoning settings;
- rate-limit or availability fallback;
- diff mode;
- title and context roots.

Do not hardcode a model or CLI syntax in this reusable runbook. Verify the command actually started and completed. A fallback applies only according to project policy.

## Assess findings

For every finding:

1. locate the exact code and affected behavior;
2. compare it with tests, architecture, task scope, acceptance criteria, and current contracts;
3. classify it as real, false, out of scope, duplicate, or uncertain;
4. fix real in-scope findings;
5. rerun affected quality gates;
6. repeat independent local review when changes are material or policy requires it.

Before applying any review-driven package, enforce the configured local
correction-round budget. Increment it once per coherent package, not once per
finding or file. The candidate produced by the final allowed round still
receives review. If that review requires another package, stop before editing,
commit, push, or pull-request creation and return the bounded cycle analysis.
After every local verdict or package, update and read back the current Codex
task's machine-readable delivery-state block before continuing.

Do not change code merely to satisfy a mistaken review. Do not dismiss a finding without evidence.

## Complete the gate

Local review passes when:

- no unresolved real finding remains;
- final diff and required gates are current;
- any rejected finding has a concise evidence-based rationale;
- any allowed external blocker is visible;
- the task still matches its specification and authorized endpoint.

Keep changes uncommitted until this gate succeeds.
