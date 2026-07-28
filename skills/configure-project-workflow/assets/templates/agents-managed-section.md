<!-- marshall-ai-agent:start -->
## Reusable project workflow

Project configuration:

- `{{PROJECT_WORKFLOW_CONFIG_PATH}}`

Active workflow modules:

{{ACTIVE_SKILL_ROUTES}}

Plain-text command catalog:

- `{{AGENT_COMMANDS_PATH}}`

Before acting on an alias or equivalent natural-language request, resolve
sticky conversation constraints, capability, current workflow phase, and
prerequisites through `commands.authority_resolution`,
`commands.session_profiles`, and `commands.sequence_guard` in
`{{PROJECT_WORKFLOW_CONFIG_PATH}}` and the command catalog. On a mismatch, stop
before mutations and recommend the exact next alias or action.

Aliases do not expand the authority defined by their owning skills or project policy.

## Project safety and engineering invariants

{{PROJECT_INVARIANTS}}
<!-- marshall-ai-agent:end -->
