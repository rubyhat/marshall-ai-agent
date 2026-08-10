# Publish a reviewed planning change

Publish only after the exact current spec head has a clean independent review.

## Prepare the commit

1. Rerun configured spec, link, schema, and documentation checks.
2. Confirm the diff still matches the approved publication manifest.
3. If clean review targeted a local correction checkpoint, verify that the
   provisional target content verdict is already stored in that commit and
   that both HEAD and the worktree remain unchanged. Do not apply any
   post-review verdict or package mutation. Reuse that exact reviewed
   checkpoint for publication.
4. If step 3 fails, invalidate the candidate clean review
   and stop rather than mutating or publishing an unreviewed checkpoint.
5. For an uncommitted-review path, require that `write-task-spec` already
   materialized provisional `Ready for implementation` before the reviewed
   manifest was computed. Reread every artifact and invalidate CLEAN if any
   byte differs.
6. When there is no reviewed checkpoint to reuse, stage only explicit paths;
   do not use a broad add when other changes exist, then create an intentional
   planning/spec commit using project conventions.

After commit, resolve the exact PR-head revision and tree OID and rebuild the
complete sorted publication-package path/mode/blob-OID manifest. Bind the candidate
clean-review record by its target kind. For a reviewed local correction
checkpoint, require the PR-head revision and tree OID to equal
the reviewed checkpoint exactly and record only
`direct_committed_base_diff`; path/mode/blob-OID equivalence alone is insufficient.
For an uncommitted-review candidate, bind evidence to the eventual commit only
when the complete manifest has exact path/mode/OID equality, including every
blob OID and every base-relative `deleted:<base-mode>` and
`deleted:<base-blob-oid>` marker, and record
`verified_uncommitted_manifest_equivalence`. If the
required revision, tree, identity, path set, mode, or any blob OID differs
before the pull request is created, invalidate the candidate and run a fresh
independent review for the new exact head before the initial push. After the
pull request exists, never use this pre-PR rebinding rule for a routine GitHub
correction; follow
[verify-post-pr-planning-correction.md](verify-post-pr-planning-correction.md)
and defer independent evidence selection until its final zero-or-one gate after
the clean GitHub generation.

Do not include generated application output, implementation code, unrelated
memory, or a release-version mutation.

A local correction checkpoint is only a way to present a complete, clean,
already committed planning diff to the reviewer. It must contain only the exact
manifest including any required content-verdict update, must remain unpushed
until clean review, and gains publication evidence only through the same
exact-head and path/mode/OID binding as any other reviewed commit. Once clean, do
not amend, replace, or add a commit before pushing that exact checkpoint.

## Push and create the pull request

- Push the exact branch without force.
- Create or reuse one pull request for the exact task specification.
- Verify head repository, head branch, base repository, target branch, and
  current head SHA.
- Link the task without closing the implementation Issue.
- Describe the shaped outcome, changed planning artifacts, independent review,
  validation, and implementation gate in the configured language.
- Read back the pull request after creation or update.

Stop at the pull-request endpoint when the user's request is narrower than full
publication.

## Respect checks and merge authority

- For full publication, start the configured head-bound GitHub review
  generation for the exact complete initial pull-request head. Do not enter
  merge gates until that head, or a later corrected exact head, has a clean
  generation and passes the conditional final-evidence gate.
- Never bypass branch protection or a reported required check.
- Treat missing, pending, or failed checks according to configured project
  policy; do not invent success.
- After a content-changing PR update, invalidate prior current evidence and use
  the deterministic routine-package gate plus the next full-head GitHub
  generation. Do not run independent review between GitHub packages.
- After a clean GitHub generation, apply the conditional zero-or-one final
  evidence gate in
  [verify-post-pr-planning-correction.md](verify-post-pr-planning-correction.md).
- Reuse prior independent evidence only when exact current head, tree, and
  complete manifest binding remain valid; otherwise run the canonical runner
  once against the current committed head.
- Preserve the bound reviewed-head revision, tree OID, package manifest, clean
  verdict, capture-contract revision, publication-attempt ID, normalized-result
  hash, complete matched-session set, and reviewer-run identity for the final
  exact-task record.
- Merge only the exact evidence-bound head after its clean full-head GitHub
  generation when user and project authority allow it.
- Never force-push, merge an unrelated PR, publish a release, deploy, or mutate
  production as part of this workflow.

An open or approved pull request is not yet canonical publication.
