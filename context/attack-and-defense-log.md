# Trustless Curation: Attack & Defense Log

This document tracks the "Red Teaming" exercises conducted against the Decentralized Curation thesis. It serves as a rigorous stress-test record, documenting how the system defends against economic, game-theoretic, social, and epistemic attacks.

---

## Section 1: Successfully Defended Attacks

_These attacks have been neutralized, and their defenses are integrated into the main manuscript._

### 1. The "Lazy Majority" Equilibrium

**Attack:** Curators will just copy the majority vote (or whale vote) without checking facts to win rewards.
**Defense:** Commit-reveal voting prevents vote copying during the commitment phase. Graduated coherence-based slashing penalizes curators whose scores fall outside the |v_i - mu| <= K*sigma band, with penalty scaling linearly from zero at the boundary to total loss of locked tokens at twice the boundary distance. This makes rubber-stamping risky when it diverges from the informed distribution, with harsher penalties for larger deviations.

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
**Defense:** The design optimizes for truth quality, not curator equality. Curation uses draw-and-lock staking: curators stake into a pool, the protocol draws seats proportional to stake, and each seat locks a fixed token amount that determines both round weight and maximum loss. Larger stakers draw more seats, contributing more information to the mean and facing proportionally larger penalties if incoherent. Permissionless pool creation allows alternative communities to form. The defense against whale manipulation is escalation: a dishonest whale who dominates a round faces a larger appeal committee where their stake fraction is diluted and their losses scale with their position. A whale who captures a pool also degrades its value, making the attack economically self-defeating for profit-seeking actors. Curator reputation has been eliminated entirely; no reputation-weighted mechanism influences drafting or scoring.

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
2. **Topic Pools + Draw-and-Lock Staking:** Curators are drafted from staked pools via stake-weighted lottery. Each drafted seat locks a fixed token amount that determines both round weight and maximum loss. No reputation influences drafting or scoring; curation is entirely stake-driven.
3. **Escalation on both layers:** For accuracy disputes, DDR handles appeals via its own escalation mechanism (larger juries at higher stakes). For relevance disputes, relevance-round escalation allows dissenting curators to appeal to a larger committee at higher stakes; the threat of appeal shifts the Schelling point from lazy consensus toward what a better-informed committee would produce.
4. **Policy-defined Domains:** When a dispute is inherently normative (e.g., "what counts as X under policy"), jurors adjudicate policy compliance, not metaphysical truth.

The defense rests on three load-bearing conditions: (a) the pool's relevance policy must be specific enough that competent curators' signals cluster around the policy-implied true value; when it is not, the mechanism degenerates toward a beauty contest; (b) escalation must shift the Schelling point from lazy consensus toward what a larger committee would produce; (c) draw-and-lock with graduated slashing must make dishonest scoring proportionally costly. The mechanism does not claim to produce truth. It produces the most common independent interpretation of a specific rubric by staked participants, bounded by escalation discipline and the aggregate collusion threshold.

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
**Status:** No protocol-level defense exists against free-riding scrapers. The protocol produces a public good; verified data is freely readable from on-chain state. Scrapers do not take stakers' money directly; they capture the output value (e.g., ad revenue from verified content) that could otherwise fund the protocol. The harm is indirect: scrapers capture value, pool funding becomes insufficient, relevance rounds pause, curators leave, and feed quality degrades. Pool revenue has two components: endogenous inflows (challenge taxes, failed-challenge counter-stake share) which are dispute-dependent and zero in peacetime, and exogenous inflows (pool creator budgets, public goods funding, advertising revenue) whose viability is assumed but not demonstrated. The paper concedes the attack ("curation as public infrastructure") and reframes it: if a scraper distributes verified content widely, it serves the protocol's information quality mission even if it contributes nothing economically. This is an honest concession, not a defense.

### OV-1. Off-Chain Collusion Above the Colluding-Bloc Threshold

**Attack:** Curators coordinate off-chain to align their scores, shifting the weighted mean toward a biased target. Honest reporters then fall outside the coherence band and are slashed while dishonest reporters survive.
**Status:** Partially mitigated by a four-layer defense: (1) commit-reveal prevents real-time on-chain vote copying; (2) draw-and-lock with graduated slashing penalizes individual deviants proportionally to their deviation distance; (3) escalation allows honest minorities to overturn captured rounds by appealing to a larger committee where sampling variance is reduced; (4) economic self-destruction deters profit-seeking majority-stake attackers because distorting a pool degrades its value and the attacker's locked capital with it. E2-Adv characterizes the collusion threshold empirically under a predecessor model (binary coherence test, fixed-rate slashing): at K=1.25 with 15-member committees, the mechanism degrades visibly when the colluding fraction exceeds approximately 0.15 to 0.20; the threshold under draw-and-lock with graduated slashing may differ and is future work. The irreducible residual: off-chain coordination by a stake majority above phi* cannot be prevented by any protocol mechanism; it can only be made detectable and economically painful. Detection is a precondition for the exit-based defense to function: interfaces and monitoring tools can observe distorted score distributions and abnormal escalation frequency, but the protocol does not automate this detection. Off-chain coordination that does not require explicit vote exchange (e.g., tacit agreements to "all vote 0.9") is not detectable by commit-reveal.

### OV-2. Legal Pressure Against Visible Participants

**Attack:** Governments or litigants target visible stakers, pool creators, or interface operators with legal action (libel suits, regulatory enforcement) to suppress participation.
**Status:** Partially mitigated. All participants operate under pseudonymous on-chain addresses, which raises the cost of linking protocol activity to a real-world identity targetable by legal action. Pooled staking and random drafting reduce individual targeting surface for curators, who do not choose which claims to score. Interface redundancy means shutting down one frontend does not destroy the protocol. However, the paper explicitly acknowledges: "Pooled staking and random drafting do not establish immunity from targeted legal action." Authors who bond claims are the most exposed: they voluntarily publish specific content with their address attached. Challengers and pool creators face moderate exposure. The practical deterrent may not be lawsuits that succeed but the cost of defense itself: even a weak legal theory can suppress participation if the cost of responding exceeds the expected curation reward. This is an operational deployment constraint, not a protocol-solvable problem.

### OV-3. Pool-Policy Degeneracy

**Attack:** Permissionless pool creation means anyone can create pools with degenerate policies (trivially satisfiable relevance criteria, adversarial templates, or policies designed to extract stake from honest curators).
**Status:** Partially mitigated by competitive selection. Pools with trivially satisfiable relevance criteria or adversarial templates fail locally: trivial pools produce undifferentiated scores with no information value; adversarial templates deter authors from submitting. In both cases, users migrate to better-curated alternatives. Interfaces filter which pools to feature, warn about, or ignore. For honeypot pools (where an entrenched biased consensus traps newcomers into slashing), escalation provides intra-pool defense: an honest newcomer who is slashed by the biased majority can appeal to a larger committee. However, escalation enforces whatever policy exists; if the policy itself is degenerate, escalation enforces it faithfully. The defense against bad policies is competitive exit, not intra-pool correction. Competitive selection requires sufficient pool alternatives and low switching costs. The blueprint identifies residual switching frictions (reputation lock-in, funder coordination, round-cycle capital commitment) that may slow this dynamic. No governance mechanism prevents degenerate pool creation; the defense is purely market-based.

### OV-4. Coordinated Capture Above the Colluding-Bloc Threshold

**Attack:** A well-funded adversary acquires enough stake across multiple identities to exceed the colluding-bloc threshold in targeted pools, systematically distorting relevance scores.
**Status:** Partially mitigated. Per-identity weight caps have been removed because they constrain only honest single-identity participants; a Sybil adversary distributes stake across cheap identities to bypass per-identity caps. Unlike OV-1 (organic collusion where sampling variance matters), this vector involves deterministic stake control: the adversary's stake fraction is the same in every committee regardless of size, so escalation provides limited additional defense here. The primary defense is the cost of capital: the adversary must lock enough stake to exceed phi* in the target pool. If the protocol uses a platform-specific staking token with limited circulating supply, this cost is superlinear: each additional token purchased costs more than the last due to slippage on a thin order book. In extreme cases, the required tokens may not be available at any price if honest stakers hold most of the supply and will not sell. The accumulation itself produces a visible price signal (rising token price) that alerts the community. The attack is doubly self-defeating for platform-specific tokens: the attacker pays a slippage premium to enter, then the captured pool's degradation depresses the token's value, compounding losses. By contrast, if staking used a deep-market token like ETH, the attacker could accumulate with negligible slippage and ETH's value would be independent of this protocol's health, removing the depreciation feedback loop. Competitive exit limits the blast radius to one pool. Residual risks: slow accumulation over time can reduce slippage; insider allocations or pre-mine can provide cheap initial stake; and the same token illiquidity that deters attackers also creates a barrier to entry for honest curators.

### OV-5. DDR Capture / Degradation

**Attack:** The external DDR provider degrades in quality (lazy jurors, inaccurate rulings, slow resolution) without being fully captured, causing the accuracy layer to inherit that degradation.
**Status:** Acknowledged as an inherited dependency. Attack #5 covers the full-capture scenario; this entry addresses gradual degradation. The protocol delegates accuracy adjudication to external DDR as a deliberate modular choice. DDR providers like Kleros have their own internal defenses against lazy juries and slow resolution (appeal escalation, finality mechanisms); the protocol inherits these by delegation. The accuracy layer's quality ceiling is bounded by DDR quality, but DDR's internal quality assurance is the first line of defense. The residual open question is what happens if DDR's own internal defenses are insufficient. The protocol emits observable quality signals that interfaces can monitor without requiring independent ground truth: appeal overturn rates (a high overturn rate suggests first-round juries are unreliable), cross-pool consistency (the same proposition challenged in different pools should produce the same DDR outcome), and justification quality (DDR juror justifications are public and evaluable). These signals make degradation detectable in principle, but the protocol does not specify detection thresholds or automated responses; monitoring is an interface responsibility. The paper does not model the coordination cost of migrating to an alternative DDR provider.

### OV-6. Cold Start / Bootstrap

**Attack:** New pools need readers, challengers, curators, and budget simultaneously. Without a critical mass of participants, the mechanisms cannot function: no challengers means false claims survive, no curators means no relevance scoring, no budget means no relevance round rewards.
**Status:** Partially mitigated by local pool economics and the accuracy-layer fallback. Pool creators seed local reward budgets to bootstrap curator participation. Even if the relevance layer fails to bootstrap (no curators, no budget), the accuracy layer functions independently: authors can post bonded claims, challengers can dispute them, and DDR adjudicates. The degradation is partial, not total; the pool works as a bonded-claim-plus-challenge system without feed ranking. Planned author reward disbursement (pro-rata to best-performing authors from the pool budget) would further incentivize early authorship, strengthening the accuracy-layer bootstrap. The bootstrap also has a funding dimension: peacetime pool revenue is entirely exogenous (see Attack #9), so the pool needs sponsors willing to fund before it has demonstrated value, and no protocol mechanism creates that incentive. The paper makes bootstrap requirements explicit rather than hiding them behind protocol-wide governance. However, the cold-start problem is real: a pool must attract sufficient participation and sustained external funding before the economic incentives become self-sustaining. The paper does not provide a bootstrap protocol or quantify the minimum viable participation threshold. Truth Post 2023 provides direct evidence: 16 on-chain transactions and no sustained usage demonstrate that cold start is a binding practical constraint, not a theoretical concern.
