# Gettier (1963): Is Justified True Belief Knowledge?

**Citation**: Gettier, E. L. (1963). Is Justified True Belief Knowledge? *Analysis*, 23(6), 121-123. doi:10.2307/3326922

## Core thesis

The classical definition of knowledge as "justified true belief" (JTB) is insufficient. Gettier provides counterexamples where a belief is justified, true, but accidentally so: the justification does not actually connect to the truth. Therefore JTB is necessary but not sufficient for knowledge.

## The counterexamples (simplified)

1. Smith is justified in believing "Jones will get the job" (the boss said so). Smith infers "the person who will get the job has ten coins in their pocket" (Smith counted Jones's coins). In fact, Smith gets the job, and Smith also happens to have ten coins. The belief is true, justified, but the justification (about Jones) is disconnected from the truth (about Smith).

2. The structure is always the same: justified belief in P, valid deduction from P to Q, P is false but Q happens to be true for unrelated reasons.

## Connection to our paper

We cite Gettier in the "Operationalizing knowledge" section to acknowledge a known limitation:

- **The protocol does not resolve Gettier cases**: a curated claim can be stake-validated and true by coincidence while the supporting evidence is misleading. Example: an author submits "Company X's revenue exceeded $1B in Q3" with evidence from a leaked draft report. The draft was wrong, but the actual revenue did exceed $1B. The claim is true, the evidence is justified (it was a real document), but the justification is disconnected from the truth.
- **Partial corrective**: the dispute mechanism allows a challenger to identify that the stated evidence is disconnected from the claim's truth and force re-evaluation. But this only works if someone notices the disconnect and finds it worth the stake.
- **Residual risk, not solvable problem**: we frame Gettier cases as a residual risk that the protocol inherits from the epistemological tradition, not as something our mechanism can solve. This is honest and defensible.

## Why this matters for framing

Citing Gettier positions the paper correctly in the epistemological landscape:
- We are not claiming to produce "knowledge" in the philosophical sense.
- We are claiming to produce "stake-weighted, contestable labels (signals) under an explicit evidence standard."
- The gap between signals and knowledge is explicitly acknowledged, and Gettier is part of why that gap exists.

This prevents reviewers from attacking the paper for overclaiming epistemological status.
