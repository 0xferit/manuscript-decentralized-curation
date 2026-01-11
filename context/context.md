# Project Context (PUW Articles)

## Goal, audience, constraints

**Goal:** Define “curation” as the upstream bottleneck behind modern coordination/governance/allocation failures, then motivate a concrete direction: **trustless curation via decentralization**.

**Audience:** CS academics and engineers—people who respond to precise definitions, causal chains, and mechanism design framing.

**Tone constraints:** Direct, non-poetic, high signal. Avoid fragile stats and avoid overfitting to current events in early “problem” sections unless explicitly requested.

## Canonical artifacts (current)

- `my new version.md` — editable master manuscript.
- `_quarto.yml` — Quarto render configuration (single-source, multi-format).
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

- Manuscript exists as a consolidated 7-part series (not split into `articleN.md`).
- Master (`my new version.md`) explicitly incorporates all items in `context/attack-and-defense-log.md` (now **15** attacks incl. “Consensus ≠ Correctness” / legal semantics).
- Master recently gained paper-style scaffolding: abstract, contributions, threat model, stress-test map; tighter mechanism definitions (claim templates, evidence policy, confidence score invariants, relevance math); and a small references section.
- `legacy/*_21699486*` artifacts are the **last released** snapshot/export (pre-Quarto) and may lag the master.
- Next release step (when desired): generate a new `<hash>` snapshot + matching HTML export from the updated master, then update the two artifact pointers above.
- Quarto path (new): install Quarto + render `my new version.md` to `outputs/` (HTML/PDF/DOCX) from the single source.
- Continuous publish (HTML): commits to `main` are rendered to `outputs/paper.html` and published to the `cf-pages` branch as `public/index.html` (for Cloudflare Pages).

