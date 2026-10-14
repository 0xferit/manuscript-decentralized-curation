# RPGF

Retroactive public goods funding (RPGF) is a public-goods application of the decentralized curation framework. This directory contains two distinct proposed funding lifecycles.

- [Batch reference design](design.md): fixed-round nomination, evaluation and disbursement proposal.
- [Public-goods companion paper](companion-paper/manuscript.md): current working source for the ongoing-funding application, with evidence records and a checked example. Review corrections remain unpublished until separately released.

Relation to the thesis:
- The thesis frames RPGF as one downstream application of the broader curation methodology.
- The batch proposal and ongoing companion share the foundational paper's protocol rules but retain their separate application lifecycles.

Source-of-truth policy:
- Edit RPGF content in this directory.
- `design.md` owns the batch reference proposal; `companion-paper/manuscript.md` owns the ongoing application. Neither is a source of new shared protocol rules.
- Published routes `/rpgf/` and `/rpgf/design/` serve the batch design through thin root-level Quarto wrappers. The companion has its own local document build and separate preprint publication record.
