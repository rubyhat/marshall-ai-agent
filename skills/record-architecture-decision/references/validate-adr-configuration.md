# Validate ADR Configuration

Validate the configured convention and the exact rendered artifacts before any
ADR mutation. Keep this gate bounded; do not build a general-purpose regex,
template, Markdown, or filesystem portability validator.

## Validate the configured convention

- Require a project-relative ADR root with no absolute prefix, drive designator,
  `.` or `..` segment, or trailing separator.
- Require a project-relative Markdown index path with the same containment
  restrictions and a filename rather than a directory destination. Require the
  index to resolve inside the ADR root and reject an index basename whose stem
  can match the configured ADR ID pattern.
- Accept only a fixed-width decimal ID regex with an optional filename-safe
  prefix, such as `ADR-[0-9]{4}` or `[0-9]{4}`. Require one to nine digits and
  reject any other regex syntax.
- Require the exact core filename pattern `<ID>.md`. Do not accept additional
  placeholders, path separators, fixed filenames, or repeated ID slots.
- Trim every status label, materiality policy, review trigger, required section,
  and authority value. Reject blank values.
- Require exactly the portable semantic states `proposed`, `accepted`,
  `rejected`, `deprecated`, and `superseded`. Require their normalized project
  labels to be pairwise distinct.
- Require explicit non-blank authority for proposal, acceptance, rejection,
  clarification, deprecation, and supersession.
- Require writer coordination to select one exact project-supported
  `exclusive_lock` or `atomic_compare_and_swap` protocol, scope it to
  `all_affected_adrs_and_index`, and stop before writing on contention or an
  unavailable precondition. Require release on every path and safe rollback or
  an explicit inconsistent-state result after partial failure.

If an existing project uses another identifier or filename convention, stop
and route it to an explicit workflow-kit configuration change. Do not silently
weaken this core contract during ADR recording.

## Validate the concrete mutation

Treat every affected ADR file, the ID allocation, and the index as one logical
mutation. Do not use independent per-file compare-and-swap calls or a
check-then-write sequence.

Prepare the approved mutation without holding a writer guard:

1. Allocate or resolve one candidate ADR ID without writing and require a full
   match against the configured ID pattern.
2. Require the concrete ID to contain only ASCII letters, digits, hyphen, and
   underscore; reject separators, dot segments, drive designators, control
   characters, and empty values.
3. Render `<ID>.md` once and resolve every lexical and real destination under
   the configured ADR root.
4. Stop if a rendered path escapes the ADR root, crosses an existing symlink
   boundary, equals the index path, makes any affected ADR file or the index an
   ancestor of another artifact, or targets an existing different ADR.
5. Require the index path to remain a file destination and the ADR root to
   remain a directory destination. Build the exact affected-artifact set and
   include an index write only when its approved content changes.
6. Show that exact preview and obtain any required confirmation. Never hold an
   exclusive writer guard while waiting for user input.

After approval and immediately before persistence:

7. Acquire the configured exclusive writer guard over the ADR namespace, every
   affected ADR file, and the index; or begin the configured whole-mutation
   transaction or compare-and-swap precondition over the same scope.
8. Under that coordination, reread the namespace, target identities, current
   ADRs, index, paths, symlinks, and collisions. Rebuild the exact mutation. If
   any approved destination or content changes, release or abort coordination,
   show a renewed preview, and obtain confirmation again.
9. Reserve a new ID only after revalidation, using exclusive-create semantics
   under the guard or an absent-target precondition inside the transaction.
10. Persist every approved affected ADR file and write the index only when its
    approved content changes. Keep the unchanged index inside the guard or
    whole-mutation precondition and post-write verification scope.
11. For a transactional or compare-and-swap strategy, commit the complete
    affected artifact set together and abort when its precondition changes.
    Reread every persisted ADR and the index and verify exact identities and
    lifecycle states before reporting success.
12. Use finally-style cleanup to release an exclusive guard on success, a
    validation stop, or a persistence error. Abort an uncommitted transaction
    on every error. After a partial non-transactional write, roll back the exact
    mutation only when the configured protocol proves that safe; otherwise
    report inconsistent state, block downstream reliance, and do not claim
    success.

Do not overwrite an existing ADR merely because its path matches the rendered
filename. Resolve identity first and use clarification, deprecation, or
supersession only through the owning lifecycle mode.
