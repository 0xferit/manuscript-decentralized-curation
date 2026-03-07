# Manuscript Additions and Revisions: Decentralized Curation — A 7-Part Series

---

## 1. Scope and Assumptions

*[To be inserted after Section 1.3 Threat Model]*

Before diving into mechanism design, it is worth making explicit what this paper takes as given, what it designs, and where the boundaries lie. Every system rests on assumptions. The honest thing to do is name them.

### Assumption 1: Trustless Arbitration Exists as an External Dependency

This paper does **not** design a Decentralized Dispute Resolver (DDR). It designs the **curation layer** that feeds disputes into a DDR. The DDR — we use [Kleros](https://kleros.io/whitepaper.pdf) as the reference implementation — is treated as a black box that accepts a well-formed dispute (claim, evidence, resolution criteria) and returns a verdict.

This is a meaningful dependency, and it requires a defense, because the DDR itself relies on Schelling-point coordination among jurors — and this paper's relevance mechanism **also** uses Schelling games (the coherence game in Part 5). We are building on Schelling coordination at two layers. That demands honesty about what Schelling coordination actually claims.

**What Schelling coordination does NOT claim:** It does not claim that consensus equals truth. A room full of people can coordinate on a wrong answer if the wrong answer is more obvious than the right one.

**What Schelling coordination DOES claim:** When a question is **well-posed** — falsifiable, with clear resolution criteria — then "correct" becomes the natural focal point, because it is the easiest answer to coordinate on. If I ask "Did Company X report revenue above $1B in Q3 2025, per their SEC filing?", the correct answer is the Schelling point because it is verifiable by anyone willing to look. Coordinating on the wrong answer requires explicit collusion; coordinating on the right answer requires only that each juror independently checks the evidence.

This is precisely why **Principle 3 (Semantic Precision)** exists. Semantic precision is not a stylistic preference — it is a **game-theoretic requirement**. Well-posed questions make the Schelling focal point align with correctness. Poorly-posed questions make it align with whatever is most "obvious," which may be wrong.

When a question is **not** well-posed — ambiguous, under-specified, or lacking clear resolution criteria — the correct Schelling focal point is **"Under-specified."** The system does not force jurors to guess True or False on a bad question. It gives them a third option that is itself the natural focal point for ambiguous inputs.

Two additional mechanisms bound the failure modes:

- **Infinite appeals** provide error-correction within the game. If a Schelling outcome is wrong, the appeal system allows escalation (see Section 4 below). Appeals must be theoretically infinite — no hard cap — because a known final round degrades via backward induction. Exponentially escalating costs make appeals self-limiting in practice.
- **Forking** provides the ultimate backstop **outside** the game. If the DDR itself is captured or systematically corrupted, the community can fork the protocol, taking the honest participants and their stakes to a new chain. This is covered in detail in Part 7 and formalized in Section 3 below.

The [Ohio State socio-legal case study of Kleros](https://moritzlaw.osu.edu/sites/default/files/2022-08/10-%20BERGOLLA%2055-98.pdf) (Bergolla, Seif & Eken, 2022) and the [Columbia Science and Technology Law Review analysis](https://journals.library.columbia.edu/index.php/stlr/blog/view/84) both document real limitations of Schelling-point adjudication — juror passivity, coordination failures, interface friction. We do not dismiss these findings. We argue that semantic precision and infinite appeals **mitigate** (not eliminate) the failure modes they identify.

### Assumption 2: Blockchain Liveness and Smart Contract Correctness

Standard cryptographic assumption. The protocol assumes the underlying blockchain (Ethereum or equivalent) provides liveness, finality, and correct execution of deployed smart contracts. If the base layer fails, everything above it fails. This is not unique to this design — it is shared by every DeFi protocol, every DAO, every on-chain system.

### Assumption 3: Evidence Authenticity Is Unverifiable On-Chain

The protocol can verify that evidence was **submitted** (timestamped, hashed, recorded on-chain). It **cannot** verify that the evidence is **genuine**. A challenger can submit a fabricated document. A claim author can cite a real-looking but doctored study.

This is explicitly acknowledged as a trust assumption. The protocol's defense is **adversarial**: if fabricated evidence is submitted, the opposing party has the incentive and the opportunity to submit counter-evidence exposing the fabrication. The DDR jurors evaluate both. But the protocol itself has no oracle for "is this PDF real?" — and pretending otherwise would be dishonest.

This limitation is shared by every dispute resolution system, including traditional courts. Courts rely on rules of evidence, expert testimony, and cross-examination to surface fabrication. The DDR relies on adversarial incentives and juror judgment. Neither is perfect.

### Assumption 4: Rational Actors with Bounded Information

Participants are **economically rational** — they respond to incentives, seek to maximize expected value, and avoid negative-expected-value actions. They are **not** omniscient. They have bounded information, bounded computational capacity, and bounded attention.

The system is designed for **rational adversaries**, not for irrational ones. An attacker who is willing to burn $10M to destroy a $1M protocol cannot be stopped by mechanism design — only by making the protocol not worth attacking in the first place. The threat model (Section 1.3) makes this explicit.

This assumption also means the system does **not** require altruism. Curators do not need to care about truth for its own sake. They need to find it profitable to curate honestly. If the incentives are right, honest behavior emerges from self-interest. That is the entire point.

---

## 2. Why This Is Not a TCR

*[To be inserted in Part 3 or Part 4]*

Token-Curated Registries are the most direct ancestor of this design. [Mike Goldin's 2017 whitepaper](https://medium.com/@ilovebagels/token-curated-registries-1-0-61a232f8dac7) proposed using stake-weighted curation to maintain quality lists without centralized gatekeepers. The idea was elegant: token holders stake to list items, challengers stake to dispute them, and the market for the token reflects the registry's quality.

TCRs were supposed to be the decentralized replacement for curated lists — ad networks ([adChain](https://adtoken.com)), token directories, even [scholarly journals](https://onlinelibrary.wiley.com/doi/abs/10.1002/leap.1302) (Kosmarski & Gordiychuk, 2020). Most of them failed. The [Gitcoin analysis of TCR mechanisms](https://gitcoin.co/mechanisms/token-curated-registry) documents the structural issues. [ChainScore Labs](https://www.chainscorelabs.com/en/blog/prediction-markets-and-information-theory/decentralized-information-markets/why-token-curated-registries-incentivize-mediocrity-not-excellence) has argued convincingly that TCRs "incentivize mediocrity, not excellence."

This design shares DNA with TCRs but addresses their known failure modes. Here is how.

### 2.1 Variable Bounties vs. Fixed Deposits

In a classic TCR, the entry deposit is **protocol-fixed**. Every item costs the same to list, regardless of how important or contested it is. This creates a flat signal: a $100 deposit on "the sky is blue" looks identical to a $100 deposit on "this experimental drug cures cancer."

In this design, the author's **bounty is variable** and directly signals conviction. A $10 bounty on a trivially true claim carries almost no weight. A $10,000 bounty on a contested claim carries enormous weight — because the author is putting real money behind their assertion. The **Confidence Score** reflects this: `f(bounty, time uncontested, validator signal)`. Low bounties never mature into high-confidence claims regardless of how long they sit unchallenged. The bounty is not just an entry fee — it is a **credibility signal**.

### 2.2 No "Listed by Default" Problem

In TCRs, entries are **added unless challenged** — challenge-based exclusion. This creates a toxic default: if no one bothers to challenge a low-quality entry, it becomes "listed," and listing implies endorsement. The result is that low-stakes lists fill with garbage that no one has the incentive to clean up, as early TCR experiments like adChain demonstrated.

Here, claims **start with no confidence**. They must **earn** confidence through bounty size, time surviving challenges, and validator attention. An unchallenged low-stake claim does not silently become "truth" — it remains low-confidence noise. The system's default state is **skepticism**, not endorsement.

### 2.3 Pooled Staking vs. Per-Item Staking

TCR curators must individually evaluate and stake on **every item**. This creates a participation bottleneck: as the registry grows, the cost (in time and attention) of evaluating every entry exceeds the expected reward. The result is the **low-participation equilibrium** that killed adChain — rational curators stop paying attention, and the registry degrades.

In this design, curators stake on **pools** (topics, domains, subject areas), and the protocol randomly drafts them for specific claims within those pools. Curators are performing **portfolio-level duty**, not per-claim research. You do not need every curator to care about every claim — you need enough curators in each pool to staff the claims that arise in that pool. This directly addresses the participation problem by making curation economically viable as a sustained activity rather than a per-item chore.

### 2.4 Separation of Accuracy and Relevance

TCRs conflate "should this be in the list?" into a **single binary vote**. This forces curators to simultaneously evaluate truthfulness, importance, and appropriateness — all in one up-or-down decision. The result, as [ChainScore Labs argues](https://www.chainscorelabs.com/en/blog/prediction-markets-and-information-theory/decentralized-information-markets/why-token-curated-registries-incentivize-mediocrity-not-excellence), is that safe, mediocre entries pass while genuinely important but controversial entries get challenged for the wrong reasons.

This design **separates** the two questions:
- **"Is it true?"** — Global, binary, resolved by evidence and DDR adjudication. This has a ground truth anchor.
- **"Is it important?"** — Local, non-binary, resolved by the coherence game within specific curation pools. This is explicitly subjective and pool-specific.

A claim can be true but irrelevant to a specific pool (accurate but boring). A claim can be highly relevant but contested on accuracy (important and wrong). By separating these dimensions, curators can do their actual job — surface what matters — without being forced to play amateur fact-checker on every entry.

Kosmarski & Gordiychuk (2020) [proposed TCRs for scholarly journals](https://onlinelibrary.wiley.com/doi/10.1002/leap.1302) with similar intuitions about decentralizing peer review. Their framework identified the right problems — editorial bias, reviewer incentive misalignment, lack of rewards — but inherited the structural limitations of the TCR model. This work builds on their insights while addressing the failure modes they identified: variable stakes replace fixed deposits, pooled curation replaces per-item voting, and the accuracy/relevance separation gives the mechanism enough dimensionality to handle scholarly claims.

---

## 3. The Economics of Forking: Why Capture Destroys the Prize

*[Revised — replaces/expands Challenge 1 in Part 7]*

Forking is the nuclear option. It is expensive, disruptive, and destroys network effects. **That is the point.** Its existence as a credible threat is what makes the attack economically irrational.

### 3.1 The Simple Model

Let:
- **V** = total value of the protocol (token market cap + utility value from integrations, users, curated knowledge)
- **C** = cost of acquiring 51% of governance/arbitration tokens
- **V_post** = value of the captured chain after the community forks away

The attacker's expected payoff:

> **E[attacker] = V_post − C**

### 3.2 Why V_post ≈ 0

The protocol's value does not live in the code. The code is open source and forkable — anyone can copy it in an afternoon. The value lives in:

- **Users** who submit and consume curated claims
- **Curators** who stake, validate, and maintain knowledge pools
- **Applications** that integrate the curated knowledge layer
- **Network effects** — the accumulated history of adjudicated claims, confidence scores, and reputation

Upon capture, honest participants fork to a new chain. The curators migrate. The applications re-point their integrations. The users follow the curators and the applications. The attacker is left controlling the code and the captured chain — but with no users, no curators, no integrations. An empty protocol with a captured governance token.

Therefore **V_post << V**, and for most realistic scenarios, **V_post ≈ 0**.

So **E[attacker] = 0 − C = −C**. The attack is pure economic loss.

### 3.3 Empirical Precedent: Ethereum / Ethereum Classic (2016)

After the DAO hack, the Ethereum community faced exactly this choice. They forked. The result, as documented on [Arkham Research](https://info.arkm.com/research/ethereum-vs-ethereum-classic):

- **ETH** (the fork with community support): market cap >$280B.
- **ETC** (the "original" chain the community abandoned): market cap <$3.5B — roughly **1.2%** of ETH's value.

ETC subsequently suffered [multiple 51% attacks](https://info.arkm.com/research/ethereum-vs-ethereum-classic) — in January 2019 ($1.1M in double-spends) and three more in August 2020 ($5.6M+ in losses) — confirming that a chain without its community becomes a security liability, not an asset.

The lesson is stark: **the value lives in the community, not the chain.** Capturing the chain without the community is buying an empty castle and then watching it get looted.

### 3.4 The Triple Threat

Three forces compound to make capture irrational:

1. **Economic suicide.** The attacker spends C to control something worth ≈ 0 post-fork. This is not a profitable trade under any realistic assumption about V_post.

2. **Acquisition slippage.** Acquiring 51% of governance tokens on open markets triggers massive price increases due to thin order books. The actual cost C is far higher than `0.51 × spot_price × total_supply` would suggest. Illiquidity is a feature, not a bug — it makes the attack progressively more expensive as the attacker buys.

3. **Community coordination advantage.** The honest majority has a natural Schelling point for coordination: "fork away from the attacker." This is **easier** to coordinate on than the attack itself, because the attack requires secrecy (to avoid front-running) while the defense is public and obvious.

### 3.5 Caveat: Forking Is Not Free

Forking destroys network effects temporarily. It splits liquidity. It requires community coordination — someone has to deploy the fork, someone has to build or re-deploy the frontend, applications need to update their integrations. It creates confusion about which chain is "real" (for a while).

Forking is a **nuclear option**, not a routine defense. The protocol's first line of defense is the economic incentives within the game (honest curation is profitable, dishonest curation is punished). The second line is the appeal system. Forking is the third line — the backstop that exists to deter the attacks that the first two lines cannot handle.

The point is not that forking is painless. The point is that its existence as a **credible threat** makes the attack irrational. The attacker must believe that the community will **not** fork — and given the Ethereum/ETC precedent, that belief is hard to sustain.

---

## 4. Infinite Appeals and Backward Induction

*[To be added to Part 5 or as a subsection of the Lone Wolf discussion]*

Why can't we just set a maximum number of appeal rounds — say, 5 — and call it done?

Because of **backward induction**.

### 4.1 The Problem with a Known Final Round

Suppose there are exactly **N** appeal rounds, and everyone knows it.

In round N, jurors know their verdict is **definitive**. There is no future appeal. No Lone Wolf can overturn them later. The economic pressure that keeps jurors honest — "if I vote incorrectly, someone will appeal and I'll lose my stake" — **disappears** on the last round.

Round N degenerates. Jurors in round N face weaker incentives to research carefully, because their only risk is intra-round (being in the minority of this round), not inter-round (being overturned on appeal). The error-correction mechanism is disabled.

Now consider round N−1. Participants in round N−1 know that round N is degenerate. They know that an appeal to round N will not reliably correct errors. So the threat of appeal is weaker in round N−1 too. And round N−2 participants know round N−1 is degraded. The degradation **cascades backward** through every round.

This is the standard backward induction problem from game theory. If the end of the game is known, strategic behavior unravels from the end.

### 4.2 The Solution: Theoretically Infinite Appeals

Appeals must always be **possible** — there must never be a round that participants know is final.

In practice, exponentially escalating costs make the process self-limiting:

| Round | Stake Required |
|-------|---------------|
| 1     | S             |
| 2     | 2S            |
| 3     | 4S            |
| k     | 2^(k−1) × S  |

At some point, no rational actor is willing to escalate further. A dispute over a $100 claim will not see a round requiring $10,000 in stakes. The process terminates **economically**, not structurally.

The key insight: **economic termination preserves incentives; structural termination destroys them.** When the game might always continue, every round's jurors face the threat of being overturned. When the game has a known endpoint, that threat evaporates at the boundary and the damage propagates inward.

This is directly analogous to the **iterated prisoner's dilemma** with an uncertain end date. Cooperation is sustainable when the game might continue indefinitely. Cooperation collapses when the end is known. Robert Axelrod demonstrated this decades ago — we are applying the same logic to dispute resolution.

The practical implication for protocol design: **never hard-code a maximum appeal count.** Let the staking schedule do the work. The game ends when no one is willing to pay — not when the protocol says "time's up."

---

## 5. Related Work

*[To be added as a new section, after Part 2 or as an appendix]*

This section positions the design relative to the existing literature. The goal is not comprehensiveness but clarity: where does this work sit, what does it borrow, and where does it diverge?

### 5.1 Mechanism Design for Public Goods

The idea that self-interest can be harnessed for socially optimal outcomes in public goods provision was formalized by [Groves & Ledyard (1977)](https://www.jstor.org/stable/1914085). Their paper solved the classical free rider problem — the assumption, dominant since [Samuelson (1954)](https://www.jstor.org/stable/1925895), that public goods would always be undersupplied because rational agents conceal their true preferences. Groves-Ledyard constructed a class of allocation-and-tax mechanisms where truthful preference revelation is the Nash equilibrium: each consumer's tax includes a penalty proportional to how much their reported valuation deviates from the mean of the others' reports. Lying costs more than truth-telling. Both Welfare Theorems hold.

Curated knowledge is a public good. It is non-excludable (anyone can consume it once produced) and non-rivalrous (one person's use does not diminish another's). The classical prediction applies: without intervention, curation will be undersupplied. Rational agents will consume curated knowledge without contributing to its production — the "lazy curator" problem this protocol explicitly addresses.

This protocol applies the Groves-Ledyard insight to knowledge production. The coherence game penalizes curators whose relevance assessments deviate excessively from the group mean — structurally analogous to the quadratic deviation penalty in the Groves-Ledyard tax rule. The bounty-and-challenge mechanism for accuracy makes it individually rational to verify rather than free-ride, because challengers capture the stakes of those who curate dishonestly. In both cases, the mechanism designer does not need to observe truth directly. The mechanism makes truth-telling the cheapest strategy.

The key difference: Groves-Ledyard assume a single, well-defined public good with cardinal preferences. Curation operates over a high-dimensional claim space with two distinct quality dimensions (accuracy and relevance), adversarial participants, and no central allocator. The mechanism design challenge is correspondingly harder — but the foundational insight is the same.

### 5.2 Token-Curated Registries

[TCRs (Goldin, 2017)](https://medium.com/@ilovebagels/token-curated-registries-1-0-61a232f8dac7) are the most direct ancestor. They proposed stake-weighted curation for maintaining quality lists — a powerful idea that struggled in practice. The [Gitcoin mechanism analysis](https://gitcoin.co/mechanisms/token-curated-registry) provides a comprehensive overview of TCR mechanics and deployment history. adChain, the first live TCR (2018), suffered from low participation and curator apathy. [Kosmarski & Gordiychuk (2020)](https://onlinelibrary.wiley.com/doi/10.1002/leap.1302) proposed TCRs for scholarly journals, identifying real problems in peer review incentives but inheriting TCR structural limitations.

This work generalizes TCRs from binary list inclusion to **structured claims with evidence**, separates accuracy from relevance, replaces fixed deposits with variable bounties, and introduces pooled staking to address the participation problem (see Section 2 above for the full comparison).

### 5.3 Kleros and Decentralized Dispute Resolution

The protocol uses Kleros-style DDR as a building block. The [Kleros whitepaper](https://kleros.io/whitepaper.pdf) (Lesaege, Ast & George, 2019) describes the Schelling-point jury mechanism, commit-reveal voting, and the appeal system. The [Ohio State socio-legal case study](https://moritzlaw.osu.edu/sites/default/files/2022-08/10-%20BERGOLLA%2055-98.pdf) (Bergolla, Seif & Eken, 2022) provides the most rigorous empirical analysis of Kleros to date — introducing the concept of the "decentralized sheriff" while documenting adoption barriers including juror interface friction, PNK token economics, and trust formation challenges. The [Columbia STLR analysis](https://journals.library.columbia.edu/index.php/stlr/blog/view/84) evaluates Kleros through a legal lens, questioning whether game-theoretic incentives can substitute for procedural safeguards.

We take these critiques seriously. The curation protocol is designed to **mitigate** known DDR failure modes: Semantic Precision (Principle 3) constrains the input quality so jurors receive well-posed questions rather than ambiguous ones. Infinite appeals provide error-correction. Forking provides an exit if the DDR itself is captured. But we do not claim these mitigations are complete — the DDR remains a trust assumption (see Section 1, Assumption 1).

### 5.4 Peer Prediction Mechanisms

Peer prediction ([Jurca & Faltings, 2014](https://arxiv.org/abs/1401.3451)) elicits truthful reports **without verification** by comparing agents' reports against each other. The core idea: if your report about X is statistically consistent with another independent reporter's observation of X, you are probably telling the truth.

Peer prediction works best when ground truth **exists** but is **unobservable** by the mechanism designer — e.g., rating a product you actually used, where the platform cannot directly observe your experience but can compare your rating to other buyers'.

Decentralized curation faces a harder problem. Ground truth is sometimes genuinely **contested** — two honest people examining the same evidence may disagree. And some claims require evaluating external evidence, not just reporting private observations. This is why the protocol needs the evidence-and-dispute layer (claim → challenge → DDR adjudication) rather than purely statistical comparison between curators. The relevance dimension, however, is closer to a peer-prediction setting — curators' relevance assessments are compared against each other in the coherence game, which borrows the core peer-prediction insight.

### 5.5 The Verifier's Dilemma

[Zhao et al. (2025)](https://arxiv.org/html/2406.01794v2) formalize Byzantine-robust peer prediction for decentralized verification — addressing the same core question: **how do you incentivize honest verification when skipping verification is cheaper?** Their framework shows that combining capture-the-flag designs with peer prediction techniques can resolve the Verifier's Dilemma even when cheating provers are extremely rare.

The key difference: their framework assumes verification is a **technical/computational task** with a well-defined correct output (valid proof or invalid proof). Curation involves **human judgment** — evaluating evidence quality, assessing claim specificity, weighing relevance. This requires the separation into accuracy (where judgment is constrained by evidence and adjudicated by a DDR) and relevance (where judgment is explicitly subjective and resolved by coherence games). The Verifier's Dilemma literature informs our design but does not directly solve our problem.

### 5.6 Decentralized Science (DeSci)

The DeSci movement ([Weidener & Spreckelsen, 2024](https://www.frontiersin.org/journals/blockchain/articles/10.3389/fbloc.2024.1375763/full), Frontiers in Blockchain) has explored blockchain-based scientific infrastructure — funding (VitaDAO), publishing, data sharing, and peer review. Their comprehensive survey defines DeSci's shared values: transparency, accessibility, reproducibility, and community governance.

Most DeSci projects, however, focus on **access and funding** rather than **epistemic quality**. They solve "who gets to publish?" and "who gets funded?" but not "is this claim actually true?" The incentive-compatible verification layer — the part that makes honest evaluation profitable and dishonest evaluation costly — is largely absent from current DeSci infrastructure. This work directly addresses that gap. A decentralized curation protocol could serve as the **verification layer** for DeSci, providing the incentive-aligned quality signal that DeSci's access and funding mechanisms currently lack.

### 5.7 Prediction Markets

Prediction markets (Augur, Polymarket, Metaculus) aggregate information through price discovery. They work brilliantly for events with **clear resolution criteria** and a **future resolution date** — elections, sports outcomes, ship arrival times.

This work addresses a different problem: curating claims about **the present and past**, where resolution requires evidence evaluation rather than waiting for an outcome. "Did Company X dump toxic waste in River Y in 2024?" cannot be resolved by waiting — it requires someone to investigate, produce evidence, and have that evidence evaluated.

The **relevance dimension** has no prediction-market analog at all. Prediction markets do not ask "is this question important?" — they only ask "what is the probability of this outcome?" A curation protocol must handle both dimensions: what is true, and what matters.

---

## 6. The Truth Post: Lessons from an MVP

*[Revised — replaces the brief mention in Part 4]*

The Truth Post launched in 2023 as a minimal viable implementation of the core submission-and-challenge flow. It is worth being honest about what happened.

### 6.1 What Was Built

The Truth Post implemented:
- **Author submission with staked bounties.** Users could submit claims and attach a token bounty as a credibility signal.
- **Challenger disputes routed to Kleros.** Anyone could challenge a claim by staking tokens, triggering a dispute in the Kleros court system.

This was the **bare minimum** of the protocol — the accuracy layer without the relevance layer.

### 6.2 What Was NOT Built

The MVP did not implement:
- **Relevance curation** (the coherence game described in Part 5)
- **Author rewards** from a protocol treasury
- **The Confidence Score** system
- **Pooled staking** for curators
- **Multiple frontends** or interface redundancy

### 6.3 What Happened

The MVP did not achieve sustained usage. Activity was sparse — a handful of claims, fewer challenges. The web frontend eventually stopped loading, likely due to a subgraph indexing failure (a common failure mode for dApps that depend on The Graph for on-chain data). The project was abandoned due to maintenance overhead.

This is not a comfortable admission in a whitepaper. But the alternative — pretending the MVP validated the design — would be dishonest, and this paper is about building systems that are hostile to dishonesty.

### 6.4 Lessons Learned

**1. The cold-start problem is real.** Without a critical mass of curators and challengers, the system lacks the economic activity needed to generate meaningful confidence signals. A claim with zero challenges and zero validators has a confidence score of approximately zero — which is correct, but useless. The system needs enough participants to generate signal before it becomes useful, and it needs to be useful to attract participants. This is a classic two-sided marketplace problem, and "build it and they will come" does not solve it.

**2. Relevance curation may be the engagement driver.** Accuracy alone — "is this true or false?" — generates a trickle of activity. Most claims are not interesting enough to challenge. The relevance layer — which turns the system into something users actively interact with, ranking and surfacing what matters — may be **necessary for bootstrapping**. People do not visit a site to verify boring truths. They visit to find out what is important. The relevance layer is what makes the protocol useful as a **product**, not just a verification mechanism.

**3. Infrastructure maintenance matters.** A decentralized protocol is only as good as its off-chain infrastructure — indexers, frontends, APIs. The Truth Post had a single frontend operated by the development team. When the subgraph broke, the entire user-facing product went down. This is a single point of failure that contradicts the protocol's own design philosophy. The lesson: the protocol must be designed so that **anyone** can deploy a frontend, and no single frontend failure kills the system. Protocol-vs-interface separation is not optional — it is a survival requirement.

These lessons directly inform the full design in this manuscript:
- **Pooled staking** reduces cold-start friction by letting curators commit to domains rather than individual claims.
- **The Confidence Score** makes the system useful even with thin participation — a single unchallenged claim with a large bounty still provides a meaningful (if incomplete) signal.
- **Protocol-vs-interface separation** ensures that the protocol survives any individual frontend's failure. If one explorer goes down, others continue operating.

---

## 7. Advertising as Proof of Truth

*[Revised — expanded version for Part 7]*

Here is an observation: advertisers already make claims about their products. "Longest battery life in its class." "Zero sugar." "Clinically proven." These claims are currently verified (if at all) by regulatory agencies operating at glacial speed, or by journalists who may or may not bother.

What if the verification mechanism was **built into the advertising itself**?

### 7.1 The Mechanism

1. An advertiser makes a **verifiable claim** about their product: *"Battery lasts 48 hours under standard use conditions (ISO 12345)."*
2. The advertiser **stakes tokens** on this claim. The stake amount signals conviction — a $50,000 stake on a product claim is a very different signal than a $50 stake.
3. **Anyone can challenge** the claim. If the challenge succeeds (independent testing shows the battery does not last 48 hours under ISO 12345 conditions), the advertiser **loses their stake** — distributed to the challenger and the protocol.
4. If the claim stands unchallenged or **survives challenges**, the advertiser recovers their stake minus a small protocol fee.

### 7.2 Why This Works

**Honest advertisers pay almost nothing.** Their stake is returned. The protocol fee is the cost of verified credibility — far cheaper than a Super Bowl ad, and far more durable. A staked claim that has survived multiple challenges is worth more than any amount of traditional advertising spend, because it carries **adversarially-tested credibility**.

**Dishonest advertisers are punished.** False claims become bounties for challengers. The more extravagant the lie, the larger the bounty. The system creates a **market for debunking** — anyone with testing equipment and a financial incentive can challenge dishonest advertising. The advertiser is literally funding their own exposure.

**Trivially true claims are possible but useless.** An advertiser could stake on "our product contains atoms" — technically true, economically unchallenged, completely meaningless. The market naturally selects for claims that are both **true AND informative**, because those are the only claims worth staking on. No one gains marketing value from proving their product contains atoms. The incentive is to stake on the strongest true claim you can defend — which is exactly the kind of claim consumers want to see.

### 7.3 Temporal Validity

Claims are staked with a **validity window**. "Battery lasts 48 hours" applies to the current product version, identified by model number and firmware version. If the product changes — new model, updated firmware, different manufacturing process — the advertiser must **withdraw or update the claim**. An outdated claim on a changed product becomes a target for challengers, because the original claim may no longer be true of the current product.

This handles the temporal decay problem: product claims do not become eternal truths. They are living assertions, maintained by the advertiser's continued stake and validated by the ongoing threat of challenge.

### 7.4 Caveats and Alternatives

This mechanism is **speculative**. It requires market validation. Several open questions remain:

- **Will advertisers actually participate?** The mechanism requires a cultural shift from "advertising as persuasion" to "advertising as verifiable assertion." This may happen in some markets (consumer electronics, supplements) faster than others (luxury goods, entertainment).
- **Will challengers emerge?** The mechanism depends on a functioning market for challenge — people willing to invest in testing and verification for the expected bounty. Consumer protection organizations, testing labs, and investigative journalists are natural participants, but their willingness to engage with on-chain mechanisms is untested.
- **Regulatory interaction.** How does staked advertising interact with existing advertising regulations (FTC in the US, ASA in the UK)? Does a staked claim provide legal cover, or does it create additional liability?

Advertising-as-proof-of-truth is presented as **one possible sustainability path**, not the sole funding model. Other paths include:

- **Public-good funding:** Grants from protocol treasuries, Gitcoin rounds, or ecosystem funds that value the knowledge layer as infrastructure.
- **Integration fees:** Downstream consumers of the curated knowledge layer — news aggregators, research platforms, AI training pipelines — pay fees for access to the curated, confidence-scored dataset.
- **Protocol fees:** Small fees on every claim submission, challenge, and appeal that accumulate in a protocol treasury for ongoing development.

The honest assessment: the protocol needs **at least one** of these revenue streams to be sustainable. Advertising-as-proof-of-truth is the most novel and potentially the most lucrative. But it is also the most uncertain. Building the protocol to support multiple funding models is the prudent approach.
