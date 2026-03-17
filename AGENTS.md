## Decentralized Curation Working Draft

This project is workspace for my thesis on decentralized curation.

### Source of truth
- Never edit files under context/ 
- `paper.qmd` is the **editable master paper source** (make substantive changes here).
- `projects/truth-post/blueprint.md` is the **canonical Truth Post design doc**.
- `projects/truth-post/implementation-report.md` is the **Truth Post deployment retrospective**.
- `projects/rpgf/design.md` is the **canonical RPGF design doc**.
- `truth-post/` and `rpgf/` at the repo root are **publish-route wrappers only**, not canonical content sources.
- `legacy/manuscript-7-part-series.md` is the **legacy series draft** (pre-paper).
- `context/attack-and-defense-log.md` tracks red-team attacks/defenses integrated into the manuscript.
- `projects/README.md` indexes the spinout project documents.
- `legacy/` contains archived pre-Quarto artifacts (older snapshots/exports).
- `releases/` (when present) contains frozen hash-versioned releases (snapshot + rendered outputs).
- Quarto project files:
  - `_quarto.yml` (render config)
  - `themes/puw.scss` (PUW custom HTML theme; aligned with `proveuswrong/website`)
  - `references.bib` (citations)
  - `analysis/run_all.py` + `requirements.txt` (deterministic simulations; generates `analysis/out/*` + `analysis/fig/*` on each run)
  - `_build-info.md` (overwritten in CI; shows deployed version + build time)
  - `outputs/` (rendered artifacts; gitignored)
  - `.github/workflows/publish-cloudflare-pages-branch.yml` (CI publish: run sims → render HTML → push `cf-pages/public/index.html`)

### Workflow expectations

- Keep wording unchanged when asked to do “formatting only” (only add Markdown structure/whitespace).
- If you cut a release, follow the “Release procedure (hash-versioned)” in `README.md`.
- Do not assume “today’s date” inside the manuscript; verify if a claim depends on currentness.
- Prefer rendering via Quarto (`quarto render`) so outputs stay consistent across formats (and run `python3 analysis/run_all.py` first if figures/summaries are referenced).
- Publishing: commits to `main` trigger HTML publish to the `cf-pages` branch (see `README.md`).
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

- Never refer to older versions of this manuscript.
- Audience: CS academics/engineers; write with precise definitions and causal chains.
- Tone: direct, non-poetic, high signal.
- Avoid fragile stats and news overfitting in early “problem” pieces unless explicitly requested.

### Scientific writing toolkit (claude-scientific-writer plugin)

The following skills from the `claude-scientific-writer` plugin are relevant to this project. Use them proactively when the task matches.

| Skill | When to use |
|---|---|
| `scientific-writing` | Revising or drafting prose sections of `paper.qmd`. Ensures IMRAD-quality writing, proper paragraph flow, and section structure. |
| `scientific-critical-thinking` | Evaluating argument strength, checking for overclaims, logical fallacies, or unsupported causal claims in the manuscript. Use before finalizing any rewritten section. |
| `citation-management` | Validating `references.bib` entries (missing volume/pages/DOI), discovering new relevant papers via Google Scholar or PubMed, generating BibTeX entries. |
| `research-lookup` / `parallel-web` | Verifying factual claims (e.g., statistics cited in the paper), finding recent related work, checking if cited sources are current. |
| `peer-review` | Systematic review of the full manuscript or specific sections for methodology gaps, overclaims, and logical issues. |
| `scientific-schematics` | Generating publication-quality conceptual diagrams (e.g., four-step framework, protocol architecture, flow diagrams). The paper has simulation figures but lacks conceptual visuals. |
| `scientific-slides` | Building presentations from the paper content (e.g., conference talks, reading group presentations). |

Skills NOT relevant to this project: clinical/healthcare skills, market research, DOCX/PPTX/XLSX processing, LaTeX posters, venue-templates, generate-image, infographics, hypothesis-generation.

### Design Principles

- NoNeedForGovernance > Good Governance > Bad Governance > No Governance
- Do not decompose quality further than your mechanisms can distinguish. Two mechanisms (challenge-based accuracy, coherence-based relevance) means two dimensions. Adding a third dimension without a third mechanism just creates noise. (Corollary of Wang and Strong's "decompose quality before you mechanize it.")
