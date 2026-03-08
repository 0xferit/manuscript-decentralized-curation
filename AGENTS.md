## PUW Articles (Agent Notes)

This project is a Markdown workspace for a multi-part article series on the information curation bottleneck and trustless/decentralized curation.

### Source of truth

- `paper.qmd` is the **editable master paper source** (make substantive changes here).
- `legacy/manuscript-7-part-series.md` is the **legacy series draft** (pre-paper).
- `context/attack-and-defense-log.md` tracks red-team attacks/defenses integrated into the manuscript.
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

_Note:_ We no longer produce DOCX outputs. Quarto renders **HTML + PDF** only.

### Workflow expectations

- Keep wording unchanged when asked to do “formatting only” (only add Markdown structure/whitespace).
- If you cut a release, follow the “Release procedure (hash-versioned)” in `README.md`.
- Do not assume “today’s date” inside the manuscript; verify if a claim depends on currentness.
- Prefer rendering via Quarto (`quarto render`) so outputs stay consistent across formats (and run `python3 analysis/run_all.py` first if figures/summaries are referenced).
- Publishing: commits to `main` trigger HTML publish to the `cf-pages` branch (see `README.md`).

### Writing constraints (default)

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
