# Truth Post

Truth Post is the news-curation project that grew out of the thesis framework.

- `blueprint.md`: canonical Truth Post protocol blueprint
- `implementation-report.md`: retrospective on the 2023 partial deployment

Relation to the thesis:
- The thesis paper remains the primary artifact and summarizes the architecture, simulations, and deployment lessons.
- This directory holds the standalone project documents that expand the Truth Post design beyond the paper's condensed treatment.

Source-of-truth policy:
- Edit Truth Post content in this directory.
- `blueprint.md` remains the canonical Truth Post paper source.
- Published routes are served via `/truth-post/` and `/truth-post/blueprint/` through thin root-level Quarto wrappers.
