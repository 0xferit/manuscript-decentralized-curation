# Troubleshooting

## Installation / environment

**`quarto: command not found`** — install from [quarto.org/docs/get-started](https://quarto.org/docs/get-started/) or `brew install quarto` / `winget install quarto`.

**`quarto check` fails** — run it to see which subsystem is broken:

```
Quarto 1.6.x
[✓] Checking versions of quarto binary dependencies...
[✓] Checking versions of quarto dependencies......
[✓] Checking Quarto installation......
[✓] Checking tools....................
[✓] Checking LaTeX....................
[✗] Checking Python 3 installation....    # <-- fix this
[✓] Checking Jupyter engine render.
```

**`Unable to locate an installed version of Jupyter`** — `pip install jupyter` (and the kernel you need, e.g. `ipykernel`). Verify with `jupyter kernelspec list`.

**`The knitr package is required`** (R) — in R: `install.packages("knitr")` and `install.packages("rmarkdown")`.

## PDF rendering

**`! LaTeX Error: File X.sty not found`** — install TinyTeX:

```bash
quarto install tinytex
```

If already installed, let Quarto auto-install missing packages by re-rendering. For a stubborn package:

```bash
tlmgr install <package>
```

**`xelatex not found`** — pick an engine that exists: `pdf-engine: pdflatex` or install TinyTeX which ships XeLaTeX.

**Unicode characters fail** — switch to `pdf-engine: xelatex` or `lualatex` and set `mainfont:` / `monofont:`.

## YAML errors

**`mapping values are not allowed in this context`** — a value contains `:` but isn't quoted:

```yaml
# wrong
title: My talk: 2026

# right
title: "My talk: 2026"
```

**`did not find expected key`** — indentation is inconsistent. Use spaces, not tabs, and keep the indent width uniform.

**`unknown option 'X'`** — the option lives under a different parent. Most format options go under `format: html:` (or `pdf:`, etc.), not at the top level.

## Cross-references not resolving

- Label missing reserved prefix (`fig-`, `tbl-`, `eq-`, `sec-`, ...). Lowercase only.
- For `@sec-`, you need `number-sections: true`.
- Underscores in labels break PDF output; use hyphens.
- Computed figures need `#| label: fig-...` as a cell option, not a div ID.

## Citations not rendering

- `bibliography:` file path is wrong or relative to the wrong directory.
- The `@key` doesn't match an entry in the `.bib` file (keys are case-sensitive).
- `format: typst` uses Typst's engine; add `citeproc: true` to force Pandoc.
- `cite-method: biblatex` ignores CSL files.

## Execution

**`Cell execution timed out`** — increase in cell: `#| execute-timeout: 300` or document-level:

```yaml
execute:
  timeout: 300
```

**Code re-runs every render and is slow** — add `execute: freeze: auto` and commit `_freeze/`.

**Shell commands with `!` fail in Python cells** — this works in Jupyter engine only, not in knitr's reticulate.

## Website / book

**Navbar links 404** — `href:` must be a `.qmd` path, not the rendered `.html`.

**Sidebar items missing** — under `website:`, `sidebar:` needs `contents:` to list files or sections explicitly, unless `auto:` is used.

**Listings empty** — `listing.contents:` must point to a directory or glob matching `.qmd` files with frontmatter that includes `title:` and `date:`.

## `quarto publish`

**`Unable to determine target`** — run with an explicit target: `quarto publish gh-pages`.

**GH Pages 404 after publish** — check repo Settings → Pages is set to serve from the `gh-pages` branch `/ (root)`.

**Changes don't appear** — `--no-browser` / clear browser cache; confirm `_publish.yml` points to the correct project ID.

## Useful debug commands

```bash
quarto render doc.qmd --log-level debug
quarto render doc.qmd --execute-debug
quarto preview doc.qmd --no-browser
quarto render --cache-refresh
quarto render --no-freeze
quarto check
quarto list tools
```
