# YAML Frontmatter Reference

YAML frontmatter is delimited by `---` at the top of the file. Options can be top-level (apply to any format) or nested under a `format:` key.

## Universal document options

| Option | Purpose |
|---|---|
| `title` | Document title |
| `subtitle` | Subtitle |
| `author` | String or list of author objects (`name`, `email`, `affiliation`, `orcid`) |
| `date` | Date string, or `today`, `last-modified`, `now` |
| `date-format` | `iso`, `long`, `medium`, `short`, or a custom Moment-style pattern |
| `abstract` | Document abstract |
| `keywords` | List of keywords |
| `doi` | Digital Object Identifier |
| `lang` | Language code (`en`, `pt`, `tr`, ...) |
| `bibliography` | Path(s) to `.bib` / `.bibtex` / CSL JSON / YAML |
| `csl` | Path or URL to CSL style file |
| `number-sections` | Number headings (required for `@sec-` refs) |
| `number-depth` | Max heading level to number |
| `toc` | Include table of contents |
| `toc-depth` | TOC max depth (default 3) |
| `toc-title` | TOC heading text |
| `include-in-header` / `include-before-body` / `include-after-body` | Inject raw content |
| `execute` | Doc-level execution defaults (see `references/execution-options.md`) |
| `filters` | List of Lua/Pandoc filters |
| `resources` | Extra files copied to output |
| `engine` | `jupyter`, `knitr`, `markdown` |
| `jupyter` | Kernel name (`python3`) or full `kernelspec` object |
| `freeze` | `true`, `false`, `auto` — skip re-execution |
| `cache` | `true`, `false`, `refresh` |

## HTML (`format: html`)

```yaml
format:
  html:
    theme: cosmo          # or flatly, darkly, litera, ..., or path to .scss
    css: styles.css
    toc: true
    toc-location: right   # body | left | right | left-body | right-body
    toc-expand: true
    number-sections: true
    code-fold: true       # true | false | show
    code-summary: "Show code"
    code-tools: true
    code-copy: hover      # true | false | hover
    code-line-numbers: true
    code-link: true
    anchor-sections: true
    smooth-scroll: true
    tabsets: true
    fig-width: 8
    fig-height: 5
    embed-resources: true # single self-contained file
```

Bootswatch themes: `cerulean, cosmo, cyborg, darkly, flatly, journal, litera, lumen, lux, materia, minty, morph, pulse, quartz, sandstone, simplex, sketchy, slate, solar, spacelab, superhero, united, vapor, yeti, zephyr`.

## PDF (`format: pdf`)

```yaml
format:
  pdf:
    documentclass: scrartcl   # or article, report, book
    papersize: a4
    geometry:
      - margin=1in
    fontsize: 11pt
    mainfont: "Source Serif Pro"
    monofont: "JetBrains Mono"
    linestretch: 1.25
    colorlinks: true
    toc: true
    number-sections: true
    highlight-style: github
    pdf-engine: xelatex       # or lualatex, pdflatex, tectonic
    cite-method: biblatex     # citeproc | biblatex | natbib
    biblio-style: authoryear
    include-in-header:
      text: |
        \usepackage{siunitx}
```

Run `quarto install tinytex` if LaTeX isn't installed.

## Typst (`format: typst`)

```yaml
format:
  typst:
    papersize: a4
    margin:
      x: 2cm
      y: 2.5cm
    mainfont: "Libertinus Serif"
    columns: 1
    section-numbering: "1.1.a"
    toc: true
    bibliographystyle: apa     # or path to CSL
    citeproc: true             # route citations through Pandoc instead of Typst
```

## MS Word (`format: docx`)

```yaml
format:
  docx:
    reference-doc: template.docx
    toc: true
    number-sections: true
    highlight-style: tango
```

`reference-doc` is the single most impactful option — pass a styled template to control all Word styling.

## Reveal.js slides (`format: revealjs`)

```yaml
format:
  revealjs:
    theme: simple        # beige blood dark default dracula league moon night serif simple sky solarized
    slide-number: true
    show-slide-number: all
    chalkboard: true
    multiplex: false
    incremental: false
    controls: true
    progress: true
    history: true
    transition: slide    # none | fade | slide | convex | concave | zoom
    background-transition: fade
    slide-level: 2
    logo: logo.png
    footer: "My Talk"
    center: false
    preview-links: auto
    code-fold: show
    highlight-style: github
```

## Beamer PDF slides (`format: beamer`)

```yaml
format:
  beamer:
    theme: Madrid
    colortheme: seahorse
    aspectratio: 169
    navigation: horizontal
```

## Dashboards (`format: dashboard`)

```yaml
format:
  dashboard:
    orientation: columns   # or rows
    scrolling: true
    nav-buttons:
      - icon: github
        href: https://github.com/
    theme: cosmo
    logo: logo.png
```

## ePub (`format: epub`)

```yaml
format:
  epub:
    cover-image: cover.png
    toc: true
    epub-metadata: meta.xml
```

## Multiple formats

```yaml
format:
  html: default
  pdf: default
  docx: default
```

Render one with `quarto render doc.qmd --to pdf`.
