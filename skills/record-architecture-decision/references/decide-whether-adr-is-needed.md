# Decide whether an ADR is needed

Use this reference before creating a decision record.

## Create an ADR for a material choice

Prefer an ADR when several of these are true:

- the decision changes a long-lived system, repository, service, data, API,
  security, deployment, or ownership boundary;
- more than one viable option has materially different consequences;
- reversal would be expensive, risky, or require migration;
- the decision affects multiple tasks, repositories, deployables, or teams;
- future work is likely to ask why the constraint exists;
- the choice changes compatibility, reliability, scalability, privacy,
  tenancy, authorization, observability, recovery, or operational posture;
- an existing accepted ADR may need to be replaced;
- forgetting the rationale would make a future change materially less safe.

Project policy may require an ADR for additional domains. Apply those triggers
without turning every implementation choice into a decision record.

## Do not create an ADR by default

Use another owner for:

- current architecture with no decision rationale: architecture documentation;
- exact implementation scope and acceptance behavior: task specification;
- current task status and priority: Issue or Project;
- a verified repeatable sequence: runbook;
- a compact current fact or gotcha: canonical memory;
- an unresolved product choice: shaping state;
- a temporary workaround: known issue or bounded exception with owner and
  expiry, unless the workaround itself changes architecture materially;
- a local, reversible, unsurprising implementation detail.

Do not create an ADR merely because work was important or completed.

## Check recoverability and ownership

Before creating:

1. search the configured ADR index and exact decision terms;
2. identify whether an existing ADR already owns the rationale;
3. distinguish a new decision from a clarification or supersession;
4. confirm that code, architecture, specs, or a runbook does not already own the
   requested information in a different form;
5. create only one record for one decision question.

When the decision is still too broad, split it into independently reviewable
choices only if they have distinct drivers and consequences. Do not fragment a
single coupled trade-off into several records merely to keep files short.
