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

_Note:_ `legacy/` contains older pre-Quarto snapshots/exports (including unversioned convenience copies).

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
- **Round 7 revisions (March 2026): K-Dense Web peer review response (Major Revision).** Addresses all 5 major issues (M1-M5), all 8 minor issues (m1-m8), and all 7 prioritized action items in one pass. Changes span `paper.qmd`, `analysis/run_all.py`, `references.bib`:
  1. **M2 / Priority 1: Multi-seed statistical infrastructure.** Refactored E1-Adv and E2-Adv to run N=100 seeds with 95% confidence intervals. Extracted `_e1_adv_single_run()` and `_e2_adv_single_run()` helpers, added `_ci95()` utility. CSV columns now include `_mean`, `_std`, `_ci95` suffixes. Figures show error bars (E1-Adv) and shaded CI bands (E2-Adv). Key results: E1-Adv at p=0.80 adversary loses -1638±68 per attack; E2-Adv mechanism breaks at 30% collusion (colluder share 0.80±0.005).
  2. **M1 / Priority 2: E4 reputation mechanism validation.** Three new experiments:
     - **E4a (alpha sweep):** 5 alphas × 3 decay rates × 100 seeds, 500 rounds, 200 curators. Measures time-to-non-whale-entry, Gini coefficient, mean error. Cash-poor experts (s_i=0.1) reach median weight in 8 rounds at alpha=0.5 vs 137 at alpha=0.
     - **E4b (reputation gaming):** Attacker with rep=200 votes randomly; measures rounds above median. At alpha=0.5, delta=0.05: attacker above-median for 61/300 rounds; delta=0 means permanent entrenchment.
     - **E4c (Sybil laundering):** 20 Sybils vote honestly for 100 rounds, then attack. Error at alpha=0.5 is 0.072 (vs 0.023 at alpha=0).
     - Added RQ4, E4 subsection with 4 figures, updated Limitations and Conclusion.
  3. **M4 / Priority 4: JTB moved to main text.** New subsection "Operationalizing knowledge: from JTB to contestable signals" in Introduction. Includes JTB definition, mapping table, departure paragraph, Gettier paragraph. Appendix A.1 now cross-references Introduction. Added `gettier1963justified` to `references.bib` (25 entries total).
  4. **M5 / Priority 3: Equilibrium caveat.** New "Focal-point uniqueness: scope and limitations" subsection after Proposition 2. States focal-point uniqueness is a design heuristic, not a theorem. Multi-modal distributions acknowledged. Formal proof flagged as open problem. Matching limitation subsection added.
  5. **M3 / Priority 5: Cold-start bootstrapping expanded.** Replaced single-paragraph limitation with "Cold start and deployment bootstrap" containing two strategies (seeded single-domain launch, retroactive validation) and honest cost assessment.
  6. **Priority 6: Threat model expansion.** Three new rows in attack-defense table: pool governance capture (#13), temporal sniping (#14), reputation laundering (#15).
  7. **Priority 7: Smart contract security.** New Limitations subsection "Smart contract attack surface" covering reentrancy, overflow, MEV, storage manipulation.
  8. **Minor issues (m1-m8):**
     - m1: Cross-pool C normalization formula added (`C_norm = C / median(C_pool)`).
     - m2: Appeal ceiling added (4 rounds or 10× original bounty).
     - m3: "Proof of Truth" renamed to "bonded product claims" with footnote.
     - m4: All 11 figure captions expanded with standalone interpretation.
     - m5: Disclosure moved from Introduction callout to dedicated "Conflicts of Interest" section; expanded to include "no PNK tokens, no financial relationship."
     - m6: Bolander citation softened from "experimental evidence" to "theoretical models of recursive belief reasoning."
     - m7: 4th Groves-Ledyard structural difference added (cardinal utility vs binary slash/reward).
     - m8: Temporal decay specified with opt-in TTL and exponential decay formula.
  9. Paper grew from ~780 to ~890 lines; `references.bib` grew from 24 to 25 entries. Reading time: ~13,431 words, 315 equations, 11 figures, 2 tables.
- **Structure rework (March 2026): first-20-minutes optimization.** Goal: get readers to the mechanism design within 12 minutes instead of 22. Four changes:
  1. **Abstract compressed:** ~1,000-word essay replaced with ~300-word conventional abstract. All citations removed (conventional style). Problem/approach/results/scope structure.
  2. **Introduction expanded:** "Information abundance, knowledge scarcity" subsection expanded from ~88 to ~230 words, absorbing the library metaphor and AI form-substance decoupling paragraph from the old abstract. "Why this matters" subsection expanded from ~80 to ~280 words, converting 4 bullet points to prose and absorbing old abstract material (bad curation as selection pressure, curation dependency/vulnerability, centralized failure modes, indistinguishability insight, Reuters 40% stat, Chomsky citation). Transition sentence added before JTB subsection.
  3. **Related Work moved:** from before System Model to after Mechanisms (before Threat Model). Forward references in Related Work (to coherence game, Flow 3 economics) become backward references. Roadmap updated to reflect new section order.
  4. **De-duplication verified:** Reuters stat appears only in Introduction, Chomsky only in Introduction, Wang & Strong only in Related Work and Appendix. No verbatim duplication between abstract and body.
- **Framework reframing (March 2026).** Repositioned paper from "protocol that separates accuracy from relevance" to "general four-step framework for trustless decentralized curation, instantiated for news." Four framework steps: problem definition, use case selection, quality identification, mechanism design. Accuracy/relevancy split reframed as consequence of quality identification for news, not a universal principle. Changes:
  1. **Abstract rewritten:** introduces four-step framework by name, positions news as chosen use case, accuracy/relevancy as quality identification result.
  2. **Introduction:** added framework introduction sentence after thesis statement.
  3. **Contributions:** added "general framework" as contribution #1; reframed "separation of powers" as "quality decomposition for news curation"; added "deployment retrospective" (Truth Post).
  4. **Quality criteria:** split into universal process properties (well-posed, auditable, contestable, incentive-aligned) and domain-specific criteria (evidence-backed->accuracy, coherent->relevance, current).
  5. **Mechanisms overview:** reframed "separation of powers" as framework output for news, not axiom; added paragraph on domain-specificity.
  6. **Truth Post section added** (new top-level section between Mechanisms and Related Work): 2023 partial deployment retrospective with what was built, what was not, what happened, and three lessons (cold start, relevance as engagement driver, protocol/interface separation). Source: legacy/manuscript-7-part-series.md.
  7. **Limitations:** "No deployment evidence" renamed to "Limited deployment evidence" with Truth Post cross-reference; cold start subsection now references Truth Post as empirical evidence.
  8. **Conclusion:** framework language added; Truth Post referenced in assumptions paragraph.
  9. **Roadmap:** updated to include Truth Post section and reframe Mechanisms description.
- **Falsification/verification asymmetry (March 2026):** Added scope paragraph to Instantiation 1 (binary accuracy) stating that the DDR mechanism is justified only when falsification is practically cheap relative to exhaustive verification. If a claim admits a compact proof, the dispute game is unnecessary; if no feasible counter-evidence exists within the stake's economic constraints, the game is inert. News claims identified as natural fit. Connects to Popper's demarcation criterion with a practical/economic dimension. ~110 words, one paragraph after the focal-point sentence.
- **Structural revision (March 2026): length reduction and section rewrites.** Five changes to `paper.qmd`:
  1. **Roadmap deleted:** removed the standalone Roadmap section (heading + paragraph). Introduction now flows directly into Background and problem statement.
  2. **Contributions trimmed:** consolidated 9 bullet points into 4 high-level contributions: general framework, news curation instantiation, adversarial evaluation, deployment retrospective.
  3. **Failure modes rewritten (Section 4.1):** replaced numbered list of 6 failure modes with 4 paragraphs deriving failures from a single structural property (opacity). Causal chain: opacity enables capture and gaming (reinforcing loop); unilateral control enables censorship and fragility; no contestability follows from unilateral control. All six named concepts preserved for Conclusion compatibility.
  4. **Adverse selection expanded (Section 4.2):** added concrete restaurant example paragraph before the Akerlof paragraph (concrete-then-abstract structure). Updated "failure mode 1"/"failure mode 2" references to just "Opacity"/"Capture".
  5. **Quality criteria rewritten (Section 4.3):** replaced "universal process properties" framing with derivation from problem structure. New opening paragraph scopes where these properties are and are not needed (playlist vs high-stakes domains). Process properties derived from specific failure modes rather than asserted as universal. Domain-specific criteria section preserved.
- **Introduction opening rewrite (March 2026):** Replaced abstract-first opening with concrete-first hook. New opening paragraph uses second-person examples (maps ratings, medical search, university rankings) to establish curation as an inescapable dependency, then pivots into the existing coordination metaphor ("Uncoordinated actions cancel out..."). Structural claim: curation is not a convenience but a dependency you cannot opt out of; every curator injects biases/incentives with no structured way to detect it. Connects forward to opacity (Section 4.1).
- **v2 re-review punch list (March 2026):** Addresses all 5 items from K-Dense Web v2 re-review (score 8.0/10, Accept with Minor Revisions). Changes to `paper.qmd`:
  1. **P1 (focal-point uniqueness):** Added formal treatment after the existing "scope and limitations" subsection: sufficient condition (single-attribute, enumerable, unambiguous policies yield unimodal distributions), counterexample (multi-dimensional "journalistic quality" produces bimodal responses), and design implication (decompose violating policies into constituent dimensions).
  2. **P2 (Bootstrap Strategy 2):** Rewrote Strategy 2 paragraph to replace underspecified "claim adoption mechanism" with explicit forward pointer identifying three open design questions (template conformance verification, adoption stake sizing, provenance tracking). Flagged as required pre-deployment deliverable.
  3. **P3 (alpha/delta recommendations):** Added deployment guidance paragraph after E4a results with concrete parameter ranges: expert-inclusion pools should use alpha in [0.25, 0.50] with delta >= 0.05; signal-fidelity pools should use alpha <= 0.10; delta should be calibrated first.
  4. **P4 (smart contract invariants):** Added 6-item checklist of accounting invariants (stake conservation, slash boundedness, commit-reveal integrity, payout exclusivity, cooldown monotonicity, confidence monotonicity) before the existing closing sentence.
  5. **Non-blocking improvements:** (A) Added mechanistic explanation of why reputation increases relevance error in E4a results. (B) Added approximate Truth Post participation metrics (fewer than 10 claims, fewer than 5 challenges, ~6-month active period). (C) Added zero-variance parenthetical for deterministic 8-round entry trajectory.
  6. **P5 (distillation to 8,000-10,000 words):** Deferred to separate revision pass.
- **Additional reviewer items (March 2026):** Three non-punch-list items from the v2 re-review addressed:
  1. **Kleros court selection:** Specified "General court" in Truth Post section for replicability.
  2. **Framework Step 2 operationalization:** Added two feasibility conditions to the contributions bullet (evidence must be publicly verifiable; falsification must be cheaper than verification).
  3. **Second framework instantiation:** Added advertising claim verification as a concrete second instantiation of the four-step framework, demonstrating domain-agnosticism. Walks through all four steps, shows the key structural difference (single quality dimension, no coherence game needed), and connects to the existing advertiser staking section.
  4. **Deferred items filed as GitHub issues:** E4b attacker realism (#2), E4d cross-domain scoping (#3), E1/E2 base multi-seed (#4), P5 distillation (#5).
- **Framework Step 1 disambiguation (March 2026):** Rewrote Step 1 description in the abstract from "identify the curation bottleneck in a target domain" to "identify curation as the upstream bottleneck behind a target coordination failure." This makes Steps 1 and 2 logically sequential: Step 1 is the analytical reframing (the problem is curation, not governance/funding/voting), Step 2 is domain selection with feasibility conditions. The other three locations (contributions, ad instantiation, conclusion) already used step names only or aligned phrasing; no changes needed there.
- **Terminology narrowing (March 2026):** Replaced all 7 instances of "news and information curation" with "news curation" in `paper.qmd`. Rationale: "information curation" is the universal concept (the paper defines curation as transforming raw information into knowledge); "news curation" is the specific domain instantiation. Conflating the two contradicted the paper's own statement that the accuracy/relevance decomposition is domain-specific ("a consequence of applying the quality identification step to news"), and conflicted with lines that already correctly used "news curation." The advertising instantiation further confirms domain-specificity: applying Step 3 to ads yields only accuracy, not accuracy + relevance.
- **Thesis example diversification (March 2026):** Added a paragraph after the scoping paragraph (Introduction) with three cross-domain examples substantiating the thesis that governance failures blamed on coordination are better explained by a corrupted knowledge layer: 2008 financial crisis (rating agency curation failure), replication crisis in science (peer review as broken curation), and 2003 Iraq WMD intelligence failure (broken analytical pipeline). Each follows the same pattern: coordination mechanisms operated as designed on corrupted inputs. Addresses the problem that all prior examples clustered in consumer-facing ranking/recommendation systems.
- **v3 re-review punch list (March 2026):** Addresses three remaining items from K-Dense Web v3 re-review (score 8.5/10, Accept with Minor Revisions). P3 and P4 were already resolved. Changes to `paper.qmd`:
  1. **N1 (monitoring requirement):** Added sentence after focal-point uniqueness subsection making high-$\sigma$ monitoring a required procedure for deployed pools, not optional.
  2. **N2 (Strategy 2 forward pointer):** Replaced ~100-word open-questions enumeration in Strategy 2 with 2-sentence forward pointer naming the claim adoption sub-protocol and deferring design to follow-on spec. Added deployability caveat.
  3. **N3 (three condensation steps):**
     - **N3a:** Collapsed Groves-Ledyard analogy from ~500 words across 4 paragraphs to ~100 words; structural differences moved to Quarto footnote.
     - **N3b:** Moved Appendix A content (Wang & Strong data-quality table + CRAAP credibility checklist) to new `appendix-data-quality.md` companion document; replaced with brief pointer.
     - **N3c:** Merged three Limitations subsections (commit-reveal/bribery, TCR participation failures, cold start/bootstrap) into single "Deployment challenges" subsection of ~300 words.
  4. **Header callout:** Updated to reflect distillation progress.
  5. Estimated word count reduction: ~1,200 words.
- **Next:** Build presentation for reading group.
