# Decentralized Curation for Public Goods

Companion preprint: **A blueprint for contestable assessment and funding**, by Ferit Tunçer.

- [Manuscript source](manuscript.md)
- [Source record and remaining questions](source-and-open-questions.md)
- [Archival source excerpts](source-evidence.md)
- [Verification record](verification-results.json)
- [Publication metadata](zenodo-metadata.json)
- [Shared bibliography](../../../references.bib)

The companion is a separate publication that cites the parent preprint. The repository’s parent-paper Zenodo uploader must not be used for this paper because it creates a new version of the parent record.

The working source includes unpublished review corrections. Its publication date and version identify the preprint from which this revision develops; they do not indicate that the corrections have been published. The `public-goods-v0.1.0` tag preserves the publication source, and the publication-preparation entries in the verification record remain historical. Current review checks are recorded separately.

## Render

From the repository root, with Pandoc, XeLaTeX and the Georgia font installed:

```sh
make render-companion
```

If XeLaTeX is not on the executable search path, pass its location as `PDF_ENGINE` to the same target. The manuscript frontmatter owns the paper size, font, margins and link colors; its table markup sets column proportions. The source also declares its relative shared bibliography path. The archival excerpts record the later working rules used by this application separately from the published parent’s version 1.2.0. The paper is a proposed design and evaluation agenda; it reports no empirical validation.
