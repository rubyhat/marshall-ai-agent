# Run independent specification review

Use a fresh read-only reviewer for the exact current specification head.

## Preserve reviewer independence

Do not give the reviewer the planning discussion transcript, the author's
private reasoning, expected findings, or intended verdict. Provide only:

- the exact task and tracker anchor;
- the agreed shaped outcome, scope, non-goals, and dependencies;
- the complete spec package and diff against the canonical base;
- applicable project instructions, architecture, code, contracts, and tests;
- the configured review rubric and stop conditions.

Use the configured model and effort. Keep reusable instructions model-neutral.
Before launch, require that the owning workflow's current-schema pre-mutation
gate has passed and that the reviewer worktree, placeholder, branch-readback,
and bound-review fields are materialized and valid. Do not apply compatibility
defaults inside the publication lifecycle; invalid configuration must already
have stopped direct publication.
Set the reviewer process working directory to the exact planning worktree
before starting an uncommitted review. Do not rely on the checkout from which
the publication alias was invoked, a path added only for read access, or prompt
text to select the reviewed diff. Verify the reviewer reports the expected
planning worktree and branch before accepting its verdict.

Invoke only the configured canonical runner at
`scripts/run_codex_spec_review.py` through the materialized command template.
The runner owns the `codex review` subprocess, direct startup-stream capture,
outer parent-session binding, child-session discovery, terminal settlement,
strict native-result validation, consolidation, metrics, and normalized result
hash. A stored command that directly launches `codex review`, a missing
placeholder, or a partial result-capture contract is invalid configuration and
must stop before model invocation.

The runner must inject the exact task anchor, selected target identity and
manifest paths, and the specification-contract rubric as model-visible
developer instructions while retaining the CLI's explicit Git target selector.
Select `--uncommitted` for an uncommitted target and `--base <revision>` for a
committed target; never substitute one selector for the other.
`--title` is diagnostic display text and is never sufficient review context.
Do not replace the target selector with a positional custom prompt: current
Codex CLI treats those modes as mutually exclusive.

Outer stdout, stderr, and process exit status are diagnostic only. Accept
review correctness solely from strict JSON in
`event_msg.task_complete.payload.last_agent_message` of a child whose exact
parent session, `source.subagent == review`, cwd, invocation boundary, target,
and manifest are bound by the runner.
Persist only bounded stream diagnostics in the normalized result: exit code,
byte length, and SHA-256 for stdout and stderr. Do not copy stream content into
review evidence or derive a verdict from those diagnostics.
Bound every reviewer subprocess with the configured invocation timeout. On
expiry, kill and reap the subprocess, return `review_invocation_timeout`, and
do not launch a technical retry. Include the exact planning branch in the
pre/post target-state fingerprint so a same-HEAD branch switch is
`target_changed` rather than CLEAN. Materialize the invocation timeout as 900
seconds by default and validate `0 < timeout <= 3600` before model invocation.

The runner prints exactly one normalized JSON object for a recognized result.
Its `review_target` serializes the complete sorted path/mode/blob-OID manifest
alongside the manifest fingerprint so publication evidence never has to
recapture mutable worktree state. The runner uses this exit mapping:
`clean` → `0`, `non_clean` → `10`,
`terminal_contract_error` → `11`, `target_changed` → `12`,
`invocation_binding_error` → `13`, `technical_retry_budget_exhausted` → `14`,
`session_settlement_timeout` → `15`, and the internal settled
`no_authoritative_terminal_result` state → `16`, and
`review_invocation_timeout` → `17`. Invalid runtime configuration stops before
model invocation with exit code `64` and stderr diagnostics.
If the post-review target can no longer be snapshotted, normalize that failure
as `target_changed` with bounded diagnostics; it is not a new pre-invocation
configuration error.

## Review the specification contract

Check for concrete defects in:

- task identity, outcome, scope, and non-goals;
- consistency with the Issue, roadmap, architecture, and current code;
- requirements, permissions, states, errors, recovery, and lifecycle behavior;
- API, data, migration, compatibility, rollout, privacy, security, billing,
  localization, accessibility, observability, or operations when applicable;
- dependency ordering and cross-repository ownership;
- acceptance-criteria coverage and actionable verification;
- invented technical detail, hidden blockers, or an oversized task.

Do not request general improvements, stylistic rewrites, speculative edge cases
without a credible current-task risk, or work assigned to another task.

## Classify and handle findings

Classify each finding as:

- `blocking`: implementation would be unsafe, ambiguous, or materially wrong;
- `actionable`: a bounded current-spec correction is required;
- `non_blocking`: useful but not required for this task;
- `out_of_scope_or_unsubstantiated`: unsupported or intentionally deferred.

Verify findings against primary sources before editing. Use `write-task-spec`
for an in-scope content correction. Return a material product, architecture,
scope, or decomposition change to `shape-project-work`.

## Enforce the correction-round budget

At the beginning of one new uninterrupted publication attempt:

1. read the configured positive `max_correction_rounds`;
2. set the in-process `correction_rounds_used` counter to zero;
3. retain the ordered review results and correction packages for the attempt.

One correction round is one bounded package of changes made in response to one
non-clean review. Multiple findings corrected together consume one round; a
finding, file, deterministic check, or clean review does not consume a round by
itself. After applying a correction package, increment the counter exactly once,
rerun affected checks, and request review of the new exact head. The corrected
head produced by the final allowed round still receives that review.

When a correction package after a non-clean review changes a publication
manifest that already has an in-scope commit on the planning branch, require the
materialized `committed_correction_review` configuration. Under the supported
`local_checkpoint_committed_base_diff` strategy, require explicit permission
for the checkpoint. Apply every in-scope correction while preserving the
provisional `Ready for implementation` target verdict. Reread the exact package
and rerun deterministic checks.

Before staging, require that the planning worktree contains no dirty path
excluded from the exact publication manifest. If an unrelated edit remains,
stop before the checkpoint and return an exact path-by-path
preservation/recovery handoff. Do not stash, delete, overwrite, or include that
edit merely to obtain a clean worktree. After the excluded paths are safely
absent from this planning worktree, stage only the exact publication manifest.
Create one local-only correction checkpoint commit before review. Verify the
worktree is then clean and the reviewer sees that exact checkpoint head against
the canonical base.
The configured push policy must remain false until clean review. The checkpoint
does not count as a second correction round or as clean-review evidence.
Missing or incomplete strategy fields stop direct publication before the first
checkpoint instead of authorizing a partial review.

Keep the exact uncommitted-review path only when the manifest has no in-scope
commit relative to the canonical base. Reject a mixed
committed-plus-uncommitted candidate before model invocation because
`codex review --uncommitted` omits its committed portion. Create an authorized
clean checkpoint and review the complete candidate with `--base <revision>`.
Evidence for a purely uncommitted candidate becomes publishable only after the
eventual committed head has the identical complete path/mode/blob-OID manifest;
it uses the separately configured
`verified_uncommitted_manifest_equivalence` binding method.

Represent a tracked path deleted relative to the canonical base as
mode `deleted:<base-mode>` plus blob OID `deleted:<base-blob-oid>` in the sorted
manifest. Use the same base-relative representation when checking the eventual
commit and merged revision so a deletion is reviewed, cannot disappear from
evidence, and remains distinct from an empty file. A rename contains both the
new path/mode/blob OID and the deleted source markers.

One clean review for the current head is terminal. Do not keep requesting review
for an unchanged clean specification. If the final allowed corrected head still
has a blocking or actionable finding, stop before any further correction,
review request, commit, push, or publication. Do not start a sixth correction
when `max_correction_rounds` is five.

## Settle and consolidate authoritative results

Before any CLEAN, NON_CLEAN, or missing-result decision:

1. require every registered review subprocess to exit;
2. resolve exactly one outer JSONL session from the directly captured startup
   session UUID and verify its `session_meta` ID, `source == exec`, exact cwd,
   and invocation boundary;
3. match only review children with that parent UUID, exact cwd and target;
4. require every matched child to reach terminal `task_complete`;
5. obtain at least two consecutive stable scans with the configured bounded
   interval and no new or changed matched JSONL artifact;
6. perform one final rescan immediately before returning a status.

A new or changed artifact resets the stable-scan count. A matched child without
terminal `task_complete`, a non-terminal outer session, or a deadline reached
before quiescence returns `session_settlement_timeout`; it is not equivalent to
an absent result.

Strict-parse every matched terminal message as native Codex review JSON.
Require `findings`, supported `overall_correctness`, non-empty
`overall_explanation`, and numeric `overall_confidence_score` in `0..1`.
Require every finding's title, body, confidence, and bounded location; accept
missing or null native priority but reject an out-of-range priority. An
incorrect verdict with no findings (`incorrect_without_findings`), fenced JSON,
missing required fields, or
another invalid terminal shape returns `terminal_contract_error` with stable
error code and exact session/event identity. It does not consume a correction
round and does not permit retry.

Union every valid finding across all invocations of the same stable manifest,
normalize its worktree-relative location, and deduplicate it by a deterministic
SHA-256 fingerprint. A finding from an earlier or late initial invocation makes
the consolidated result NON_CLEAN even when another terminal result is clean.
Only a settled result set with no findings and correct terminal results is
CLEAN.

Permit one technical retry only when settlement and final rescan return
`no_authoritative_terminal_result`. Keep the original publication attempt and
its invocation/session set. After the retry, rescan both invocations so a late
initial result is consolidated. A second miss returns
`technical_retry_budget_exhausted`; binding errors, terminal-contract errors,
target changes, and settlement timeouts never start another model invocation.

Report a bounded cycle analysis containing the reviewed heads, finding
fingerprints and classifications, correction packages, still-open findings,
and the reason the cycle persists. Return a material scope or outcome problem
to planning; otherwise stop for an explicit user decision.

Resume the same attempt only when the exact counter and ordered review/correction
history are provable from the retained conversation state. If an interruption
or resumed session makes either uncertain, fail closed: do not reset the counter
or continue automatically. Require an explicit user decision before starting a
new publication attempt. This limit does not require or authorize persistent
runtime state files, locks, archives, migrations, or a crash-recovery protocol.

Report the clean-review evidence without copying the full review transcript
into the specification.

## Capture a bindable clean-review record

Before accepting a clean verdict, capture a bounded durable candidate record:

- review capture-contract revision, publication-attempt ID, normalized-result SHA-256,
  complete matched reviewer session/event set, model, effort,
  completion time, cumulative token usage, technical-retry usage, settlement
  evidence, and terminal clean verdict;
- review target kind, canonical base revision, planning worktree, branch, and
  the reviewed commit when the target was already committed;
- the complete sorted publication-package manifest with every allowed
  project-relative path, Git mode, and content blob OID.

Do not treat model and effort alone, a PR-description claim, or an unbound
verdict as review evidence. A full private reasoning transcript is neither
required nor copied into the specification. When the clean review targeted
uncommitted content, keep the manifest as candidate evidence; the publication
workflow must bind it to the eventual committed PR head by exact path/mode/OID
equality before merge. Any manifest change invalidates the clean verdict and
requires a fresh review.
