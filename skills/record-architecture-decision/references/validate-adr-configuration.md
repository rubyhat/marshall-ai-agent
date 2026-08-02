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

If an existing project uses another identifier or filename convention, stop
and route it to an explicit workflow-kit configuration change. Do not silently
weaken this core contract during ADR recording.

## Validate the concrete mutation

1. Allocate or resolve one exact ADR ID and require a full match against the
   configured ID pattern.
2. Require the concrete ID to contain only ASCII letters, digits, hyphen, and
   underscore; reject separators, dot segments, drive designators, control
   characters, and empty values.
3. Render `<ID>.md` once and resolve the lexical and real destination under the
   configured ADR root.
4. Stop if the rendered path escapes the ADR root, crosses an existing symlink
   boundary, equals the index path, makes either file artifact an ancestor of
   the other, or targets an existing different ADR.
5. Require the index path to remain a file destination and the ADR root to
   remain a directory destination.
6. Recheck the path, symlink, collision, and ADR identity conditions immediately
   before persistence, especially after any preview or confirmation pause.
7. Recheck the same destinations after persistence and before reporting
   success.

Do not overwrite an existing ADR merely because its path matches the rendered
filename. Resolve identity first and use clarification, deprecation, or
supersession only through the owning lifecycle mode.
