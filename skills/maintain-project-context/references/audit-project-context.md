# Audit project context

Use this runbook for phase 1 only. The output is evidence for review, not authorization to change files.

## Select scope

1. Use the scope explicitly named by the user.
2. If the request is `--context-audit` without arguments, use the configured internal-memory and project-documentation roots.
3. Gather metadata across those roots.
4. Resolve every configured reference-bearing root that can link to context
   artifacts. Scan it only for incoming-link evidence; do not add files outside
   the selected scope to candidate, size, age, duplicate, or broken-link results.
5. Inspect file contents only for bounded candidate classification and link
   evidence.
6. Do not follow symlinks or expand into repositories, dependency trees, build
   outputs, secret-like files, or archives outside the selected scope and
   declared reference roots.

For a very broad project, audit one logical layer at a time when that produces a clearer report. Say which configured roots were not included.

## Run the standard-library audit

From the skill directory, run:

```bash
python3 scripts/audit_project_context.py \
  --root <workspace> \
  --scope <scope-one> \
  --scope <scope-two> \
  --reference-root <configured-reference-root> \
  --active-root <active-root> \
  --canonical <canonical-file-or-directory> \
  --protected <protected-file-or-directory> \
  --historical-root <historical-root> \
  --archive-root <archive-root> \
  --task-id-regex <configured-validation-regex> \
  --include-content-signals \
  --include-git-state \
  --format text
```

Useful optional flags:

- `--format json` for structured stdout;
- `--age-buckets 30,90,180` for display buckets;
- `--top 20` for largest-file and duplicate summaries;
- `--candidate-limit 50`, or `0` for all detected candidates;
- repeatable `--exclude-dir <name>` for project-specific generated directories.
- repeatable `--reference-root <path>` for all configured maps, canonical
  context, runbooks, and other context roots that can link to an audit
  candidate while remaining outside the candidate scope;
- `--task-id-regex <regex>` to enable Task-ID counts and chronology signals
  through the project's configured validation pattern; without it those
  metrics remain empty rather than guessing from hyphenated words.

Numbers are report controls and discovery filters, not retention thresholds.

The script reports:

- file and byte totals;
- optional line totals and bounded content signals;
- heading counts, task-linked heading counts, largest section size, and
  lifecycle-mixing signals for text artifacts;
- age distribution;
- largest files;
- location-state hints;
- exact-content duplicate groups;
- possible broken Markdown references;
- incoming-link coverage status and counts from sources outside the candidate
  scope; without declared reference roots, counts are explicitly marked
  `scoped_only_incomplete`;
- Git state when available;
- candidate signals without printing file contents.

The script never moves, edits, archives, or deletes files.

## Fallback for macOS/Linux

If Python 3.9+ is unavailable, use bounded read-only commands against explicit scopes:

```bash
find <scope> -type f -print
du -sh <scope>
find <scope> -type f -exec wc -c {} +
rg -n --glob '*.md' 'TODO|FIXME|BLOCKED|unresolved|superseded' <scope>
git -C <workspace> status --short -- <scope>
git -C <workspace> ls-files -- <scope>
```

Constrain or paginate output before reading large results. Do not use shell pipelines that delete, move, overwrite, or rewrite files.

## Perform semantic review

For each surfaced candidate:

1. Confirm its role and lifecycle.
2. Resolve the canonical owner and any replacement.
3. Check active blockers and unresolved markers in context.
4. Check incoming references, maps, configured paths, and external spec links.
   The script validates only its declared roots and explicitly does not compare
   them with project configuration. Do not treat zero incoming links as manifest
   evidence unless the report's exact root list matches the configuration,
   coverage is complete for those declared roots, and no reference source was
   skipped.
5. Check whether Git provides a committed recovery source.
6. Apply the retention policy classification.

For an oversized canonical artifact, do not assign one action to the whole file
unless its role and content are genuinely uniform. Use
[compact-oversized-canonical-context.md](compact-oversized-canonical-context.md)
to choose one section or domain and prepare a section-level manifest.

Read only candidate files needed for this decision. Do not read all historical notes merely because they share a directory.

## Report and stop

Return:

- audited roots and exclusions;
- aggregate health signals;
- classified candidates with concise evidence;
- protected or dirty items excluded from cleanup;
- broken references;
- uncertainties requiring human judgment;
- the smallest useful next step.

End with an explicit statement that no files were changed. Do not create a repository report unless the user chooses cleanup or explicitly requests a saved report.
