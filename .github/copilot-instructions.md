## Decentralized Curation Working Draft

This repository is the workspace for a thesis on decentralized curation: a Quarto-based academic manuscript (`paper.qmd`) proposing a decentralized, incentive-compatible protocol for information curation. Supporting infrastructure includes deterministic simulations (`analysis/run_all.py`), a BibTeX citation database (`references.bib`), and CI-driven HTML publishing to Cloudflare Pages.

### Source of truth
- Never edit files under context/ 
- `paper.qmd` is the **editable master paper source** (make substantive changes here).
- `projects/truth-post/blueprint.md` is the **canonical Truth Post design doc**.
- `projects/truth-post/implementation-report.md` is the **Truth Post deployment retrospective**.
- `projects/rpgf/design.md` is the **canonical RPGF design doc**.
- `truth-post/` and `rpgf/` at the repo root are **publish-route wrappers only**, not canonical content sources.
- `context/attack-and-defense-log.md` tracks red-team attacks/defenses integrated into the manuscript.
- `projects/README.md` indexes the spinout project documents.
- `releases/` (when present) contains frozen hash-versioned releases (snapshot + rendered outputs).
- `diagrams/generate_diagrams.py` generates conceptual figures (claim states, actor flow, architecture, etc.) into `diagrams/fig-*.png`. Uses matplotlib; run directly with `python3 diagrams/generate_diagrams.py`.
- `talks/` contains presentation materials (slide decks, talk scripts). Not part of the Quarto render pipeline.
- Quarto project files:
  - `_quarto.yml` (render config)
  - `references.bib` (citations)
  - `analysis/run_all.py` + `requirements.txt` (deterministic simulations; generates `analysis/out/*` + `analysis/fig/*` on each run)
  - `_build-info.md` (overwritten in CI; shows deployed version + build time)
  - `outputs/` (rendered artifacts; gitignored)
  - `.github/workflows/publish-cloudflare-pages.yml` (CI publish: run sims → render HTML → Direct Upload to Cloudflare Pages)
  - `.github/workflows/copilot-setup-steps.yml` (Copilot coding agent environment: installs Python deps, runs sims, verifies Quarto render)
  - `.github/agents/peer-reviewer.agent.md` (GitHub Copilot agent: 7-stage scientific peer review using Claude Opus)

### Workflow expectations

- Keep wording unchanged when asked to do “formatting only” (only add Markdown structure/whitespace).
- If you cut a release, follow the “Release procedure (hash-versioned)” in `README.md`.
- Do not assume “today’s date” inside the manuscript; verify if a claim depends on currentness.
- Prefer rendering via Quarto (`quarto render`) so outputs stay consistent across formats (and run `python3 analysis/run_all.py` first if figures/summaries are referenced).
- Publishing: commits to `main` trigger HTML publish to Cloudflare Pages via Direct Upload (see `README.md`).
- Treat the repo root as the thesis/shared-assets layer. Standalone project docs belong under `projects/`, not at the root.
- Route wrapper files at the repo root exist only to publish stable URLs for project papers. Edit project prose under `projects/`, not in those wrappers.

### Literature reference notes

- `literature/` contains internal working notes on foundational works that inform the paper (Akerlof, Schelling, George, Ostrom, etc.).
- These are for agent use during paper refinement: consult them to understand how each work connects to our arguments, what limitations apply, and which concepts we draw from.
- Not referenced from the paper itself; `references.bib` remains the citation source of truth.
- See `literature/README.md` for the full index.

### Project notes

- `projects/truth-post/` and `projects/rpgf/` are standalone spinout document areas.
- They are canonical for their respective project designs.
- Published project routes are served through root-level Quarto wrappers at `/truth-post/`, `/truth-post/blueprint/`, `/rpgf/`, and `/rpgf/design/`.
- Shared diagrams, simulations, and bibliography remain at the repo root unless explicitly reorganized later.

### Writing constraints (default)

- **Audience:** CS academics and engineers. Write with precise definitions and causal chains.
- **Tone:** Direct, non-poetic, high signal. No hedging without justification.
- **Stats:** Avoid fragile statistics and news-cycle overfitting in early “problem” pieces unless the user explicitly requests them.
- **Versioning:** Never refer to older versions of this manuscript.

### Scientific writing toolkit

Project-local skill wrappers under `.claude/skills/` engrave this project's conventions (source-of-truth file map, writing constraints, design principles, 7-stage peer-review rubric) over the upstream `claude-scientific-writer:*` plugin skills. Wrappers auto-surface when their triggers match and delegate methodology to the upstream plugin while applying this project's invariants. Each wrapper's `SKILL.md` documents its own triggers and inlined rules.

| Project wrapper | Wraps upstream plugin skill |
|---|---|
| `paper-draft` | `claude-scientific-writer:scientific-writing` |
| `paper-review` | `claude-scientific-writer:peer-review` |
| `paper-audit-claims` | `claude-scientific-writer:scientific-critical-thinking` |
| `paper-refs` | `claude-scientific-writer:citation-management` |
| `paper-fact-check` | `claude-scientific-writer:research-lookup` and `:parallel-web` |
| `paper-schematic` | `claude-scientific-writer:scientific-schematics` |
| `paper-slides` | `claude-scientific-writer:scientific-slides` |

Skills NOT relevant to this project: clinical / healthcare, market research, DOCX / PPTX / XLSX processing, LaTeX posters, venue-templates, generate-image, infographics, hypothesis-generation.

### Scientific review criteria (peer-review, 7-stage framework)

When reviewing or suggesting changes to manuscript content (`.qmd`, `.md`), apply the `claude-scientific-writer` peer-review systematic evaluation:

#### Stage 1: Initial assessment
Evaluate scope, novelty, and overall contribution quality before diving into details.

#### Stage 2: Section-by-section review
Walk through Abstract, Introduction, Methods, Results, Discussion, and References individually. Check that each section fulfills its role and connects logically to adjacent sections.

#### Stage 3: Methodological and statistical rigor
- Are causal claims logically sound? Flag non-sequiturs, circular reasoning, and unsupported generalizations.
- Evaluate simulation design, parameter choices, and data handling in `analysis/`. Check for cherry-picked scenarios.
- Are quantitative claims properly qualified? Flag p-hacking patterns, survivorship bias, or missing confidence intervals.

#### Stage 4: Reproducibility and transparency
- Can simulations be re-run deterministically from `analysis/run_all.py`?
- Are parameters, assumptions, and data sources fully documented?

#### Stage 5: Figure and data presentation
- Do figures accurately represent underlying data? Check axis labels, scales, and legends.
- Flag misleading visualizations or missing error bars.

#### Stage 6: Ethical considerations and research integrity
- Verify proper attribution; flag potential plagiarism or missing acknowledgments.

#### Stage 7: Writing quality
- Tone must be direct, non-poetic, high signal. No hedging without justification.
- Definitions must be precise; flag ambiguous terminology.
- Does language match evidence strength? Flag "proves" when "suggests" is warranted, or universal claims from limited examples.
- Do claims reference appropriate literature? Flag assertions that need citations or cite outdated/retracted work.
- Can key claims be tested or disproven? Identify unfalsifiable assertions.

#### Report structure
Organize feedback as: **Summary statement** (1-2 paragraphs with recommendation), **Major comments** (critical issues), **Minor comments** (improvements), **Questions for authors** (clarification requests).

### Code review criteria

For changes to `analysis/run_all.py` or other Python code:
- Determinism: simulations must produce identical outputs given identical inputs.
- No hardcoded paths; use relative paths from project root.
- Figures should be publication-quality (labeled axes, legible fonts, vector format when possible).

### Design Principles

- NoNeedForGovernance > Good Governance > Bad Governance > No Governance
- Do not decompose quality further than your mechanisms can distinguish. Two mechanisms (challenge-based accuracy, coherence-based relevance) means two dimensions. Adding a third dimension without a third mechanism just creates noise. (Corollary of Wang and Strong's "decompose quality before you mechanize it.")

### Model preference

Prefer Claude Opus for review tasks requiring deep reasoning about argument structure and methodology.
