# Project topology

Use this compact index to resolve the owning component and its canonical
sources before reading repository or domain context. Keep architecture detail,
commands, task state, and history in the linked owners.

## Component index

| Key | Purpose | Type | Lifecycle | Local path | Remote repository | Stack / package manager | Entry point | Task scope | Owner | Deploy boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{{TOPOLOGY_COMPONENT_ROWS}}

## Context routing

| Component | Instructions | Architecture | Context / memory | Operational runbook |
| --- | --- | --- | --- | --- |
{{TOPOLOGY_CONTEXT_ROWS}}

## Dependency edges

| From | Relationship or shared contract | To |
| --- | --- | --- |
{{TOPOLOGY_DEPENDENCY_ROWS}}

Use stable component keys. Write `unknown` when setup could not safely establish
a material fact and `not_applicable` when a field does not apply. Update this
map only for structural changes such as a component addition, removal, rename,
lifecycle or ownership change, route change, dependency change, or deploy
boundary change.
