# Miller, Resnick & Zeckhauser (2005): Eliciting Informative Feedback: The Peer-Prediction Method

**Citation**: Miller, N., Resnick, P., & Zeckhauser, R. (2005). Eliciting Informative Feedback: The Peer-Prediction Method. *Management Science*, 51(9), 1359-1373.

## Core thesis

Proposes a mechanism for eliciting honest reports about subjective experiences (e.g., product quality) by scoring each report against a randomly selected peer's report. Under assumptions about signal correlation and proper scoring rules, truthful reporting is a Nash equilibrium, even without access to ground truth.

## Key concepts

- **Peer prediction**: your report is scored based on how well it predicts a randomly chosen peer's report. If agents' signals are correlated (they observe the same underlying quality), honest reporting maximizes expected score.
- **Proper scoring rules**: the scoring function must be "proper" (truthful reporting maximizes expected score given the agent's belief). Common examples: logarithmic, quadratic.
- **No ground truth required**: like BTS, the mechanism does not need external verification. Truth is extracted from inter-agent consistency.

## Connection to our paper

Peer prediction is cited as related work in the mechanism design landscape:

- **Comparison with our coherence game**: both peer prediction and our coherence game reward consistency among agents. The difference: peer prediction uses pairwise comparison with a random peer; our coherence game aggregates all ratings and uses a K-sigma threshold. Our approach is closer to a Schelling game than to peer prediction.
- **Design tradeoff**: the coherence game uses a single scalar report and a public policy as an intended focal point. The policy does not substitute for the assumptions needed by a truthful-elicitation theorem. Its simpler reporting interface comes with unresolved incentive compatibility, including the deviation in [Claim 3](../paper.qmd#curator-voting-strategy).
- **Potential hybrid**: peer prediction ideas could strengthen our coherence game, e.g., by cross-checking outlier ratings against peers before slashing. This is not explored in the current paper.

## Limitations

- Assumes agents' signals are conditionally independent given the true state. In information markets, signals may be correlated through common sources, violating this assumption.
- Requires known prior distributions or sufficient data to estimate them. In cold-start scenarios, priors are unavailable.
- Equilibrium existence and selection are separate questions. A public policy may supply a focal point, but that alone does not prove selection of a truthful equilibrium in our game.
