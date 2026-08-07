# Select Workflow Modules

Use `assets/workflow-modules.json` as the machine-readable module catalog.

## Recommend a profile

- `full_product`: long-lived product development with context, roadmap, specifications, implementation, delivery, frontend, QA, and external references.
- `core_development`: context, shaping, specifications, implementation, and delivery without domain-specific modules.
- `product_discovery`: context, shaping, frontend interaction design, and product-reference analysis.
- `context_only`: context loading, recording, and manual maintenance.
- `custom`: exact user-selected modules.

Treat profiles as recommendations, not permission to install.

## Resolve applicability

Base selection on:

- project type and lifecycle;
- actual repositories and surfaces;
- operational tracker availability;
- whether project documentation should persist;
- implementation and delivery needs;
- frontend, QA, or reference-analysis work;
- user restrictions and existing workflows.

Do not install a domain module only because a framework is detected.

## Enforce dependencies

For each selected module:

1. add its required dependencies;
2. explain recommended integrations separately;
3. reject an impossible dependency under current safety or provider policy;
4. record why every optional module is selected or skipped;
5. enable a `conditional_aliases` entry only when all of its listed modules are
   selected; otherwise suppress that alias without disabling the owning module;
6. if the user explicitly selects a conditional alias, add its required modules
   or report why the requested command cannot be enabled;
7. store the exact enabled command set in setup state as
   `modules.enabled_aliases`;
8. store each selected optional cross-skill capability in
   `modules.enabled_capabilities`, add every module required by its catalog
   entry, and report any impossible dependency;
9. validate uniqueness across aliases and capabilities.

Removing a module disables its routing and configuration only. Do not delete its existing task specs, memory, references, Issues, or historical artifacts automatically.

## Present the decision

Show:

- recommended profile and evidence;
- selected modules;
- automatically required dependencies;
- optional modules and trade-offs;
- skipped modules and reasons;
- unsupported provider or environment gaps;
- configuration stages activated by the selection.
