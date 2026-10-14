# Groves & Ledyard (1977): Optimal Allocation of Public Goods

**Citation**: Groves, T., & Ledyard, J. O. (1977). Optimal Allocation of Public Goods: A Solution to the "Free Rider" Problem. *Econometrica*, 45(4), 783-809.

## Core thesis

Proposes a decentralized allocation and taxation mechanism whose Nash-equilibrium outcomes are Pareto efficient under its assumptions. Its messages and quadratic transfers implement a public-goods allocation game; they are not a direct truthful-reporting rule for scalar assessments. Equilibrium efficiency should not be restated as a universal truth-telling guarantee. See the [original article](https://doi.org/10.2307/1912672).

## Key concepts

- **Free-rider problem**: in public goods provision, individuals have incentive to understate their valuation because they benefit from the good regardless of their contribution. This leads to underprovision.
- **Deviation penalty**: the cost imposed on an agent is a function of how much their reported preference deviates from the mean of others' reports. The quadratic transfer enters an agent's entire allocation problem. A penalty term alone does not prove that reporting a sincere scalar assessment is optimal.
- **Efficient equilibrium**: the mechanism targets efficient allocation without requiring the planner to observe private preferences. Its game and information assumptions matter to that result.

## Connection to our paper

We draw a structural parallel between the Groves-Ledyard deviation penalty and our coherence game's slashing mechanism:

- **Coherence-game deviation penalties**: the protocol penalizes some reports outside its coherence band, subject to the dispersion guard. That is a penalty for disagreement, not a proof of truthful incentives; [Claim 3](../paper.qmd#curator-voting-strategy) gives a unilateral report that increases the single-round reward below the guard in a single-asset analytical model. This is not a counterexample to the selected fixed per-seat fee; the two-asset game requires separate analysis.
- **Limited structural analogy**: Groves-Ledyard concerns public-goods allocation. The relevance mechanism uses a different reward and penalty rule for news scoring. Sharing a deviation-penalty idea does not transfer an equilibrium result.
- **Public goods framing**: in the closing section, we frame the allocation problem as optimization over a weight vector summing to 1. The Groves-Ledyard connection reinforces that the information problem (how do you know the right weights?) is upstream of the allocation problem.

## Key takeaway

The parallel motivates examining deviation penalties. It does not establish incentive compatibility of the coherence game; that requires an analysis of its own utilities, information and payment rules.
