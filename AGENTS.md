## Decentralized Curation Working Draft

This repository is the workspace for a thesis on decentralized curation: a Quarto-based academic manuscript (`paper.qmd`) proposing a decentralized, incentive-compatible protocol for information curation. Supporting infrastructure includes deterministic simulations (`analysis/run_all.py`), a BibTeX citation database (`references.bib`), and CI-driven HTML publishing to Cloudflare Pages.

This file is the canonical agent-facing guidance for the repository. `CLAUDE.md` symlinks here so Claude Code reads it. Codex CLI and GitHub Copilot surfaces that support `AGENTS.md` (cloud agent, VS Code Chat, Copilot CLI, JetBrains/Xcode cloud agent) read it directly. The GitHub Copilot **code-review** surface does not read `AGENTS.md` (see [Copilot custom-instructions support](https://docs.github.com/en/copilot/reference/custom-instructions-support)); its narrower brief lives at `.github/copilot-instructions.md` and covers only the PR-review rubric and code-review criteria.

### Source of truth
- Never edit files under `context/`
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

### Design Principles

- NoNeedForGovernance > Good Governance > Bad Governance > No Governance
- Do not decompose quality further than your mechanisms can distinguish. Two mechanisms (challenge-based accuracy, coherence-based relevance) means two dimensions. Adding a third dimension without a third mechanism just creates noise. (Corollary of Wang and Strong's "decompose quality before you mechanize it.")
