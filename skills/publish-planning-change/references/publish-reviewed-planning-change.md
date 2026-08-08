# Publish a reviewed planning change

Publish only after the exact current spec head has a clean independent review.

## Prepare the commit

1. Rerun configured spec, link, schema, and documentation checks.
2. Confirm the diff still matches the approved publication manifest.
3. If clean review targeted a local correction checkpoint, verify that the
   highest supported content verdict is already stored in that commit and that
   both HEAD and the worktree remain unchanged. Do not apply a post-review
   verdict mutation. Reuse that exact reviewed checkpoint for publication.
4. If a clean checkpoint review explicitly authorizes a higher verdict that is
   not stored yet, let `write-task-spec` apply only that verdict mutation from
   the clean handoff. Rerun checks, create a replacement local checkpoint, and
   obtain clean review for the replacement before publication. This mechanical
   promotion does not consume a correction round.
5. If step 3 fails for any other reason, invalidate the candidate clean review
   and stop rather than mutating or publishing an unreviewed checkpoint.
6. For an uncommitted-review path that did not use a local correction
   checkpoint, ask
   `write-task-spec` to assign the highest supported content verdict, then
   reread every changed artifact.
7. If the verdict update in step 6 changes a tracked artifact, run the
   configured bounded independent review against that resulting exact head. Do
   not publish a head that differs from the clean-review evidence.
8. When there is no reviewed checkpoint to reuse, stage only explicit paths;
   do not use a broad add when other changes exist, then create an intentional
   planning/spec commit using project conventions.

After commit, resolve the exact PR-head revision and tree OID and rebuild the
complete sorted publication-package path/blob-OID manifest. Bind the candidate
clean-review record by its target kind. For a reviewed local correction
checkpoint, require the PR-head revision and tree OID to equal
the reviewed checkpoint exactly and record only
`direct_committed_base_diff`; path/blob-OID equivalence alone is insufficient.
For an uncommitted-review candidate, bind evidence to the eventual commit only
when the complete manifest has exact path/OID equality, including every blob
OID, and record `verified_uncommitted_manifest_equivalence`. If the
required revision, tree,
identity, path set, or any blob OID differs, invalidate the candidate and run a
fresh independent review for the new exact head before push or merge.

Do not include generated application output, implementation code, unrelated
memory, or a release-version mutation.

A local correction checkpoint is only a way to present a complete, clean,
already committed planning diff to the reviewer. It must contain only the exact
manifest including any required content-verdict update, must remain unpushed
until clean review, and gains publication evidence only through the same
exact-head and path/OID binding as any other reviewed commit. Once clean, do
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

- Never bypass branch protection or a reported required check.
- Treat missing, pending, or failed checks according to configured project
  policy; do not invent success.
- Re-review the exact current head after a content-changing PR update.
- Preserve the bound reviewed-head revision, tree OID, package manifest, clean
  verdict, and reviewer-run identity for the final exact-task record.
- Merge only the exact reviewed head when user and project authority allow it.
- Never force-push, merge an unrelated PR, publish a release, deploy, or mutate
  production as part of this workflow.

An open or approved pull request is not yet canonical publication.
