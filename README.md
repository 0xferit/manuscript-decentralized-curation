# Decentralized Curation

[![Build & Publish](https://github.com/0xferit/manuscript-decentralized-curation/actions/workflows/publish-cloudflare-pages-branch.yml/badge.svg)](https://github.com/0xferit/manuscript-decentralized-curation/actions/workflows/publish-cloudflare-pages-branch.yml)

A paper-first workspace for a Quarto-based academic manuscript on decentralized curation, plus spinout project documents for Truth Post and RPGF. The thesis remains the primary build and publish surface; project docs live under `projects/`.

## Building locally

Prerequisites: [Quarto](https://quarto.org/docs/get-started/), Python 3.11+, and (for PDF) a LaTeX distribution (`quarto install tinytex`).

```bash
pip install -r requirements.txt
python analysis/run_all.py   # deterministic simulations (figures + data)
quarto render                # outputs: thesis + project routes under outputs/, plus outputs/paper.pdf
```

## Publishing

Every push to `main` triggers a [GitHub Actions workflow](.github/workflows/publish-cloudflare-pages-branch.yml) that runs simulations, renders HTML, and deploys to [manuscript-decentralized-curation.pages.dev](https://manuscript-decentralized-curation.pages.dev) via Cloudflare Pages Direct Upload. Pull requests get a preview URL automatically.

The workflow requires two GitHub Actions secrets: `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.

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
- `analysis/fig/`, `analysis/out/`: generated figures and data (gitignored)
- `_quarto.yml`: Quarto render config for the paper
- `diagrams/`: shared thesis/project diagrams
- `context/`: thesis-supporting notes and logs
- `legacy/`: pre-Quarto drafts and exports
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
2. Build: `python analysis/run_all.py && quarto render`
3. Freeze artifacts into `releases/<hash>/` (source, outputs, config, analysis script)

## License

- **Manuscript (text/figures):** CC BY 4.0. See [LICENSE](LICENSE).
- **Code/scripts:** MIT. See [LICENSE-MIT](LICENSE-MIT).
