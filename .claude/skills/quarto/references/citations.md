# Citations and Bibliography

Quarto uses Pandoc's citeproc by default. Citations go in square brackets with `@key`; the bibliography is auto-generated from a `.bib`, `.bibtex`, `.json` (CSL), or `.yaml` file.

## Setup

```yaml
---
title: "Paper"
bibliography: references.bib      # or list: [refs1.bib, refs2.bib]
csl: nature.csl                   # optional style; URL also works
---
```

## Citation syntax

| Markdown | Author-date | Numeric |
|---|---|---|
| `[@knuth1984]` | (Knuth 1984) | [1] |
| `[-@knuth1984]` | (1984) | [1] |
| `@knuth1984` | Knuth (1984) | [1] |
| `[@knuth1984, p. 33]` | (Knuth 1984, 33) | [1] p. 33 |
| `[see @knuth1984; also @wickham2015]` | (see Knuth 1984; also Wickham 2015) | [see 1; also 2] |

Keys may contain alphanumerics, `_`, and `:.#$%&-+?<>~/`.

## Bibliography placement

By default Pandoc appends the reference list at the end. To control location:

```markdown
## References

::: {#refs}
:::
```

Suppress with `suppress-bibliography: true`.

## Including uncited items

```yaml
nocite: |
  @smith2020, @doe2021
```

Wildcard (include everything in the bib):

```yaml
nocite: |
  @*
```

## Styles (CSL)

- Default: Chicago Manual of Style author-date
- Browse 8,500+ styles at the [Zotero Style Repository](https://www.zotero.org/styles)
- Point `csl:` at a local `.csl` file or a URL

```yaml
csl: https://www.zotero.org/styles/apa
```

## PDF with biblatex or natbib

```yaml
format:
  pdf:
    cite-method: biblatex        # citeproc (default) | biblatex | natbib
    biblatexoptions: [sorting=nyt]
    biblio-style: authoryear
```

CSL is ignored when `cite-method` is not `citeproc`.

## Typst citations

`format: typst` uses Typst's own engine by default. Two choices:

```yaml
# Keep Typst's engine
format: typst
bibliography: refs.bib
csl: apa                    # Typst built-in style name or CSL path
```

```yaml
# Route through Pandoc citeproc
format: typst
citeproc: true
bibliography: refs.bib
csl: https://www.zotero.org/styles/apa-with-abstract
```

## .bib entry example

```bibtex
@article{knuth1984,
  author  = {Donald E. Knuth},
  title   = {Literate Programming},
  journal = {The Computer Journal},
  year    = {1984},
  volume  = {27},
  number  = {2},
  pages   = {97--111}
}
```
