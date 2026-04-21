---
name: paper-review
description: "Systematic peer review of paper.qmd or project design docs using the thesis's 7-stage rubric. Use when the user asks to review, critique, evaluate, assess, or peer-review a manuscript section, or before finalizing substantive prose changes."
allowed-tools: [Read, Grep, Glob, Bash, Agent]
context: inherit
---

# paper-review: 7-stage peer review for the decentralized-curation manuscript

## When to use
Trigger when the user asks to review, critique, evaluate, assess, audit, or peer-review `paper.qmd`, `projects/*/blueprint.md`, `projects/*/design.md`, or `projects/*/implementation-report.md`. Also trigger as a self-check before finalizing any substantive prose change.

## Delegate methodology to
`claude-scientific-writer:peer-review` for the general toolkit. Apply the 7-stage rubric below for this project.

## Project-specific rubric (7 stages)

This rubric mirrors the `Scientific review criteria` section of `.github/copilot-instructions.md` (the PR-review instructions read by GitHub's Copilot code-review surface) so Claude Code and GitHub Copilot reviewers produce comparable output. Repo-wide context lives in `AGENTS.md`.

### Stage 1: Initial assessment
Evaluate scope, novelty, and overall contribution quality before diving into details.

### Stage 2: Section-by-section review
Walk through Abstract, Introduction, Methods, Results, Discussion, and References individually. Check that each section fulfills its role and connects logically to adjacent sections.

### Stage 3: Methodological and statistical rigor
- Are causal claims logically sound? Flag non-sequiturs, circular reasoning, and unsupported generalizations.
- Evaluate simulation design, parameter choices, and data handling in `analysis/`. Check for cherry-picked scenarios.
- Are quantitative claims properly qualified? Flag p-hacking patterns, survivorship bias, or missing confidence intervals.

### Stage 4: Reproducibility and transparency
- Can simulations be re-run deterministically from `analysis/run_all.py`?
- Are parameters, assumptions, and data sources fully documented?

### Stage 5: Figure and data presentation
- Do figures accurately represent underlying data? Check axis labels, scales, and legends.
- Flag misleading visualizations or missing error bars.

### Stage 6: Ethical considerations and research integrity
- Verify proper attribution; flag potential plagiarism or missing acknowledgments.

### Stage 7: Writing quality
- Tone must be direct, non-poetic, high signal. No hedging without justification.
- Definitions must be precise; flag ambiguous terminology.
- Does language match evidence strength? Flag "proves" when "suggests" is warranted, or universal claims from limited examples.
- Do claims reference appropriate literature? Flag assertions that need citations or cite outdated / retracted work.
- Can key claims be tested or disproven? Identify unfalsifiable assertions.

## Report structure
Organize feedback as: **Summary statement** (1-2 paragraphs with recommendation); **Major comments** (critical issues); **Minor comments** (improvements); **Questions for authors** (clarification requests).

## Project invariants to check against
- Writing Constraints (see the `Writing constraints` section of `CLAUDE.md`).
- Design Principles (see the `Design Principles` section of `CLAUDE.md`): NoNeedForGovernance > Good Governance > Bad Governance > No Governance; do not decompose quality beyond two mechanisms.
- Red-team log: consult `context/attack-and-defense-log.md` for known attacks/defenses when evaluating robustness claims.
