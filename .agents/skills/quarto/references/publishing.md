# Publishing

`quarto publish` renders and uploads in one step. It stores target settings in `_publish.yml` next to the project so subsequent runs are one command.

## Targets

| Target | Command | Notes |
|---|---|---|
| Quarto Pub | `quarto publish quarto-pub` | Free, fast, public; account required |
| GitHub Pages | `quarto publish gh-pages` | Pushes rendered site to `gh-pages` branch |
| Netlify | `quarto publish netlify` | Requires Netlify CLI auth; custom domains |
| Posit Connect | `quarto publish connect` | Server URL prompt |
| Posit Connect Cloud | `quarto publish connect-cloud` | Hosted |
| Confluence | `quarto publish confluence` | Pages in team Spaces |
| Hugging Face Spaces | `quarto publish huggingface` | Docs alongside models/datasets |

Run once interactively; after that, settings persist in `_publish.yml`:

```yaml
- source: project
  quarto-pub:
    - id: 5f3abafe-68f9-4c1d-835b-9d668b892001
      url: https://myname.quarto.pub/my-site
```

## GitHub Pages workflows

### Option A: publish from gh-pages branch

```bash
# one time: create an empty gh-pages branch
git checkout --orphan gh-pages
git reset --hard
git commit --allow-empty -m "init"
git push origin gh-pages
git checkout main

# publish
quarto publish gh-pages
```

### Option B: GitHub Actions CI

`.github/workflows/publish.yml`:

```yaml
on:
  push:
    branches: [main]

name: Quarto Publish

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - uses: quarto-dev/quarto-actions/setup@v2

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - run: pip install jupyter matplotlib pandas

      - name: Render and publish
        uses: quarto-dev/quarto-actions/publish@v2
        with:
          target: gh-pages
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

For R projects, add `r-lib/actions/setup-r@v2` and `setup-renv@v2` steps.

## Netlify

```bash
# one time
netlify login
quarto publish netlify
```

Or use Netlify's git integration: push `_site/` (or build in CI with `quarto render`) and point Netlify at the output directory.

## Quarto Pub

```bash
quarto publish quarto-pub
```

Prompts for your account the first time.

## Render without publishing

Sometimes you want to build locally and hand the output to another tool:

```bash
quarto render                # builds to _site/, _book/, or output-dir
```

Then deploy the output directory however you like.

## Preflight in CI

```bash
quarto check                 # verifies installation, engines, kernels
quarto render --log-level warn
```

## Freeze in CI

Commit `_freeze/` so CI doesn't need to re-execute slow code:

```yaml
execute:
  freeze: auto
```

## Suppressing drafts

```yaml
project:
  render:
    - "*.qmd"
    - "!drafts/"
```

Or per-file:

```yaml
draft: true                   # post excluded from listings
```
