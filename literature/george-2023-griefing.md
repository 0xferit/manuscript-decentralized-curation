# George (2023): An Analysis of Griefs and Griefing Factors

**Citation**: George, W. (2023). An analysis of griefs and griefing factors. *Frontiers in Blockchain*, 6. doi:10.3389/fbloc.2023.1137155

## Core thesis

Provides a formal framework for measuring the cost of attacks on cryptoeconomic mechanisms. The **griefing factor** (GF) quantifies how much harm an adversary can inflict per unit of self-cost: GF = harm_victim / cost_attacker. A mechanism with GF <= 1 ensures the attacker pays at least as much as the victim loses.

## Key concepts

- **Griefing factor**: the ratio of harm to attack cost. The lower the GF, the more expensive it is to attack. GF = 1 means the attacker pays dollar-for-dollar. GF >> 1 means the attack is cheap relative to the damage.
- **Griefs**: categorized by type (e.g., stake-based, vote-based, Sybil). Each type has a characteristic GF range.
- **Design target**: mechanisms should aim for GF <= 1 for all attack vectors. If some vectors have GF > 1, the mechanism has a known, bounded vulnerability.

## Connection to our paper

We use the griefing factor framework as the formal security metric for our mechanisms:

- **DDR disputes**: for a challenger attacking a true claim with p = 0.80 and S/B = 0.25, GF is approximately 37. The attacker pays 37x what the victim loses. This makes frivolous challenges extremely expensive.
- **For a legitimate challenger** disputing a false claim, the asymmetry is reversed: the false claim author pays more than the challenger risks. This is the intended incentive alignment.
- **Coherence game**: the colluding plurality threshold (~20-30% of stake) is the point where GF crosses 1 for coordinated attacks. Below that threshold, colluders lose more than they inflict; above it, they can redefine the coherent band.

## Key takeaways

1. GF provides a single number to compare mechanism security across designs. Useful for the simulation section.
2. The GF framework makes attack costs concrete and comparable. Reviewers can evaluate whether the mechanism is "secure enough" without running simulations.
3. The distinction between GF for legitimate challengers (low, by design) and GF for frivolous challengers (high, by design) is the core of the incentive argument.
