# Copilot Instructions: Decentralized Curation Manuscript

## Project context

This is a Quarto-based academic manuscript workspace. The paper (`paper.qmd`) proposes a decentralized, incentive-compatible protocol for information curation. Supporting infrastructure includes deterministic simulations (`analysis/run_all.py`), a BibTeX citation database (`references.bib`), and CI-driven HTML publishing to Cloudflare Pages.

## Key files

| File | Role |
|---|---|
| `paper.qmd` | Editable master paper source (Quarto Markdown) |
| `references.bib` | BibTeX citations; validate DOIs, volumes, page ranges |
| `analysis/run_all.py` | Deterministic simulations; generates `analysis/out/*` and `analysis/fig/*` |
| `context/context.md` | Living handoff doc for collaborators |
| `_quarto.yml` | Quarto render config (HTML + PDF only; no DOCX) |

## Writing constraints

- **Audience:** CS academics and engineers.
- **Tone:** Direct, non-poetic, high signal. No hedging without justification.
- **Precision:** Use exact definitions and causal chains. Avoid fragile statistics and news-cycle overfitting.

## Scientific review criteria

When reviewing or suggesting changes to manuscript content (`.qmd`, `.md`), apply these dimensions:

1. **Argument rigor**: Are causal claims logically sound? Flag non-sequiturs, circular reasoning, and unsupported generalizations.
2. **Falsifiability**: Can key claims be tested or disproven? Identify unfalsifiable assertions.
3. **Methodology**: Evaluate simulation design, parameter choices, and data handling in `analysis/`. Check for cherry-picked scenarios.
4. **Statistical validity**: Are quantitative claims properly qualified? Flag p-hacking patterns, survivorship bias, or missing confidence intervals.
5. **Citation completeness**: Do claims reference appropriate literature? Flag assertions that need citations or cite outdated/retracted work.
6. **Overclaim detection**: Does the language match the evidence strength? Flag "proves" when "suggests" is warranted, or universal claims from limited examples.

## Code review criteria

For changes to `analysis/run_all.py` or other Python code:
- Determinism: simulations must produce identical outputs given identical inputs.
- No hardcoded paths; use relative paths from project root.
- Figures should be publication-quality (labeled axes, legible fonts, vector format when possible).

## Model preference

Prefer Claude Opus for review tasks requiring deep reasoning about argument structure and methodology.
