# Decentralized Curation

[![Build & Publish](https://github.com/0xferit/manuscript-decentralized-curation/actions/workflows/publish-cloudflare-pages.yml/badge.svg)](https://github.com/0xferit/manuscript-decentralized-curation/actions/workflows/publish-cloudflare-pages.yml) [![DOI](https://zenodo.org/badge/1132295542.svg)](https://doi.org/10.5281/zenodo.20543760)

A paper-first workspace for a Quarto-based academic manuscript on decentralized curation, plus a public-goods companion paper and application documents for Truth Post and retroactive public goods funding (RPGF). The thesis remains the primary build and publish surface; project docs live under `projects/`.

## Building locally

Prerequisites: [Quarto](https://quarto.org/docs/get-started/), Python 3.11+, and (for PDF) a LaTeX distribution (`quarto install tinytex`). The publication workflow pins the Quarto version it renders with in [its setup step](.github/workflows/publish-cloudflare-pages.yml). Record the actual Quarto, Python and TeX versions with a reviewed build; different versions can change line and page breaks. The standalone companion also requires Pandoc, XeLaTeX and the font specified in its [render instructions](projects/rpgf/companion-paper/README.md). Put the TeX binaries on `PATH`, or set `PDF_ENGINE` to the intended XeLaTeX executable when invoking `make render-companion`.

```bash
python3 -m venv .venv
source .venv/bin/activate
make setup
make render-html            # cold-safe HTML render; regenerates analysis outputs first when needed
make render-pdf             # cold-safe PDF render of the Quarto project
make render-companion       # standalone public-goods companion PDF
make render-papers          # both paper PDFs, plus Quarto project PDFs
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

`make setup` installs the hash-locked binary distributions in `requirements.lock`; it does not re-resolve dependencies or build packages from source. `requirements.txt` declares the direct dependencies; update and review the lock when those declarations change. The lock records its release-age cutoff and resolver command. `make check-invariants` fails while any version pinned in `requirements.txt` differs from the lock; Dependabot updates only `requirements.txt`, so its pip pull requests need the lock regenerated with the recorded command before they pass.

For an existing virtual environment, the same lock can also be installed with uv, retaining hash checks, binary-only packages and a 15-day release-age gate:

```bash
uv pip sync --python .venv/bin/python --require-hashes --only-binary=:all: --exclude-newer "15 days" requirements.lock
```

Raw `quarto render` is intentionally not the recommended entrypoint for local or agent-driven work, because the manuscript includes generated snippets from `analysis/out/`.

## Publishing

Every push to `main` triggers a [GitHub Actions workflow](.github/workflows/publish-cloudflare-pages.yml) that runs simulations, renders HTML, and deploys to [manuscript-decentralized-curation.pages.dev](https://manuscript-decentralized-curation.pages.dev) via Cloudflare Pages Direct Upload. Pull requests get a preview URL automatically.

The workflow requires one GitHub Actions secret: `CLOUDFLARE_API_TOKEN`. The Cloudflare account ID is not sensitive and is hardcoded in the workflow file.

The shared document sidebar, search and previous/next links are generated from `_quarto.yml`. The article table of contents remains separate. Published routes form this reading tree:

- `/`: foundational paper
- `/rpgf/`: public-goods overview
  - `/rpgf/companion/`: current public-goods companion, as a working website revision
- `/truth-post/`: news-application overview
  - `/truth-post/blueprint/`: protocol blueprint
  - `/truth-post/implementation/`: historical deployment retrospective

The retired `/rpgf/design/` route redirects to the companion. Website publication does not create a new preprint release. The companion's source and evidence links distinguish its current working text from the frozen published source.

## Repository layout

- `paper.qmd`: editable thesis master source
- `truth-post/`, `rpgf/`: thin Quarto route wrappers for published project pages
- `projects/truth-post/`: Truth Post spinout documents
- `projects/rpgf/`: RPGF spinout documents
- `references.bib`: shared BibTeX citation source for both papers and project documents
- `projects/rpgf/companion-paper/`: standalone companion source, archival evidence and publication records
- `requirements.lock`: hashed Python dependency resolution used for local setup
- `reviews/`: dated verification records, separate from current specifications
- `analysis/run_all.py`: simulation code (E1-E4, adversarial variants)
- `Makefile`: canonical task entrypoints for setup, verification, analysis, and render
- `analysis/fig/`, `analysis/out/`: generated figures and data (gitignored)
- `scripts/check_repo_invariants.py`: machine-checkable wrapper/render/citation guardrails
- `_quarto.yml`: Quarto render config for the paper
- `diagrams/`: shared thesis/project diagrams
- `context/`: thesis-supporting notes and logs
- `talks/`: slides and talk scripts derived from the thesis

## Projects

- `projects/truth-post/blueprint.md`: Truth Post application blueprint under the shared rules in `paper.qmd`
- `projects/truth-post/implementation-report.md`: Truth Post 2023 deployment retrospective
- `projects/rpgf/companion-paper/manuscript.md`: current public-goods application paper; the website working revision is separate from the deposited preprint
- `projects/README.md`: index of project documents

Publish wrappers:

- `truth-post/index.qmd`: published Truth Post landing page
- `truth-post/blueprint/index.qmd`: published Truth Post blueprint route
- `truth-post/implementation/index.qmd`: published deployment retrospective route
- `rpgf/index.qmd`: published RPGF landing page
- `rpgf/companion/index.qmd`: published companion route

Conceptual diagrams are tracked outputs of `diagrams/generate_diagrams.py`; regenerate them after editing that source. Simulation figures and tables under `analysis/` are generated and ignored. Preserve historical source excerpts and published checksums; a new local build does not replace a released artifact.

## Release procedure

1. Merge the reviewed changes to `main`. Compute the release id from the first eight hexadecimal characters of `shasum -a 256 paper.qmd`.
2. In a clean checkout of the exact release commit, set `_build-info.md` to `**Version:** vMAJOR.MINOR.PATCH` and run `make verify-full` and `make render-pdf` with the recorded build dependencies. Inspect the rendered PDF, citations and figures.
3. Freeze the source, build inputs, rendered outputs and analysis into `releases/<hash>/`. Record the build versions and checksums. Attach the reviewed PDF as `paper.pdf` and a `manifest.json` to a draft GitHub release targeting the same commit. The manifest must contain `release_version` (the full tag), `source_commit` (the full commit hash), `manuscript_sha256` and `reviewed_pdf_sha256`.
4. Run `RELEASE_TAG=vMAJOR.MINOR.PATCH python3 .github/scripts/publish_to_zenodo.py --verify-only` with those two assets in `outputs/`. Publish the GitHub release only after review. The [Zenodo workflow](.github/workflows/publish-zenodo.yml) verifies that the tag belongs to `main`, validates the manifest and uploads the attached PDF without rebuilding it.
5. Check the completed workflow and download the published Zenodo PDF to confirm its SHA-256 digest matches the reviewed asset. A matching already-published version is a no-op; conflicting content or an existing unpublished Zenodo draft requires inspection before retrying. Do not create or edit a Zenodo draft concurrently with the workflow. The separate Zenodo GitHub-integration webhook must be disabled to avoid a second publisher.

The publication boundary and its assumptions are documented in [ARCHITECTURE.md](ARCHITECTURE.md).

## License

- **Manuscript (text/figures):** CC BY 4.0. See [LICENSE](LICENSE).
- **Code/scripts:** MIT. See [LICENSE-MIT](LICENSE-MIT).
