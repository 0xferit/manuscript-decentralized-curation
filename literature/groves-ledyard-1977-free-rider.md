# Groves & Ledyard (1977): Optimal Allocation of Public Goods

**Citation**: Groves, T., & Ledyard, J. O. (1977). Optimal Allocation of Public Goods: A Solution to the "Free Rider" Problem. *Econometrica*, 45(4), 783-809.

## Core thesis

Proposes a mechanism for optimal public goods allocation that solves the free-rider problem. The key innovation is a **deviation penalty**: agents who deviate from the group's preferred allocation bear a cost proportional to their deviation. Under this mechanism, truthful revelation of preferences is a Nash equilibrium, achieving Lindahl pricing without requiring a central planner to know preferences.

## Key concepts

- **Free-rider problem**: in public goods provision, individuals have incentive to understate their valuation because they benefit from the good regardless of their contribution. This leads to underprovision.
- **Deviation penalty**: the cost imposed on an agent is a function of how much their reported preference deviates from the mean of others' reports. This creates incentive to report honestly: deviating is costly, and the cost is proportional to the deviation.
- **Lindahl equilibrium**: each agent pays a personalized price equal to their marginal valuation. Groves-Ledyard achieves this without requiring the planner to know valuations.

## Connection to our paper

We draw a structural parallel between the Groves-Ledyard deviation penalty and our coherence game's slashing mechanism:

- **Coherence-game deviation penalties**: the protocol penalizes some reports outside its coherence band, subject to the dispersion guard. That is a penalty for disagreement, not a proof of truthful incentives; [Claim 3](../paper.qmd#curator-voting-strategy) gives a profitable deviation below the guard.
- **Limited structural analogy**: Groves-Ledyard concerns public-goods allocation. The relevance mechanism uses a different reward and penalty rule for news scoring. Sharing a deviation-penalty idea does not transfer an equilibrium result.
- **Public goods framing**: in the closing section, we frame the allocation problem as optimization over a weight vector summing to 1. The Groves-Ledyard connection reinforces that the information problem (how do you know the right weights?) is upstream of the allocation problem.

## Key takeaway

The parallel motivates examining deviation penalties. It does not establish incentive compatibility of the coherence game; that requires an analysis of its own utilities, information and payment rules.
