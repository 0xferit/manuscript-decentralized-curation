## PUW Articles (Agent Notes)

This project is a Markdown workspace for a multi-part article series on the information curation bottleneck and trustless/decentralized curation.

### Source of truth

- `context/context.md` is the always-up-to-date handoff/context doc for agents and collaborators.
- `paper.qmd` is the **editable master paper source** (make substantive changes here).
- `legacy/manuscript-7-part-series.md` is the **legacy series draft** (pre-paper).
- `context/attack-and-defense-log.md` tracks red-team attacks/defenses integrated into the manuscript.
- `context/` contains supporting reference docs (Anti-Sybil, DDR, etc.).
- `legacy/` contains archived pre-Quarto artifacts (older snapshots/exports).
- `releases/` (when present) contains frozen hash-versioned releases (snapshot + rendered outputs).
- Quarto project files:
  - `_quarto.yml` (render config)
  - `styles.css` (HTML styling; aligned with `proveuswrong/website`)
  - `references.bib` (citations)
  - `analysis/run_all.py` + `requirements.txt` (deterministic simulations; generates `analysis/out/*` + `analysis/fig/*` on each run)
  - `_build-info.md` (overwritten in CI; shows deployed version + build time)
  - `outputs/` (rendered artifacts; gitignored)
  - `.github/workflows/publish-cloudflare-pages-branch.yml` (CI publish: run sims → render HTML → push `cf-pages/public/index.html`)

*Note:* We no longer produce DOCX outputs. Quarto renders **HTML + PDF** only.

### Workflow expectations

- Keep wording unchanged when asked to do “formatting only” (only add Markdown structure/whitespace).
- After any meaningful edit to the manuscript, update `context/context.md` so it reflects the current state (what changed, canonical drafts, next steps).
- Prefer adding new material in the master manuscript, then summarizing in `context/context.md` (avoid duplicating long drafts in multiple places unless explicitly requested).
- If you cut a release, follow the “Release procedure (hash-versioned)” in `README.md`, then update `context/context.md` to point to the latest release.
- Do not assume “today’s date” inside the manuscript; verify if a claim depends on currentness.
- Prefer rendering via Quarto (`quarto render`) so outputs stay consistent across formats (and run `python3 analysis/run_all.py` first if figures/summaries are referenced).
- Publishing: commits to `main` trigger HTML publish to the `cf-pages` branch (see `README.md`).

### Writing constraints (default)

- Audience: CS academics/engineers; write with precise definitions and causal chains.
- Tone: direct, non-poetic, high signal.
- Avoid fragile stats and news overfitting in early “problem” pieces unless explicitly requested.
