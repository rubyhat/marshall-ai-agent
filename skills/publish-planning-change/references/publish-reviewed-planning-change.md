# Publish a reviewed planning change

Publish only after the exact current spec head has a clean independent review.

## Prepare the commit

1. Rerun configured spec, link, schema, and documentation checks.
2. Confirm the diff still matches the approved publication manifest.
3. Ask `write-task-spec` to assign the highest supported content verdict for
   the reviewed head.
4. Reread every changed artifact after the verdict update.
5. If the verdict update changes a tracked artifact, run the configured bounded
   independent review against that resulting exact head. Do not publish a head
   that differs from the clean-review evidence.
6. Stage only explicit paths. Do not use a broad add when other changes exist.
7. Create an intentional planning/spec commit using project conventions.

After commit, resolve the exact PR-head revision and tree OID and rebuild the
complete sorted publication-package path/blob-OID manifest. Bind the candidate
clean-review record to that head only when the manifest exactly equals the one
seen by the reviewer; require exact path/OID equality. Record whether binding
was a direct committed-base-diff
review or verified uncommitted-manifest equivalence. If identity, path set, or
any blob OID differs, invalidate the candidate and run a fresh independent
review for the new exact head before push or merge.

Do not include generated application output, implementation code, unrelated
memory, or a release-version mutation.

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
