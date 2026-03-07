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
- `themes/puw.scss` — custom PUW HTML theme (optional; see `_quarto.yml`).
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
- Incorporated thesis-style critique fixes: explicitly frames outputs as **stake-weighted signals** (not philosophical knowledge), expands **Vagueness = Rejection** into a formal claim-schema section, adds commit-reveal/bribery limitations, and strengthens the Limitations section with citations.
- **Reading group prep (March 2026):** Tier 1 + Tier 2 fixes applied:
  - **Conclusion** expanded from 2 sentences to 4 paragraphs (thesis restatement, mechanism summary, key assumptions, open problems).
  - **Roadmap** no longer uses explicit section numbers; uses section names only.
  - **Quality criteria** (Section 4.2) expanded from 5 terse items to 7 with explanations; added **contestability** and **incentive alignment**.
  - **Threat model** now includes a 12-row attack-defense summary table inline (no longer defers to repo file).
  - **System model actors** split into 7 roles: authors, validators, challengers, jurors, interface operators, governance participants, readers. DDR black-box properties stated explicitly.
  - **Pooled staking** (Flow 2) expanded to full subsection: pool formation, random drafting, liability diffusion.
  - **Flow 3** (challenge/dispute) presented as numbered protocol steps with economic model (EV formula).
  - **Flow 4** (relevance) adds Schelling argument for coherence, whale manipulation risk + weight caps, accuracy-relevance interaction.
  - **Limitations** expanded: "no deployment evidence" added as first item; cold start, scalability, UX friction added; temporal decay, governance capture, domain expertise unbundled into separate subsections.
- HTML uses the default Quarto theme + grid; the PUW theme is saved in `themes/puw.scss` (enable via `_quarto.yml`).
- `legacy/*_21699486*` artifacts are the **last released** snapshot/export (pre-Quarto) and may lag the master.
- Quarto path (new): install Quarto + render `paper.qmd` to `outputs/` (HTML/PDF) from the single source.
- Continuous publish (HTML): commits to `main` run simulations, render `outputs/paper.html`, and publish to `cf-pages` as `public/index.html` (for Cloudflare Pages).
- **Abstract rewrite (March 2026):** Replaced the original 3-paragraph abstract with a research-grounded 6-paragraph version. Opens from the information paradox (quantity vs quality), introduces Wang & Strong's multi-dimensional quality framework, splits centralized curation failure into incompetence vs weaponization (with Reuters 40% trust data and Chomsky/Herman propaganda model), derives the indistinguishability insight, and closes with the manuscript's thesis. Added `chomsky1988manufacturing` to `references.bib`. Proper Quarto citations for all inline references.
- **Legacy merge (March 2026):** Merged 7 new/revised sections from `manuscript-additions.md` into `legacy/manuscript-7-part-series.md`: Scope and Assumptions, Related Work, Why This Is Not a TCR, Infinite Appeals and Backward Induction, The Truth Post (expanded MVP retrospective), Advertising as Proof of Truth (expanded), The Economics of Forking (expanded). ToC updated.
- **Groves-Ledyard addition (March 2026):** Added "Mechanism design for public goods" as the first entry in the Related Work section of `paper.qmd`. Groves & Ledyard (1977) formalized how self-interest can achieve Pareto-optimal public goods allocation via deviation penalties — structurally parallel to the coherence game's slashing of outlier curators. Added `groves1977freeriderproblem` and `samuelson1954publicgoods` to `references.bib`. Frames curated knowledge explicitly as a public good subject to free-rider dynamics.
- **Round 2 revisions (March 2026):** Eight edits to `paper.qmd`:
  1. Qualified the public good claim — tied non-excludability to permissionless architecture rather than asserting it as an inherent property of knowledge.
  2. Added "Prediction markets and futarchy" to Related Work — cites Hanson (2013), positions prediction markets as parallel approach with different cost structure, notes shared resolution ambiguity problems. Added `hanson2013futarchy` to `references.bib`.
  3. Added "Commons governance" to Related Work — cites Ostrom (1990), maps her 8 design principles to protocol structures (pools = boundaries, slashing = graduated sanctions, DDR = conflict resolution), notes divergence (digital/pseudonymous vs physical/stable communities). Added `ostrom1990commons` to `references.bib`.
  4. Formalized Flow 4 (coherence game) — full 7-step protocol spec: eligibility via staking, VRF-based drafting, commit-reveal with [0,1] scalar ratings, aggregation, coherence rule, payout (slashed stakes + optional reward R to coherent curators). Added subsections: premature reveal defense (report-based), Nash equilibrium argument (focal point + payoff structure + competence-as-natural-selection), whale manipulation risk, accuracy-relevance interaction.
  5. Specified Confidence Score formula — $C = \sum_t B_t \cdot \Delta t$ (bounty × time, summed over intervals). Raw score; reader interprets. Statistical inference available as system matures.
  6. Added juror independence caveat — inline note after EV formula + new Limitations subsection ("Juror independence assumption").
  7. Dropped "fast-path challenges" bullet (Under-specified challenges cheaper than accuracy challenges) — removed as non-essential and confusing.
  8. Expanded reputation/alpha analysis — added tradeoff discussion ($\alpha = 0$ vs high $\alpha$), decay rationale, explicit flagging as open parameter design problem.
- **Next:** Cherry-pick remaining Tier 3 fixes (contributions list, adversarial eval acknowledgment, appendix mappings). Build presentation for March 10.
