# Schelling (1960): The Strategy of Conflict

**Citation**: Schelling, T. C. (1960). *The Strategy of Conflict*. Harvard University Press.

## Core thesis

In games where players benefit from coordination but cannot communicate, they converge on **focal points**: outcomes that are salient, obvious, or culturally prominent. Coordination does not require explicit agreement; shared context is sufficient. The key insight is that the structure of the game and the salience of certain options do the work that communication would otherwise do.

## Key concepts

- **Focal point (Schelling point)**: a solution that people tend to choose by default in the absence of communication. It is "obvious" or "natural" given shared context. The classic example: two people told to meet somewhere in New York City will likely choose Grand Central Station, not because it is optimal but because it is salient.
- **Tacit coordination**: coordination achieved without explicit communication, relying on shared expectations and common knowledge of the situation.
- **Salience**: the property of an option that makes it "stand out" from alternatives. Can be driven by uniqueness, cultural prominence, simplicity, or prior convention.
- **Mixed-motive games**: games where players have both common and conflicting interests. Schelling's framework applies to the cooperative dimension, where players benefit from choosing the same thing.

## Connection to our paper

Schelling's focal point theory is the theoretical foundation for both our mechanism designs:

### Accuracy (DDR disputes)
- Jurors face a binary choice (Valid/Invalid) and must coordinate without communication (commit-reveal).
- The focal point is the verdict consistent with the evidence standard and curation policy.
- Binary choice is the simplest focal point structure: one option is consistent with the evidence, the other is not. Salience is high when the evidence is clear.

### Relevance (coherence game)
- Curators independently rate policy conformity on [0,1] and must converge.
- The focal point is the "honest assessment of curation policy conformity."
- This is where Schelling's theory does the heaviest lifting: the curation policy is what creates the focal point. Without a specific, public policy, there is no salient coordination target, and the game degenerates.
- **Proposition 2** in our paper is essentially: if the curation policy is specific enough to induce a unique focal point, honest reporting is a Nash equilibrium under commit-reveal.

### Why policy specificity matters
Schelling's insight explains why vague curation policies break the system. A vague policy provides a weak focal point; curators coordinate on an *interpretation* rather than a *reality*. The interpretation may be wrong, and worse, it may be manipulable. The specificity of the curation policy is not a UX concern; it is a game-theoretic requirement for equilibrium existence.

## Key passages worth keeping

> "Most situations ... provide some clue for coordinating behavior, some focal point for each person's expectation of what the other expects him to expect to be expected to do." (p. 57)

This recursive expectation structure is exactly what makes focal points work: not just "I think X" but "I think you think I think X."

> "The coordination problem is not one of guessing what the other will do, but of finding a rule that both can find." (paraphrased from Chapter 3)

This maps to our design: the curation policy is the "rule that both can find."

## Limitations relevant to us

- Schelling assumes common knowledge of the game structure. In practice, curators may not fully understand the curation policy or the coherence mechanism, weakening the focal point.
- Focal point theory does not predict what happens when two competing focal points exist (e.g., two plausible interpretations of a policy). Our defense is claim templates and the Under-specified verdict: if ambiguity creates competing focal points, the claim should be rejected.
- George (2023) proves that for three or more ranked alternatives, truthful reporting cannot always be an equilibrium. Our binary and scalar instantiations are designed to avoid this impossibility, but the boundary conditions matter.
