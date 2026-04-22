# Presentations

Quarto produces three slide formats from the same source:

- `revealjs` — HTML slides (recommended default)
- `beamer` — LaTeX/PDF slides
- `pptx` — PowerPoint

## Slide structure

Same rules across formats:

- `##` (level 2) heading starts a new slide with a title
- `#` (level 1) heading starts a section/divider slide
- `---` (horizontal rule) starts an untitled slide
- `slide-level: N` changes which heading level breaks a slide

```markdown
---
title: "Talk"
author: "Name"
format: revealjs
---

# Section One

## Slide A
- bullet 1
- bullet 2

## Slide B
Some text.

---

Untitled slide content.
```

## Reveal.js options

```yaml
format:
  revealjs:
    theme: simple          # beige blood dark default dracula league moon night serif simple sky solarized
    slide-number: c/t      # c, c/t (current/total), h.v, h/v
    show-slide-number: all # all | print | speaker
    chalkboard: true       # press 'b' to draw, 'c' for chalkboard
    multiplex: false
    incremental: false
    controls: true
    progress: true
    history: true
    menu: true
    transition: slide      # none | fade | slide | convex | concave | zoom
    background-transition: fade
    logo: logo.png
    footer: "© 2026"
    center: false
    preview-links: auto
    slide-tone: false
    auto-stretch: true
```

## Incremental content

Global:

```yaml
format:
  revealjs:
    incremental: true
```

Per-block:

```markdown
::: {.incremental}
- Step 1
- Step 2
:::

::: {.nonincremental}
- All at once
:::
```

Mid-slide pause:

```markdown
## Slide

First part

. . .

Second part
```

## Columns

```markdown
:::: {.columns}

::: {.column width="40%"}
Left column content.
:::

::: {.column width="60%"}
Right column content.
:::

::::
```

## Speaker notes

```markdown
## Slide

Visible content.

::: {.notes}
Speaker-only notes. Press 'S' in reveal.js for speaker view.
:::
```

## Fragments (custom reveal)

```markdown
- [Fade in]{.fragment}
- [Grow]{.fragment .grow}
- [Highlight red]{.fragment .highlight-red}
- [Fade out]{.fragment .fade-out}
- [Semi-transparent]{.fragment .semi-fade-out}
```

## Backgrounds

```markdown
## Slide {background-color="black"}
## Slide {background-image="bg.png"}
## Slide {background-video="clip.mp4" background-video-loop="true"}
## Slide {background-iframe="https://example.com"}
```

## Auto-animate

```markdown
## Step {auto-animate=true}
```cpp
x = 1
```

## Step {auto-animate=true}
```cpp
x = 1
y = 2
```
```

## Beamer (PDF slides)

```yaml
format:
  beamer:
    theme: Madrid
    colortheme: seahorse
    aspectratio: 169
    navigation: horizontal
    fonttheme: serif
    fig-width: 10
    fig-height: 6
```

## PowerPoint

```yaml
format:
  pptx:
    reference-doc: template.pptx   # inherit master slides
    slide-level: 2
```

The `reference-doc` template controls all PowerPoint styling; Quarto fills in content layouts.
