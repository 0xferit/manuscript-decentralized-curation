# Decentralized Curation for Public Goods

Companion preprint: **A blueprint for contestable assessment and funding**, by Ferit Tunçer.

- [Manuscript source](manuscript.md)
- [Source record and remaining questions](source-and-open-questions.md)
- [Archival source excerpts](source-evidence.md)
- [Verification record](verification-results.json)
- [Publication metadata](zenodo-metadata.json)
- [Shared bibliography](../../../references.bib)

The companion is a separate publication that cites the parent preprint. The repository’s parent-paper Zenodo uploader must not be used for this paper because it creates a new version of the parent record.

## Render

From this directory, with Pandoc, XeLaTeX and the Georgia font installed:

```sh
pandoc manuscript.md --from=markdown+tex_math_single_backslash --standalone --citeproc --pdf-engine=xelatex --variable papersize=a4 --variable fontsize=11pt --variable geometry=margin=24mm --variable mainfont=Georgia --variable colorlinks=true --variable linkcolor=black --variable urlcolor=blue --variable citecolor=black --output companion-paper.pdf
```

The source declares its relative shared bibliography path. The archival excerpts record the later working rules used by this application separately from the published parent’s version 1.2.0. The paper is a proposed design and evaluation agenda; it reports no empirical validation.
