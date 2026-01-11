# Project Context (PUW Articles)

## Goal, audience, constraints

**Goal:** Define “curation” as the upstream bottleneck behind modern coordination/governance/allocation failures, then motivate a concrete direction: **trustless curation via decentralization**.

**Audience:** CS academics and engineers—people who respond to precise definitions, causal chains, and mechanism design framing.

**Tone constraints:** Direct, non-poetic, high signal. Avoid fragile stats and avoid overfitting to current events in early “problem” sections unless explicitly requested.

## Canonical artifacts (current)

- `paper.qmd` — editable master paper source (Quarto).
- `analysis/run_all.py` — simulations + figure generation (E1–E3).
- `requirements.txt` — pinned Python dependencies for evaluation.
- `_quarto.yml` — Quarto render configuration (single-source, multi-format).
- `styles.css` — custom CSS for the HTML output (embedded into `outputs/paper.html`).
- `references.bib` — bibliography for Quarto/Pandoc citations.
- `legacy/decentralized-curation-series-in-7-articles_21699486.md` — last released snapshot of the manuscript (pre-Quarto).
- `legacy/Decentralized_Curation_7_Part_Series_21699486.html` — reader-mode-friendly HTML built from that released snapshot (pre-Quarto).
- `context/attack-and-defense-log.md` — red-team log; defenses are integrated into the manuscript.

*Note:* `legacy/` contains older pre-Quarto snapshots/exports (including unversioned convenience copies).

## Core model (definitions)

- **Curation:** The process that transforms raw information into decision-grade knowledge.
- **Actors:** **Authors** (submit claims + stake), **Curators** (validate/challenge; may be jurors via DDR), **Readers** (consume; may become curators).
- **Accuracy:** Not “objective truth”; it is **human judgment**, but treated as **binary classification** (Valid/Invalid) under a defined evidence standard, resolved via **decentralized dispute resolution (DDR)** as a black box (e.g., Kleros-style).
- **Relevance:** A **non-binary** “importance” signal produced by a **policy-guided coherence game** (Schelling-point mechanism) inside a curation pool.
- **Semantic precision:** Claims must be **falsifiable**; missing context/vagueness is rejected (“Vagueness = Rejection”).

## Supporting reference docs

- `context/anti-sybil-architecture.md`
- `context/decentralized-dispute-resolution-research-proposal.md`

## Current status / next steps

- Paper source (`paper.qmd`) is now paper-structured (Abstract → Conclusion + Appendix) and includes an explicit Related Work section with BibTeX-backed citations.
- Evaluation is implemented as deterministic simulations (E1–E3) that generate figures and a short in-paper summary via `analysis/run_all.py`.
- Incorporated thesis-style critique fixes: explicitly frames outputs as **stake-weighted signals** (not philosophical knowledge), expands **Vagueness = Rejection** into a formal claim-schema section, adds commit–reveal/bribery limitations, and strengthens the Limitations section with citations.
- HTML is styled for a more editorial reading experience via `_quarto.yml` (Bootswatch theme + grid) and `styles.css` (typography, spacing, callouts, figures/tables).
- `legacy/*_21699486*` artifacts are the **last released** snapshot/export (pre-Quarto) and may lag the master.
- Quarto path (new): install Quarto + render `paper.qmd` to `outputs/` (HTML/PDF/DOCX) from the single source.
- Continuous publish (HTML): commits to `main` run simulations, render `outputs/paper.html`, and publish to `cf-pages` as `public/index.html` (for Cloudflare Pages).

