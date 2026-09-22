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
- Curators report policy conformity on [0,1].
- Honest assessment is the intended focal point. A specific public policy can make that target salient, but participants may coordinate on other reports.
- Salience does not establish truthful best responses or equilibrium selection. [Claim 3 in the paper](../paper.qmd#curator-voting-strategy) gives a profitable unilateral deviation under permitted reward parameters.

### Why policy specificity matters
Policy specificity makes policy-faithful assessment easier to define. Vague policies leave competing interpretations, but a precise policy alone does not make honest reporting an equilibrium. The full reward, penalty and appeal rules determine best responses.

## Key passages worth keeping

> "Most situations ... provide some clue for coordinating behavior, some focal point for each person's expectation of what the other expects him to expect to be expected to do." (p. 57)

This recursive expectation structure is exactly what makes focal points work: not just "I think X" but "I think you think I think X."

> "The coordination problem is not one of guessing what the other will do, but of finding a rule that both can find." (paraphrased from Chapter 3)

This maps to our design: the curation policy is the "rule that both can find."

## Limitations relevant to us

- Schelling assumes common knowledge of the game structure. In practice, curators may not fully understand the curation policy or the coherence mechanism, weakening the focal point.
- Competing policy interpretations can support different coordination targets. Templates and typed `NonFalsifiable` or `TemplateViolation` challenges enforce the pool’s explicit requirements; policy ambiguity alone does not establish that a challenge succeeds.
- George (2023) identifies limits on truthful equilibria in ranked-alternative games. Applying that result to our scalar mechanism requires a formal mapping; a different reporting space is not evidence of incentive compatibility.
