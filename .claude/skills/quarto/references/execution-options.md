# Execution Options

Executable code cells are fenced blocks whose language is wrapped in braces: ` ```{python} `, ` ```{r} `, ` ```{julia} `, ` ```{ojs} `, ` ```{bash} ` (knitr only). Cell-level options use YAML comments starting with `#|`.

````markdown
```{python}
#| label: fig-hist
#| fig-cap: "Histogram"
#| echo: false
#| warning: false
import matplotlib.pyplot as plt
plt.hist([1, 2, 3, 2])
```
````

## Cell options

| Option | Values | Purpose |
|---|---|---|
| `label` | string starting with reserved prefix for refs | Cell identifier; required for cross-refs |
| `eval` | `true` / `false` / list of line numbers | Execute the cell |
| `echo` | `true` / `false` / `fenced` | Show source code |
| `output` | `true` / `false` / `asis` | Include results; `asis` = raw markdown |
| `warning` | `true` / `false` | Show warnings |
| `error` | `true` / `false` | Show errors without halting render |
| `message` | `true` / `false` | (knitr) show messages |
| `include` | `true` / `false` | Catch-all; `false` hides both code and output |
| `fig-cap` | string | Figure caption |
| `fig-subcap` | list or `true` | Subcaptions for multi-output cells |
| `fig-alt` | string | Alt text |
| `fig-width` / `fig-height` | inches | Per-cell figure size |
| `fig-align` | `default` / `left` / `center` / `right` |  |
| `fig-pos` | LaTeX placement, e.g. `H` |  |
| `layout-ncol` / `layout-nrow` | int | Multi-plot grid |
| `layout` | 2D array of widths | Custom multi-panel layout |
| `tbl-cap` | string | Table caption |
| `tbl-subcap` | list or `true` | Subtable captions |
| `classes` | list | CSS classes on output block |
| `panel` | `tabset` / `center` / `sidebar` | Wrap cell output in a panel |
| `column` | `body` / `margin` / `screen` / `screen-inset` / `body-outset` | Placement in advanced page layout |
| `renderings` | list of names | Multiple output variants (e.g. `[light, dark]`) |
| `cache` | `true` / `false` / `refresh` | Cache cell results |
| `freeze` | `true` / `auto` | Skip re-execution at project level |

## Document-level defaults

```yaml
execute:
  echo: false
  warning: false
  cache: true
  freeze: auto
```

## Figure size defaults (inches)

| Format | Default |
|---|---|
| Default | 7 × 5 |
| HTML Slides | 9.5 × 6.5 |
| Reveal.js | 9 × 5 |
| PDF | 5.5 × 3.5 |
| Beamer | 10 × 7 |
| PowerPoint | 7.5 × 5.5 |
| Word / ODT / RTF / EPUB | 5 × 4 |
| Hugo | 8 × 5 |

## Engine specifics

### Jupyter

```yaml
jupyter: python3
# or full spec:
jupyter:
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
```

- Shell magics work inside Python cells: `!pip install pandas`
- `ipynb-shell-interactivity: all` prints all top-level expressions (default `last_expr`)
- Intermediate: `keep-ipynb: true` preserves the generated notebook

### Knitr

```yaml
knitr:
  opts_chunk:
    collapse: true
    comment: "#>"
    R.options:
      knitr.graphics.auto_pdf: true
```

- Supports `{r}`, `{python}` (via reticulate), `{bash}`
- All standard knitr chunk options work (`dev`, `dpi`, `tidy`, `results`)
- Intermediate: `keep-md: true` keeps the post-knit markdown

### Markdown-only

```yaml
engine: markdown
```

Disables execution entirely; executable fences error out.

## Freeze and cache

- `freeze: auto` — re-execute only when the source changes (recommended for projects with slow code)
- `freeze: true` — never re-execute; use committed results from `_freeze/`
- `cache: true` — per-cell knitr-style cache in `_cache/`

`_freeze/` should be committed to version control so CI builds match local.
