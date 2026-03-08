# Trustless Curation: Attack & Defense Log

This document tracks the "Red Teaming" exercises conducted against the Decentralized Curation thesis. It serves as a rigorous stress-test record, documenting how the system defends against economic, game-theoretic, social, and epistemic attacks.

---

## ✅ Section 1: Successfully Defended Attacks

_These attacks have been neutralized, and their defenses are integrated into the main manuscript._

### 1. The "Lazy Majority" Equilibrium

**Attack:** Curators will just copy the majority vote (or whale vote) without checking facts to win rewards.
**Defense:** **Commit-and-Reveal Voting** prevents copying. **The Shark (Diligent Challenger)** punishes rubber-stamping by finding the one false article they approved and seizing their stake.

### 2. The "Subreddit War" (Echo Chambers)

**Attack:** A "Conspiracy Pool" will successfully curate lies because their policy allows it.
**Defense:** **Global Accuracy vs. Local Relevance.** A pool can have a biased _Relevance_ policy, but _Accuracy_ is a global standard enforced by the cross-pool Kleros court. You can curate "Relevant Conspiracy Theories," but you cannot tag them as "Accurate" without being slashed.

### 3. The "Post-Truth" Apathy

**Attack:** Users don't care about truth; they want dopamine.
**Defense:** **Feature, not Bug.** The protocol is middleware. It provides the "Truth Supply Chain." If a consumer app wants to sell truth (like The Economist), we enable it. We don't force users to eat their vegetables, but we label the junk food.

### 4. The "Boring Dystopia" (Liquidity Crisis)

**Attack:** Low-stakes lies will survive because no one bothers to challenge them.
**Defense:** **Low Stake = Low Signal.** The Trust Score is `f(Stake, Time)`. An article with a $5 stake is treated as "Noise" by the interface, regardless of age. Apathy results in invisibility, not validation.

### 5. The "Oracle Capture" (51% Attack)

**Attack:** A billionaire buys 51% of Kleros tokens to force false verdicts.
**Defense:** **Economic Suicide & Forking.** Buying 51% is prohibitively expensive (slippage). If successful, the token value collapses (attacker burns their own money). If they persist, the community forks to a new token, leaving the attacker ruling a dead chain.

### 6. The "Rich Get Richer"

**Attack:** Competent curators accumulate all the capital, forming an oligarchy.
**Defense:** **Utilitarian Efficiency.** We optimize for Truth Quality, not Curator Equality. If BlackRock is the best truth-checker, society benefits. Also, **Reputation as Capital** lowers the barrier for cash-poor experts.

### 7. The "Chilling Effect" (Liability)

**Attack:** Staking on truth exposes curators to libel lawsuits.
**Defense:** **Pooled Staking.** Curators stake on a _Topic Pool_, not specific items. The protocol randomly drafts them (Jury Duty). This randomness creates "Herd Immunity" against targeted liability.

### 8. The "Meta-Curation" Trap

**Attack:** The Protocol is neutral, but the Interface (Wallet/App) re-centralizes control.
**Defense:** **Middleware Resilience.** The Protocol provides the "Sanity Check." Users can always bypass a biased interface to check the raw chain. We provide the "Base Reality," even if apps tint it.

### 9. The "Deflationary Spiral" (No Yield in Peacetime)

**Attack:** If there are no lies, there are no disputes, so curators leave.
**Defense:** **Advertising as Proof of Truth.** Honest advertisers stake on their claims. This provides a constant stream of "Peacetime Yield" for curators (verifying commercial claims) even when political misinformation is low.

### 10. The "Toxic Content" Trap

**Attack:** Permissionless publishing means hosting hate speech/illegal content.
**Defense:** **Protocol vs. Interface.** The Protocol is the Internet (neutral pipe); the Interface is the Browser (filter). Interfaces can block toxic pools to comply with local laws without compromising global censorship resistance.

### 11. The "Self-Fulfilling Prophecy" (Mediocrity)

**Attack:** Jurors vote for "Consensus" (Conventional Wisdom), crushing nuanced/surprising truth.
**Defense:** **The Lone Wolf Payoff.** A single expert can appeal against the herd. Each appeal raises stakes. If the expert wins the final ruling, they take the entire herd's stake. The threat of this "Jackpot" forces jurors to look beyond lazy consensus.

### 12. The "Context Collapse" (Epistemic Vacuum)

**Attack:** Malicious authors submit technically true but misleadingly vague statements ("Prices rose 5%").
**Defense:** **Vagueness = Rejection.** If a claim lacks necessary context (timeframe, definition) to be falsifiable, the protocol rejects it. The system enforces **Semantic Precision**. Authors must be hyper-specific ("US CPI rose 5% in Jan 2024") to get verified. Ambiguity is punished as severely as falsehood.

### 13. The "Frozen Truth" (Temporal Decay)

**Attack:** Truth changes (e.g., science evolves), but the blockchain is immutable. The ledger becomes a graveyard of outdated facts.
**Defense:** **Truth Decay = Profit Opportunity.** Validation is not a lifetime warranty. If a fact changes, the old claim becomes false. This creates a bounty opportunity for a Challenger to debunk it. Authors are incentivized to **withdraw** (un-stake) claims that are becoming obsolete to save their capital. The repository self-cleans: dead truths are eaten or withdrawn; only living truths remain staked.

### 14. The "Attention Arbitrage" (Vampire Attack)

**Attack:** Vampires scrape the verified data for free and monetize it with ads, paying nothing to the protocol. Stakers go bankrupt.
**Defense:** **Curation as Public Infrastructure.** We accept this is a public good.

1.  **The Truth Automata:** We built a machine that efficiently converts Funding → Truth. Philanthropists, NGOs, and States will fund this just as they fund Wikipedia or clean water.
2.  **Vampires are Distributors:** If a Vampire site distributes our truth to 100M people, they are helping us win the information war.
3.  **Sustainability:** The system is funded by a mix of "Advertiser Staking" (commercial utility) and "Public Funding" (social utility). We don't need to capture all the value; we just need to fund the machine.

### 15. "Consensus ≠ Correctness" (Ambiguous Questions / Legal Semantics)

**Attack:** In Schelling-style juries (and many prediction market resolution systems), voters maximize _coherence_ with other voters, not truth. When questions are ambiguous or require domain expertise (legal definitions, subtle semantics), the equilibrium can converge on a lazy or naive interpretation rather than the correct outcome.
**Defense:** The system must treat _question design_ as first-class:

1.  **Semantic Precision / Claim Templates:** Claims must be falsifiable and well-posed (timeframe, definitions, sources). Under-specified claims are rejected/slashable instead of forcing jurors to guess.
2.  **Topic Pools + Reputation:** Jurors are drawn from staked pools and reputation-weighted over time, creating decentralized pre-selection without a central gatekeeper.
3.  **Appeals + Lone Wolf Payoff:** If a lazy majority converges on the wrong interpretation, expert minorities can profitably appeal; higher stakes attract more expertise (high-court effect).
4.  **Policy-defined Domains:** When a dispute is inherently normative (e.g., “what counts as X under policy”), jurors adjudicate _policy compliance_, not metaphysical truth.

---

## ⚠️ Section 2: Open Attack Vectors

_No open vectors currently tracked. Add new attacks here as they come up._
