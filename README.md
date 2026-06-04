# Decentralized Curation

[![Build & Publish](https://github.com/0xferit/manuscript-decentralized-curation/actions/workflows/publish-cloudflare-pages.yml/badge.svg)](https://github.com/0xferit/manuscript-decentralized-curation/actions/workflows/publish-cloudflare-pages.yml)
[![DOI](https://zenodo.org/badge/1132295542.svg)](https://doi.org/10.5281/zenodo.20543760)

A paper-first workspace for a Quarto-based academic manuscript on decentralized curation, plus spinout project documents for Truth Post and RPGF. The thesis remains the primary build and publish surface; project docs live under `projects/`.

## Building locally

Prerequisites: [Quarto](https://quarto.org/docs/get-started/), Python 3.11+, and (for PDF) a LaTeX distribution (`quarto install tinytex`).

```bash
make setup
make render-html            # cold-safe HTML render; regenerates analysis outputs first when needed
make render-pdf             # cold-safe PDF render
```

Useful agent-friendly entrypoints:

```bash
make check-invariants       # wrapper/source-of-truth + citation sanity checks
make verify-fast            # fast repo checks + reading-time snippet refresh
make verify-full            # invariants + deterministic analysis + HTML render
make analysis               # regenerate the full analysis bundle only
python3 analysis/run_all.py reading-time
python3 analysis/run_all.py summary
```

Raw `quarto render` is intentionally not the recommended entrypoint for local or agent-driven work, because the manuscript includes generated snippets from `analysis/out/`.

## Publishing

Every push to `main` triggers a [GitHub Actions workflow](.github/workflows/publish-cloudflare-pages.yml) that runs simulations, renders HTML, and deploys to [manuscript-decentralized-curation.pages.dev](https://manuscript-decentralized-curation.pages.dev) via Cloudflare Pages Direct Upload. Pull requests get a preview URL automatically.

The workflow requires one GitHub Actions secret: `CLOUDFLARE_API_TOKEN`. The Cloudflare account ID is not sensitive and is hardcoded in the workflow file.

Published routes:

- `/`: thesis paper
- `/truth-post/`: Truth Post project landing page
- `/truth-post/blueprint/`: canonical Truth Post project paper
- `/rpgf/`: RPGF project landing page
- `/rpgf/design/`: canonical RPGF project paper

## Repository layout

- `paper.qmd`: editable thesis master source
- `truth-post/`, `rpgf/`: thin Quarto route wrappers for published project pages
- `projects/truth-post/`: Truth Post spinout documents
- `projects/rpgf/`: RPGF spinout documents
- `references.bib`: BibTeX citations for the thesis
- `analysis/run_all.py`: simulation code (E1-E4, adversarial variants)
- `Makefile`: canonical task entrypoints for setup, verification, analysis, and render
- `analysis/fig/`, `analysis/out/`: generated figures and data (gitignored)
- `scripts/check_repo_invariants.py`: machine-checkable wrapper/render/citation guardrails
- `_quarto.yml`: Quarto render config for the paper
- `diagrams/`: shared thesis/project diagrams
- `context/`: thesis-supporting notes and logs
- `talks/`: slides and talk scripts derived from the thesis

## Projects

- `projects/truth-post/blueprint.md`: canonical Truth Post protocol blueprint
- `projects/truth-post/implementation-report.md`: Truth Post 2023 deployment retrospective
- `projects/rpgf/design.md`: canonical RPGF instantiation design
- `projects/README.md`: index of project documents

Publish wrappers:

- `truth-post/index.qmd`: published Truth Post landing page
- `truth-post/blueprint/index.qmd`: published Truth Post blueprint route
- `rpgf/index.qmd`: published RPGF landing page
- `rpgf/design/index.qmd`: published RPGF design route

## Release procedure

1. Compute release id: first 8 hex chars of `shasum -a 256 paper.qmd`
2. Build: `make render`
3. Freeze artifacts into `releases/<hash>/` (source, outputs, config, analysis script)

## License

- **Manuscript (text/figures):** CC BY 4.0. See [LICENSE](LICENSE).
- **Code/scripts:** MIT. See [LICENSE-MIT](LICENSE-MIT).
