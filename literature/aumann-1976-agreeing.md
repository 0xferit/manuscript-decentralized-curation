# Aumann (1976): Agreeing to Disagree

**Citation**: Aumann, R. J. (1976). Agreeing to Disagree. *The Annals of Statistics*, 4(6), 1236-1239.

## Core thesis

If two agents have common priors and their posteriors are common knowledge, then their posteriors must be equal. Put differently: rational agents with the same prior who share their conclusions cannot "agree to disagree." If they still disagree, either their priors differ or their beliefs are not truly common knowledge.

## Key concepts

- **Common knowledge**: not just "I know X and you know X" but the infinite recursion: I know that you know that I know that you know... ad infinitum. This is a very strong condition.
- **Common prior assumption**: both agents start from the same prior distribution. The theorem breaks if priors differ.
- **Impossibility of rational disagreement**: under common priors + common knowledge of posteriors, disagreement is logically impossible. This is a benchmark, not a description of reality.

## Connection to our paper

We use Aumann's formalization of common knowledge in the Introduction section ("When common knowledge fails") to set up why coordination breaks down:

- **The gap between shared knowledge and common knowledge**: people routinely treat shared knowledge as if it were common knowledge. Aumann's definition makes precise what common knowledge actually requires: the infinite recursive structure. In practice, this never holds.
- **Why coordination fails upstream**: if common knowledge is the prerequisite for safe coordination, and common knowledge rarely exists, then the quality of the *shared* knowledge layer becomes the binding constraint. This motivates our entire project: improve the knowledge layer because the coordination layer depends on it.
- **Bolander et al. (2020)** extends this by modeling bounded-depth reasoning: humans stop the recursion at shallow depths, producing an "illusion of shared knowledge" that masks incompatible understanding.

## Key takeaway

Aumann gives us the formal definition of common knowledge. We use it to show that the real world almost never satisfies this condition, which means coordination depends on the quality of the knowledge layer even more than the theory suggests. The paper's contribution is making the knowledge layer the object of design.
