---
name: paper-refs
description: "Validate, add, or fix BibTeX entries in references.bib. Use when the user asks to check references, validate citations, add a new citation, verify DOIs, or check volume/pages/year fields. references.bib is the single citation source of truth for this repo."
allowed-tools: [Read, Edit, Grep, Glob, WebFetch, Bash]
---

# paper-refs: BibTeX management for the decentralized-curation manuscript

## When to use
Trigger when the user asks to validate references, check a BibTeX entry, find a citation, add a paper to the bibliography, verify a DOI, or fix missing volume / pages / year fields.

## Delegate methodology to
`claude-scientific-writer:citation-management` for BibTeX generation, metadata lookup via Google Scholar / PubMed / DOI resolvers, and entry validation.

## Project invariants
- **`references.bib` is the single source of truth** for citations. Every `@cite` key used in `paper.qmd` or any `projects/*/*.md` must resolve here.
- **`literature/*.md` is NOT a citation source.** Those files are internal working notes on foundational works (Akerlof, Schelling, George, Ostrom, and similar) that inform the paper: they provide context for the model but never substitute for a BibTeX entry. See `literature/README.md` for the index.
- **Minimum fields** for every journal entry: author, title, journal, year, volume, pages, DOI (where available). For books: author / editor, title, year, publisher, ISBN. For preprints: author, title, year, archive prefix, eprint identifier.
- **Avoid outdated / retracted work**; prefer primary sources over review articles when both exist.

## Checks to run before adding an entry
1. Does the cite key collide with an existing key?
2. Is the DOI resolvable?
3. Are volume / issue / pages present for journal articles?
4. Does the entry type match the source (`@article`, `@book`, `@inproceedings`, `@misc`, etc.)?

## Output shape
When adding: print the proposed entry, the location it will be inserted, and any existing similar-looking keys the user should consider before duplicating. When validating: produce a list of entries with flagged issues, keyed by BibTeX cite-key.
