# Decentralized Curation

[![Build & Publish](https://github.com/0xferit/manuscript-decentralized-curation/actions/workflows/publish-cloudflare-pages-branch.yml/badge.svg)](https://github.com/0xferit/manuscript-decentralized-curation/actions/workflows/publish-cloudflare-pages-branch.yml)

A Quarto-based academic manuscript proposing a decentralized, incentive-compatible protocol for information curation. The paper defines curation as the upstream bottleneck behind coordination failures and presents a four-step framework for trustless curation, instantiated for news.

## Building locally

Prerequisites: [Quarto](https://quarto.org/docs/get-started/), Python 3.11+, and (for PDF) a LaTeX distribution (`quarto install tinytex`).

```bash
pip install -r requirements.txt
python analysis/run_all.py   # deterministic simulations (figures + data)
quarto render                # outputs: outputs/paper.html, outputs/paper.pdf
```

## Publishing

Every push to `main` triggers a [GitHub Actions workflow](.github/workflows/publish-cloudflare-pages-branch.yml) that runs simulations, renders HTML, and pushes `public/index.html` to the `cf-pages` branch. Cloudflare Pages serves that branch.

## Repository layout

| Path | Description |
|---|---|
| `paper.qmd` | Master paper source |
| `references.bib` | BibTeX citations |
| `analysis/run_all.py` | Simulation code (E1-E4, adversarial variants) |
| `analysis/fig/`, `analysis/out/` | Generated figures and data (gitignored) |
| `_quarto.yml` | Quarto render config (HTML + PDF) |
| `themes/puw.scss` | Optional PUW HTML theme |
| `context/` | Supporting docs (attack-defense log) |
| `legacy/` | Pre-Quarto drafts and exports |

## Release procedure

1. Compute release id: first 8 hex chars of `shasum -a 256 paper.qmd`
2. Build: `python analysis/run_all.py && quarto render`
3. Freeze artifacts into `releases/<hash>/` (source, outputs, config, analysis script)

## License

- **Manuscript (text/figures):** CC BY 4.0. See [LICENSE](LICENSE).
- **Code/scripts:** MIT. See [LICENSE-MIT](LICENSE-MIT).
