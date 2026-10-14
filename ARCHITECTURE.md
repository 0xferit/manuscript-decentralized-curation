# Architecture

## Release publication

Manuscript builds and publication are separate operations. The release maintainer builds and reviews a PDF from an exact commit on `main`, then attaches it and a manifest to a draft GitHub release. The manifest binds the release tag, source commit, manuscript digest and reviewed PDF digest. The release event publishes those bytes to Zenodo; it cannot substitute a fresh render. `.zenodo.json` in the tagged source owns deposit metadata.

The publication job has read-only GitHub access and exposes the Zenodo credential only to the upload step after local validation. Publications are serialized across all tags in this repository. The uploader refuses an existing unpublished draft, a conflicting published version or an upload checksum mismatch. A retry after successful publication checks the existing version and performs no mutation when its PDF and descriptive metadata match.

GitHub release maintainers remain trusted to review and attach the intended artifacts. Manifest checks establish artifact identity, not scientific validity. The Zenodo account must use a single publisher: its separate GitHub integration must be disabled, and a maintainer must not edit drafts concurrently with publication. The legacy Zenodo API cannot atomically reserve a new draft against a concurrent manual edit; failed or uncertain uploads require inspection before retrying.

## Manuscripts and application boundaries

`paper.qmd` owns the general Decentralized Curation framework and shared protocol rules. `projects/truth-post/blueprint.md` develops the news application; `projects/truth-post/implementation-report.md` records the partial 2023 deployment. `projects/rpgf/companion-paper/manuscript.md` is the current public-goods application and supersedes `projects/rpgf/design.md`. The earlier fixed-round design is retained for provenance, with no authority over current rules. Historical designs and workshop demonstrations do not establish that an integrated implementation exists.

The companion cites a released foundational preprint for its research context and records the later working decisions it uses separately. Its source excerpts, source digests and publication-preparation results are historical evidence. Published snapshots and editable working sources are separate; local corrections do not change prior publication or human-verification records.

## Accuracy and eligibility

The foundational paper's Accuracy layer owns optimistic publication, bonded challenges and item closure. Structural transaction checks precede publication; semantic claims remain contestable. Closure affects the bonded item and its future eligibility, without banning its publisher or beneficiary from fresh submissions. Reputation is separate from submission eligibility.

Application funding rules distinguish prospective allocation from amounts already earned. The ongoing public-goods profile preserves earned beneficiary entitlements through disputes, revisions and closure. Neither a later assessment nor payment collection may reinterpret an earlier entitlement.

## Relevance accounting and settlement

The foundational paper's Relevance layer owns drafting, quorum, service fees, penalties, rounding and public appeal settlement. Utility-token collateral and redistribution use a ledger separate from ether (ETH) jury-service funds and appeal capital. Reference fee and workload values are defined in the paper; application documents refer to those definitions. Workload assumptions are not proof of effort, and fixed service fees do not establish truthful or competent assessment.

Each pool defines its own relevance rubric and numeric interpretation. A direct proportional funding application uses scores as relative allocation weights, subject to its eligibility and cap rules. The Truth Post feed uses its separate ranking formula. Neither allocation weights nor coherence measure public benefit directly.

Ordinary attempts already drawn before exit and funded contested appeal chains retain the continuation rights specified in the paper. Continuation preserves pinned assessments and financial commitments without restoring the closed item's eligibility. Earned jury fees, contribution refunds, backer payouts and beneficiary earnings remain distinct obligations. Unused reservations return through their original funding paths; assigned but unclaimed entitlements are not reusable funds.

The paper owns the execution-order rule for fresh service-budget reservations, the positive proof-opening window, bounded leak confiscation, exact integer allocation and recipient-controlled receiving addresses. Implementation details explicitly left open there remain open in application documents. In particular, applications must not infer an asset conversion rate or resolve unspecified same-round penalty ordering by combining ledgers or collecting collateral twice.

## Build and generated artifacts

The Makefile owns local build entrypoints. The Quarto website configuration selects the foundational paper and project publication wrappers and owns the shared page tree. Native navigation supplies a responsive document sidebar, search, section breadcrumbs and previous/next links; each article's table of contents is separate on the right. The root remains the foundational paper, with public-goods and Truth Post branches preserving existing routes. The superseded public-goods design retains its legacy URL and shared sidebar for return navigation but is excluded from the active page tree and search index. The custom figure script only switches figure variants; it does not replace website navigation or theme controls.

Wrappers include their canonical project sources rather than maintaining copies. The companion wrapper declares its source directory as a resource path for bibliography resolution and uses the source's mathematical input notation. Its website rendering is a working revision separate from the frozen preprint. Analysis outputs are generated and ignored; tracked conceptual diagrams are regenerated from `diagrams/generate_diagrams.py`. The shared bibliography is `references.bib`. Shared HTML overflow rules live in `layout.css` so tables and equations can scroll within the article in both color themes.

The companion uses Pandoc with its declared bibliography and explicit mathematical-input extension. Local review outputs under `outputs/` are separate from released preprints, publication records and historical artifact digests. The website pipeline publishes HTML, so it does not advertise local-only PDF files as downloads. A build verifies document production, not the economic mechanism or the completeness of human source verification.
