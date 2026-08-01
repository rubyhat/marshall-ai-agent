# Context preflight and targeted search

Use this runbook when candidate context documents are broad, historical, multi-domain, or otherwise likely to contain much more information than the current task needs.

## Apply semantic preflight

Before reading a candidate:

1. State the question the source is expected to answer.
2. Check the file's shape and size.
3. Inspect headings or other structural markers.
4. Search exact anchors and close synonyms.
5. Read the smallest coherent range that includes the evidence and its qualifiers.
6. Decide whether the question is answered.
7. Expand only for a named remaining gap.

Do not use fixed numeric budgets. Judge sufficiency by relevance, authority, and whether the next action is safe and justified.

## Prefer targeted commands

Use `rg` first when available:

```bash
rg --files -g 'AGENTS.md' -g '*.md'
rg -n '^#{1,6} ' path/to/document.md
rg -n -i 'TASK-ID|domain term|component name' path/to/document.md
wc -l -c path/to/document.md
sed -n 'START,ENDp' path/to/document.md
```

Use repository state only when it helps identify the task:

```bash
git branch --show-current
git status --short
git diff --name-only
```

Quote paths and search terms when they contain spaces or shell metacharacters. Use the next best local tool without broadening scope when `rg` is unavailable.

## Control output by purpose

- List filenames before opening file bodies.
- Inspect headings before broad prose.
- Search exact task IDs before general domain words.
- Prefer one coherent range over many disconnected matches.
- Avoid printing entire directories, logs, histories, specs, or memory files.
- Never full-read an oversized or mixed-era canonical artifact when a map,
  heading, exact anchor, or bounded section can answer the question.
- Avoid rereading content already present in the current conversation.
- Summarize evidence instead of repeating source text.

Do not hide a necessary source merely because it is large. Narrow the read to
the relevant section, then widen only if surrounding context changes the
meaning. When section routing is missing, report that context-health gap rather
than compensating with an unbounded read.

## Reassess after each pass

Ask:

- Did the source answer the intended question?
- Is the source current and authoritative?
- Is another source required by a hard project rule?
- Would more reading change the next action?
- Is the remaining uncertainty material?

Stop when additional reading would add background rather than alter the next justified action.
