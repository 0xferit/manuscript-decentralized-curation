# PUW Articles (Quarto setup)

This workspace is a manuscript + supporting context docs. It is configured as a Quarto project so you can render **HTML / PDF** from a single source.

## Source of truth

- **Paper source:** `paper.qmd`
- **Legacy series draft:** `legacy/manuscript-7-part-series.md` (pre-paper draft)
- **Quarto config:** `_quarto.yml`
- **Bibliography:** `references.bib`
- **Supporting docs:** `context/`

## Render outputs

### Prerequisites

- **Quarto** (macOS): `brew install quarto`
- **PDF only:** a LaTeX installation (recommended: TinyTeX)

```bash
quarto install tinytex
```

### Render all formats (HTML/PDF)

```bash
python3 -m pip install -r requirements.txt
python3 analysis/run_all.py
quarto render
```

Outputs are written to `outputs/` and currently standardized as:

- `outputs/paper.html`
- `outputs/paper.pdf`

## Styling (HTML)

- **Theme + layout:** `_quarto.yml` → `format.html` (default theme, grid, TOC).
- **Custom theme:** `themes/puw.scss` (PUW styling; enable with `theme: [default, themes/puw.scss]`).

To preview styling changes locally:

```bash
python3 analysis/run_all.py
quarto render --to html
open "outputs/paper.html"
```

## Publish procedure (every commit → HTML)

We publish the latest manuscript HTML on every commit to `main`, using **Cloudflare Pages**.

### One-time setup (Cloudflare Pages)

In Cloudflare Pages, connect this repository and configure:

- **Production branch:** `cf-pages`
- **Build command:** `exit 0`
- **Build output directory:** `public`

### Ongoing workflow

1. Make changes to `paper.qmd` (and/or `references.bib`, `analysis/`)
2. Commit + push to `main`
3. GitHub Actions renders HTML and updates the `cf-pages` branch (`public/index.html`)
4. Cloudflare Pages deploys the updated `cf-pages` branch

The publishing workflow file is: `.github/workflows/publish-cloudflare-pages-branch.yml`

## License

- **Manuscript (text/figures):** CC BY 4.0 (attribution required). See `LICENSE`.
- **Code/config/scripts:** MIT. See `LICENSE-MIT`.

## Release procedure (hash-versioned)

**Definition:** the _unreleased master_ is `paper.qmd`. A _release_ is a frozen snapshot keyed by a content hash, plus rendered outputs.

1. **Compute the release id**

```bash
shasum -a 256 "paper.qmd"
```

Use the first 8 hex chars of the SHA-256 as `<hash>`.

2. **Render from the master**

```bash
python3 -m pip install -r requirements.txt
python3 analysis/run_all.py
quarto render
```

Do not edit the manuscript between steps (1) and (2).

3. **Freeze the release artifacts**

```bash
mkdir -p "releases/<hash>"
cp "paper.qmd" "releases/<hash>/paper.qmd"
cp "outputs/paper.html" "releases/<hash>/paper.html"
cp "outputs/paper.pdf" "releases/<hash>/paper.pdf"
cp "_quarto.yml" "releases/<hash>/_quarto.yml"
cp "references.bib" "releases/<hash>/references.bib"
cp "requirements.txt" "releases/<hash>/requirements.txt"
mkdir -p "releases/<hash>/analysis"
cp "analysis/run_all.py" "releases/<hash>/analysis/run_all.py"
```

4. **Update pointers**

- Update `context/context.md` so “last released snapshot/export” points to the new `<hash>` artifacts (and optionally add a 1–3 bullet release note).
