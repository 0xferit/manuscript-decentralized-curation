---
name: quarto
description: "Author and render Quarto documents, presentations, websites, books, and dashboards. Load when working with .qmd files, _quarto.yml projects, Quarto YAML frontmatter, reveal.js slides, or when the user mentions Quarto, knitr, Jupyter/Python/R/Julia/Observable reproducible reports, scientific publishing, or rendering to HTML/PDF/Word/Typst. Covers cell execution options, cross-references, citations, callouts, shortcodes, projects, and the quarto CLI (render, preview, publish, create)."
license: MIT
metadata:
  version: '1.0'
  source: https://quarto.org/
---

# Quarto

Quarto is an open-source scientific and technical publishing system built on Pandoc. It renders `.qmd`, `.ipynb`, and `.Rmd` files to HTML, PDF, MS Word, Typst, reveal.js slides, ePub, websites, books, and dashboards, executing embedded R, Python, Julia, or Observable JS code along the way.

## When to Use This Skill

Load this skill when the user:

- Edits or creates `.qmd` files or `_quarto.yml` projects
- Asks to render, preview, or publish a Quarto document
- Wants a reproducible report, paper, slide deck, website, or book from code and markdown
- Needs Quarto-specific syntax: YAML frontmatter, code cell options (`#|`), cross-references (`@fig-`, `@tbl-`, `@eq-`, `@sec-`), callouts, divs/spans, shortcodes, citations
- Converts between formats (HTML ↔ PDF ↔ Word ↔ Typst ↔ revealjs)
- Troubleshoots execution engines (knitr vs jupyter), kernels, or rendering errors
- Asks about `quarto publish` to GitHub Pages, Quarto Pub, Netlify, Posit Connect, Confluence, or Hugging Face Spaces

Do **not** load this skill for generic Markdown or Jupyter questions unrelated to Quarto.

## Core Mental Model

A Quarto document is plain-text Markdown with three components:

1. **YAML frontmatter** between `---` delimiters at the top: metadata, format, execution options.
2. **Markdown body**: Pandoc markdown plus Quarto extensions (callouts, divs, shortcodes, cross-refs, citations).
3. **Executable code cells** using fenced code blocks with `{lang}` braces:

   ````markdown
   ```{python}
   #| label: fig-polar
   #| fig-cap: "A line plot on a polar axis"
   import matplotlib.pyplot as plt
   ```
   ````

   Cell options go in YAML comments prefixed with `#|`.

**Engine selection (automatic):**

| File | Engine |
|---|---|
| `.qmd` with `{r}` block | knitr |
| `.qmd` with other executable blocks | jupyter (kernel from first exec block) |
| `.qmd` with no exec blocks | none (pure markdown) |
| `.ipynb` | jupyter |
| `.Rmd` | knitr |

Override in YAML with `engine: jupyter` / `engine: knitr` / `engine: markdown`, or pin a kernel with `jupyter: python3`.

## Minimal Working Examples

### HTML article (Python)

```markdown
---
title: "Analysis"
author: "Jane Doe"
date: today
format:
  html:
    toc: true
    code-fold: true
    theme: cosmo
jupyter: python3
---

## Introduction

Inline math: $E = mc^2$.

```{python}
#| label: fig-sine
#| fig-cap: "A sine wave."
import numpy as np, matplotlib.pyplot as plt
x = np.linspace(0, 2*np.pi, 200)
plt.plot(x, np.sin(x)); plt.show()
```

See @fig-sine for the plot.
```

### PDF article with citations

```yaml
---
title: "Paper"
format: pdf
bibliography: references.bib
csl: nature.csl
---
```

Cite with `[@knuth1984]`, in-text `@knuth1984`, or suppress author `[-@knuth1984]`.

### Reveal.js slides

```markdown
---
title: "Talk"
format:
  revealjs:
    theme: simple
    incremental: true
---

## First slide

- Point one
- Point two

## Two columns

:::: {.columns}
::: {.column width="50%"}
Left
:::
::: {.column width="50%"}
Right
:::
::::
```

Level-2 headings `##` start new slides, `#` starts a section/title slide, `---` creates an untitled slide, `. . .` creates a pause, `::: {.notes}` adds speaker notes.

## Common Patterns

**Callouts** (5 types: `note`, `tip`, `warning`, `caution`, `important`):

```markdown
::: {.callout-note}
Important context here.
:::
```

**Cross-references** — label must start with a reserved prefix (`fig-`, `tbl-`, `eq-`, `sec-`, `thm-`, `lem-`, `def-`, `exm-`, `alg-`, etc.). Reference with `@label`.

```markdown
![Caption](img.png){#fig-elephant}
See @fig-elephant.

$$ y = mx + b $$ {#eq-line}

## Intro {#sec-intro}   <!-- requires number-sections: true -->
```

**Code cell options** (always `#|` inside the cell):

```
#| label: fig-plot
#| fig-cap: "My plot"
#| echo: false          # hide source
#| eval: true           # execute
#| warning: false       # hide warnings
#| include: false       # suppress code AND output
#| output: asis         # treat output as raw markdown
```

**Shortcodes**: `{{< pagebreak >}}`, `{{< video URL >}}`, `{{< kbd Ctrl-C >}}`, `{{< include _file.qmd >}}`, `{{< meta title >}}`.

**Raw blocks** to escape format-specific content:

````markdown
```{=html}
<iframe src="..."></iframe>
```
````

## Quarto CLI

Run these from a terminal. Always prefer `quarto preview` during authoring — it watches the file and live-reloads.

| Command | Purpose |
|---|---|
| `quarto render doc.qmd` | Render a single document |
| `quarto render doc.qmd --to pdf` | Render to a specific format |
| `quarto render` (in project dir) | Render whole project |
| `quarto preview doc.qmd` | Live-reloading local preview |
| `quarto create project <type> <name>` | Scaffold a new project (`default`, `website`, `blog`, `manuscript`, `book`, `confluence`) |
| `quarto publish <target>` | Publish (`gh-pages`, `quarto-pub`, `netlify`, `connect`, `confluence`, `huggingface`) |
| `quarto add <extension>` | Install an extension |
| `quarto install tinytex` | Install TinyTeX for PDF rendering |
| `quarto check` | Diagnose install, engines, kernels |
| `quarto list` | List installed extensions / tools |

## Projects (`_quarto.yml`)

A project is a directory with a `_quarto.yml` that shares config across many documents. Minimal website project:

```yaml
project:
  type: website

website:
  title: "My Site"
  navbar:
    left:
      - href: index.qmd
        text: Home
      - about.qmd

format:
  html:
    theme: cosmo
    toc: true
```

Project types: `default`, `website`, `blog`, `book`, `manuscript`, `confluence`.

Files starting with `_` or `.`, plus `README.md`, `CLAUDE.md`, `AGENTS.md`, are skipped by default. Control explicitly:

```yaml
project:
  render:
    - "*.qmd"
    - "!draft.qmd"
```

## Deep-Dive References

Read these files from `references/` only when the current task needs them:

- `references/yaml-frontmatter.md` — Common YAML options across formats (title/author/toc/numbering/code options), per-format sections for HTML, PDF, Typst, Word, revealjs.
- `references/execution-options.md` — Full cell option matrix, knitr vs jupyter specifics, `freeze`, `cache`, `keep-md`, figure sizing defaults.
- `references/cross-references.md` — Every reserved prefix (figures, tables, equations, sections, theorems, listings, callouts), subfigure/subtable panels, custom prefixes, group refs.
- `references/citations.md` — `bibliography`, `csl`, `cite-method` (citeproc/biblatex/natbib), `nocite`, Typst citation handling, `#refs` div placement.
- `references/presentations.md` — revealjs slides, themes, fragments, columns, speaker notes, chalkboard, Beamer, PowerPoint.
- `references/projects-websites-books.md` — `_quarto.yml` for websites, blogs, books, manuscripts; navbar/sidebar; listings; freeze; output directories.
- `references/publishing.md` — `quarto publish` per target, GitHub Actions CI, `_publish.yml`, previews.
- `references/troubleshooting.md` — Common errors (missing kernel, LaTeX package, pandoc version, YAML colons, freeze issues).

## Authoring Workflow (default)

1. **Clarify the target format first.** HTML article? PDF paper? Slides? Website? The YAML and which options matter depend entirely on this.
2. **Start the YAML frontmatter** with `title`, `author`, `format:`, and the execution engine/kernel if code is involved.
3. **Write the body** in Pandoc markdown. Use Quarto extensions (callouts, cross-refs, shortcodes) instead of raw HTML where possible — they render across all output formats.
4. **For code cells**, always prefer `#|` cell options over chunk-level knitr syntax, and always set `#| label:` when you need to cross-reference the output.
5. **Render with `quarto render`** and report any diagnostics. For PDF, if the user hits a missing LaTeX package, recommend `quarto install tinytex`.
6. **When writing to a file**, use the `.qmd` extension and produce the YAML frontmatter as the first bytes of the file (no blank lines before `---`).

## Rules and Gotchas

- The very first three characters of a `.qmd` must be `---` (YAML opener). Same rule as SKILL.md.
- Cell option values that contain `:` must be quoted (`fig-cap: "Title: subtitle"`).
- Cross-reference labels must be **lowercase** and start with a reserved prefix. Underscores in labels break PDF output — use hyphens.
- Lists in Quarto require a blank line above them (stricter than GitHub-flavored Markdown).
- `number-sections: true` is required before `@sec-` references resolve.
- When mixing R and Python in one doc, use the knitr engine (reticulate handles Python).
- Typst output uses Typst's own citation engine by default. Set `citeproc: true` to route through Pandoc instead.
- Never rewrite a user's YAML with options they didn't ask for. Preserve custom keys.
- When asked to "convert to Quarto", prefer minimal changes: rename to `.qmd`, add YAML frontmatter, convert code fences to `{lang}` execution blocks only if the user wants execution.

## Output Style

When explaining a Quarto concept, show the YAML or markdown snippet first, then a one-line explanation. Keep snippets runnable — a reader should be able to paste them into a fresh `.qmd` and render.
