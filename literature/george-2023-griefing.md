# George (2023): An Analysis of Griefs and Griefing Factors

**Citation**: George, W. (2023). An analysis of griefs and griefing factors. *Frontiers in Blockchain*, 6. doi:10.3389/fbloc.2023.1137155

## Core thesis

Provides a formal framework for measuring the cost of attacks on cryptoeconomic mechanisms. The **griefing factor** (GF) quantifies how much harm an adversary can inflict per unit of self-cost: GF = harm_victim / cost_attacker. A mechanism with GF <= 1 ensures the attacker pays at least as much as the victim loses.

## Key concepts

- **Griefing factor**: the ratio of harm to attack cost. The lower the GF, the more expensive it is to attack. GF = 1 means the attacker pays dollar-for-dollar. GF >> 1 means the attack is cheap relative to the damage.
- **Griefs**: categorized by type (e.g., stake-based, vote-based, Sybil). Each type has a characteristic GF range.
- **Design target**: mechanisms should aim for GF <= 1 for all attack vectors. If some vectors have GF > 1, the mechanism has a known, bounded vulnerability.

## Connection to our paper

The framework supplies a possible metric for future analysis of our mechanisms. The manuscript does not establish a common griefing-factor bound across disputes and relevance attacks.

- **DDR disputes**: a griefing calculation must distinguish expected attacker cost from expected victim loss and include the specified fees, payout rules and adjudication error. A cost-to-harm ratio would be the inverse of GF as defined above.
- **Coherence game**: the paper reports relevance error and stake trajectories under specified collusion strategies. Its observed degradation range is not a measured GF=1 crossing or a security boundary; [Claim 3](../paper.qmd#curator-voting-strategy) also gives a profitable unilateral deviation without a colluding coalition.

## Key takeaways

1. GF can compare particular attacks when harm and cost use compatible definitions and assumptions.
2. Defining the metric does not compute it for this protocol. Attack-specific analysis remains necessary.
3. Legitimate correction and malicious disruption have different objectives; classify the action before interpreting the ratio.
