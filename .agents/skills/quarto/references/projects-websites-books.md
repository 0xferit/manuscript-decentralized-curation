# Projects, Websites, Books, Manuscripts

A Quarto project is a directory with a `_quarto.yml` file. It:

- Shares YAML across many documents
- Renders many files with one command
- Redirects output into `_site/` or `_book/`
- Supports `freeze` (skip re-execution)

Create: `quarto create project <type> <name>` where type is `default | website | blog | book | manuscript | confluence`.

## Default project

```yaml
# _quarto.yml
project:
  type: default
  output-dir: _output

format:
  html:
    theme: cosmo

execute:
  freeze: auto
```

## Controlling render targets

```yaml
project:
  render:
    - "*.qmd"
    - "!draft-*.qmd"
    - "!_internal/"
```

Files prefixed with `.`, `_` (non-top-level), and `README.md` / `CLAUDE.md` / `AGENTS.md` are skipped by default.

## Website

```yaml
project:
  type: website

website:
  title: "My Site"
  description: "Notes and essays"
  site-url: https://example.com
  repo-url: https://github.com/me/site
  repo-actions: [edit, issue]
  navbar:
    background: primary
    search: true
    left:
      - href: index.qmd
        text: Home
      - href: about.qmd
        text: About
      - href: posts.qmd
        text: Posts
    right:
      - icon: github
        href: https://github.com/me
  sidebar:
    style: floating
    contents:
      - index.qmd
      - section: "Guides"
        contents:
          - guides/one.qmd
          - guides/two.qmd
  page-footer:
    left: "© 2026"
    right:
      - icon: rss
        href: index.xml

format:
  html:
    theme: cosmo
    css: styles.css
    toc: true
```

## Blog (listings)

A blog is a website with a listing page. `index.qmd`:

```markdown
---
title: "Blog"
listing:
  contents: posts
  sort: "date desc"
  type: default          # default | table | grid
  categories: true
  sort-ui: false
  filter-ui: false
  feed: true
page-layout: full
---
```

Individual posts live in `posts/<name>/index.qmd` with their own frontmatter:

```yaml
---
title: "My post"
author: "Me"
date: 2026-04-22
categories: [research, notes]
image: cover.png
---
```

## Book

```yaml
project:
  type: book

book:
  title: "My Book"
  author: "Name"
  date: today
  chapters:
    - index.qmd
    - intro.qmd
    - part: "Part 1"
      chapters:
        - ch1.qmd
        - ch2.qmd
    - summary.qmd
    - references.qmd
  appendices:
    - appendix.qmd
  repo-url: https://github.com/me/book
  downloads: [pdf, epub]

bibliography: references.bib

format:
  html:
    theme: cosmo
  pdf:
    documentclass: scrbook
  epub:
    cover-image: cover.png
```

Cross-references work across chapters automatically. `references.qmd` should contain a `# References\n\n::: {#refs}\n:::` placeholder.

## Manuscript

A manuscript is a notebook-first scholarly article that produces both a typeset PDF/HTML and downloadable computational notebooks.

```yaml
project:
  type: manuscript

manuscript:
  article: index.qmd
  notebooks:
    - notebook: analysis.ipynb
      title: "Data analysis"

format:
  html: default
  pdf: default
  jats: default          # archival XML for journal submission
```

## Shared output directory

```yaml
project:
  output-dir: _output    # default | website: _site | book: _book
```

## Freeze (skip re-execution)

```yaml
execute:
  freeze: auto           # re-execute only when source changes
```

Commit the `_freeze/` directory so CI builds reproduce local results without re-running code.

## Project profiles

Different configs for different contexts (e.g., draft vs production):

```yaml
# _quarto.yml
project:
  type: website

profile:
  default: production
  group:
    - [draft, production]
```

```yaml
# _quarto-draft.yml
website:
  title: "DRAFT: My Site"
```

Render with `quarto render --profile draft`.
