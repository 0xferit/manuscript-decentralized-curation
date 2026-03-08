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
- **Round 3 revisions (March 2026):** Three major changes to `paper.qmd` and `analysis/run_all.py`:
  1. **E2 scale fix:** Changed coherence game simulation from [0,10] to [0,1] scale to match the formalized Flow 4 protocol. Updated `noise_sigma` from 0.8 to 0.08 (proportional). Updated paper text.
  2. **Adversarial simulations (E1-Adv, E2-Adv):** Added two new experiments with strategic adversaries:
     - **E1-Adv (repeated attack):** Well-funded adversary submits 50 false claims. Result: system is economically punitive at all jury accuracy levels (adversary loses ~35× bounty per attack at p=0.80).
     - **E2-Adv (colluding bloc):** Coordinated curators bias ratings by +0.30. Result: mechanism ejects colluding minorities (<20%); at 30% collusion, mechanism breaks (colluders capture 79% stake share, signal error triples). Identifies concrete robustness threshold.
     - Added RQ1a and RQ2a to Research Questions. Added figures `e1_adversarial.png`, `e2_adversarial.png`. Updated eval summary with adversarial data points. Updated Conclusion.
  3. **Appendix A expansion:** Replaced 3 placeholder subsections with full mapping tables: JTB components → protocol mechanisms, Wang & Strong quality dimensions → protocol operationalization, CRAAP credibility checklist → on-chain verifiable indicators.
- **Round 4 revisions (March 2026):** Fourteen edits to `paper.qmd` and `references.bib`:
  1. **Scoping paragraph:** Added explicit statement that coordination (phase two) is out of scope; the paper addresses only the information-to-knowledge transformation.
  2. **Contributions list updated:** Added formalized coherence game, public good framing (Groves-Ledyard), and adversarial evaluation program as named contributions.
  3. **Advertiser staking expanded:** Added economic argument (when staking is rational vs. third-party certification), ad fraud statistics ($170B projected losses by 2028), and explicit limitations. Elevated from sketch to proper subsection.
  4. **Author disclosure:** Added callout noting multi-year operational experience with Kleros (informs design, not empirical validation).
  5. **Reputation limitation:** New Limitations subsection flagging that the reputation mechanism ($\alpha$, decay) is specified but not experimentally validated.
  6. **Simulation limitations:** New Limitations subsection noting E1-Adv single-seed variance.
  7. **Notation table:** Added @tbl-notation before Mechanisms with all symbols ($B$, $S$, $C$, $v_i$, $w_i$, $\mu$, $\sigma$, $K$, $\alpha$, $R$, $N$, $p$, $d$, $n$).
  8. **Flow 1 formalized:** Added 5-step protocol (claim authoring → template validation → submission → confidence accumulation → outcome). Clarified $C$ unit (token·time), constant-bounty simplification ($C = B \cdot T$), and cross-pool non-comparability.
  9. **Flow 2 formalized:** Added 5-step protocol (pool creation → staking with cooldown → random drafting → participation → payout/slashing) plus design rationale subsection.
  10. **Groves-Ledyard paragraph split:** Broke 12-sentence wall into 3 focused paragraphs (mechanism, public good claim, protocol application).
  11. **Roadmap capitalization fixed:** Section names now match actual headings.
  12. **Dead references removed:** `shumailov2023recursion` and `kosmarski2020tcrjournal` removed from `references.bib`.
  13. **E2-Adv clarified:** Explained that colluders are competent-with-bias (not random), detailed population composition at each collusion level, added note that honest curators become the ones ejected when the mechanism breaks.
  14. Paper grew from 620 to 688 lines; `references.bib` trimmed from 19 to 17 entries.
- **Round 5 revisions (March 2026):** Twelve edits to `paper.qmd` and `references.bib`:
  1. **Reality.eth added to Related Work** as DDR-layer prior art (bond escalation + arbitrator), distinct from curation.
  2. **BTS (Prelec 2004) added to Related Work** as alternative information elicitation approach; comparison flagged as future work.
  3. **Groves-Ledyard analogy tightened:** spelled out what transfers (deviation penalty, truth-telling incentive) and what doesn't (G-L excludes own report from mean, assumes cardinal preferences for single good, proves Pareto optimality — coherence game does none of these).
  4. **Optimistic finality named** as explicit design choice in Flow 1 step 5, with tradeoff discussion.
  5. **EV formula split** into challenger-level ($\text{EV}_{\text{challenger}}$) and system-level ($\text{EV}_{\text{system}}$) with distinct semantics.
  6. **Common knowledge cited:** Aumann (1976) cited on first use of "common knowledge" in Introduction.
  7. **Validator role clarified:** explained that validators and curators are the same actors in different contexts.
  8. **DDR acronym defined** on first use (Reality.eth paragraph in Related Work).
  9. **Token X → $s_i$:** fixed notation conflict in Flow 4 step 1.
  10. **Confidence score invariant refined:** monotone invariant now specifies behavior during challenge (pauses) and reinstatement (resumes).
  11. **Ad fraud citation added:** Juniper Research source for $170B projected losses.
  12. **Draft notice added:** callout at top of paper + author/date/status metadata in YAML front matter.
  13. New `references.bib` entries: `realityeth2023`, `prelec2004bts`, `aumann1976agreeing`, `juniperresearch2023adfraud` (17 → 21 entries).
  14. Paper grew from 689 to ~701 lines.
- **Round 6 revisions (March 2026): peer review response, issues #1+#2+#3.** Three changes to `paper.qmd` and `references.bib`:
  1. **Unified Schelling game formalization (Issues #1+#2):** New "Formal model: Schelling coordination under restricted conditions" subsection in Mechanisms. Defines a base Schelling coordination game with two instantiations: binary accuracy (DDR disputes, avoids George's impossibility via binary choice) and scalar relevance (coherence game, avoids it via continuous aggregation rather than rankings). Three numbered propositions: Condorcet connection (Prop 1), focal point equilibrium (Prop 2), competence selection (Prop 3). Cites George (2023, Math. Soc. Sci.) impossibility theorem as the constraint the design responds to. Added griefing factor framework (George 2023, Frontiers in Blockchain) for attack cost quantification. Added 3 references: `george2023strategic`, `george2023griefing`, `ast2023decentralized`. Updated notation table with $\mathcal{V}$, $v^*$, $u_i$, $P_{\mathrm{maj}}$, $GF$. Updated Flow 3 to use $P_{\mathrm{maj}}$ notation and reference minimum-$p$ requirements. Updated Flow 4 equilibrium argument to reference Propositions 2 and 3. Added "Formalization gaps in decentralized justice" paragraph to Related Work. Added minimum-$p$ requirements paragraph after E1 results in Evaluation.
  2. **Curation policy bootstrap problem (Issue #3):** New subsection in Mechanisms naming the circularity (curation policies needed for equilibrium, but writing them is a governance problem). Frames as constitutional layer with 4-part bootstrapping direction (start minimal, amendment-as-dispute, forking as safety valve, cross-pool competition). New Limitations entry acknowledging the open empirical question.
  3. Paper grew from ~701 to ~780 lines; `references.bib` grew from 21 to 24 entries.
- **Next:** Build presentation for March 10.
