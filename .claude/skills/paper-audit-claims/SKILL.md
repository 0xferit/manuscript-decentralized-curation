---
name: paper-audit-claims
description: "Audit claims, causal chains, and conclusions in the manuscript or project design docs for scientific rigor. Use when the user asks to check claims, verify arguments, test causal chains, check for overclaiming, or before finalizing any section that makes empirical or causal assertions."
allowed-tools: [Read, Grep, Glob, Agent]
context: inherit
---

# paper-audit-claims: claim audit for the decentralized-curation manuscript

## When to use
Trigger when the user asks to audit claims, check for overclaims, verify causal chains, test assertions, or evaluate whether an argument is supported by the evidence and mechanisms actually available. Also trigger as a pre-merge check on any prose change that adds or strengthens a causal claim.

## Delegate methodology to
`claude-scientific-writer:scientific-critical-thinking` for the claim-extraction and evidence-sufficiency workflow.

## Project-specific targets
- **Causal claims** about incentive alignment and mechanism-as-proof reasoning in `paper.qmd`.
- **Uniqueness / sufficiency claims** in `projects/*/design.md` and `projects/*/blueprint.md`.
- **Red-team robustness claims:** cross-check against `context/attack-and-defense-log.md`, which tracks integrated attacks and defenses.

## Project Design Principles to uphold
- **NoNeedForGovernance > Good Governance > Bad Governance > No Governance.** Flag designs that justify added governance without ruling out the simpler "no governance needed" case.
- **Do not decompose quality further than your mechanisms can distinguish.** Two mechanisms (challenge-based accuracy, coherence-based relevance) mean two dimensions. A third dimension without a third mechanism is noise. (Corollary of Wang and Strong's "decompose quality before you mechanize it.")

## Writing-quality signals to flag
- "Proves" when "suggests" is warranted.
- Universal claims from limited examples.
- Unfalsifiable assertions.
- Mechanism-as-proof claims: describing design as if design proves correct behavior.
- Appeals to absence of evidence.

## Output shape
For each claim: (1) the claim verbatim with location; (2) what would need to hold for it to be true; (3) whether support is strong / mixed / weak / absent; (4) suggested revision or evidence needed.
