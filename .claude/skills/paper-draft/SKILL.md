---
name: paper-draft
description: "Draft or revise prose in this thesis repo (paper.qmd, projects/*/blueprint.md, projects/*/design.md, projects/*/implementation-report.md). Use when the user asks to draft, write, revise, rewrite, expand, tighten, polish, or edit manuscript or project-design prose. Enforces the thesis writing constraints and source-of-truth file map."
allowed-tools: [Read, Edit, Write, Grep, Glob, Bash]
context: inherit
---

# paper-draft: drafting for the decentralized-curation manuscript

## When to use
Trigger when the user asks to draft, write, revise, rewrite, expand, tighten, polish, or edit prose in:
- `paper.qmd` (editable master paper source)
- `projects/truth-post/blueprint.md` (canonical Truth Post design doc)
- `projects/truth-post/implementation-report.md` (Truth Post deployment retrospective)
- `projects/rpgf/design.md` (canonical RPGF design doc)
- `literature/*.md` (internal working notes on foundational works)

Do **not** trigger for edits to `truth-post/` or `rpgf/` at the repo root: those are publish-route wrappers, not canonical content sources.

## Delegate methodology to
`claude-scientific-writer:scientific-writing` for IMRAD structure, paragraph-flow discipline, and the two-stage (outline then prose) process.

## Project invariants (non-negotiable)
- **Audience:** CS academics and engineers. Write with precise definitions and causal chains.
- **Tone:** Direct, non-poetic, high signal. No hedging without justification.
- **Stats:** Avoid fragile statistics and news-cycle overfitting in "problem" pieces unless the user explicitly requests them.
- **Versioning:** Never refer to older versions of this manuscript.
- **Date handling:** Do not assume "today's date" inside the manuscript. For any date-sensitive claim, verify against the user-memory `currentDate` field or ask the user first.
- **Never edit** anything under `context/`: it is read-only source material.
- **"Formatting only" rule:** If the user asks for formatting-only changes, keep wording unchanged and only add Markdown structure or whitespace.

## Output shape
Full paragraphs with flowing prose; never bullet points in final manuscript output. Cite via BibTeX keys resolvable in `references.bib` (see the `paper-refs` skill for citation management).
