# Popper (1934/1959): The Logic of Scientific Discovery

**Citation**: Popper, K. R. (1959). *The Logic of Scientific Discovery*. Hutchinson. (Original work published 1934 as *Logik der Forschung*.)

## Core thesis

Popper proposes falsifiability as a criterion of scientific status: a theory must expose itself to possible empirical refutation. This is a demarcation criterion, not a claim that non-scientific statements are meaningless. Verification is logically asymmetric with falsification; no finite set of observations can prove a universal claim, but a single counterexample can refute it. This asymmetry is the demarcation criterion separating science from non-science.

## Key concepts

- **Falsifiability as demarcation**: the boundary between scientific and non-scientific claims is not verifiability but falsifiability. A claim that no possible evidence could refute is not empirical.
- **Asymmetry of verification and falsification**: universal claims ("all swans are white") cannot be verified by enumeration but can be falsified by a single counterexample. This is a logical asymmetry; it does not establish that finding, obtaining, and adjudicating a counterexample is economically cheaper in every application.
- **Degree of falsifiability**: claims that forbid more states of affairs are more falsifiable, and therefore more informative. Vague claims that are compatible with any observation have low empirical content.
- **Corroboration vs. confirmation**: a theory that survives severe tests is "corroborated" but never confirmed. Popper rejects inductive logic; surviving tests increases confidence but never proves.

## Connection to our paper

The paper draws on Popper in three ways:

1. **Challenge-mechanism selection**: the framework applies the falsifiability prerequisite to challenge-based accuracy, not to every curation task or domain. It seeks cases where falsification is feasible and offers an economic advantage over exhaustive verification. Popper's logic motivates this design choice but does not prove viability: discovery costs, admissible evidence, adjudication reliability, and participant incentives still matter. Other mechanism families have different prerequisites.

2. **Testability in the current profiles**: Truth Post and RPGF retain explicit template and evidence requirements. In Truth Post, semantic non-falsifiability need not prevent initial on-chain admission: NonFalsifiable and TemplateViolation challenges enforce the relevant pool requirements after publication. A successful challenge produces Debunked and ends active eligibility, while preserving history. The broader framework could use relevance without factual-truth adjudication, but the current Truth Post lifecycle does not implement that mode.

3. **Dispute mechanism as institutionalized contestability**: challengers post counter-stake and evidence against an explicit proposition. Counter-evidence can support a Debunking challenge, but admitting one evidence item does not automatically establish refutation or a successful ruling. The external DDR applies the pool's evidence policy; successful challenges close the item. Challenge survival is not proof of truth.

## Key passages / takeaways

- "The criterion of the scientific status of a theory is its falsifiability, or refutability, or testability." (Ch. 1, Section 6)
- The logical asymmetry between verification and falsification: "no matter how many instances of white swans we may have observed, this does not justify the conclusion that all swans are white." But one black swan refutes it.
- Popper's insistence on *degree* of falsifiability maps to the protocol's insistence on claim specificity: the more specific the claim, the more ways it can be tested, and the more informative a surviving verdict is.

## Limitations for our use

- Popper's framework addresses scientific theories, not individual factual claims. The protocol applies falsifiability to bounded propositions ("CPI rose 5% in January 2024"), which is a narrower use than Popper intended.
- Popper's demarcation is binary (falsifiable or not). The protocol needs a spectrum: some claims are more cheaply falsifiable than others, and economic viability requires favorable costs and incentives as well as logical possibility.
- Popper does not address incentive structures. The protocol adds an economic layer (staking, slashing) that Popper's epistemology does not consider.
