---
name: paper-slides
description: "Build talk slide decks or talk scripts for the thesis. Use when the user asks to create a presentation, build slides, draft a talk, or prepare a deck from manuscript or project content."
allowed-tools: [Read, Write, Edit, Bash, Agent]
context: inherit
---

# paper-slides: presentations for the decentralized-curation manuscript

## When to use
Trigger when the user asks to create, build, draft, or prepare a presentation, slide deck, or talk script derived from `paper.qmd`, `projects/*/blueprint.md`, or `projects/*/design.md`.

## Delegate methodology to
`claude-scientific-writer:scientific-slides` for slide design, AI-assisted slide generation, and visual validation.

## Project file conventions
- **Presentation materials live under `talks/`.** This directory is **outside** the Quarto render pipeline (see the `Source of truth` section of `CLAUDE.md`); do not wire decks into `_quarto.yml`.
- Binaries and exports (`talks/*.pdf`, `talks/slides/`, `talks/march10-presentation/`) are gitignored; commit only source files (scripts, Markdown, reveal.js config, and similar).

## Project invariants
- **Audience:** CS academics and engineers. Same calibration as the manuscript.
- **Tone:** Direct, non-poetic, high signal. No hedging without justification. Same calibration as the manuscript.
- **Versioning:** Never refer to older versions of the manuscript from a talk.
- **Stats:** Same fragility caution as the manuscript: avoid brittle headline statistics unless the talk context explicitly calls for them.

## Output shape
Either a new file under `talks/` (source format matching existing talks in that directory) or a patch to an existing talk. Include a per-slide speaker-notes section so the deck stands alone when the user is not in the room.
