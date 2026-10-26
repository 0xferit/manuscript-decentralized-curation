# Source record and author-review questions

This record accompanies [the manuscript](manuscript.md). It records agent inspection, not human scientific verification. No source or claim has been marked human-verified. The author authorized publication of version 0.1.0 as a preprint on 14 October 2026 and of version 0.2.0 on 25 October 2026. Author identity and identifier are taken from the parent manuscript metadata; no affiliation, funding declaration or consent statement is inferred. Human source-verification flags remain unchanged.

Version 0.1.0 quoted the shared mechanism rules from an unpublished working copy of the parent manuscript. The parent's version 1.3.0 publishes those rules, so version 0.2.0 cites and quotes that release instead. The version 0.1.0 source record remains at the `public-goods-v0.1.0` tag, and its publication-preparation checks remain under `publication_preparation` in [the verification record](verification-results.json). Availability notes may record later removal of working documents without changing their recorded digests or verification status.

## Authority and scope

The paper develops the author's current **ongoing public-goods curation and funding** design. This is a settled direction, not a choice awaiting ratification against the earlier fixed-round application document. The author clarified that current design decisions take precedence over outdated prose under the project directories and requested this consistency audit.

For this revision, authority follows the latest explicit author decisions, the published parent version 1.3.0 for shared mechanism rules, and the current author-clarification record for application-specific behavior. Application-specific operational choices are not attributed to the parent. The earlier fixed-round document has been deleted. E004 below preserves the inspection record of an uncommitted working copy; it is not a competing specification or a released source snapshot.

The [presentation evidence register](https://github.com/0xferit/decentralized-curation/blob/73000c9e696ee08c91681e729d0d0927630c11de/docs/presentation-sources.md) records the current ongoing-funding decisions. The parent leaves some beneficiary-payout conditions to the application; for this application, the author's explicit immediate-claimability decision supplies that condition. No batch terminal-disbursement rule, holdback of already-earned funds, allocation-sized challenge stake or universal one-entry-per-round rule is imported.

The [claim register](claims.csv) maps numbered evidence comments in the manuscript to [source identifiers](source_manifest.json). Each claim hash covers the immediately preceding prose paragraph or contiguous list block, omits the evidence comment itself and normalizes whitespace to single spaces. For a list, all items in that block are covered, not only the final item. Published works use the repository’s [shared bibliography](../../../references.bib). The [verification record](verification-results.json) maps evidence identifiers to their scholarly citation keys; working sources and the synthetic example remain evidence records. All claim verification statuses remain `unverified`, because the skill's verification gate requires a named human.

## Inspected evidence

Relevant parent and presentation-register passages are preserved in [the archival evidence supplement](source-evidence.md); the full-source digests identify the versions from which they were extracted.

Inspection date: 14 October 2026; E001 and E002 were re-inspected on 25 October 2026 for version 0.2.0. Local source digests identify the bytes inspected even where the working tree was uncommitted. They do not make those bytes a publicly archived release.

| ID | Source and role | Inspection and boundary |
| --- | --- | --- |
| E001 | Ferit Tunçer, *Decentralized Curation: Trustless Transformation of Information into Knowledge*, version 1.3.0. [Published preprint](https://doi.org/10.5281/zenodo.23636842). | Zenodo metadata and the released Portable Document Format (PDF) file opened directly. Metadata gives 25 October 2026, version 1.3.0 and the stated title and creator. Framework, inherited concepts, shared mechanism rules and published limitations. |
| E002 | [Archived parent excerpts](source-evidence.md) from the published version 1.3.0 source. | Quotes `paper.qmd` at the published source revision `8dafde2cd6407cfb4631d70677a3fa22801a9c69`: accuracy, relevance, jury, fees, coherence penalties, appeals and their limits. Each excerpt's digest binds it to that source. |
| E003 | [Presentation evidence register](https://github.com/0xferit/decentralized-curation/blob/73000c9e696ee08c91681e729d0d0927630c11de/docs/presentation-sources.md). | Inspected author clarifications about ongoing funding, accuracy, existing earnings, allocation, appeals, source scope and evidence limits. This is the local authority for the selected ongoing profile. It is not a peer-reviewed study or executable specification. |
| E004 | Earlier fixed-round application document (deleted). | Working copy modified at parent repository HEAD `ba7eb4ec37eda970dc7d7051a066ec5ad67dc573`. Re-read only to locate stale requirements and conflicting lifecycle/accounting rules. The recorded digest identifies those uncommitted bytes, not a released or retrievable Git snapshot. No adopted mechanism claim in this draft depends on it. |
| E005 | [Workshop policy definitions](https://github.com/0xferit/decentralized-curation/blob/73000c9e696ee08c91681e729d0d0927630c11de/public/domain.js). | Inspected `POLICY` only for the research-infrastructure illustration. The scope, prompts and attribution rule are workshop-specific. No project-specific empirical claim from the nominee descriptions is reused. |
| E006 | Clément Lesaege, Federico Ast and William George, *Kleros: Short Paper*, version 1.0.7, September 2019. [Primary PDF](https://kleros.io/static/whitepaper.pdf). | Title page and sections 2 and 4 opened. Supports attribution of the Schelling-point and coherence-incentive design family, not proof that this application is truthful or secure. |
| E007 | Nolan Miller, Paul Resnick and Richard Zeckhauser, *Eliciting Informative Feedback: The Peer-Prediction Method*, 2005. [Publisher record](https://pubsonline.informs.org/doi/10.1287/mnsc.1050.0379); [author-hosted copy](https://rzeckhauser.scholars.harvard.edu/sites/g/files/omnuum4441/files/rzeckhauser/files/feedback.pdf). | Publisher metadata and abstract, author record and page 1360 opened. Supports the narrow distinction between rewarding agreement and eliciting informative reports. Its equilibrium result is not attributed to this game. |
| E008 | Timothy Kassis, Vinayak Agarwal, Yuhuan He, Darshil Patel and Aubrey M. Brueckner, *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*, 2026. [arXiv record](https://arxiv.org/abs/2609.00065). | Current record opened; version 2 lists these authors. Included only for the preparation method. |
| E009 | [Worked example](worked-example.json). | Synthetic parameters and exact arithmetic generated for this manuscript. No observations, participant data, costs, market prices or study results are implied. |
| E010 | Author decisions supplied in the current conversation and this revision request. | The author stated that current decisions are more up to date than project documents and requested correction of inherited stale assumptions. The revision brief confirms the ongoing profile, optional later beneficiary funding, preserved immediate claimability, nomination-scoped challenges and separate relevance procedures. This is an instruction/provenance record, not empirical evidence. |
| E011 | Vitalik Buterin, *SchellingCoin: A Minimal-Trust Universal Data Feed*, Ethereum Foundation blog, 28 March 2014. [Blog post](https://blog.ethereum.org/2014/03/28/schellingcoin-a-minimal-trust-universal-data-feed). | Post opened. Supports attribution of the Schelling-point oracle pattern, its interquartile payout and its hedged premise that the truth is the most powerful Schelling point. It raises a small briber's attack only to judge it impractical, so it is not a source for that attack, and it is not evidence about this application's payoffs. |
| E012 | Ferit Tunçer, [author decision on exceptional-intervention authority](https://github.com/0xferit/manuscript-decentralized-curation/issues/183), issue #183, filed 25 October 2026. | Issue opened on 26 October 2026; its body had no edits. Supports only the design's position on exceptional-intervention authority and the scope of the disclosure rule. |

### Exact source fingerprints

The 256-bit Secure Hash Algorithm (SHA-256) digests below identify the inspected source bytes.

| Source | SHA-256 |
| --- | --- |
| Released parent PDF, E001 | `d127537d76fea58b7836c34b5ea9c193b2daf3cd4283658a731c4335b6c1c2d3` |
| Published parent manuscript source, E002 | `9cb527b355bad111e6cd5956be38fa4f6a42aff849e19e5c3bc48889b7e15e6f` |
| Presentation register, E003 | `ca74354d104da4f1eaff64d23f4efa6a3038f40a9c9a8658f2782c6d731908c8` |
| Working fixed-round design, E004 | `760c73555074770cd17b51ab2b4812ece9f2fbe31256fb6a84d1c962521a5b15` |
| Workshop policy source, E005 | `18fd821d8d74c7e10ad688f1c006c8176f7a2f1d67257dddd2533a50b03aef6d` |

The published source revision is [8dafde2cd6407cfb4631d70677a3fa22801a9c69](https://github.com/0xferit/manuscript-decentralized-curation/tree/8dafde2cd6407cfb4631d70677a3fa22801a9c69). The released PDF and metadata were read through public Zenodo endpoints. No unpublished manuscript text was transmitted to an external service.

## Decisions already settled

| Topic | Rule used by this paper | Evidence |
| --- | --- | --- |
| Scope | Public-goods curation is one application of the broader framework. | E001, E003, E010 |
| Curation and funding | Relative weights can be established before a beneficiary budget exists. Curation still needs service resources. | E003, E010 |
| Allocation | Effective weight is the lesser of the requested cap and adopted score. Positive eligible weights divide the distributable amount; zero eligible total supplies no allocation vector. | E002, E003 |
| Initial holdback | New nominations wait before first earning. Later adopted rating changes create no new holdback. | E003, E010 |
| Earned balances | Existing earnings remain attributed to their beneficiary and immediately claimable despite an edit, appeal, pending accuracy dispute or final debunking. Future eligibility is separate. | E003, E010 |
| Accuracy | Active nominations remain challengeable before and during relevance assessment. Successful challenges transfer the bond and return the counter-stake to the fact-checker, close that nomination and permit a fresh nomination under ordinary rules. | E002, E003, E010 |
| Other accuracy cashflows | The counter-stake is the greater of the pool minimum and one quarter of the pinned bond. A configured tax goes to the pool on activation; a failed counter-stake is split between nominator and pool. The external arbitration fee is sunk. | E002 |
| Relevance | Private reports, separate service fees and utility-token coherence incentives; honesty, care and competence are distinct. Competence selection is conditional, not proved by winning a round. | E002, E003, E010 |
| Appeals and reassessment | Fixed-target public score positions and a common appeal jury/pot; periodic reassessment is separate. Issuance, finality, refunds, prior funded contests and qualifying post-exit continuation retain their specified meanings. | E002, E003 |
| Attribution | The research-infrastructure example credits shared work once while permitting distinct contributions by the same beneficiary. | E005 |
| Intervention authority | The design gives no actor a power to pause, upgrade or override execution outside the published rules. A deployment that adds such an authority, or relies on an asset, registry or arbitrator that holds one, must make that authority and its duration visible. | E001, E012 |

## Documentation drift corrected in this draft

The previous draft treated the earlier fixed-round document as a coequal source and asked the author to ratify the already-selected ongoing profile. That framing is removed. The old document's finite holdback/disbursement lifecycle does not restrict the ongoing application's active-nomination challenge window or the immediate collection of earnings.

The previous draft also borrowed a universal materiality threshold and a mandatory bounded period per nomination. The current shared accuracy rules support proposition-specific challenges and do not impose that materiality condition. A pool may publish relevant temporal and evidentiary requirements, but the example template is not a protocol-wide mandatory schema. The current shared challenge grounds include factual falsification, lack of testability, topic-scope violations and semantic template violations; the old batch profile's removal of a scope-violation type is not inherited.

The incomplete-cashflows question is narrowed. Counter-stake basis, tax basis, successful transfers, the unsuccessful counter-stake split and sunk arbitration fees are already specified in the parent. What remains is concrete pool configuration and any genuinely absent external-arbitrator timeout behavior. The old batch document's allocation-based prices, full losing stake to the author and timeout default do not supply those choices.

No protocol claim in the revised manuscript uses E004 as normative support. Deleting the obsolete document does not change the historical inspection record or its verification status.

## Remaining implementation questions

These are narrower than the already-decided behavior above:

1. **New accrual during a pending accuracy dispute.** The record settles claimability of prior earnings and termination of future earning at debunking. It does not expressly define every pending-dispute earning transition. Do not infer either a freeze or uninterrupted new accrual from the right to collect past earnings.
2. **First-earning eligibility and pool parameters.** Implement the initial holdback's precise start, interruption and completion conditions and bind concrete durations, amounts, tax rates and split parameters. This is not permission to reapply holdback to later rating changes or lock an earned balance.
3. **Beneficiary admission and amendments.** Specify the ongoing profile's registry or recipient controls, claimant authorization, permitted edits and any multiple-active-nomination constraints. Preserve the selected example's duplicate-work rule without importing the batch profile's one-entry-per-round limit. A new revision requires its own adopted score; historical rulings and earnings remain attached to their original revision.
4. **Zero-weight storage and timeout outcomes.** The absence of an allocation vector at zero eligible total is decided. The complete storage, return or later-use rules for unallocated beneficiary funds need a funding adapter. External arbitration timeout behavior must be explicit rather than borrowed from the batch document.
5. **Remaining mechanism interfaces.** The parent and source register still identify proof validation, some numerical representations and fee/target rounding, receiving-address/update interfaces and exceptional cancellations as implementation work. Existing appeal admission, funding, quorum, issuance, finality and post-exit rules are not reopened by these gaps.

## Research and publication work

The evaluation agenda must test net returns, evidence acquisition, effort and competence separately, including asset valuations, opportunity costs and adversarial coordination. The absence of an informational edge alone does not establish a negative total expected payoff. Work on causal impact needs a policy and evidentiary standard distinct from the current-reliance illustration.

The author has authorized a separate preprint. Journal selection, future scope and any additional declarations remain author decisions. These are not unresolved protocol mechanics. The release binds the companion source and reviewed PDF to a specific commit. Remaining implementation interfaces remain explicitly open.

## Verification record

- Agent inspected the sources and verified public bibliographic metadata, with source roles kept distinct.
- Exact arithmetic and manuscript-to-registry consistency checks are recorded in [verification-results.json](verification-results.json).
- Human source verification and scientific approval remain pending. Automated checks do not certify truth, completeness, novelty, incentive compatibility or publication readiness.
- No human subjects, observations, experiments, deployments or performance measurements were created or claimed.
