# Report the specification handoff

Use this format after creating or updating a task specification. Keep the
result compact enough to scan while making the next workflow decision
unambiguous.

## Report required fields

Include:

1. exact Task ID and full task title when the project uses stable IDs;
   otherwise the exact project-local task anchor and title, with Task ID
   explicitly marked not configured;
2. canonical tracker or Issue URL, or an explicit unavailable/not-configured
   result;
3. specification entrypoint and any created annexes;
4. owning or affected repositories and deployable units;
5. specification content verdict;
6. operational tracker status as a separate field;
7. a short observable outcome expected from implementation;
8. blockers, prerequisite state, and the recommended next action;
9. material warnings, objections, assumptions, or accepted risks when present.

Do not conflate the content verdict with tracker status. A specification can be
content-ready while its task remains blocked by an upstream dependency.

## Determine the next action

Use the configured work graph, hierarchy, dependency evidence, and current
tracker state. Never infer the next task from numbering alone.

- Name the next exact Task ID and title when one task should proceed next.
- List multiple tasks when they are genuinely unblocked and may run in
  parallel.
- State the missing gate when specification or implementation cannot proceed.
- Say that this is the final planned task when the configured Epic or plan has
  no remaining work.
- Say that the next task is not established when canonical evidence does not
  define one; do not invent it.

Recommend the project-configured implementation command with the exact task
anchor only when the content verdict is `Ready for implementation` and all
operational prerequisites and dependency gates are currently satisfied. When
content is ready but operational work is blocked, name the missing gate and
recommend the action that clears it. Do not start implementation automatically.

## Suggested presentation

```text
Task: <TASK-ID or exact project-local anchor> — <full title>
Issue: <URL or explicit unavailable state>
Spec: <entrypoint and annexes>
Repositories: <one or more owners>

Content verdict: <Draft spec | Spec ready | Ready for implementation>
Project status: <configured status or pending/unavailable>

Expected outcome:
<one short observable result>

Next:
<exact task, parallel tasks, missing gate, or final-task statement>

Warnings:
<only material items; omit the section when none exist>
```
