# Project context map

Read only the routes relevant to the current task.

| Context | Canonical source | When to read |
| --- | --- | --- |
| Project topology | `{{PROJECT_TOPOLOGY_PATH}}` | Before selecting an owning component, repository, architecture, or runbook |
| Project model | `{{PROJECT_CONTEXT_PATH}}` | When the task depends on product or repository scope |
| Engineering rules | `{{ENGINEERING_RULES_PATH}}` | Before architecture, implementation, or review decisions |
| Active task state | `{{ACTIVE_TASK_NOTES_ROOT}}` | Only for the exact active task |

Historical or archived context is not part of default loading.
