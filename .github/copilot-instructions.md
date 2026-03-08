# Copilot Instructions: Decentralized Curation Manuscript

## Project context

This is a Quarto-based academic manuscript workspace. The paper (`paper.qmd`) proposes a decentralized, incentive-compatible protocol for information curation. Supporting infrastructure includes deterministic simulations (`analysis/run_all.py`), a BibTeX citation database (`references.bib`), and CI-driven HTML publishing to Cloudflare Pages.

## Key files

| File | Role |
|---|---|
| `paper.qmd` | Editable master paper source (Quarto Markdown) |
| `references.bib` | BibTeX citations; validate DOIs, volumes, page ranges |
| `analysis/run_all.py` | Deterministic simulations; generates `analysis/out/*` and `analysis/fig/*` |
| `_quarto.yml` | Quarto render config (HTML + PDF only; no DOCX) |

## Writing constraints

- **Audience:** CS academics and engineers.
- **Tone:** Direct, non-poetic, high signal. No hedging without justification.
- **Precision:** Use exact definitions and causal chains. Avoid fragile statistics and news-cycle overfitting.

## Scientific review criteria (peer-review skill, 7-stage framework)

When reviewing or suggesting changes to manuscript content (`.qmd`, `.md`), apply the `claude-scientific-writer` peer-review systematic evaluation:

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
- Do claims reference appropriate literature? Flag assertions that need citations or cite outdated/retracted work.
- Can key claims be tested or disproven? Identify unfalsifiable assertions.

### Report structure
Organize feedback as: **Summary statement** (1-2 paragraphs with recommendation), **Major comments** (critical issues), **Minor comments** (improvements), **Questions for authors** (clarification requests).

## Code review criteria

For changes to `analysis/run_all.py` or other Python code:
- Determinism: simulations must produce identical outputs given identical inputs.
- No hardcoded paths; use relative paths from project root.
- Figures should be publication-quality (labeled axes, legible fonts, vector format when possible).

## Model preference

Prefer Claude Opus for review tasks requiring deep reasoning about argument structure and methodology.
