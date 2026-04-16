# Trustless Curation: Attack & Defense Log

This document tracks the "Red Teaming" exercises conducted against the Decentralized Curation thesis. It serves as a rigorous stress-test record, documenting how the system defends against economic, game-theoretic, social, and epistemic attacks.

---

## Section 1: Successfully Defended Attacks

_These attacks have been neutralized, and their defenses are integrated into the main manuscript._

### 1. The "Lazy Majority" Equilibrium

**Attack:** Curators will just copy the majority vote (or whale vote) without checking facts to win rewards.
**Defense:** Commit-reveal voting prevents vote copying during the commitment phase. Coherence-based slashing punishes curators whose scores fall outside the |v_i - mu| <= K*sigma band, making rubber-stamping risky when it diverges from the informed distribution.

### 2. The "Subreddit War" (Echo Chambers)

**Attack:** A "Conspiracy Pool" will successfully curate lies because their policy allows it.
**Defense:** A pool can have a biased relevance policy, but accuracy is adjudicated by a cross-pool external DDR court. Any bonded claim is challengeable regardless of which pool it belongs to; a conspiracy pool cannot shelter a factually false claim from external DDR. However, the accuracy/relevance separation addresses only the factual half of the echo chamber problem. A biased pool can still distort which accurate claims are surfaced by scoring them as highly or lowly relevant. The design relies on pool competition and user exit for relevance quality, not on a protocol-level guarantee.

### 3. The "Post-Truth" Apathy

**Attack:** Users don't care about truth; they want dopamine.
**Defense:** The protocol is middleware. It provides a contestable accuracy signal. If a consumer app wants to sell truth, the protocol enables it. The protocol does not force users to consume verified content, but it produces adjudication outcomes for bonded claims that interfaces can use to distinguish tested from untested content.

### 4. The "Boring Dystopia" (Liquidity Crisis)

**Attack:** Low-stakes lies will survive because no one bothers to challenge them.
**Defense:** Low stake equals low signal. Confidence is continuous bond-time; there is no protocol-level dollar cutoff at which a claim becomes "noise." A low-bond claim carries weak evidence because little capital is at risk and, by Claim 1, the bond is too small to deter high-value deception. The blueprint confirms: "There is no protocol-level hard cutoff." Any fixed visibility threshold (such as the "$5 stake" interface illustration) is a downstream interface choice with no protocol guidance on where to draw that line, not a validated protocol constant.

### 6. The "Rich Get Richer"

**Attack:** Competent curators accumulate all the capital, forming an oligarchy.
**Defense:** The design optimizes for truth quality, not curator equality. Curation uses pure stake-weighted drafting (d_i = s_i) with weight caps: w_i = min(s_i, c * total_committee_stake). Permissionless pool creation allows alternative communities to form. The weight cap bounds individual influence within a single committee but does not prevent stake concentration across multiple protocol identities. Curator reputation has been eliminated entirely; no reputation-weighted mechanism influences drafting or scoring.

### 7. The "Chilling Effect" (Liability)

**Attack:** Staking on truth exposes curators to libel lawsuits.
**Defense:** Curators stake into topic pools and are randomly drafted into committees. This randomness reduces targeted pre-selection: curators do not choose which claims they score, and an adversary cannot predict committee membership before drafting. All participants operate under pseudonymous on-chain addresses, which raises the cost of linking protocol activity to a real-world identity targetable by legal action. Authors and challengers face higher legal exposure than curators because they voluntarily select specific claims to publish or challenge; random drafting does not protect them. The paper acknowledges this is a partial mitigation: pooled staking and random drafting do not establish immunity from targeted legal action.

### 8. The "Meta-Curation" Trap

**Attack:** The Protocol is neutral, but the Interface (Wallet/App) re-centralizes control.
**Defense:** Protocol state is canonical and publicly readable on-chain, so a biased interface cannot falsify protocol outputs; it can only choose what to surface. Multiple interfaces can coexist because all curation work (adjudication, relevance scoring, confidence accounting) is done on-chain; an interface only reads and renders, making the barrier to entry for a transparent competitor low. A distorting interface creates a differentiation opportunity for any competitor willing to render canonical state faithfully. In practice, the defense depends on interface competition actually materializing rather than on individual users reading raw chain data. The architecture is a precondition for this competition, not a guarantee of it.

### 9. The "Deflationary Spiral" (No Yield in Peacetime)

**Attack:** If there are no lies, there are no disputes, so curators leave.
**Defense:** Pool reward budgets, funded by pool creators, challenge taxes, and the pool-budget share of failed challenger counter-stakes, decouple relevance-round rewards from dispute activity. The architecture makes peacetime curator compensation possible. However, both dispute-dependent inflows (challenge tax, counter-stake share) are zero in peacetime; a peaceful pool generates zero endogenous revenue. Peacetime funding is therefore entirely sponsor-dependent, and no protocol mechanism creates a sponsorship incentive. If sponsors do not fund the pool, relevance rounds pause while the accuracy layer continues. Advertising staking is presented in the paper as a plausible additional revenue source, but it is a speculative second instantiation: the paper explicitly states "this sketch does not constitute a full instantiation." Whether exogenous sponsorship can sustain a pool long-term is an open empirical question.

### 10. The "Toxic Content" Trap

**Attack:** Permissionless publishing means hosting hate speech/illegal content.
**Defense:** The protocol is the neutral pipe; the interface is the filter. Interfaces can block toxic pools to comply with local laws without compromising the protocol's censorship resistance. The protocol-interface separation makes this architecturally explicit. Content-layer operators (indexers, gateways, pinning services) face analogous filtering decisions: they choose which claim blobs to host or serve, and may face jurisdiction-specific legal pressure independently of interface operators.

### 12. The "Context Collapse" (Epistemic Vacuum)

**Attack:** Malicious authors submit technically true but misleadingly vague statements.
**Defense:** Claims must be falsifiable and well-posed (timeframe, definitions, sources). Under-specified claims are rejectable via the `NonFalsifiable` challenge reason; ambiguity is punished as severely as falsehood. Structured claim templates and evidence policies enforce semantic precision at the pool level.

### 13. The "Frozen Truth" (Temporal Decay)

**Attack:** Truth changes (e.g., science evolves), but the blockchain is immutable. The ledger becomes a graveyard of outdated facts.
**Defense:** Validation is not a lifetime warranty. If a fact changes, the old claim becomes challengeable. This creates a bounty opportunity for a challenger to debunk it. Authors are incentivized to withdraw (un-stake) claims that are becoming obsolete to save their capital. Confidence only accumulates while bonded; withdrawn claims remain historical rather than active.

### 15. "Consensus != Correctness" (Ambiguous Questions / Legal Semantics)

**Attack:** In Schelling-style juries, voters maximize coherence with other voters, not truth. When questions are ambiguous or require domain expertise, the equilibrium can converge on a lazy or naive interpretation rather than the correct outcome.
**Defense:** The system treats question design as first-class:

1. **Semantic Precision / Claim Templates:** Claims must be falsifiable and well-posed (timeframe, definitions, sources). Under-specified claims are rejected/slashable via `NonFalsifiable` challenge reason instead of forcing jurors to guess.
2. **Topic Pools + Stake-Weighted Drafting:** Curators are drafted from staked pools via stake-weighted lottery with weight caps (w_i = min(s_i, c * total_committee_stake)). No reputation influences drafting or scoring; curation is entirely stake-driven.
3. **External DDR Appeals:** If a lazy majority converges on the wrong outcome, appeals are handled entirely by the external DDR. The protocol does not implement its own escalating-stakes appeal ladder or any protocol-native "lone expert versus herd" jackpot.
4. **Policy-defined Domains:** When a dispute is inherently normative (e.g., "what counts as X under policy"), jurors adjudicate policy compliance, not metaphysical truth.

---

## Section 2: Open Attack Vectors

_These attacks are partially mitigated but not fully resolved. Each entry notes what the paper currently provides and what remains open._

### 5. The "Oracle Capture" (DDR Capture)

**Attack:** An adversary captures the external DDR provider (e.g., by acquiring a majority of DDR governance tokens) to force false verdicts on challenges.
**Status:** Partially mitigated; explicitly acknowledged as outside validated claims. The paper's partial mitigations are economic arguments: the slippage argument holds that acquiring a majority DDR stake would be expensive on thin markets, and the economic-suicide argument holds that success would collapse the token's value, making the attack self-defeating for a profit-seeking attacker. If the community detects capture, it can fork to a new DDR provider. However, the paper explicitly states: "If the external court is captured, lazy, or inaccurate, the accuracy layer inherits that degradation." No quantitative market-cap threshold or slippage curve is provided. The economic-suicide argument does not hold for attackers whose goal is to corrupt specific rulings rather than profit from the token. More broadly, DDR adjudication is only trustworthy for disputes where the value at stake is less than the cost of capturing the DDR provider; when the external benefit of corrupting a ruling exceeds the cost of acquiring and burning a majority DDR stake, capture becomes rational as a cost of business. Fork defense requires community coordination under adversarial conditions, which is not analyzed. The paper does not model DDR capture cost. This threat is outside the paper's validated claims.

### 11. The "Self-Fulfilling Prophecy" (Mediocrity)

**Attack:** Curators vote for consensus (conventional wisdom), crushing nuanced or surprising truth.
**Status:** Mitigated by coherence slashing plus relevance-round escalation. Coherence-based slashing punishes lazy consensus when it diverges from well-informed signals: curators outside the |v_i - mu| <= K*sigma band lose stake. The coherence game alone rewards convergence, not correctness; a coordinated but wrong consensus can survive if it dominates the committee. Relevance-round escalation addresses this gap: any staked curator may appeal a finalized relevance score by posting an appeal stake, triggering a new round with a larger committee at higher stakes. By the Condorcet jury theorem, the larger appeal committee produces a mean closer to the policy-implied true relevance, giving a well-informed minority a credible path to overturn a lazy majority. The primary disciplining force is the threat of appeal: first-round curators anticipate what an appeal committee would produce and score accordingly, shifting the Schelling focal point from "lazy consensus" toward "what would survive escalation." DDR does not adjudicate relevance disputes; escalation is the relevance layer's own appeal mechanism. Simulation of escalation dynamics is future work.

### 14. The "Attention Arbitrage" (Vampire Attack)

**Attack:** Vampires scrape the verified data for free and monetize it with ads, paying nothing to the protocol. Stakers go bankrupt.
**Status:** No protocol-level defense exists against free-riding scrapers. The protocol produces a public good; verified data is freely readable from on-chain state. Sustainability depends on external funding sources: pool creator budgets, challenge tax revenue, potential public goods funding, and advertising revenue. The viability of these funding sources is assumed but not demonstrated. The paper concedes the attack ("curation as public infrastructure") and reframes it: if a scraper distributes verified content widely, it serves the protocol's information quality mission even if it contributes nothing economically. This is an honest concession, not a defense.

### OV-1. Off-Chain Collusion Above the Colluding-Bloc Threshold

**Attack:** Curators coordinate off-chain to align their scores, shifting the weighted mean toward a biased target. Honest reporters then fall outside the coherence band and are slashed while dishonest reporters survive.
**Status:** Partially mitigated. Commit-reveal prevents direct vote copying. Weight caps limit individual influence within each committee. E2-Adv characterizes the collusion threshold empirically: at K=1.25 with 15-member committees, the mechanism degrades visibly when the colluding fraction exceeds approximately 0.15 to 0.20. Below this threshold, small colluding minorities cause limited damage. Above it, coordinated blocs can bend the signal and preserve their own stake. The design narrows the attack surface but does not eliminate it. Off-chain coordination that does not require explicit vote exchange (e.g., tacit agreements to "all vote 0.9") is not detectable by commit-reveal.

### OV-2. Legal Pressure Against Visible Participants

**Attack:** Governments or litigants target visible stakers, pool creators, or interface operators with legal action (libel suits, regulatory enforcement) to suppress participation.
**Status:** Partially mitigated. Pooled staking and random drafting reduce individual targeting surface for curators. Interface redundancy means shutting down one frontend does not destroy the protocol. However, the paper explicitly acknowledges: "Pooled staking and random drafting do not establish immunity from targeted legal action." Authors who bond claims are publicly visible and directly targetable. Pool creators and interface operators face jurisdiction-specific legal exposure that the protocol cannot eliminate. This is an operational deployment constraint, not a protocol-solvable problem.

### OV-3. Pool-Policy Degeneracy

**Attack:** Permissionless pool creation means anyone can create pools with degenerate policies (trivially satisfiable relevance criteria, adversarial templates, or policies designed to extract stake from honest curators).
**Status:** Partially mitigated by competitive selection. The paper's defense is structural: bad pools lose users to better-curated alternatives, just as bad newspapers lose readers. Interfaces filter which pools to feature, warn about, or ignore. However, competitive selection requires sufficient pool alternatives and low switching costs. The blueprint identifies residual switching frictions (reputation lock-in, funder coordination, round-cycle capital commitment) that may slow this dynamic. No governance mechanism prevents degenerate pool creation; the defense is purely market-based.

### OV-4. Coordinated Capture Above the Colluding-Bloc Threshold

**Attack:** A well-funded adversary acquires enough stake across multiple identities to exceed the colluding-bloc threshold in targeted pools, systematically distorting relevance scores.
**Status:** Partially mitigated. Weight caps (w_i = min(s_i, c * total_committee_stake)) force the adversary to acquire multiple identities to control committee outcomes. The same collusion threshold described in OV-1 applies, but this vector differs in attack surface: a funded adversary can manufacture the required identities rather than relying on organic coordination. The paper does not model the cost of acquiring the required stake fraction in specific pools or the cost of maintaining Sybil identities. The weight cap limits influence per protocol identity only; it is not a Sybil-resistance guarantee.

### OV-5. DDR Capture / Degradation

**Attack:** The external DDR provider degrades in quality (lazy jurors, inaccurate rulings, slow resolution) without being fully captured, causing the accuracy layer to inherit that degradation.
**Status:** Acknowledged as an inherited dependency. Attack #5 covers the full-capture scenario; this entry addresses gradual degradation. The protocol delegates accuracy adjudication to external DDR as a deliberate modular choice. The tradeoff is direct: the accuracy layer's quality ceiling is bounded by DDR quality. Gradual degradation (as opposed to outright capture) may be harder to detect and harder to justify a fork over, since the community must distinguish DDR laziness from genuinely difficult cases. The paper does not model detection thresholds for DDR quality decline or the coordination cost of migrating to an alternative DDR provider.

### OV-6. Cold Start / Bootstrap

**Attack:** New pools need readers, challengers, curators, and budget simultaneously. Without a critical mass of participants, the mechanisms cannot function: no challengers means false claims survive, no curators means no relevance scoring, no budget means no relevance round rewards.
**Status:** Partially mitigated by local pool economics. Pool creators seed local reward budgets. Interfaces can ignore inactive pools. The paper makes bootstrap requirements explicit rather than hiding them behind protocol-wide governance. However, the cold-start problem is real: a pool must attract sufficient participation before the economic incentives become self-sustaining. The paper does not provide a bootstrap protocol or quantify the minimum viable participation threshold. The complete end-state design has not been deployed; Truth Post 2023 validated only a partial predecessor and did not bootstrap sustained usage.
