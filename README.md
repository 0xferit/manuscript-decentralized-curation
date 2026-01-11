# PUW Articles (Quarto setup)

This workspace is a manuscript + supporting context docs. It is configured as a Quarto project so you can render **HTML / PDF / DOCX** from a single source.

## Source of truth

- **Paper source:** `paper.qmd`
- **Legacy manuscript source:** `my new version.md` (raw material / prior canonical draft)
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

### Render all formats (HTML/PDF/DOCX)

```bash
python3 -m pip install -r requirements.txt
python3 analysis/run_all.py
quarto render
```

Outputs are written to `outputs/` and currently standardized as:
- `outputs/paper.html`
- `outputs/paper.pdf`
- `outputs/paper.docx`

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

**Definition:** the *unreleased master* is always `my new version.md`. A *release* is a frozen snapshot keyed by a content hash, plus rendered outputs.

1. **Compute the release id**

```bash
shasum -a 256 "my new version.md"
```

Use the first 8 hex chars of the SHA-256 as `<hash>`.

2. **Render from the master**

```bash
quarto render
```

Do not edit the manuscript between steps (1) and (2).

3. **Freeze the release artifacts**

```bash
mkdir -p "releases/<hash>"
cp "my new version.md" "releases/<hash>/my new version.md"
cp "outputs/paper.html" "releases/<hash>/paper.html"
cp "outputs/paper.docx" "releases/<hash>/paper.docx"
cp "outputs/paper.pdf" "releases/<hash>/paper.pdf"
cp "_quarto.yml" "releases/<hash>/_quarto.yml"
cp "references.bib" "releases/<hash>/references.bib"
```

4. **Update pointers**

- Update `context/context.md` so “last released snapshot/export” points to the new `<hash>` artifacts (and optionally add a 1–3 bullet release note).


