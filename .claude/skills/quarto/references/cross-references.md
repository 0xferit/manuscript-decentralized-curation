# Cross-References

Cross-references produce numbered, hyperlinked pointers to figures, tables, equations, sections, code listings, theorems, and callouts. The label on the target and the `@` reference in the body must both use a reserved prefix.

## Reference syntax

| Syntax | Output |
|---|---|
| `@fig-elephant` | Figure 1 |
| `@Fig-elephant` | Figure 1 (capitalized) |
| `[Fig @fig-elephant]` | Fig 1 (custom prefix) |
| `[-@fig-elephant]` | 1 (no prefix) |
| `[@fig-a; @fig-b; @fig-c]` | Figures 1, 2, 3 (group) |

## Reserved prefixes

| Prefix | Type | Printed name |
|---|---|---|
| `fig-` | Figure | Figure |
| `tbl-` | Table | Table |
| `eq-` | Equation | Equation |
| `sec-` | Section | Section |
| `lst-` | Listing | Listing |
| `tip-` / `nte-` / `wrn-` / `imp-` / `cau-` | Callouts | Tip / Note / Warning / Important / Caution |
| `thm-` / `lem-` / `cor-` / `prp-` / `cnj-` | Theorems | Theorem / Lemma / Corollary / Proposition / Conjecture |
| `def-` / `exm-` / `exr-` / `sol-` / `rem-` / `alg-` | Proofs etc | Definition / Example / Exercise / Solution / Remark / Algorithm |

Labels must be **lowercase** and start with the prefix. Avoid `_` (breaks PDF); use `-`.

## Figures

### Markdown image

```markdown
![An elephant](elephant.png){#fig-elephant}

See @fig-elephant.
```

### Div syntax (multiline caption / custom content)

```markdown
::: {#fig-elephant}
![](elephant.png)

An elephant in the Serengeti.
:::
```

### Subfigures

```markdown
::: {#fig-elephants layout-ncol=2}
![Surus](surus.png){#fig-surus}

![Hanno](hanno.png){#fig-hanno}

Famous elephants
:::

See @fig-elephants and specifically @fig-surus.
```

### Computed figures

````markdown
```{python}
#| label: fig-plot
#| fig-cap: "A sine curve."
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])
```

See @fig-plot.
````

Multiple outputs with subcaptions:

```yaml
#| label: fig-plots
#| fig-cap: "Two plots"
#| fig-subcap:
#|   - "First"
#|   - "Second"
#| layout-ncol: 2
```

Reference: `@fig-plots`, `@fig-plots-1`, `@fig-plots-2`.

## Tables

### Markdown table

```markdown
| Col1 | Col2 | Col3 |
|------|------|------|
| A    | B    | C    |

: My caption {#tbl-letters}

See @tbl-letters.
```

### Computed table

````markdown
```{r}
#| label: tbl-iris
#| tbl-cap: "Iris dataset"
knitr::kable(head(iris))
```
````

### Subtables

```markdown
::: {#tbl-panel layout-ncol=2}
| A | B |
|---|---|
| 1 | 2 |

: First {#tbl-first}

| X | Y |
|---|---|
| 3 | 4 |

: Second {#tbl-second}

Main caption
:::
```

## Equations

```markdown
$$
\sigma(z) = \frac{1}{1 + e^{-z}}
$$ {#eq-sigmoid}

See @eq-sigmoid.
```

## Sections

Requires `number-sections: true`.

```markdown
## Introduction {#sec-intro}

See @sec-intro.
```

## Code listings

````markdown
```{.python #lst-fib lst-cap="Fibonacci"}
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)
```

See @lst-fib.
````

## Theorems and proofs

```markdown
::: {#thm-line}
## Equation of a line

$$ y = mx + b $$
:::

See @thm-line.

::: {.proof}
Follows from the definition of slope.
:::
```

## Callouts as references

```markdown
::: {#tip-workflow .callout-tip}
## Use `freeze: auto` in projects
Saves re-execution time.
:::

See @tip-workflow.
```

## Changing printed names

```yaml
crossref:
  fig-title: "Fig."
  tbl-title: "Tab."
  fig-prefix: "fig."
  eq-prefix: "eqn."
  sec-prefix: "§"
```
