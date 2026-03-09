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
- **Why we chose Schelling over peer prediction**: (1) peer prediction requires assumptions about signal correlation structure that may not hold for news relevance; (2) our curation policy provides a focal point that substitutes for the structural assumptions; (3) the Schelling game is simpler for participants (report a single number, not a probabilistic assessment).
- **Potential hybrid**: peer prediction ideas could strengthen our coherence game, e.g., by cross-checking outlier ratings against peers before slashing. This is not explored in the current paper.

## Limitations

- Assumes agents' signals are conditionally independent given the true state. In information markets, signals may be correlated through common sources, violating this assumption.
- Requires known prior distributions or sufficient data to estimate them. In cold-start scenarios, priors are unavailable.
- The mechanism can have equilibria where everyone reports the same (uninformative) answer. Additional structure (like our curation policy focal point) may be needed to select the truthful equilibrium.
