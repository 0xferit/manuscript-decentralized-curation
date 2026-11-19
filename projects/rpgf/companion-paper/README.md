# Decentralized Curation for Retroactive Public Goods Funding

Companion preprint: **A Blueprint for Credible Consensus**, by Ferit Tunçer.

- [Manuscript source](manuscript.md)
- [Source record and remaining questions](source-and-open-questions.md)
- [Archival source excerpts](source-evidence.md)
- [Verification record](verification-results.json)
- [Publication metadata](zenodo-metadata.json)
- [Shared bibliography](../../../references.bib)

The companion is a separate publication that cites the parent preprint and has its own Zenodo concept record. To deposit a version after its source merges:

1. Tag the merged commit `public-goods-vX.Y.Z`. The verification record at that commit holds the reviewed PDF's SHA-256 as `release_X_Y_Z.checks.pdf_sha256`.
2. Publish a GitHub pre-release of the tag with the reviewed PDF attached as `decentralized-curation-public-goods-vX.Y.Z.pdf`. It must be a pre-release, because every other published release starts the parent's deposit.
3. Run the [Zenodo workflow](../../../.github/workflows/publish-zenodo.yml) on `main` with that tag. It verifies the release, builds an unpublished draft and prints it.
4. Check the draft, then run the workflow again with the draft's ID as `publish_draft`.

The website renders the current source. Each `public-goods-v*` tag preserves the source of a deposited preprint version, and the verification record keeps each version's publication checks. Corrections made after a release appear on the website before the next preprint version.

The website route `/rpgf/companion/` includes this canonical manuscript through a thin Quarto wrapper. It links to the working evidence records and the frozen preprint source separately.

## Render

From the repository root, with Pandoc, XeLaTeX and the Georgia font installed:

```sh
make render-companion
```

If XeLaTeX is not on the executable search path, pass its location as `PDF_ENGINE` to the same target. The manuscript frontmatter owns the paper size, font, margins and link colors; its table markup sets column proportions. Raw LaTeX header commands apply only to the PDF. The source also declares its relative shared bibliography path. The archival excerpts quote the shared rules used by this application from the published parent’s version 1.3.0. The paper is a proposed design and evaluation agenda; it reports no empirical validation.
