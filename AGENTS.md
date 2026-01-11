## PUW Articles (Agent Notes)

This project is a Markdown workspace for a multi-part article series on the information curation bottleneck and trustless/decentralized curation.

### Source of truth

- `context/context.md` is the always-up-to-date handoff/context doc for agents and collaborators.
- `my new version.md` is the **editable master manuscript** (make substantive changes here).
- `context/attack-and-defense-log.md` tracks red-team attacks/defenses integrated into the manuscript.
- `context/` contains supporting reference docs (Anti-Sybil, DDR, etc.).
- `legacy/` contains archived pre-Quarto artifacts (older snapshots/exports).
- `releases/` (when present) contains frozen hash-versioned releases (snapshot + rendered outputs).
- Quarto project files:
  - `_quarto.yml` (render config)
  - `references.bib` (citations)
  - `outputs/` (rendered artifacts)

### Workflow expectations

- Keep wording unchanged when asked to do “formatting only” (only add Markdown structure/whitespace).
- After any meaningful edit to the manuscript, update `context/context.md` so it reflects the current state (what changed, canonical drafts, next steps).
- Prefer adding new material in the master manuscript, then summarizing in `context/context.md` (avoid duplicating long drafts in multiple places unless explicitly requested).
- If you cut a release, follow the “Release procedure (hash-versioned)” in `README.md`, then update `context/context.md` to point to the latest release.
- Do not assume “today’s date” inside the manuscript; verify if a claim depends on currentness.
- Prefer rendering via Quarto (`quarto render`) so outputs stay consistent across formats.
- Publishing: commits to `main` trigger HTML publish to the `cf-pages` branch (see `README.md`).

### Writing constraints (default)

- Audience: CS academics/engineers; write with precise definitions and causal chains.
- Tone: direct, non-poetic, high signal.
- Avoid fragile stats and news overfitting in early “problem” pieces unless explicitly requested.
