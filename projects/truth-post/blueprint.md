> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Copyright (c) 2026 Ferit Tunçer.

Status: proposed end-state design for the Truth Post news application. The 2023 minimum viable product (MVP) was a partial deployment, described in the [implementation report](https://github.com/0xferit/manuscript-decentralized-curation/blob/main/projects/truth-post/implementation-report.md). This blueprint is not a claim that the complete protocol is implemented or fully specified: the open questions below and the shared appeal implementation choices remain unresolved. The [foundational paper](../../) defines the shared relevance mechanism; this document specifies the news profile.

Normative language: **MUST**, **SHOULD**, and **MAY** are used in their usual engineering sense.

## Purpose

Truth Post is a trust-minimized news-curation protocol that separates **accuracy** from **relevance** and makes both outputs contestable.

The protocol curates **claims**, not vague posts. Interfaces may render those claims as article pages, feeds, newsletters, or dashboards, but the canonical protocol unit is always one bonded, content-addressed claim blob.

The complete system exists to solve three failures that the original Truth Post MVP did not solve:

- the MVP could punish false claims, but could not surface what matters
- the MVP had a trust/confidence metric, but no standing curator layer
- the MVP depended too heavily on a single frontend and off-chain dependencies

This blueprint proposes mechanisms intended to address those gaps, including:

- author submission with bonded claims
- protocol-native confidence accounting
- external decentralized dispute resolution for accuracy
- pooled staking and drafted curators for relevance
- reputation with decay
- durable claim history with withdrawal-based exit
- multi-interface, multi-indexer, multi-gateway operation

## Legacy MVP Policy Surface Versus End-State Policy Stack

The deployed Truth Post MVP did have one real policy surface: a fixed `News` dispute policy document referenced through the Kleros metaevidence URI. That document told jurors, at a high level, what counted as news, how to think about inaccuracy, and what kinds of evidence were expected.

That legacy policy surface matters, but it was still minimal:

- one static pool-level document
- no structured claim schema enforced before posting
- no explicit non-falsifiability challenge path
- no per-claim or per-version policy pinning beyond the pool-level metaevidence reference
- no separation between submission template rules and dispute evidence rules

This blueprint replaces that single-document approach with a versioned policy stack:

- `ClaimTemplate` defines what must be present before a claim can be posted
- `EvidencePolicy` defines what evidence rules accuracy disputes must use
- `RelevancePolicy` defines how internal relevance curation rounds operate

The point is not to erase the legacy MVP policy. The point is to make its role explicit and then formalize it into components that are precise enough to implement and evaluate.

## Design Goals

Design ordering:

`NoNeedForGovernance > GoodGovernance > BadGovernance > NoGovernance`

Truth Post therefore prefers designs that make protocol-wide governance unnecessary. If governance cannot be eliminated, it should be minimized and tightly scoped. Completely absent governance is worse than good governance when a shared control surface still exists, but the first preference is to remove the need for that control surface.

- Produce a public, contestable accuracy signal for news claims.
- Produce a separate relevance signal for ranking and feed construction.
- Minimize trust in any single publisher, frontend, or operator.
- Prefer immutable contracts and local pool failure over governance-controlled intervention.
- Make non-falsifiability punishable instead of forcing jurors to guess.
- Let readers consume ranked outputs without needing to inspect all raw evidence.
- Keep the protocol legible enough that another team could implement it from this document.

## Non-Goals

- Proving philosophical truth.
- Replacing all journalism.
- Eliminating all trust from off-chain content hosting.
- Enforcing atomic on-chain decomposition of every article into separately bonded subclaims.
- Making every claim free, instant, or suitable for any domain.

## Default Truth Post News Pool

This blueprint defines one default pool profile for the initial complete Truth Post deployment. Other pools may change parameters, but this profile is the reference implementation target. Ether (ETH) funds monetary obligations; the dedicated utility token is separate under the asset rules in System Overview.

There is no protocol-level minimum author bond in the initial complete build. Authors may post claims with very small bonds. The consequence is not rejection, but weak economic weight: such claims accumulate confidence slowly and are less likely to matter in ranking or attract challenge attention.

Challenge tax is a pool-configurable parameter, not a single global constant. The suggested starting default for the reference news deployment is `0.5%` of the author bond.

| Parameter | Default |
|---|---|
| Domain | General news, subdivided into topic pools |
| Author withdrawal cooldown | 7 days |
| Claim lifetime | Infinite while bonded; historical after withdrawal |
| Challenger counter-stake | `max(0.0125 ETH, 25% of author bond)` |
| Challenge tax | Variable; suggested default `0.5%` of author bond |
| Relevance round target size | 15 seat-tickets drawn |
| Reveal quorum | At least 80% of originally drawn seat weight; no curator-count minimum |
| Relevance cadence | Variable; suggested default one round per week while claim is live |
| Relevance coherence threshold `K` | 1.25 |
| Seat size `L` | Pool-configurable; `L > 0`, measured in the dedicated utility token’s smallest on-chain unit |
| Dispersion floor `epsilon_sigma` | 0.02 |
| Pre-reveal leak slash multiplier | Variable; suggested default `3x` original offending-round locked tokens (`w_i`); capped by the paper's eligible current balance, excluding other active-round locks |
| Post-reveal leak-proof duration | Positive duration frozen with the round timetable at round creation; the paper owns the fixed exclusive deadline. The provisional default is specified in the paper's Relevance layer |
| Appeal admission and funding windows | Admission opens at valid ruling issuance; its positive duration and a positive common funding duration are frozen then. The funding deadline is admission closure plus the common funding duration, provisionally defaulting to 72 elapsed hours under the paper; admission also provisionally defaults to 72 elapsed hours; both deadlines are exclusive under Flow F-bis |
| Counter-stake author split (`counterStakeAuthorSplitBps`) | 8000 (80% to author, 20% to pool budget; pool-configurable) |
| Author reputation decay | Variable; suggested default `1%` per 30-day epoch |
| Author busted-publication slash | Variable; suggested default `50%` of current author reputation |
| Author successful-defense reward | Variable; suggested default `+1` reputation unit |
| Appeal score positions | One position per referenced ruling and allowed score from 0.00 to 1.00 in steps of 0.01, backed through permissionless public contributions; any two distinct fully funded scores oppose each other. Positive accepted contributions retain immutable funding-order intervals for the paper’s backer payout rule under Flow F-bis |
| Unopposed funded score | After admission closes and all funding outcomes resolve, one distinct fully funded score becomes final by procedural forfeiture; its contributions are refunded in full without a fee or profit |
| Adjudicated appeal payout | All funded opposing positions against one ruling share one pot and one pool-first jury-fee deduction; ideal payouts use normalized inverse absolute error from the chain’s final score, then the paper’s whole-wei position rounding and same-pool residual rule apply under Flow F-bis; a unique exact prediction receives the entire net pot |
| Appeal escalation | No fixed depth limit; each further appeal must be filed within its referenced ruling's window and requires fresh funding |
| Reference ETH service fee per seat | The paper’s [Relevance layer](../../#relevance-layer) owns the provisional reference rate; a pool may choose another positive rate fixed at creation |
| Jury-service fee reservation | Ordinary jury size multiplied by configured ETH base pay per seat; funded from the pool’s ETH budget |
| Utility-token coherence reward | Redistribute actual distance-based incoherence slashes under the paper’s per-curator round-down rule; the rounding remainder goes once to this pool’s separate utility-token balance |
| Protocol grace period | 7 days (604,800 seconds) |

### Parameter Status And Calibration Limits

These defaults are reference-deployment starting points, not empirically validated optima. The table above records reference choices for the ordinary news-pool flows. It is not a complete implementation specification for public appeal crowdfunding; Flow F-bis identifies the unresolved settlement terms. It should not be read as claiming that the listed values have already passed formal calibration or joint sensitivity analysis.

The parameter families also have different justification levels. Challenge-friction parameters such as the counter-stake, challenge tax, and failed-challenge payout split are partially grounded by the later deterrence arithmetic in this blueprint: under the stated assumptions, raising challenger cost improves frivolous-challenge deterrence but also makes legitimate correction harder, while lowering challenger cost does the reverse. That supports only directional claims under those assumptions. It does not identify a robust optimum across heterogeneous claim values, bond sizes, or DDR fee regimes.

Relevance-game parameters such as coherence threshold `K`, seat size `L`, dispersion floor `epsilon_sigma`, the leak multiplier, the post-reveal leak-proof duration, the ETH per-seat service rate and any eventual appeal parameters require calibration. Fee planning uses the paper’s provisional active-assessment workload for one juror representing one seat on one item; this is a planning assumption, not measured effort or quality, and adds no deadline, evidence, logging or payment condition. The provisional reference ETH rate follows the paper’s [Relevance layer](../../#relevance-layer), while pools may choose another positive rate fixed at creation. The same rate applies to initial and appeal service; changing the reference default does not retrofit existing pools or establish a fiat peg. Multiple represented seats still multiply pay without implying that assessment work grows per seat. Appeal settlement also requires the choices listed in Flow F-bis before calibration alone would suffice. Different parameters affect different incentives: weaker slashing may reduce disagreement costs, while a lower service fee may discourage participation. Higher fees can reward low-effort participation, and stronger penalties can deter informative disagreement. These effects require joint analysis; no monotonic discipline or quality guarantee follows from increasing every parameter. The main paper reports sensitivity sweeps for selected relevance parameters, but these do not establish truthful reporting as an equilibrium or calibrate the full parameter family. Its Curator voting strategy section gives an analytical example for the single-asset analytical subsidized reward rule, in which a unilateral report increases the single-round reward below the distance-slashing floor. For the same valid revealers and original drawn seats, that example’s dispersion change cannot increase an ETH service fee under the current fixed per-seat rule. The reported simulations do not evaluate the complete two-asset design; other profitable deviations, including effects on utility-token redistribution and appeal proceeds, remain to be assessed.

Reputation parameters such as decay, successful-defense reward, and bust slash are likewise placeholders for how much long-run publisher history should matter relative to single-claim outcomes. If set too low, reputation becomes mostly cosmetic; if set too high, a small number of outcomes can dominate future participation. Their interaction with posting frequency, pool migration, and heterogeneous author quality remains unvalidated.

Accordingly, the strongest justified claim at present is narrow: these are starting defaults for the specified ordinary-round rules of a reference Truth Post news pool and support the later illustrative calculations. Public appeal crowdfunding still requires the settlement terms in Flow F-bis before the complete mechanism can be implemented. Neither the defaults nor the calculations establish robustness or optimality. Before treating them as validated economics, the design still needs at least three kinds of sensitivity work: one-at-a-time sweeps for the challenge, relevance, and reputation parameter families; joint sweeps for coupled parameters such as counter-stake/tax/payout split, `K`/`L`/`epsilon_sigma`/ETH service rate/appeal parameters, and reputation decay/reward/slash size; and adversarial tests covering suppression, low-participation rounds, escalation dynamics, and stake concentration.

## System Overview

The internal relevance jury uses a dedicated utility token for availability staking, voting weight, incoherence and non-participation penalties, and coherence rewards. Ether (ETH) is separate: author bonds, accuracy challenges, beneficiary funding, appeal contributions and settlements, and jury-service fees use ETH. Coherent curators receive utility-token rewards only by redistribution of actual integer distance-based incoherence slashes, with each curator’s aggregate entitlement rounded down under the paper’s rule. The rounding remainder belongs to the same pool’s separate utility-token balance; unclaimed integer rewards remain assigned to their recipients. There is no minted reward, token subsidy or separately prefunded utility-token reward reserve. Non-participation penalties and the existing no-coherent-recipient fallback are held in a distinct utility-token pool balance; they cannot credit or finance the ETH budget, and no new redistribution rule for that balance is specified. In a round that issues a valid ruling, every timely valid revealer earns the fixed ETH service fee for each of its originally drawn seats under the paper’s [Relevance layer](../../#relevance-layer), regardless of its score, coherence or the round’s dispersion. Missing, invalid or late reveals earn no fee, and failed-quorum rounds earn no fee. Multiple represented seats earn the corresponding multiple of the per-seat rate. This entitlement measures valid participation, not verified research effort or report accuracy; earned fees become immediately withdrawable in the valid-ruling issuance transition under the paper’s rule. Anyone may trigger an already-claimable internal ETH payment under the claim-execution rule below. It follows the original recipient’s current receiving address for the paying contract, which defaults to the original recipient. The authenticated update interface, cryptographic format if used, replay-protection representation, transfer isolation, batching and record representation remain open. The ETH and utility-token balances MUST NOT be added, netted or converted implicitly. The successful reporter of a proven pre-reveal leak receives the actual utility tokens confiscated from the violator plus the violator’s entire normal earned ETH service fee for that round, if any, under the paper’s [Relevance layer](../../#relevance-layer). This is an explicit utility-token payment exception: there is no conversion, additional ETH bounty or separate ETH collateral. The proven-leak recipient override MUST be resolved before the fee becomes withdrawable; the gross jury fee and its funding source are unchanged.

Truth Post has two independent but connected outputs:

- **Adjudication output**: whether a claim is `Unchallenged`, `ChallengeFailed`, or `Debunked`
- **Relevance output**: how important the claim is for a specific pool right now, scored on `[0,1]`

These outputs come from different mechanisms:

- **Challenge adjudication** is resolved through challenge, evidence submission, and external decentralized dispute resolution.
- **Relevance** is resolved through an internal coherence game among drafted curators.

Truth Post does not declare claims universally true or false. It records challenge outcomes, evidence, confidence accumulation, and dispute history so readers can interpret the record for themselves.

Truth Post also maintains a reputation system:

- **Author reputation**: a pool-scoped, slow-decaying credibility stock that acts as a standing non-monetary bond for publishers

The system has four architectural layers:

1. **Smart contracts**
   - canonical accounting, pool registry, claim lifecycle, curator stake, relevance rounds, pool reward budgets, reputation state, dispute hooks
2. **External DDR**
   - binary challenge-succeeds adjudication with typed challenge reasons and appeals
3. **Content and indexing**
   - claim JSON, article body, evidence manifests, denormalized feed views, search, percentile calculations
4. **Interfaces**
   - browse pages, article pages, dispute pages, moderation/compliance filters, alternative clients

### Separation Of Roles

- Internal curators handle **relevance**.
- External DDR jurors handle **accuracy**.
- The same actor may play multiple roles across the system, but the mechanisms remain separate.

This separation is deliberate. Truth Post SHOULD NOT reuse internal curators as accuracy jurors in the initial complete build.

### Protocol Unit Versus Interface Unit

- The canonical protocol unit is a **Claim**.
- A claim is a bonded, content-addressed article/statement blob stored off-chain and referenced on-chain by CID.
- A claim blob MAY contain one or many subclaims.
- A challenge MUST name the explicit natural-language proposition being disputed inside that blob.
- If the challenge succeeds, the entire claim blob is `Debunked`.
- The canonical interface unit is an **Article Page** or feed item derived from that claim blob and its current revision.

Design note: whole-blob debunking is intentionally disproportionate. One successfully challenged proposition debunks the entire article, even if other subclaims within the blob are accurate. Partial debunking would require the protocol to track per-subclaim accuracy state, which conflicts with the explicit non-goal of atomic on-chain decomposition. The design trades proportionality for simplicity.

This tradeoff has predictable behavioral consequences:

- **Author risk scales with subclaim count.** A blob with N falsifiable subclaims exposes the author to N independent challenge surfaces, while a challenger needs to find only one error. Rational authors will respond by posting fewer subclaims per blob, making claims less precise (harder to falsify), or decomposing into separate bonded units. The first two responses reduce the protocol's usefulness for complex reporting; the third multiplies capital requirements (one bond per blob).
- **Challengers select the weakest subclaim.** An article that is broadly accurate but contains a minor factual error (wrong date, imprecise attribution) is just as debunkable as one that is fundamentally false. The protocol cannot distinguish the severity of the error.
- **Voluntary decomposition is capital-intensive.** Telling authors to split claims into separate bonded units shifts the complexity cost from the protocol to the author. An investigative article with ten falsifiable assertions would require ten bonds and ten separate confidence tracks, which is economically prohibitive for most authors and defeats the purpose of blob-level simplicity.

The protocol retains whole-blob debunking because the alternatives are worse in a different dimension. Per-subclaim state tracking would require on-chain decomposition (adding storage, gas, and indexing complexity), create new attack surfaces (e.g., strategically debunking minor subclaims to damage confidence while leaving the core claim intact), and force the protocol to define subclaim boundaries (a semantic judgment the protocol cannot make). The resulting complexity would undermine the minimal on-chain footprint that makes the protocol deployable.

The honest scope limitation is that this design is better suited to discrete, well-scoped claims than to long-form investigative articles with many independent assertions. Pools that want to curate complex journalism should set higher bonds (compensating authors for the increased exposure) and adopt templates that encourage focused, single-assertion submissions. The protocol does not attempt to serve all publication formats equally.

## Actors

### Authors

Authors create claim blobs, upload evidence items, post author bonds, and may withdraw or amend claims.

Authors may also carry pool-scoped author reputation. That reputation is not escrowed per claim, but every new claim exposes the author's standing credibility to a large downside if the claim is later busted.

### Challengers

Challengers dispute claims by posting counter-stake, an explicit challenged proposition, counter-evidence, and a challenge reason such as `NonFalsifiable`.

### Curators

Curators stake into pools. Their stake makes them eligible for relevance-round drafting. Curators are not accuracy jurors.

### Jurors

Jurors belong to the external DDR system. They resolve only accuracy disputes and appeals.

### Pool Creators

Any address may create a pool. Pool creators choose the pool's parameters and policy references at creation time.

Pool creators do not govern the protocol as a whole. They only define one pool configuration. If that pool is poorly designed, interfaces and users can ignore it.

### Interface Operators

Interface operators build consumer-facing products. They MAY filter or rearrange protocol outputs, but they MUST NOT alter canonical protocol records.

### Readers

Readers consume feeds, article pages, dispute histories, and pool dashboards. They MAY later become authors, challengers, or curators.

## Canonical Objects

Each object below is part of the authoritative end-state design.

### Pool

Purpose: define a domain, policy surface, and parameter set.

Required fields:

- `poolId`
- `slug`
- `name`
- `status` (`Active`, `Deprecated`)
- `topicDescription`
- `claimTemplateVersion`
- `evidencePolicyVersion`
- `relevancePolicyVersion`
- `withdrawalCooldownSeconds`
- `minChallengeStakeWei`
- `challengeTaxBps`
- `counterStakeAuthorSplitBps` (pool-configurable; suggested default 8000 = 80%)
- `seatSizeWei` (legacy field name for L; an amount in smallest utility-token units, not wei of ETH)
- `relevanceRoundTargetSize`
- `relevanceCadenceSeconds`
- `coherenceK`
- `epsilonSigma` (dispersion floor)
- `preRevealLeakSlashMultiplier`
- `appealWindowSeconds`
- common ruling-target rule, input snapshot and recorded-target storage, common funding-duration and deadline representation, revision-target serialization and rounding: fields remain to be specified under Flow F-bis
- `authorReputationDecayBpsPerEpoch`
- `authorReputationDecayEpochSeconds`
- `authorBustSlashBps`
- `authorChallengeFailedRepReward`
- `roundRewardFloorWei` (ETH service-fee reservation in wei, derived from ordinary jury size and configured ETH base pay per seat)
- `protocolGracePeriodSeconds`
- `ddrTimeoutSeconds`
- `ddrProviderId`
- `successorPoolId` (nullable)
- `createdBy`
- `createdAt`

Authority:

- created permissionlessly by any address
- pool parameters and policy references are immutable after creation; mutable per-pool state (e.g., reward budget balances) is updated by the protocol at round finalization. The creator MAY mark the pool `Deprecated` or publish a successor reference for interface discovery

Storage plane:

- on-chain for ids, parameters, versions, status
- content storage for policy documents referenced by version

### ClaimTemplate

Purpose: define the minimum schema for claim submission in a pool.

This object generalizes what the legacy MVP never formalized. In the MVP, jurors had one News policy document, but authors did not post against a structured on-chain or content-addressed claim template.

Required fields:

- `templateVersion`
- `requiredFields`
- `fieldValidationRules`
- `allowedSourceClasses`
- `challengeabilityRequirements`
- `amendmentPolicy`

Authority:

- authored by the pool creator or any policy author the pool creator chooses before pool creation
- immutable once referenced by a live claim

Storage plane:

- content storage as canonical JSON
- on-chain by version pointer and hash

### EvidencePolicy

Purpose: specify admissible evidence and tie-break logic for accuracy disputes.

This object is the formal successor to the MVP's single News juror-policy document. In the complete system, evidence rules MUST be versioned explicitly rather than inferred from one fixed metaevidence text.

Required fields:

- `policyVersion`
- `admissibleSourceClasses`
- `canonicalSources`
- `tieBreakRules`
- `insufficientEvidenceRule`
- `nonFalsifiabilityRule`
- `evidenceFreshnessRules`

Authority:

- chosen by the pool creator at pool creation time and versioned by content hash

Storage plane:

- content storage with on-chain hash and version pointer

### RelevancePolicy

Purpose: specify how internal relevance rounds should interpret the pool's ranking task.

This object separates qualitative relevance rules from the numeric pool parameters. Pool parameters set the economics and cadence; `RelevancePolicy` defines what curators are being asked to score.

Each pool creator crafts its own rubric; there is no protocol-wide default curation policy. Where an application allocates a budget directly in proportion to relevance, the paper’s funding-weight interpretation applies: the numbers express relative funding weights, beyond merely ordering nominations. Scores of 0.75 and 0.25 imply a 3:1 funding-weight ratio before binding caps or other application factors, without establishing three times the public benefit, causal impact or value of another grant. The pool’s rubric should explain the numeric meaning it intends. This conditional interpretation does not add budget allocation to Truth Post or change its news-feed formula, and it is separate from curator voting weights and inverse-distance appeal payouts.

Required fields:

- `policyVersion`
- `scoringQuestion`
- `scoreRange`
- `scoringRubric`
- `timelinessRule`
- `commitWindowSeconds`
- `revealWindowSeconds`
- `coherenceRule`
- `nonParticipationRule`
- `preRevealLeakRule`

Authority:

- chosen by the pool creator at pool creation time and versioned by content hash

Storage plane:

- content storage with on-chain hash and version pointer

### Claim

Purpose: represent one bonded, content-addressed claim/article blob.

Required fields:

- `claimId`
- `poolId`
- `author`
- `claimTemplateVersion`
- `evidencePolicyVersion`
- `articleBodyCid`
- `claimManifestCid`
- `initialEvidenceCids`
- `revisionHistoryCid`
- `currentRevision`
- `authorBondWei`
- `pendingBondAdjustmentWei` (nullable)
- `bondAdjustmentEffectiveAt` (nullable)
- `operationalState`
- `preChallengeOperationalState` (nullable)
- `adjudicationOutcome`
- `adjudicationSource`
- `lastResolvedAdjudicationOutcome` (nullable)
- `lastResolvedChallengeId` (nullable)
- `lastResolvedRevision` (nullable)
- `confidenceIntegral`
- `lastConfidenceAccrualBlock`
- `confidenceAccrualState`
- `activeChallengeId`
- `queuedChallengeCount`
- `relevanceScore` (nullable; an adopted score for `currentRevision`, absent until that revision has its own assessment outcome)
- `nextRelevanceRoundAt`
- `createdAtBlock`
- `updatedAtBlock`

Authority:

- created by author
- status changes by protocol actions

Storage plane:

- on-chain for ids, accounting, status, current CIDs, timestamps, version pointers
- content storage for manifest, article body, evidence items, revision history

The same claim blob CID MAY be posted to multiple pools as independent claims. Each pool instance has independent adjudication, confidence, relevance, and bond accounting. A `Debunked` outcome in one pool MUST NOT propagate to claims in other pools.

`Claim` SHOULD expose `lastResolvedAdjudicationOutcome`, `lastResolvedChallengeId`, and `lastResolvedRevision`. Amendment finalization MUST reset the current revision's `adjudicationOutcome` to `Unchallenged`, but MUST NOT erase the most recent resolved adjudication from claim history.

### EvidenceItem

Purpose: represent one evidence submission by any party.

Required fields:

- `itemId`
- `claimId`
- `challengeId` (nullable; null for author-submitted pre-challenge evidence)
- `submittedBy`
- `submittedAt`
- `label`
- `sourceClass`
- `uriOrCid`
- `contentHash`
- `publishedAt`
- `retrievedAt`
- `authorStatement` (nullable)

Authority:

- any address MAY submit evidence items
- items are append-only and immutable once submitted
- submission window closes when the DDR evidence phase closes

Storage plane:

- content storage
- on-chain by item hash and pointer

### Challenge

Purpose: open a formal accuracy dispute against a claim.

Required fields:

- `challengeId`
- `claimId`
- `challenger`
- `challengedProposition`
- `challengedRevision`
- `challengedManifestCid`
- `bondAtChallengeOpenWei`
- `reasonType` (`Debunking`, `NonFalsifiable`, `ScopeViolation`, `TemplateViolation`)
- `counterStakeWei`
- `challengeTaxWei`
- `arbitrationFeeWei`
- `queuePosition`
- `status` (`Queued`, `Active`, `Cancelled`, `Refunded`, `Finalized`)
- `queuedAt`
- `activatedAt`
- `cancellationWindowEndsAt`
- `linkedDisputeId`

A challenge MUST record the `currentRevision`, `claimManifestCid`, and `authorBondWei` of the claim at the time of filing. DDR evaluation MUST use the pinned revision, not the claim's current content. All challenge economics and winner payout MUST use `bondAtChallengeOpenWei`.

Authority:

- created by challenger
- finalized by dispute outcome

Storage plane:

- on-chain for amounts, status, ids
- counter-evidence is linked via `EvidenceItem.challengeId`

### Dispute

Purpose: track the external DDR process for the active challenge.

Required fields:

- `disputeId`
- `claimId`
- `challengeId`
- `ddrProviderId`
- `externalDisputeId`
- `phase`
- `currentRound`
- `appealDeadline`
- `finalRuling` (`ChallengeFailed`, `Debunked`)
- `finalizedAt`

Authority:

- created by protocol via DDR adapter
- updated by DDR callbacks or relayed proofs
- in a timeout resolution, `finalRuling` and `finalizedAt` may remain unset; the protocol-level timeout determines the claim's adjudication outcome independently (see Timeout And Fallback)

Storage plane:

- on-chain for ids, phases, rulings, deadlines

### CuratorStake

Purpose: record a curator’s domain commitment and eligibility.

Required fields:

- `stakeId`
- `poolId`
- `curator`
- `depositedWei` (legacy field name for the total utility-token deposit, measured in smallest utility-token units)
- `lockedWei` (legacy field name for utility tokens locked in active rounds; not withdrawable)
- voluntary ETH appeal contribution records: a separate asset ledger whose storage layout remains to be specified; each positive accepted contribution records its backer, accepted amount and immutable interval in that position’s funding-acceptance order under Flow F-bis; contributions by the same address remain separate records, and settlement must prevent reuse of a paid interval; accepted contributions remain independent of curator status and MUST NOT be subtracted from or represented as utility-token deposits; earlier jury participation alone MUST NOT commit additional funds
- `status` (`Pending`, `Active`, `Exited`)
- `joinedAt`
- `lastSlashedAt`

Authority:

- created by curator
- state transitions by protocol

Storage plane:

- on-chain

### RelevanceRound

Purpose: compute a pool-local relevance score for one pinned content revision via utility-token draw-and-lock staking, graduated slashing, and redistribution of distance-based incoherence slashes, with separately funded ETH jury service.

When an ordinary round starts, before curator reports are accepted, it MUST record the assessed revision and immutable manifest, body and bundled-evidence references, together with the applicable pool policy versions. An appeal round MUST inherit the target of its referenced ruling. All levels and retries in that appeal chain MUST keep the target, even if the claim's current pointers change. The representation of this target record remains to be specified; its identity MUST be unambiguous. Additional evidence MAY be admitted under the applicable evidence rules without retargeting the publication. Identifier pinning alone is not an availability guarantee.

Required fields:

- `roundId`
- `poolId`
- `claimId`
- `snapshotBlock`
- `targetRoundSize`
- `actualDraftSize` (positive seat count fixed when the draft succeeds)
- `draftedCurators`
- `commitClosesAt`
- `revealClosesAt`
- `finalizedAt` (technical round-completion and ruling-issuance time; ruling finality is separate)
- `revealedScores`
- `effectiveWeights` (original weights fixed at the successful draw, preserved for quorum and score calculation)
- `meanScore`
- `stdDev`
- `epsilonSigma`
- `distanceSlashingSkipped` (boolean; true when sigma < epsilonSigma; non-participation slashing may still apply)
- `coherentCurators`
- `preRevealLeakReports`
- `relevanceScore`
- `slashSummary`
- `rewardSummary`
- `reservedRoundRewardWei` (ETH service-fee reserve in wei)
- `status`

Authority:

- created by protocol scheduler
- finalized by protocol at or after the fixed proof deadline and after processing qualifying accepted proofs

Storage plane:

- on-chain for commitments, reveals, scores, rewards, slashes
- indexer for denormalized views

### AuthorReputationBalance

Purpose: track topic-scoped, non-transferable publisher credibility at risk.

Required fields:

- `poolId`
- `author`
- `rep`
- `lastDecayEpoch`
- `lastUpdatedAt`

Authority:

- updated by accuracy outcomes and periodic decay

Storage plane:

- on-chain

### ConfidenceScore

Purpose: denormalized view of stake-at-risk over time for one claim.

This is NOT a separate canonical object. The canonical confidence fields (`confidenceIntegral`, `lastConfidenceAccrualBlock`, `confidenceAccrualState`) live on the `Claim` object. `ConfidenceScore` is an indexer/interface convenience view that adds the computed display percentile.

Derived fields:

- `claimId`
- `confidenceIntegral` (read from `Claim`)
- `lastAccrualBlock` (read from `Claim.lastConfidenceAccrualBlock`)
- `accrualState` (read from `Claim.confidenceAccrualState`)
- `displayPercentile` (indexer-computed)

Authority:

- raw value is canonical on the `Claim` object
- display percentile is indexer/interface derived

Storage plane:

- raw state on-chain (via `Claim`)
- percentile off-chain

### PoolRewardBudget

Purpose: track ETH jury-service funding for one pool. Its `balanceWei` and reservations contain ETH only. Utility-token penalties and redistribution MUST be accounted separately. Legacy utility fields whose names end in `Wei` retain utility-token denomination; aligning those public field names, the separate token-balance representation, and the former `rho`, `sigmaRefAlpha`, `emaSigma`, `sigmaRef` and `rewardFactor` fields with this design remains implementation work. Those former reward-scaling fields do not define a current reward rule.

Required fields:

- `poolId`
- `balanceWei`
- `lastCreditedAt`
- `lastDebitedAt`
- `pausedForInsufficientFunds`

Authority:

- any address MAY top up the pool
- protocol credits challenge-tax and failed-challenge inflows
- protocol debits round reward floors

Storage plane:

- on-chain

### InterfaceFeed

Purpose: define a renderable, ranked, reader-facing feed.

Required fields:

- `feedId`
- `poolId`
- `filterPolicyVersion`
- `rankingPolicyVersion`
- `includedClaimIds`
- `feedScores`
- `generatedAt`

Authority:

- built by indexers and interface operators

Storage plane:

- off-chain only

## Component Boundaries

### Smart Contracts MUST own

- pool parameters and version pointers
- claim ids, state, bond accounting, confidence integral
- challenge ids, queue state, and counter-stake accounting
- curator deposits and round locks; voluntary appeal contribution records
- relevance round commitments, reveals, slashes, rewards
- reputation balances and decay
- pool reward budgets
- DDR dispute ids and final rulings

### External DDR MUST own

- juror selection
- evidence and voting phases for accuracy disputes
- appeal mechanics
- final dispute ruling callback or equivalent proof

### Content Storage MUST own

- claim manifest JSON
- article body content
- evidence items
- pool policy documents

### Indexers MUST provide

- searchable denormalized views
- current confidence display percentiles
- feed materialization
- status dashboards
- fallback read models for interfaces

### Interfaces MUST provide

- claim submission UX with linting
- article pages
- dispute pages
- curator dashboard
- pool dashboard
- degraded-mode read-only behavior when some dependencies fail

## Claim State Model

The complete build uses two separate state dimensions for claims to avoid overloaded status logic.

### Operational State

- `Draft`: local/off-chain only, not posted
- `Live`: active, challengeable, confidence accrues
- `PendingEdit`: author is preparing a new revision, confidence paused, claim out of the main feed, challengeable on last finalized revision
- `WithdrawPending`: author initiated withdrawal cooldown, confidence paused, challenge still allowed
- `Challenged`: external dispute active, confidence paused
- `Closed`: final DDR outcome executed, historical only
- `Withdrawn`: author exited after cooldown

### Adjudication Outcome

- `Unchallenged`
- `ChallengeFailed`
- `Debunked`

`NonFalsifiable`, `ScopeViolation`, and `TemplateViolation` remain challenge reasons, not final adjudication labels. A successful challenge of any type yields the final outcome `Debunked`.

### Adjudication Source

- `None`
- `DDR`
- `Timeout`

### Allowed Claim Transitions

- `Draft -> Live`
  - trigger: successful submission and bond deposit
  - side effect: `adjudicationOutcome = Unchallenged`, `adjudicationSource = None`
- `Live -> Challenged`
  - trigger: first active challenge filed while claim is active
- `Live -> PendingEdit`
  - trigger: author initiates amendment with no active or queued accuracy challenge; a relevance appeal alone MUST NOT prohibit an otherwise permitted amendment
  - side effect: confidence pauses and claim leaves the main feed
- `PendingEdit -> Live`
  - trigger: author finalizes new revision
  - side effect: current CID pointers update, revision history updates, confidence resets to zero, `adjudicationOutcome = Unchallenged`, and the new revision has `relevanceScore = null` until its own assessment. A fresh relevance assessment is queued subject to pool funding, the ordinary-round hold and the full-cadence resumption rule
  - design note: earlier relevance scores and appeal outcomes MUST remain attached to their assessed revisions. They MUST NOT be relabeled as judgments of the new revision. The new revision MUST NOT inherit a historical score, including as a labeled provisional proxy. Until it has its own adopted relevance score, it MUST remain outside score-dependent ranking and new score-dependent funding under Flow F-bis, while direct links and pending views remain available
- `PendingEdit -> Challenged`
  - trigger: challenge filed targeting the last finalized revision
  - side effect: edit finalization is blocked, confidence remains paused, `preChallengeOperationalState = PendingEdit`
- `Live -> WithdrawPending`
  - trigger: author initiates withdrawal with no active or queued challenge
- `WithdrawPending -> Withdrawn`
  - trigger: cooldown ends with no challenge
  - relevance appeals: completed withdrawal applies the paper’s common terminal-exit rule under Flow F-bis; the request and cooldown alone do not trigger it, and no wait for appeal-chain finality is added
- `WithdrawPending -> Challenged`
  - trigger: challenge filed during cooldown
  - side effect: pending withdrawal MUST be cancelled; `preChallengeOperationalState = WithdrawPending`; if challenge later resolves as `ChallengeFailed`, claim returns to `Live` (not `WithdrawPending`) and the author MUST initiate a new withdrawal cooldown to exit
- `Challenged -> Live`
  - trigger: DDR final ruling or timeout resolution is `ChallengeFailed`, no queued challenge remains, and `preChallengeOperationalState` was `Live` or `WithdrawPending`
  - side effect: `adjudicationOutcome = ChallengeFailed`, `adjudicationSource = DDR` or `Timeout`, `confidenceIntegral` preserved, `lastConfidenceAccrualBlock = currentBlock`, accrual resumes
- `Challenged -> PendingEdit`
  - trigger: DDR final ruling or timeout resolution is `ChallengeFailed`, no queued challenge remains, and `preChallengeOperationalState` was `PendingEdit`
  - side effect: `adjudicationOutcome = ChallengeFailed`, `adjudicationSource = DDR` or `Timeout`, author may resume editing
- `Challenged -> Challenged`
  - trigger: DDR final ruling or timeout resolution is `ChallengeFailed` and a queued challenge auto-activates after the cancellation window
  - side effect: active challenge id advances to the next queued challenge; `preChallengeOperationalState` is preserved
- `Challenged -> Closed`
  - trigger: DDR final ruling is `Debunked`, OR timeout resolution yields `Debunked` (forfeiture)
  - side effect: `adjudicationOutcome = Debunked`, `adjudicationSource = DDR` (merits) or `Timeout` (forfeiture), confidence terminates, queued challenges are refunded, and claim is removed from active feeds

A claim with `operationalState = Closed` and `adjudicationOutcome = Debunked` is terminal for feed purposes and remains queryable historically. Interfaces SHOULD distinguish `adjudicationSource = Timeout` (debunked by forfeiture) from `adjudicationSource = DDR` (debunked on merits). This terminal item state MUST NOT cancel an ongoing relevance-appeal chain that had a contested level fully funded before closure; the paper’s continuation rule applies under Flow F-bis. Completing that chain MUST NOT reopen the claim or reverse the accuracy outcome. A successfully drawn ordinary attempt may finish and open its own first appeal window under the separate continuation rule in Flow F-bis, without reopening the claim. If the initial appeal process is still open and no contested level was fully funded before closure, Flow F-bis instead closes initial appeal funding and creates full refund entitlements under the paper’s pre-contest closure rule.

There is no special post-publication grace state in the complete design. A new claim is simply `Live` with very low accumulated confidence until time and bond size differentiate it from older claims.

## Dispute State Model

- `Open`
- `Evidence`
- `Commit`
- `Reveal`
- `Appeal`
- `Executable`
- `Finalized`

Transitions are driven by the DDR adapter. Truth Post MUST mirror the authoritative external dispute phase on-chain or via verified callback.

## Relevance Round State Model

`Finalized` in this technical round state model means the jury computation is complete and its ruling is issued. It does not mean that the ruling has survived its appeal window. Ruling finality and appeal backer payout release follow Flow F-bis. The paper’s fixed post-reveal leak-proof period MUST finish before a drafted round issues a ruling or completes a quorum-failure cancellation. The existing `Scoring` phase MAY include this wait and proof processing; the representation of its frozen timetable remains implementation work, with no new state or public field specified here.

- `Scheduled`
- `CommitOpen`
- `RevealOpen`
- `Scoring`
- `Finalized`
- `Cancelled`

`Cancelled` is allowed whenever a round cannot safely produce a relevance score. In that case:

- If no eligible backed seat can be drawn, the round is cancelled before drafting, nobody is slashed, and the same pinned revision keeps its previous relevance score if one exists; no older revision's score can make a newer revision eligible. There is no minimum distinct-curator count.
- If the round is drafted but valid reveals cover less than 80% of its originally drawn weight, it MUST retain the full fixed leak-proof period and its own remaining round collateral before completing cancellation. After the proof deadline and applicable penalty processing, drafted curators who failed to commit or reveal MUST be slashed as non-participants, but no curator service fee or coherence reward MUST be paid and no new relevance score MUST be produced. Non-participation slashes from such a cancelled round MUST be credited to the separate utility-token pool balance, never the ETH reward budget. Leak detection and token slashing still apply. A successful timely reporter receives the actual confiscated utility tokens under the paper’s leak rule, but no ETH service fee exists to divert when the round fails quorum. For an otherwise eligible active item, a replacement round is scheduled at the next cadence. After final accuracy closure or completed author withdrawal, no fresh ordinary retry may be drawn under the paper’s rule in Flow F-bis, even if an ordinary retry allowance remains.
- Low-dispersion rounds are not cancelled as degenerate, and the weighted mean remains a valid relevance score. The dispersion floor keeps the coherence band at least `K * epsilon_sigma` wide; it does not exempt valid revealers from distance-based slashing at chain finality. A round whose reports all fall inside the band produces no distance-based slashes and therefore no additional utility-token reward; surviving stake is returned separately. ETH jury-service fees follow the paper’s fixed per-seat entitlement for every timely valid revealer when a valid ruling is issued, without dispersion scaling. No subsidized `rho` or `f_reward` rule applies to utility rewards. The smooth subsidized analytical rule survives only as an analytical example in the paper and in previously generated simulations; its dispersion-based ETH reward increase is absent for the same valid revealers and original drawn seats under the fixed service fee, and those results do not validate the remaining two-asset incentives. Voluntary ETH appeal contributions retain their separate locks under Flow F-bis; jury service alone does not commit them. More broadly, the coherence mechanism assumes that a pool’s relevance policy is specific enough to anchor curator signals near a defensible ground truth. If all curators share the same bias, they can converge on a wrong answer while avoiding incoherence penalties, unless an appeal moves the chain's terminal adjudicated score outside their band. The hypothesized defense is competitive pool selection: if biased curation produces bad feeds, users migrate to better pools, and the biased pool loses relevance. The protocol does not prevent bad curation within a pool; the design intention is that bad curation remains pool-local rather than protocol-global. The additional proposed defense is public crowdfunding of an appeal with a doubled planned jury target through independent score positions. Flow F-bis summarizes the common pot, single jury-fee deduction and scalar payouts based on inverse absolute error from the chain’s final score.

This hypothesis has not been empirically validated. Several well-documented dynamics in platform economics could prevent pool competition from functioning as described:

- **Information asymmetry**: users cannot easily evaluate curation quality without independently verifying claims, which defeats the purpose of the protocol. Biased curation produces outputs that look normal to users who share the bias, making quality differences difficult to observe.
- **Network effects**: the first pool with sufficient curators and content may dominate regardless of quality, because authors go where curators are and curators go where claims are. This winner-take-most dynamic is common in two-sided platforms and does not require the winning pool to be the highest-quality one.
- **Switching costs**: curators who have tokens locked in active rounds cannot withdraw immediately; authors who have accumulated confidence on claims in one pool lose that history if they repost in another. These frictions slow migration even when quality differences are recognized.
- **Coordination failure**: migration requires multiple actors (curators, authors, sponsors) to move roughly simultaneously for a new pool to be viable. Individual exit does not automatically solve this collective action problem (see the analogous analysis of pool migration friction in the RPGF design document).

Competitive pool selection should therefore be read as a conditional hypothesis, not as an intrinsic correction mechanism. It can discipline within-pool bias only if users can observe persistent quality differences, at least one funded alternative pool for the same domain exists, and authors, curators, and sponsors can coordinate migration before incumbency and network effects entrench the biased pool. If those conditions do not hold, the coherence game remains a consensus mechanism without an internal path from consensus to correctness.

Empirical signals that would indicate whether pool competition is functioning: measurable user migration from pools with demonstrably biased feeds, successful bootstrapping of competing pools in the same topic domain, and declining curator participation in pools whose feeds diverge from verifiable ground truth. Until these signals are observed, the protocol should be understood as relying on an untested market mechanism for its primary defense against within-pool bias.

## Curator Stake State Model

- `Pending`
- `Active`
- `Exited`

Transitions:

- `Pending -> Active` after stake finalization
- `Active -> Exited` when the curator requests exit and no tokens are locked in unresolved rounds; voluntary appeal contributions retain their separate locks after curator exit
- `Active -> Active` after slash/reward events, deposit top-ups, or partial withdrawals of unlocked balance

There is no separate `Slashed` state. Slashing is an accounting event against an active stake. The ordinary-round rules impose no curator exit cooldown: curators may withdraw utility tokens not committed to active-round locks. ETH appeal contributions are accounted separately and cannot encumber utility tokens. Voluntary appeal contributions retain the separate lock defined in Flow F-bis, independently of curator status.

## Protocol Flows

### Flow A: Permissionless Pool Creation

1. A pool creator authors a pool package:
   - pool parameters
   - claim template
   - evidence policy
   - relevance policy
2. The pool creator submits the package hash and parameters on-chain.
3. The pool creator SHOULD seed the pool reward budget so the first relevance rounds can run.
4. The pool becomes `Active` immediately.
5. Once active, referenced policy versions and pool parameters are immutable for all future claims.
6. Any policy or parameter change requires a new pool deployment; existing claims remain pinned to the old pool and old versions.
7. Interfaces decide independently which pools to feature, suppress, warn on, or ignore.

Design note:

- this flow deliberately replaces the MVP's single static News metaevidence policy with separately versioned template, evidence, and relevance policy objects
- claims posted under one pool version remain bound to that version forever
- the design intention is that bad pool design fails locally through non-use rather than through a protocol-level governance gate; this relies on the competitive pool selection hypothesis described in the Relevance Round State Model, which has not been empirically validated and may fail under network effects or coordination failures

### Flow B: Author Submission And Template Validation

1. The author drafts a claim manifest locally.
2. The interface lints the manifest against the pool template and shows semantic warnings without requiring editorial approval to publish.
3. The author uploads:
   - claim manifest JSON
   - article body
   - initial evidence items
4. The author deposits the author bond.
5. The protocol stores current CIDs, version pointers, timestamps, revision metadata, and bond accounting on-chain.
6. The claim enters `Live`.
7. Confidence accrual starts immediately.
8. The scheduler queues the claim for its initial relevance round if the pool reward budget can fund it.

One claim blob MAY contain multiple subclaims. Truth Post does not require the author to decompose them into separate bonded on-chain units. Instead, any challenger must name the explicit natural-language proposition they are challenging inside the blob.

Posting a claim does not require pre-existing author reputation. But once the claim is live, the author's pool-scoped reputation is exposed to downside if the claim is later `Debunked`. That historical accounting does not debunk or ban the author. Under the paper's Accuracy layer, the outcome closes the bonded claim and forfeits its bond; the same author may publish a fresh bonded claim under the ordinary submission rules. A previous debunking alone MUST NOT bar that submission, reopen the old claim or transfer its score or entitlements to the new claim.

Contracts and the canonical frontend MUST enforce minimal structural field presence: non-empty `articleBodyCid`, `claimManifestCid`, and `initialEvidenceCids`; valid `claimTemplateVersion` and `evidencePolicyVersion` matching the pool's current versions. Structural validity does not certify truth, source quality or falsifiability. Semantic linting MAY warn about field content, source-class conformance or falsifiability, but MUST NOT become a required editorial approval or evidence-availability gate. Such violations remain challengeable after publication through the applicable `Debunking`, `NonFalsifiable`, `ScopeViolation` or `TemplateViolation` reason. An item-level loss MUST NOT become a publisher-level ban.

### Bond Adjustment

Author bonds are adjustable after posting, subject to the pool's configured grace period.

- `authorBondWei` MAY be increased or decreased by the author.
- Bond adjustments are allowed only when `operationalState = Live`.
- Bond adjustments MUST NOT be initiated during `PendingEdit`, `Challenged`, `WithdrawPending`, `Closed`, or `Withdrawn`.
- When the author initiates a bond change:
  1. The protocol records `pendingBondAdjustmentWei` and `bondAdjustmentEffectiveAt = now + pool.protocolGracePeriodSeconds`.
  2. Until the effective time, the current `authorBondWei` continues to apply for confidence accrual, challenge pricing, and payout calculations.
  3. After the effective time AND when no active or queued challenge exists, the new bond takes effect: `authorBondWei = pendingBondAdjustmentWei`, confidence is snapshotted, and accrual continues at the new rate.
  4. For bond decreases, the released collateral cannot be withdrawn until the bond change takes full effect.
  5. If the claim leaves `Live` state (e.g., enters `PendingEdit`, `WithdrawPending`, or `Challenged`) before the grace period ends, the pending bond adjustment is cancelled and the author must re-initiate it after returning to `Live`.
- The suggested default for `pool.protocolGracePeriodSeconds` is 7 days (604,800 seconds).

### Flow C: Confidence Score Accumulation

Canonical protocol term: **Confidence Score**. Interfaces MAY label it `Trust Score` for continuity.

Raw confidence is the on-chain integral:

```text
C_raw = C_snapshot + bondWei * (currentBlock - lastAccrualBlock)
```

Rules:

- confidence accrues only while `operationalState = Live`
- confidence pauses in `PendingEdit`, `WithdrawPending`, and `Challenged`
- confidence terminates permanently on `Debunked` or `Withdrawn`
- after a successful defense: `confidenceIntegral` is preserved in all cases; for `Challenged -> Live`, `lastConfidenceAccrualBlock = currentBlock` and accrual resumes at the current `authorBondWei` rate; for `Challenged -> PendingEdit`, the integral is preserved but accrual remains paused (since `PendingEdit` is a paused state)
- only amendments reset confidence to zero
- confidence does not use protocol-level exponential decay in the initial complete build

Design note:

- linear bonded stake-time is intentional
- confidence measures accumulated capital-at-risk exposure, not accuracy or credibility; the absence of challenge is not evidence of accuracy and may reflect insufficient scrutiny
- `feedScore` uses confidence as a weight because higher-bond, longer-lived claims have been more exposed to potential challenge, not because they are more likely to be true
- a large bond is not by itself sufficient for main-feed dominance at a single moment because main-feed ranking still multiplies confidence by curator-produced relevance
- however, linear non-decaying confidence does create incumbency pressure: older high-bond claims can accumulate durable percentile advantages over newer claims
- this blueprint does not yet justify stronger claims about steady-state newcomer catch-up, percentile compression, or long-run feed churn under realistic claim arrival and withdrawal rates

Display logic:

- indexers compute `confidencePercentile` within each active pool
- interfaces display both `C_raw` and percentile
- the default Truth Post frontend uses percentile in ranking and raw score in detail pages

There is no protocol-level hard cutoff such as "$5 = noise." Low-bond claims simply sit lower in the pool's confidence distribution and therefore contribute weakly to feed ranking unless they also earn high relevance. Any fixed visibility cutoff is an interface choice, not a protocol constant.

### Flow D: Challenge, Dispute, Appeals, Finality

1. A challenger chooses a claim in `Live`, `PendingEdit`, or `WithdrawPending` state.
2. The challenger submits:
   - `reasonType`
   - explicit natural-language `challengedProposition`
   - counter-evidence items
   - counter-stake `S = max(pool.minChallengeStakeWei, bondAtChallengeOpenWei / 4)`
   - challenge tax `T = pool.challengeTaxBps * bondAtChallengeOpenWei / 10,000`
   - DDR arbitration fee
   - design note: challenge cost scales with author bond; large bonds create higher barriers to challenge, which could deter economically rational challengers from attacking wealthy authors' claims; the design accepts this tradeoff because higher bonds also mean more capital at risk if the challenge succeeds, maintaining the economic incentive structure, but the deterrence effect is real
3. The challenge MUST record the claim's `currentRevision`, `claimManifestCid`, and `authorBondWei` at the time of filing as `challengedRevision`, `challengedManifestCid`, and `bondAtChallengeOpenWei`. Counter-stake and tax calculations MUST use `bondAtChallengeOpenWei`.
4. If no challenge is active, the protocol:
   - records `preChallengeOperationalState`
   - pauses confidence (if not already paused)
   - moves claim to `Challenged`
   - marks this challenge `Active`
   - credits `challengeTaxWei` to the pool reward budget
   - opens a dispute through the DDR adapter
   - design note: the claim leaves the main feed at this point, before merits resolution; this is an intentional conservative design choice but creates a griefing surface (see Failure Handling > Challenge-Based Suppression)
5. If another challenge is already active, the new challenge enters the FIFO queue. For queued challenges, `counterStakeWei`, `challengeTaxWei`, and `arbitrationFeeWei` MUST remain in challenge-specific escrow until activation. A queued challenge MUST NOT credit `challengeTaxWei` to `PoolRewardBudget.balanceWei` before it becomes `Active`. If a queued challenge is cancelled before activation or is mooted by an earlier `Debunked` ruling, the protocol MUST refund all three amounts in full.
6. The filed `challengedProposition` MUST be a fair reading of the claim blob. That is part of what DDR evaluates.
7. The DDR adapter asks one binary question: should this filed challenge succeed under the stated `reasonType`, `challengedProposition`, pool policy, and submitted evidence?
8. The DDR process runs through evidence, voting, and possible appeals.
9. Each queued challenge has exactly one cancellation window. That window MUST begin only when the challenge becomes first in FIFO order after the preceding active challenge resolves as `ChallengeFailed`. At that moment the protocol MUST set `cancellationWindowEndsAt = now + 24 hours` while keeping the claim in `Challenged`. The queued challenger MAY cancel during this window and recover their escrowed stake, tax, and DDR fee. If the queued challenger does not cancel before `cancellationWindowEndsAt`, the protocol MUST activate the challenge, open the DDR dispute, and credit its `challengeTaxWei` to the pool reward budget.
10. Final ruling outcomes are interpreted as:
   - `ChallengeFailed`: if no queued challenge remains, the claim returns to its `preChallengeOperationalState` (`Live`, `PendingEdit`, or `Live` if it was `WithdrawPending`) and the author gains `pool.authorChallengeFailedRepReward`
   - `ChallengeFailed`: if a queued challenge remains, the next queued challenge enters its cancellation window as described in step 9
   - `Debunked`: claim moves to `Closed`, author bond is slashed (using `bondAtChallengeOpenWei`), current author reputation in that pool is reduced by `pool.authorBustSlashBps`, and all queued challenges are refunded in full; any already-funded contested relevance-appeal chain continues under Flow F-bis without reversing these accuracy effects
11. `Debunked` covers any successful `Debunking`, `NonFalsifiable`, `ScopeViolation`, or `TemplateViolation` challenge, as well as timeout forfeiture (see Timeout And Fallback). Timeout forfeiture produces the same economic outcome but uses `adjudicationSource = Timeout` instead of `DDR`.
12. Appeal funding is handled by DDR crowdfunding. The author, challenger, or any third party MAY fund either side in exchange for the underlying DDR-side reward logic. If the author's side is not funded, the author loses the appeal opportunity.

Default payout rule (suggested; requires empirical calibration; all amounts reference `bondAtChallengeOpenWei` for the relevant challenge):

- if challenger wins:
  - challenger receives `bondAtChallengeOpenWei`
  - challenger receives their own counter-stake back
  - challenge tax remains in the pool reward budget
  - losing-side appeal reward logic is inherited from DDR
- if challenger loses:
  - author keeps author bond locked unless later withdrawn
  - challenger counter-stake is split between author reward and pool reward budget at `pool.counterStakeAuthorSplitBps` (suggested default: 8000 = 80% author, remainder to pool budget)
  - DDR fee is not refunded by Truth Post

The counter-stake split ratio is a pool-configurable parameter. The suggested 80/20 default is a starting point. No sensitivity analysis has been conducted on this ratio; see Parameter Status And Calibration Limits above for the current epistemic status of this default.

### Flow E: Draw-And-Lock Staking And Curator Eligibility

1. A curator deposits the dedicated utility token into a pool contract. Let `s_i` denote curator `i`’s deposited utility-token balance, with both `s_i` and seat size `L` (`pool.seatSizeWei`, a legacy field name) measured in that token’s smallest on-chain unit, not wei of ETH.
2. The curator’s stake becomes `Active` after confirmation.
3. Only curators with `s_i >= L` are eligible for drafting. The draft weight is the integer number of full seat-tickets the curator holds: `d_i = floor(s_i / L)`.
4. When drafted, each drawn ticket locks `L` tokens from the curator’s deposited balance. Let `n_i` denote the number of seats drawn for curator `i`. The curator’s round weight is `w_i = n_i * L`. Locked tokens are simultaneously the curator’s influence on the weighted mean and their maximum loss from coherence slashing in that round.
5. The unlocked utility-token remainder (`s_i - n_i * L`) stays in the pool contract and is not subject to coherence slashing in that round. It remains withdrawable subject to other utility-token round locks and separately specified penalties such as pre-reveal leak penalties. ETH appeal contributions under Flow F-bis are separate and do not reduce this balance.
6. Each curator submits one score weighted by `w_i`. Multiple seats increase the curator’s weight on that single score, not the number of independent votes.
7. Under the ordinary-round rules, a curator MAY withdraw utility tokens not committed to active rounds without an exit cooldown. Voluntary ETH appeal contributions retain the separate lock defined in Flow F-bis, independently of curator status.
8. A curator MAY exit the curator role once active-round locks have cleared. Exit MUST NOT release voluntary appeal contributions; those remain locked under Flow F-bis.

Important clarification:

- draw-and-lock staking belongs only to the internal relevance layer
- authors still bond claims individually
- challengers still challenge claims individually
- external DDR jurors still resolve accuracy disputes independently of curator pools

### Flow F: Relevance Curation And Coherence Game

1. Every newly live claim gets an initial relevance round immediately after posting if the pool reward budget can fund it.
2. Every `Live` claim gets a new relevance round at the pool's configured cadence while the claim remains bonded and not withdrawn. Per `(poolId, claimId)`, at most one ordinary relevance round MAY be unfinished, across all revisions. The protocol MUST atomically check ordinary-round exclusivity, create the round in `Scheduled` and reserve its ordinary jury budget. If another ordinary round is already scheduled or running, the attempt MUST defer without creating a second round or reserving another budget. The guard MUST cover preparation, drafting, commitment, revelation, the fixed post-reveal proof period and scoring until valid ruling issuance or completed cancellation. A later due time, amendment or concurrent scheduler MUST NOT bypass it. On cancellation, ordinary-round exclusivity MUST be released under the existing cancellation rules; a permitted replacement or retry MUST acquire it anew and satisfy the existing timing, funding and eligibility conditions. Other claims and pools MUST remain independent. A new ordinary round for a claim MUST NOT be scheduled or started while any applicable appeal filing window is open, even if no appeal has been filed, or while any of its appeals is fundraising, awaiting jury funding or being adjudicated. This hold MUST NOT block the appeal jury itself or rounds for other claims. The scheduler MUST defer held claims while preserving the specified ordering among eligible claims. Ordinary scheduling MUST follow the post-hold rule in [Public appeal funding](../../#sec-appeal-funding): after the last applicable filing window or active appeal ends, the next ordinary round MUST wait one full pool cadence. The protocol hold-end timestamp, not its later recognition or any refund or payout claim, MUST anchor that interval. The prior calendar phase and missed occurrences MUST NOT create catch-up rounds. A previously due but unstarted round MUST NOT bypass the new eligibility time. Any subsequent applicable hold MUST block the start and require a fresh full cadence from the end of the last hold. Closing one group while another hold remains MUST NOT start the interval. Funding, ordinary eligibility and scheduling conditions MUST still apply at or after that time; execution then is not guaranteed. An already-started ordinary round MAY finish under its existing rules; this MUST NOT authorize a second concurrent ordinary round for the same claim and pool. This rule MUST NOT delay appeal juries or change failed-appeal retry timing. The suggested default for the reference news deployment is one round per week. `Claim` MUST include `nextRelevanceRoundAt`. When multiple claims in the same pool are simultaneously due for scheduling, the protocol MUST process them in ascending `(nextRelevanceRoundAt, claimId)` order.
3. For ordinary scheduled rounds, `pool.roundRewardFloorWei` is the maximum ETH service-fee reservation in wei, derived from the positive configured ordinary target jury size multiplied by the positive ETH per-seat base pay; it is not a separately chosen total budget. If the actual draw is smaller under the existing rules, `R` uses the actual drawn count. Unused seat capacity is returned under the ordinary finalization or cancellation rule. If the pool reward budget cannot cover that derived round reward floor, no new round is scheduled and the current revision keeps its own previous relevance score if one exists; no older revision's score can make a newer revision eligible. When a round enters `Scheduled`, the protocol MUST reserve `pool.roundRewardFloorWei` from the pool reward budget immediately, atomically with the single-round admission in step 2 and the paper’s shared-budget reservation rule. The check MUST use only unencumbered ETH; earlier reservations, earned claims and other obligations remain unavailable. A failed admission MUST leave neither a new round nor an additional reservation. The reserved ETH MUST be unavailable to later rounds and released if the round is cancelled. Only a valid issued ruling earns the fixed per-seat service entitlement defined in the paper’s [Relevance layer](../../#relevance-layer); each earned fee MUST become withdrawable in the valid-ruling issuance transition under that rule. The final entitlement counts the original drawn seats of timely valid revealers. The unused ordinary ETH reservation MUST return to the pool budget; it MUST NOT augment another juror’s fee. A round MUST NOT enter `CommitOpen` unless its reward floor is reserved in full. Appeal rounds use the funding and reservation rules in Flow F-bis instead of this ordinary-round funding step.
4. The scheduler snapshots the eligible curator set for the claim's pool.
5. Let:

```text
target = pool.relevanceRoundTargetSize
n = min(target, sum(d_i for all eligible curators))
```

6. If `n == 0`, the round is cancelled because no backed seat can be drawn. An empty draft MUST NOT satisfy quorum. No minimum number of distinct eligible curators applies:
   - no new relevance score is produced
   - any previous relevance score for the same pinned revision remains in force; it cannot supply a newer revision's missing score
   - claims whose current revision has no prior finalized relevance round remain out of the default main feed
   - a replacement round is scheduled at the next cadence
7. Otherwise, the scheduler draws `n` seats from the ticket pool using VRF randomness. The draw samples individual seat-tickets (not unique curators); a curator with more tickets may be drawn multiple times. Drafting MUST use a verifiable randomness source. The seed MUST be derived as `seed = H(poolId, claimId, roundId, snapshotBlock, randomness(snapshotBlock+1))`. If randomness is unavailable by a configurable deadline, the round MUST be cancelled and rescheduled. `relevanceRoundTargetSize` defines the number of seats to draw (not the number of distinct curators). Each curator's ticket count is:

```text
d_i = floor(s_i / L)
```

where `L = pool.seatSizeWei`. Only curators with `s_i >= L` are eligible.

8. The protocol draws seats from the ticket pool. Each drawn ticket locks `L` tokens from the corresponding curator. A curator may receive at most `d_i` seats in a single round. Let `n_i` denote the number of seats drawn for curator `i`. The curator’s round weight equals their total locked tokens:

```text
w_i = n_i * L
```

Locked utility tokens are simultaneously the curator’s influence on the weighted mean and their maximum loss from coherence and non-participation slashing. The unlocked remainder (`s_i - n_i * L`) stays in the pool contract and is not subject to coherence slashing, but may be exposed to separately specified utility-token penalties (e.g., pre-reveal leak). Immediately before this draft, snapshot `availableDepositedWei_i` as the curator’s utility-token deposit available for this draft, excluding pre-existing utility-token round locks. Despite its legacy name, this snapshot is measured in smallest utility-token units. ETH appeal contributions occupy a separate ledger and MUST NOT be subtracted from utility deposits or counted as utility-token seat backing. This snapshot remains fixed during the draft; the cumulative `(k + 1) * L` check below accounts for seats already locked by this draft. Locked ETH contributions remain unavailable for withdrawal or reuse in another ETH commitment under Flow F-bis. Drafting MUST be implemented as a deterministic pseudorandom permutation of the snapshot seat-ticket pool derived from the round seed. The protocol iterates through that ordered ticket list, visiting at most `min(totalTickets, 3 * n)` tickets (a hard cap that bounds gas consumption even for large pools): for each visited ticket, the protocol attempts to lock one seat of size `L` for that ticket’s curator. A ticket is fundable only if the curator’s available balance can cover the additional lock (i.e., after `k` seats already locked for curator `i` in this round, the next ticket is fundable only if `availableDepositedWei_i >= (k + 1) * L`). Unfundable tickets are skipped. If `n` backed seats are locked before the iteration cap is reached, drafting succeeds. At that point, the positive sum of original locked weights MUST be fixed as the quorum denominator. Later penalties, slashes, withdrawals or balance changes MUST NOT reduce it. The original weight assigned to each curator MUST remain available for checking its reveal. If the iteration cap is exhausted before `n` backed seats are locked, the round is cancelled as underfunded (no score produced, any previous score retained only for the same pinned revision, replacement round scheduled at next cadence). Only `w_i` MAY determine vote weight or coherence/non-participation slash exposure for that round.

9. Each drafted curator commits a single relevance score in `[0,1]`, weighted by `w_i`. Multiple seats increase the curator’s weight on that single score, not the number of independent votes.
10. Each drafted curator reveals the score.
11. The paper's fixed 80% reveal-weight quorum MUST apply to initial and appeal rounds. Quorum requires valid, timely reveals representing at least 80% of the original weight fixed at the successful draw. It has no minimum distinct-curator count; one curator MAY satisfy quorum through its original drawn weight. Exact 80% MUST pass, and a zero-weight draft MUST fail. The comparison MUST preserve the exact threshold without rounding it down; for equal-weight seats, at least the ceiling of four-fifths of the drawn seat count must be represented. If quorum fails, the drafted round MUST retain the paper’s full fixed post-reveal proof period and its own remaining round collateral before completing cancellation; it MUST NOT cancel early because all reveals are already known or nobody has precommitted a leak report. After the proof deadline and applicable penalty processing, cancellation follows these rules:
   - drafted curators who failed to commit or reveal are slashed as non-participants (graduated slashing applies using a penalty fraction of 1, i.e., total loss of locked tokens)
   - any previous relevance score for the same pinned revision remains in force; it cannot supply a newer revision's missing score
   - if the claim's current revision has no previous finalized relevance round, it remains unscored for feed purposes
   - for an otherwise eligible active item, a replacement round is scheduled at the next cadence under the existing retry limit; after final accuracy closure or completed author withdrawal, a fresh ordinary retry MUST NOT be drawn, even if that allowance is unspent
12. Otherwise, the protocol computes weighted mean and standard deviation. For a round with valid reveal set `V` (guaranteed non-empty by the quorum check in step 11), let `W = sum(w_i for i in V) > 0`. The protocol MUST compute:

```text
mu = sum(w_i * v_i for i in V) / W
sigma = sqrt(sum(w_i * (v_i - mu)^2 for i in V) / W)
```

`mu` and `sigma` MUST be computed over valid reveals only.

13. The protocol MUST derive the committed ETH service budget, each curator’s entitlement and the actual total jury fee from the fixed per-seat rule in the paper’s [Relevance layer](../../#relevance-layer), which owns these formulas. The configured per-seat rate and planned jury size MUST be positive. Ordinary rounds reserve ETH from the pool budget; appeal rounds use Flow F-bis. Only a valid issued ruling earns a service fee within its frozen ceiling. Every timely valid revealer MUST earn the configured rate for each of its originally drawn seats, including when its report is incoherent; score, dispersion, coherence and surviving utility-token stake MUST NOT change that ETH entitlement. Multiple seats represented by one valid reveal MUST earn the corresponding multiple of the rate. Missing, invalid or late reveals MUST earn no fee; a failed-quorum round MUST pay no jury service fee. Fees unearned by one curator MUST NOT be redistributed to other curators. The actual total fee, rather than the full reservation, MUST enter ordinary settlement or the pool-first appeal accounting. Any unused ordinary reservation MUST return to the pool budget. Appeal pool reserves and unused common-pot funds MUST follow Flow F-bis, including continued locking of the unused pot until chain finality. Under the paper's Relevance layer, the valid-ruling issuance transition MUST make earned ETH fees immediately withdrawable, without waiting for the appeal window, chain finality or another participant. A later appeal score change MUST NOT reduce or claw back the earned fee. A proven leak MUST redirect the violator’s entire normal fee to the successful reporter under the paper’s leak rule, with the recipient fixed before or in the issuance transition and before withdrawal becomes possible. This changes the recipient, not the gross fee or actual total jury charge. Unclaimed fee entitlements MUST remain committed to their designated recipients and outside the backer pot; collecting a fee MUST NOT charge its funding source a second time. The same fee MUST NOT be paid to both violator and reporter, or paid again for another report. Anyone MAY trigger payment of an already-claimable fee under the paper’s standing receiving-address rule. Each transfer MUST resolve the current receiver for its original recorded juror or leak-reporter recipient and paying contract; a caller MUST NOT override it with a per-claim destination. No new per-payment signature or approval is required to trigger payment. This does not require automatic distribution, grant the caller a fee or change the earned amount or its unlock time. A failed transfer MUST leave the entitlement unpaid, reserved and retryable without charging its source again. The authenticated update interface, cryptographic format if used, replay-protection representation, transfer isolation, batching and record representation remain open. Utility-token rewards use only actual distance-based incoherence slashes under step 16. They have no minted reward, subsidy or separate prefunded reserve; the analytical `rho` and `f_reward` subsidy does not apply.

14. Coherence settlement timing: valid revealers' round locks MUST remain locked until the round's appeal chain reaches finality under the paper's [Public appeal funding](../../#sec-appeal-funding) rules, and distance-based slashing for every committee in the chain MUST run once at that event. Without an admitted appeal, the ruling becomes final at admission closure. The mean is accepted as a valid relevance score whatever its dispersion. Non-participants who failed to commit or reveal MUST be slashed at `p_i = 1` under the non-participation rules below without waiting for finality; their `delta_i = w_i` goes to the separate utility-token pool balance, not to the coherence reward distribution or the ETH budget. The ETH service-fee outcome remains separate under step 13 and MUST NOT wait for finality. Voluntary appeal contributions retain the separate lock defined in Flow F-bis, independently of curator status.

15. The protocol MUST apply the graduated-slashing rule in step 7 of the paper's [Relevance layer](../../#relevance-layer), which owns the coherence reference (the chain's terminal adjudicated ruling, never a score set by forfeiture), the floored dispersion scale, the penalty formula and its integer round-down. Every committee in the chain MUST be graded against that same reference. Low dispersion MUST NOT exempt valid revealers from distance-based slashing; the dispersion floor bounds the band width instead.

16. The protocol MUST apply the utility-token entitlement and integer round-down rule defined in the paper’s [Relevance layer](../../#relevance-layer), which owns the redistribution formula, coherent-recipient definition and residual bound. Its input contains only actual integer distance-based incoherence penalties from valid revealers in this round, excluding non-participation and leak penalties. Each coherent curator’s complete original round weight MUST be counted once, aggregating all represented seats before rounding its reward down to the smallest token unit; rounding separately by seat MUST NOT replace this rule. When each committee’s rewards are allocated at chain finality under step 14, the resulting rounding remainder MUST be credited exactly once to this same pool’s separate utility-token balance. A committee’s penalties MUST fund only that committee’s coherent curators. Some or all coherent curators can receive zero after rounding even when penalties were collected. With no eligible penalties, the additional reward and rounding remainder are zero. If there are no coherent recipients, the paper’s existing fallback credits all collected eligible penalties to that separate utility-token balance. The recipient-count residual bound MUST follow the paper and MUST NOT use the limit on appeal-score positions. Unclaimed integer reward entitlements MUST remain reserved for their recipients and MUST NOT be swept into the pool balance as rounding dust. The redistribution MUST NOT mint tokens, require a token subsidy or reserve, use ETH service fees, convert assets, or draw from that pool token balance. Returned surviving stake is separate from the reward. The existing floor on each incoherence penalty remains unchanged. Claim execution and the numerical representation of the defined formulas remain implementation work. Unused ETH service-fee reserves follow the applicable round-funding rule; appeal reserves follow Flow F-bis. The pool MUST enforce `K > 0` so the `p_i` formula is well-defined and `epsilon_sigma > 0` so the floored dispersion scale is positive.
17. The paper’s [Relevance layer](../../#relevance-layer) owns the fixed post-reveal proof deadline and the positive duration frozen with the round timetable at creation. The provisional default MUST follow the paper's Relevance layer, which owns the duration value. For every drafted round, ordinary or appeal, the full period MUST remain available even if all jurors have already revealed, quorum is already known to fail, or no report is pending. A ruling MUST NOT issue and a quorum-failure cancellation MUST NOT complete before the deadline. The offending round’s remaining collateral MUST stay locked through that period and applicable penalty processing. This MUST NOT freeze otherwise unlocked deposits or prolong collateral locks belonging to other rounds.
18. A reporter who receives a leaked intended vote MAY precommit `hash(leakedPayload)` before reveal closes.
19. A reporter MAY open a qualifying payload before the paper’s fixed proof deadline; valid earlier openings MUST remain eligible. A proof MUST be included and validated before that exclusive deadline to qualify. Inclusion at or after the deadline MUST be rejected even if the round has not yet finalized. The original precommit deadline in step 18 MUST remain unchanged. Early reveals, precommits, invalid reports, unopened precommits and delayed finalization MUST NOT shorten, reset or extend the proof period. An unopened precommit MUST NOT create a later claim. After the deadline, completion MUST process qualifying timely proofs and fix the fee recipient before making the affected fee withdrawable.
20. A leak report is valid only if the opened payload proves that a drafted curator disclosed their vote before their on-chain reveal and the payload later matches the curator’s actual reveal and commitment for that round.
21. If a valid leak report is confirmed, the guilty curator is slashed. For every drafted curator `i`, define `baseLeakSlashWei_i = w_i` (total locked tokens for that curator) regardless of whether curator `i` is later coherent or incoherent. A confirmed pre-reveal leak by curator `i` MUST trigger:

```text
preRevealLeakSlashWei_i = min(pool.preRevealLeakSlashMultiplier * baseLeakSlashWei_i, leakSlashableWei_i)
```

Define `leakSlashableWei_i` from the eligible current balance in the paper's [Relevance layer](../../#relevance-layer): remaining utility tokens locked for the offending round plus currently unlocked utility-token deposits, counted once. Collateral still locked for every other active round MUST be excluded and MUST NOT be reduced, released or reassigned by this penalty. Amounts already confiscated or transferred MUST NOT remain in the eligible balance. The cap and corresponding debit MUST use one atomic balance state, so concurrent penalties cannot reuse the same tokens. The legacy `Wei` names in this formula denote smallest utility-token units. ETH appeal contributions are separate and MUST NOT be subtracted from that token balance or consumed by this penalty. The multiplier still applies to the offending round's original `w_i`; it does not guarantee full collection. If the eligible balance is insufficient, the actual penalty is smaller, without extra debt, a top-up or loss of another round's collateral. Other rounds' original voting and quorum weights remain unchanged. The fixed proof period retains only this round’s remaining collateral; it MUST NOT impose a new freeze on otherwise unlocked deposits or extend another round’s locks. Transactions otherwise permitted before enforcement may reduce the eligible balance. Unclaimed token entitlements MUST NOT be counted as deposited collateral until actually credited. The successful reporter MUST receive the actual utility tokens confiscated by this penalty and the violator’s entire normal earned ETH service fee for this round, if any, under the paper’s [Relevance layer](../../#relevance-layer). The fee covers all original drawn seats represented by the violator’s timely valid reveal; the reporter receives that entitlement instead of the violator. No independent bounty, conversion or additional ETH collateral is introduced. If the round produces no valid ruling, or the violator’s reveal is missing, late or invalid, the ETH component MUST be zero; the existing utility-token penalty still applies. Only a qualifying proof opened before the fixed exclusive proof deadline may support the recipient override. The override MUST be applied at or after that deadline, before or in actual valid-ruling issuance and before any withdrawal; there is no post-issuance proof or clawback path. The diversion MUST NOT increase the actual total jury fee, create a refund to its funding source or pay the same fee twice. If multiple valid reports exist for the same leak, the earliest valid precommit determines the successful report. The actual confiscated utility tokens MUST NOT enter the coherent-curator reward pool or the ETH service budget. The token transfer and diverted ETH entitlement remain separate asset amounts.

22. This penalty is in addition to any graduated slashing that already applies in the same round.
23. The round MUST record `mu` as the relevance score of its pinned revision. Only if that revision equals the claim's `currentRevision` MAY this result update the claim's revision-specific `relevanceScore`. Otherwise the result MUST remain in revision history and MUST NOT overwrite a newer revision's assessment or establish that newer revision's assessed status.
24. After the full fixed proof period ends and qualifying timely proofs are processed, a round with valid quorum completes and issues its ruling. The earliest permitted completion is the paper’s fixed proof deadline; early readiness MUST NOT permit early issuance. Its technical round state becomes `Finalized`, and its earned ETH fees become withdrawable and its appeal window opens in the same actual issuance transition (see Flow F-bis). A later completion MUST NOT reopen or extend proof acceptance. For an ordinary round, releasing ordinary-round exclusivity and opening the appeal hold MUST be atomic; no scheduling gap MAY admit another ordinary round.

Non-participation rules:

- failure to commit or reveal counts as maximum-penalty incoherence (`p_i = 1`, total loss of locked tokens)
- repeated non-participation beyond 3 missed rounds in 30 days SHOULD auto-exit the curator

Pre-reveal leak rules:

- a drafted curator MUST NOT disclose their intended vote or reveal preimage before their own on-chain reveal
- successful collusion requires revealing the intended vote to at least one other participant
- any recipient of that leak can precommit by the unchanged original deadline and open a qualifying proof before the fixed exclusive proof deadline; valid early openings remain eligible, and the successful reporter receives actual confiscated utility tokens plus the violator’s normal earned ETH service fee, if any
- only cryptographically verifiable reports that match the curator’s later reveal and commitment count
- a confirmed leak triggers the existing additional utility-token penalty, capped at the deposited balance, and the paper’s fee-recipient override

### Flow F-bis: Relevance-Round Escalation (Appeals)

The paper's [Public appeal funding](../../#sec-appeal-funding) section owns the common appeal rules, fee accounting and scalar payout formula for all funded opposing positions. This flow applies those rules to a claim; the open terms identified below still require specification.

The paper also owns the continuation rule for an ordinary attempt whose nonempty jury draw completed successfully before a final accuracy closure or completed permitted author withdrawal. That current attempt MUST finish against its pinned revision and policy under its existing commitments, reveals, quorum, proof period, penalties, ETH service-fee rule and funding reservations. A scheduled attempt or incomplete draw does not qualify merely because preparation started. Protocol execution order determines whether the successful draw preceded the exit. If the attempt issues a valid ruling, it earns its normal ETH fee and opens its normal first appeal window despite the item’s inactive state. That first window and the chain it starts MUST follow the ordinary appeal rules; the earlier exit MUST NOT be replayed to cancel them for lacking already-funded positions. This is a narrow exception permitting only the appeal chain attached to that current attempt, not an unrelated chain or a new independent ordinary round. It MUST NOT reverse the exit, restore the feed or beneficiary funding, relock a returned bond or make the author a party merely through authorship.

A qualifying current attempt MAY itself be an ordinary retry whose nonempty draw completed before the exit. If that continued attempt fails quorum, it MUST finish its existing proof period and normal fee-free, no-score failure settlement, release its unused ordinary ETH service-fee reservation through the normal cancellation path, and open no new appeal window. Final accuracy closure or completed author withdrawal MUST bar every fresh ordinary retry draw for the inactive item, even if an ordinary retry allowance remains. This does not reset the proof period, waive applicable penalties, alter the normal lock settlement, refund already-earned fees, reactivate the item or change the author-bond effects. Still-active items retain their existing ordinary-retry rules and limits. The protected appeal-chain retry rules remain separate and unchanged.

The paper’s common terminal-exit appeal rule applies to a final accuracy closure and to completed voluntary author withdrawal of this exact claim instance in this pool. A withdrawal request or pending cooldown alone MUST NOT trigger it. Before selecting an exit branch, the protocol MUST evaluate finality already established by the existing deadlines or outcomes at the effective exit time, even if no transaction has recorded it. Existing logical finality takes precedence at the same timestamp as a deadline: an already-final score, including a forfeiture score, and its settlement entitlements MUST NOT be replaced, reopened or refunded again by the later exit.

If any contested level in the same ongoing relevance-appeal chain had at least two distinct positions fully funded before the terminal exit, that chain MUST continue under the paper’s funded-chain rule. This protection MUST apply even when exit occurs during a later level’s admission or fundraising and that later level is not yet fully funded. The assessed revision, existing terms, reserves and clocks MUST remain unchanged. Existing admission and funding windows MUST continue under their deadlines. Juries MUST retain the common quorum, proof-period and unlimited appeal-retry rules; valid issued rulings earn normal fees and open their normal further appeal windows, which MAY receive fresh funding within this same chain until normal finality.

The exit MUST NOT force that chain’s relevance score to zero, finalize it early, refund its adjudicated capital, release its reservations or create an extra exit. Already-earned jury fees MUST remain earned. Accuracy-closed items remain closed with their accuracy consequences; voluntarily withdrawn items remain withdrawn with their existing bond-return and confidence consequences. Continued relevance proceedings MUST NOT reactivate the feed or beneficiary funding, relock a returned author bond, or make authorship alone a party to the contest. This rule neither changes withdrawal eligibility or cooldown nor requires withdrawal to wait for appeal-chain finality. It does not authorize new independent ordinary rounds or unrelated appeal chains for the inactive item; the qualifying already-drawn ordinary attempt described above may finish and start its own normal first appeal chain.

If the initial appeal process is still open and no contested level in that same chain was fully funded before the effective terminal exit, the paper’s pre-contest terminal-exit cancellation rule MUST apply atomically. Admission and contribution acceptance MUST stop immediately, without waiting for their scheduled deadlines. The already-issued referenced ruling’s score MUST become terminal; exit MUST NOT force zero, issue a new jury ruling or let an unopposed proposal win by forfeiture. Every accepted contribution MUST become refundable in full, including a fully funded lone position, and refund entitlements MUST remain assigned independently of collection. This branch covers no positions, partial funding, one fully funded position and multiple positions without a funded contest.

An appeal jury MUST NOT be drawn and an appeal fee MUST NOT be earned for that cancelled process. Unused appeal fee reservations MUST return to their original sources: the pool recovers only its unused pool-funded reservation, while contribution-backed amounts remain reserved for contributor refunds. The same ETH MUST NOT be credited both to the pool and refund entitlements, and no additional refund funding is created. Already-earned ordinary jury fees MUST NOT be clawed back. Refunds follow the common permissionless claim and current receiving-address rules. Cancellation ends only this process’s hold and MUST NOT affect other claims’ or pools’ holds, reserves or proceedings, or permit a new ordinary round for the inactive item.

After existing logical finality is resolved, valid protocol state transitions MUST determine the race between the terminal exit and funding. Acceptance completing the second distinct fully funded position before exit protects the chain. If exit takes effect first while no contested level was previously fully funded, later proposals or contributions MUST be rejected and MUST NOT restore the cancelled process. The ordinary deadline and forfeiture provisions below are subject to this explicit pre-contest terminal-exit exception; jury voting, proof and other deadlines are unchanged. A qualifying already-drawn ordinary attempt follows the continuation rule above, but final accuracy closure or completed withdrawal permits no fresh ordinary retry draw for that inactive item.

Every appeal MUST inherit the referenced ruling's pinned revision, immutable content references and pool policy versions. Subsequent levels and quorum retries MUST preserve this target. Where amendments are otherwise permitted, publishing a new revision MUST NOT cancel or retarget an existing relevance appeal, reset its deadlines, change its funding terms, refund contributions or release adjudicated capital. All jury, forfeiture and zero-funded outcomes MUST remain attached to the assessed revision, and its own chain MUST govern backer settlement. Later outcomes for that revision MUST NOT overwrite a newer revision's adopted score. The new revision awaits its own assessment under the same-item hold and resumption rules; it MUST NOT inherit an older score for ranking or new score-dependent funding, even provisionally. It MUST wait for its own adopted score under the existing adoption rules; no extra chain-finality wait is introduced. Direct links and pending views remain available. An absent score MUST NOT be replaced with synthetic zero; an adopted 0.00 remains a valid outcome. Ordinary state, funding and holdback conditions still apply after adoption. This eligibility rule MUST NOT change the older revision's appeal settlement. In applications with beneficiary funding accrued before the edit, that balance MUST retain its original revision attribution and remain subject to the beneficiary, claim, holdback and accuracy-challenge conditions already governing it. An amendment alone MUST NOT erase it, return it to the pool, move it to the new revision or restart its payout conditions. Preservation MUST NOT be treated as immediate or unconditional claimability. The confidence reset on amendment MUST NOT reset a separately accrued funding balance. Requested budgets, reservations and provisional allocations MUST NOT be converted into accrued balances by this rule; their existing cancellation and redistribution rules remain applicable. The contest record MUST preserve the content that the funded positions concern and its outcomes: an update MUST NOT change the subject after backers have committed capital. Settlement MUST use that revision's chain-final score. Authorship alone MUST NOT make the author a party or put the author bond at stake; an author backing a position MUST participate under the ordinary backer rules. Accuracy-challenge amendment restrictions remain unchanged.

1. **Issue the ruling and open admission.** A valid jury-round completion MUST issue a ruling, make the earned jury fees immediately withdrawable under the paper's fee rule and open one bounded appeal admission window in the same transition. Issuance MUST NOT be treated as ruling finality. Ordinary and appeal rulings MUST use the same positive pool-configured admission duration, provisionally defaulting to 72 elapsed hours and frozen for the ruling at issuance together with a positive pool-configured common funding duration, whose provisional default is 72 elapsed hours. The admission deadline MUST equal issuance time plus the frozen admission duration. The common funding deadline MUST equal that admission deadline plus the frozen funding duration. Both cutoffs MUST be exclusive: use the protocol inclusion timestamp, admit a new position only before its admission deadline and accept funding only before its funding deadline. At or after a cutoff, the corresponding phase MUST be closed even if no transaction has explicitly recorded closure. Transaction ordering at the same timestamp MUST NOT extend acceptance. An earlier signature or broadcast MUST NOT make late inclusion timely. Existing admitted positions MAY still fund at or after admission closure, strictly before their separate funding cutoff. This convention MUST NOT change juror or external-court deadlines. Later configuration changes, party actions, contributions, fee collection and payout or refund claims MUST NOT alter or restart either deadline. The explicit pre-contest terminal-exit rule instead ends that process immediately without resetting or extending those deadlines. Failed-quorum attempts, funding failures and procedural forfeiture outcomes MUST NOT open a new window; a new ruling MUST NOT reopen an older ruling's closed window. New ordinary rounds for the claim MUST be blocked from issuance through any open admission window or active appeal, without a gap. This hold MUST NOT cancel an already-started ordinary round or block the claim's appeal jury or rounds for other claims; it MUST NOT be interpreted as permission to admit overlapping ordinary rounds.
2. **Admit public score positions.** The one-position-per-ruling-and-numeric-score rule MUST hold under concurrent submissions. Anyone, including the nominator, MAY propose or fund a fixed numeric relevance score without approval or role-based exclusion. A contribution MUST NOT require a curator deposit or prior jury membership. Each position MUST record its score and referenced ruling before accepting contributions. A proposed score MUST equal `k / 100` for an integer `k` from 0 through 100 inclusive: exactly 101 allowed values. Off-grid proposals, such as 0.599 or 0.705, MUST be rejected before contributions and MUST NOT be silently rounded. This restriction applies only to proposed appeal positions, not juror reports, the existing ruling or its weighted mean. Changing a proposed score requires a different allowed position. Any two fully funded positions proposing different scores are counterparties, whether or not either score equals the existing ruling. The existing score MAY itself be proposed and funded if it is on the allowed grid, but MUST NOT receive automatic funded status. More than two funded positions are permitted. There MUST be at most one position for a given referenced ruling and numeric proposed score. A duplicate position MUST NOT be admitted; anyone backing that score MAY contribute to its existing position while funding remains open, subject to the same shared contribution cap. Repeating the same score MUST NOT create a new target, payout weight or funding clock. Numerically equal values, such as 0.70 and 0.700, refer to the same position. Distinct allowed positions are at least 0.01 apart; neighboring scores such as 0.59 and 0.60 remain permitted. An appellant or backer selected by the ordinary draw MAY serve under the same rules as other selected curators.
3. **Freeze funding terms and accept contributions.** Every position against the same ruling MUST use the common positive target derived by the paper's pinned pool rule and input snapshot before admission opens. Proposer, score, filing time, later rule changes and extra contributions MUST NOT change that target. The snapshot MUST freeze the contribution multiplier, planned jury size, base pay per seat and resulting maximum shared-jury fee. The multiplier defaults to 2; target rounding and alternative multipliers MUST preserve the paper's strict two-position fee-capacity condition. A position MUST atomically accept only its remaining target amount, with excess left with or returned immediately to the contributor. Acceptance of a positive amount and creation of its immutable contribution interval MUST occur atomically under the paper’s funding-order interval rule. The record MUST identify the backer and accepted amount, preserve its place in cumulative accepted funding for that position, and MUST NOT later be merged, reordered or reassigned. Multiple contributions by one address MUST remain separate intervals; that address’s entitlement is their sum. A zero accepted amount, including a fully funded position’s rejected excess, MUST create no interval. Only accepted funds count toward the target, refunds and ideal proportional payouts. Refundable principal MUST remain the exact accepted amount; the adjudicated-payout rounding rule MUST NOT reduce a principal refund. Accepted contributions MUST lock immediately until an applicable refund or chain-final settlement. They MUST NOT be withdrawn, reused for another position, appeal level or ordinary-round seat, or consumed by unrelated penalties. The lock MUST survive curator exit and MUST NOT cover unrelated curator balances. Every admitted position MAY accept capped contributions from its admission strictly before the common funding deadline. A position below its target at that deadline MUST be cancelled and refund its accepted contributions in full, without a jury fee or score-setting right. A partially funded position MUST NOT expire before that deadline except when the paper’s explicit pre-contest terminal-exit rule cancels the process and creates full refund entitlements.
4. **Close admission before drawing the shared jury.** All proposals admitted against one ruling MUST belong to one group and share its common funding deadline. Reaching two distinct fully funded scores MUST make the group contested but MUST NOT close admission or start the jury early. Further proposals MAY enter strictly before the original admission deadline; no new positions MAY be admitted after it. The admission deadline MUST fix membership. Every admitted position retains the full common funding duration after the complete slate is visible; earlier admissions have more total funding time. There MUST NOT be separate per-position fundraising or matching clocks. A contested group’s jury MAY proceed once admission has closed and every admitted funding outcome is known. If all admitted positions are fully funded, that jury need not wait for unused time before the common funding deadline. While any admitted position remains below its target before the common funding deadline, the jury MUST wait. That position’s funding outcome becomes known on full funding or on cancellation at the deadline. Timeout recognition MUST NOT depend on collecting a refund. Failed-quorum retries MUST NOT reopen admission or funding, or reset either deadline.
5. **Adjudicate contested scores from one common pot.** At least two distinct fully funded scores MUST proceed to one shared jury scoring the underlying claim over the full relevance scale. All fully funded opposing positions against that ruling MUST combine their accepted funds into one common pot, while retaining each position's score and each backer's contribution record. Positions MUST NOT create separate pairwise pots or separate jury fees. The jury MUST NOT be restricted to selecting a submitted score. Initial and appeal juries MUST use the same commitment, reveal, aggregation, reward and penalty rules under Flow F. The next appeal's planned seat-ticket target MUST equal twice the planned target of the valid round that issued the referenced ruling, under the paper's jury-sizing rule. A smaller actual draw MUST NOT reduce that baseline. A referenced round planned for 20 seats but drawing 12 therefore gives the next appeal a target of 40 seats. The target MUST NOT be treated as a guarantee of filled seats or independent curators. Additional positions and failed-quorum retries MUST NOT multiply that level's frozen jury target again. Only a valid issued ruling MUST incur the protocol-verifiable actual fee within the frozen ceiling; unused seat capacity MUST NOT be charged. The pool MUST fund that one shared fee first, with only its shortfall deducted once from the common pot, without a replenishment wait. The paper's common-pot accounting applies to any number of admitted, fully funded distinct positions greater than one. Its maximum liability MUST be reserved before drawing or seating and MUST NOT be reused. The paper’s shared-budget rule MUST allocate available ETH subsidy in successful fee-reservation execution order, after this group satisfies its existing admission and funding-readiness conditions. That reservation MUST preserve earlier commitments and freeze this group’s funding snapshot; later deposits or returned reserves MUST NOT resnapshot it. Unused pool reserves MUST return to the pool when the fee is determined; unused common-pot reserves MUST remain in the locked pot until chain finality. The paper’s [Public appeal funding](../../#sec-appeal-funding) MUST govern ideal inverse-absolute-error allocations and whole-wei position payouts against the actual ultimate final score of the same chain. Each ideal position amount MUST be rounded down to whole wei as specified there. At chain finality, the resulting aggregate rounding residual MUST be credited exactly once to this same pool’s ETH jury-service budget, without waiting for payout claims. Before chain finality, that residual MUST NOT become spendable pool funds. Each rounded position amount MUST remain assigned to its backers and MUST NOT be swept into that budget merely because it is unclaimed. Backer entitlements MUST follow the paper’s cumulative rounded-interval rule in fixed funding-acceptance order. For a funded position, its immutable contribution intervals MUST partition the full accepted target, and their integer entitlements MUST distribute the entire rounded position payout. Claims in any order MUST preserve those entitlements, and the same interval MUST NOT be claimed twice. There is no second backer-rounding residual and no additional credit to the pool from this step; unclaimed entitlements remain assigned. Anyone MAY trigger an already-claimable payout under the paper’s standing receiving-address rule. Each transfer MUST use the current receiver for the original recorded backer and paying contract, without changing the amount, unlock time or ownership. A failed transfer MUST leave the unpaid entitlement reserved and retryable, with the current receiver resolved again on retry. The authenticated update interface, cryptographic format if used, replay-protection representation, transfer isolation, batching and ledger representation remain open. Settlement MUST NOT round that final score to the appeal grid. If all errors are positive, each position's weight MUST be the reciprocal of its absolute error, normalized across the positions; no artificial error floor is added. A unique exact prediction MUST receive the entire net pot. The existing two-position formula is the reduction of this general rule. With all errors positive, the ideal unrounded allocation is larger for a closer position and equal for equal errors. Whole-wei round-down may turn unequal ideal allocations into equal payouts or a small positive allocation into zero. Even a closer position can lose principal after fees. Because each numeric score has only one position per referenced ruling, an exact prediction cannot create separate exact-match positions. The exact-match branch MUST allocate the entire net pot to that position with no position-rounding residual; the same cumulative contribution-interval rule MUST distribute that entire allocated payout among its backers.
6. **Retry quorum failures.** A drafted shared-jury attempt that fails the 80% reveal-weight quorum MUST keep its full fixed proof period and remaining own-round collateral, process qualifying timely proofs, then complete cancellation without a new score, jury fee or curator reward subsidy. The contested level MUST remain active and receive a fresh jury at the existing cadence, without a retry-count limit or elapsed-time cancellation. Each attempt MUST use its own completed draw for quorum coverage while retaining the level's fixed membership, scores, target, planned size, pay rate, fee ceiling and funding reservations. Contributions and reserves MUST remain unavailable for reuse; failure MUST NOT spend or release them, reopen funding or require top-ups. Ordinary non-participation penalties, leak detection and token slashing, and release of valid participants' round locks after the fixed proof deadline and applicable penalty processing MUST still apply; a successful timely leak report transfers the actual confiscated utility tokens under Flow F, with no ETH component because the failed attempt earns no jury fee. The pinned revision's effective score and the same-item ordinary-round hold MUST persist. That historical score MUST NOT be relabeled as an assessment of newer content. Independent accuracy, eligibility and withdrawal effects remain applicable.
7. **Resolve funding outcomes.** For a process not already cancelled by the pre-contest terminal-exit rule, if proposals were admitted but none is fully funded at the common funding deadline, the referenced ruling MUST become final at that deadline, using its issued score as the chain's terminal score. An appeal jury MUST NOT be drawn for that group, and a new jury fee MUST NOT be charged. All its accepted partial contributions MUST be refundable in full. Earlier earned jury fees MUST remain charged, and earlier adjudicated pots MUST settle against the referenced ruling's score under the common payout formula, with payouts claimable at finality. Finality MUST NOT depend on a closure transaction or collection of any refund or payout. This outcome MUST NOT create a new ruling or appeal window. It MUST end only this group's hold; any other applicable admission window or active appeal MUST continue to block new ordinary rounds. Failed fundraising MUST NOT be presented as additional evidence of the ruling's correctness. If that process remains active and exactly one distinct proposed score is fully funded after admission closes and every admitted funding outcome is known, that score MUST become the chain's final score by forfeiture. Its origin MUST be recorded as procedural, not a jury finding or evidence of consensus, and it MUST NOT open a new appeal window. Its own accepted contributions MUST be returned in full, without a fee or profit on that position. Two different fully funded scores MUST NOT both be treated as unopposed: they require adjudication. The forfeiture score can change payouts from earlier adjudicated levels of the same chain.
8. **Preserve chain finality and settlement.** Every issued relevance ruling MAY be appealed again within its own window, with no fixed depth limit and fresh voluntary funding. Earlier locked capital and reservations MUST NOT be reused. Each level MUST retain its own common pot, recorded positions and contribution records. Pots MUST NOT combine across levels, and a later jury MUST NOT charge an earlier level. After the earned jury fee is deducted, no remaining adjudicated backer funds MAY be released before the chain ends. This lock MUST NOT delay withdrawal of earned jury fees under the paper's Relevance layer. The ultimate final score MUST determine all adjudicated backer payouts, including earlier levels, and those payouts MUST become claimable immediately at chain finality. Intermediate scores MUST NOT create a fixed or withdrawable backer entitlement. Later ordinary rounds or separate chains MUST NOT reopen that settlement reference. Absent the explicit pre-contest terminal-exit exception, with no admitted proposals a ruling MUST become final at admission closure. The admitted-but-zero-funded outcome MUST follow step 7. While awaiting a valid new jury score or qualifying final forfeiture score for the same revision, that revision's previous score MUST retain its funding role under the applicable revision policy without overriding independent accuracy, eligibility, withdrawal or other funding inputs. This retention MUST NOT assign an old revision's judgment to a newer revision. Mere score retention MUST NOT establish finality or release adjudicated funds; the explicit finality conditions, including step 7, MUST govern.

Repeated funded appeals and quorum failures can lock capital and ordinary scheduling indefinitely. Pooling contributions can mobilize capital beyond one participant's wealth, but correction still depends on sufficient funding and expected proceeds. The appeal grid limits proposal resolution; it does not establish resistance to capital-based influence or strategic use of neighboring scores. Extra jury seats improve precision only if they add useful independent information; neither crowdfunding nor a larger jury establishes truthful reporting or eliminates common bias. The single-asset analytical reward-padding example’s dispersion-based ETH fee increase is absent under the fixed per-seat rule for the same valid revealers and original drawn seats. It does not evaluate the remaining utility-token, effort, concentration or appeal incentives of the current design. Under the paper’s cumulative backer rule, the rounding discrepancy is less than one wei per accepted contribution, not per person or address. Adjacent splitting is neutral, but interleaved contributions and funding order can change who receives rounding wei; the rule does not establish resistance to identity splitting.

The asset split is specified: utility-token staking and coherence incentives are separate from ETH service fees and appeal settlement. Target rounding, numerical representation of the defined formulas, non-default multiplier calibration, the authenticated update interface, cryptographic format if used, replay-protection representation, transfer isolation, batching, record representation and other cancellation outcomes remain to be specified. Shared ETH subsidy allocation follows the paper’s successful-reservation execution-order rule. Position-level whole-wei rounding, the same-pool ETH residual destination and cumulative contribution-interval backer payouts are fixed by the paper’s Public appeal funding rule. Per-curator utility-token reward rounding and its separate same-pool token residual are fixed by the paper’s Relevance layer. The leak-proof duration uses the paper's provisional default and is frozen for each round. Proof validity, processing liveness and reporter-coalition incentives also require adversarial analysis; the fixed deadline prevents early completion from shrinking the window, and the protected-collateral cap above governs the penalty’s utility-token reach. This flow is not a complete implementation algorithm.

### Flow G: Rewards, Slashing, And Withdrawals

#### Internal ETH Claim Execution

The paper’s [Public appeal funding](../../#sec-appeal-funding) owns the common claim-execution and standing receiving-address rules for internal ETH jury-service fees, including fees redirected to a successful leak reporter, and relevance-appeal backer payouts and refunds. Anyone MAY trigger an already-claimable payment without a new per-payment signature or approval. The original recorded recipient MUST remain the entitlement’s owner. Each original recipient and paying contract MUST have one current receiving address, defaulting to that original recipient, for every currently unpaid and future entitlement within this scope.

Only the original recipient MAY authentically update that receiving address or reset it to itself, without first suffering a failed transfer. The receiving address MUST NOT become a new owner or gain authority to change future routing. A caller, operator or prior receiver MUST NOT choose or authorize a replacement unilaterally. If the original recipient is a contract, only that contract through its authorized mechanism MAY change the receiving address; the protocol MUST NOT infer authority from a supposed human controller or recovery administrator. Superseded update instructions MUST be rejected, and an instruction MUST NOT be reused against another original recipient, paying contract or chain. The precise authenticated update interface and replay-protection representation remain implementation work.

Each payment MUST resolve the receiving address current at transfer time, rather than freezing it when the entitlement accrues. Atomic on-chain execution order MUST govern a payment racing an update: a payment executed first uses the old receiver, while an update executed first makes the payment use the new receiver. A per-claim grant, stale destination or caller-selected address MUST NOT override that current receiver. An update MUST NOT alter ownership, the amount, unlock time, fee calculation, refund or rounding rules, or redirect a successfully settled payment retroactively.

Successful transfer MUST satisfy its corresponding entitlement exactly once. Failed transfer MUST NOT satisfy the claim, release its unpaid reservation or charge the funding source again; the unpaid entitlement MUST remain reserved and retryable, resolving the current receiver again on a later attempt. Payment grants no caller fee or reimbursement entitlement and requires no automatic distribution. These rules do not extend to author bonds, beneficiary or registry claims, utility-token rewards or stake withdrawals. The authenticated update interface, cryptographic message format if used, nonce or other replay-protection representation, transfer isolation, batching and record representation remain open; no batch atomicity is selected.

#### Authors

- earn no direct protocol reward by default
- benefit by keeping bond intact and accumulating confidence
- may later withdraw after cooldown if claim remains live

#### Challengers

- profit when they correctly debunk or flag non-falsifiable claims
- lose counter-stake when they challenge incorrectly

#### Curators

- receive per-curator rounded-down utility-token rewards only when drafted, coherent and actual distance-based incoherence slashes are available for redistribution; an otherwise eligible reward may round to zero
- earn the fixed ETH service fee per originally drawn seat represented by a timely valid reveal when the round issues a valid ruling, regardless of score, coherence or dispersion; the earned fee becomes immediately claimable at issuance for its original recorded recipient and is paid to that recipient’s current configured receiving address under the paper’s rule, with a proven leak redirecting it to the successful reporter; anyone may trigger an already-claimable payment under Internal ETH Claim Execution, while the remaining transfer mechanics stay open
- do not earn passive yield merely for sitting in a pool

#### Pool Reward Budget

Each pool has its own ETH jury-service budget. This is not a discretionary governance treasury. The separate utility-token pool balance holds applicable token penalties and the same pool’s coherence-reward rounding remainders, credited once when valid-round rewards are allocated under the paper’s rule. It excludes unclaimed rewards already assigned to curators and has no new spending or redistribution policy in this revision. It MUST NOT finance ETH obligations or augment the round’s distance-slash redistribution.

For every otherwise eligible fresh ordinary-round or appeal fee commitment, the paper’s [Public appeal funding](../../#sec-appeal-funding) reservation rule MUST apply: checking unencumbered ETH and reserving it occur atomically, and successful execution order determines which commitment obtains that available subsidy. Existing reservations, earned but unclaimed fees and other obligations MUST be excluded and MUST NOT be preempted. Filing, readiness, a due time, off-chain intent or broadcasting a transaction MUST NOT by themselves reserve funds. The existing relative scheduler order for ordinary rounds remains in force; an appeal MUST still complete its admission and funding-readiness requirements before committing a fee. Ordinary rounds still require sufficient budget, while appeals cover their shortfall from their own common pot without a replenishment wait.

A completed reservation’s funding snapshot MUST NOT be replaced because of later deposits or returned reserves. Existing reservations retained across appeal retries MUST remain intact; releases still follow the applicable completion or cancellation rule. Faster transaction inclusion can obtain subsidy first and leave otherwise unreserved ordinary work waiting. This is a defined allocation order, not a fairness or security guarantee.

Pool reward budgets receive:

- challenge tax paid by challengers at challenge activation (not at filing for queued challenges)
- 20% of failed challenger counter-stake
- direct top-ups from the pool creator, sponsors, or any third party
- position-rounding residuals from this pool’s adjudicated appeal pots, credited once at chain finality under the paper’s Public appeal funding rule; unclaimed assigned payouts are excluded, and cumulative backer payouts create no additional residual

Pool reward budgets pay:

- ordinary-round ETH service-fee reservations
- the available ETH pool-funded portion of shared appeal-jury fees under Flow F-bis

Rules:

- the pool creator SHOULD seed the initial reward budget to bootstrap curator participation
- any address MAY replenish a pool reward budget
- a peaceful pool SHOULD assume round rewards are primarily sponsor-funded rather than financed by failed challenges
- if the budget cannot cover the derived round reward reservation, new ordinary relevance rounds pause until the pool is funded again; contested appeals use Flow F-bis fee funding
- no protocol mechanism creates a sponsorship incentive; pool economics depend on external actors (pool creators, sponsors, or third parties) voluntarily funding the reward budget; if funding does not materialize, ordinary relevance rounds pause, while a contested appeal can fund its jury from its common pot under Flow F-bis and the accuracy layer remains fully functional; this is a critical bootstrapping dependency

**Sustainability and the free-rider problem.** The relevance layer exhibits a classic public-goods free-rider problem: curated feeds benefit all readers, but ordinary-round sponsorship costs fall on those who contribute. Rational sponsors have an incentive to let others fund the pool while still consuming its outputs. A well-functioning pool with few challenges generates negligible self-funding because challenge-tax and failed-challenge inflows are inherently tied to dispute volume: a peaceful pool (the desired outcome) produces the least endogenous revenue.

When funding dries up, the degradation is partial but significant: ordinary relevance rounds pause, new claims receive no initial relevance score and cannot enter the main feed (which requires a finalized relevance round and an adopted score for the current revision), and assessed current revisions retain their own last adopted relevance scores but receive no ordinary refreshes; an unassessed amended revision cannot inherit a prior score; contested appeals can still produce a new score under Flow F-bis, subject to its remaining open implementation terms. Ranking among existing scored claims continues to shift as confidence accrues, but the feed becomes increasingly stale as new content is excluded and relevance scores age. Without funded appeals, existing rankings drift on confidence alone without relevance recalibration. The protocol's competitive pool selection hypothesis (see Relevance Round State Model) also depends on funded competitors existing; if no pool in a given topic domain is funded, there is no competitive alternative for users to migrate toward.

The current design accepts this as a limitation. Ordinary-round funding intentionally avoids token inflation, mandatory protocol fees or automated treasury management because each introduces governance surfaces that conflict with the design ordering `NoNeedForGovernance > GoodGovernance`. Whether exogenous sponsorship can sustain a pool long-term is an open empirical question. Possible external funding models (advertising revenue sharing, subscription access, grant funding, or interface-operator subsidies) exist but are outside the protocol's scope and have not been analyzed for incentive compatibility with the curation mechanism.

### Flow H: Withdrawal, Historical Persistence, And No TTL

Truth Post claims do not expire by protocol TTL.

Default rules:

- a claim remains active as long as its author bond remains locked and there is no terminal accuracy ruling
- withdrawal is the only ordinary author-controlled path from active history into inactive history
- amendments are allowed only when there is no active or queued accuracy challenge; a pending relevance appeal alone does not bar an otherwise permitted amendment
- when an author initiates an amendment, the claim enters `PendingEdit`, current confidence pauses, and the claim leaves the main feed
- when the amendment finalizes, the same claim id points to new content CIDs, revision history is preserved, confidence resets to zero, and the new revision awaits its own relevance assessment. An existing appeal continues against its original revision under Flow F-bis
- when an author initiates withdrawal, the claim enters `WithdrawPending` for the pool cooldown
- if no challenge arrives during the cooldown, the bond is returned and the claim becomes `Withdrawn`
- `Withdrawn` claims remain visible in historical interfaces
- completed withdrawal applies the paper’s common terminal-exit appeal rule under Flow F-bis; it preserves an already-funded contested chain or cancels still-open initial funding without a funded contest, after respecting any existing logical finality. The request and cooldown alone do not trigger this rule, and appeal finality is not a new condition for completing an otherwise eligible withdrawal. A qualifying ordinary attempt drawn before completion may finish and open its normal first appeal chain under Flow F-bis; this does not restore the item or relock the returned bond
- the accumulated confidence score remains frozen at its last value after withdrawal
- `Withdrawn` claims do not return to the main active feed unless a later protocol version explicitly introduces rebonding

The initial complete build SHOULD use withdrawal-based persistence rather than TTL-based expiry or protocol-level exponential confidence decay.

### Flow I: Interface Consumption And Ranking

The default Truth Post interface has three views:

- `Main Feed`
- `Under Dispute`
- `Archive`

Default inclusion rules:

- `Main Feed`
  - include only claims with `operationalState = Live`
  - require `adjudicationOutcome in {Unchallenged, ChallengeFailed}`
  - require at least one finalized relevance round for `currentRevision` and a non-null adopted `relevanceScore` for that revision
- `Under Dispute`
  - include claims with `operationalState = Challenged`
- `Archive`
  - include claims with `operationalState in {Withdrawn, Closed}`
  - interfaces SHOULD surface `Debunked` claims with the winning challenge reason, including `NonFalsifiable` where applicable
  - interfaces SHOULD distinguish `adjudicationSource = Timeout` (debunked by forfeiture) from `adjudicationSource = DDR` (debunked on merits) so readers can assess outcome provenance

A revision without its own adopted relevance score MUST remain accessible through direct links or pool-level pending views, but MUST NOT enter score-dependent ranking or receive new score-dependent funding. It MUST NOT inherit any older revision's score, including as a labeled provisional proxy, or receive a synthetic score. An absent score and an adopted score of 0.00 are distinct. The main-feed formula below applies only after the current revision meets the score and ordinary eligibility conditions; it MUST NOT coerce an absent score to zero. Admission uses the existing score-adoption rules and does not impose an additional chain-finality wait. Pre-edit accrued beneficiary funding follows the preservation rule in Flow F-bis, including its existing holdbacks and accuracy-challenge conditions. This does not fund the new revision or alter the older revision's appeal settlement.

Default main-feed score:

```text
feedScore = relevanceScore * confidencePercentile
```

No separate recency multiplier is applied because timeliness belongs inside relevance policy rather than protocol expiry.

## Reputation Models

### Author Reputation Model

Author reputation is pool-scoped and non-transferable.

Author reputation acts as a standing non-monetary bond for publishers. It is not separately escrowed per claim. Instead, any claim that is later `Debunked` can trigger a large slash against the author's current pool-scoped reputation balance.

Update rule:

- every 30-day epoch applies the pool's configured slow decay; suggested default is `1%`
- a final DDR ruling of `ChallengeFailed` adds `pool.authorChallengeFailedRepReward`; suggested default is `+1`
- a final DDR ruling of `Debunked` applies `pool.authorBustSlashBps`; suggested default is `50%`

No sensitivity analysis has been conducted on the decay, reward, or slash parameters. These values should be treated as initial calibration targets; see Parameter Status And Calibration Limits above.

Rules:

- author reputation is not portable across pools
- author reputation is not directly withdrawable
- author reputation does not replace the monetary author bond; it is an additional downside layer
- author reputation MAY be shown in interfaces as publisher credibility context, but MUST NOT bypass challengeability or dispute resolution
- a reputation reward or slash caused by one claim MUST NOT change the `confidenceIntegral`, `confidenceAccrualState`, or `relevanceScore` of any other claim by the same author; other claims continue under their own bond-time history unchanged

## Security Requirements And Invariants

The complete implementation MUST satisfy these invariants:

- one active challenge at most per claim, with optional queued challenges behind it
- at most one ordinary relevance round per claim and pool MAY be scheduled or running, across revisions; admission and its budget reservation MUST be atomic under Flow F
- new ordinary relevance rounds MUST obey the appeal hold and full-cadence resumption rule in Flow F; its appeal jury and rounds for other claims remain permitted
- every challenge MUST name an explicit challenged proposition in natural language
- claim policy versions are immutable after posting
- author bond cannot become negative
- author reputation cannot become negative
- challenger counter-stake cannot become negative
- pool reward budgets cannot become negative
- confidence is monotone while active, paused during dispute/withdraw cooldown, terminated on terminal exit
- withdrawn claims MUST remain queryable as historical records with their last finalized confidence value
- author reputation balances are pool-scoped and non-transferable
- only locked tokens MAY determine vote weight and ordinary relevance-round slash exposure (coherence and non-participation); the pre-reveal leak penalty may additionally draw from unlocked utility-token deposits, but MUST exclude collateral locked for other active rounds
- a revealed relevance score must match its commitment hash
- every relevance round and ruling MUST identify its assessed revision; subsequent edits MUST NOT retarget a round or appeal chain, erase its revision history or apply its judgment to a different revision
- a confirmed pre-reveal leak MUST apply the utility-token penalty capped by the paper's eligible current balance, protect other active-round collateral, transfer actual confiscated tokens and redirect any normal earned ETH fee without increasing the total fee or paying it twice
- no amendment may start while a claim has an active or queued accuracy challenge; relevance appeals remain pinned and continue through otherwise permitted amendments
- main-feed inclusion MUST require non-terminal adjudication status, a finalized relevance round for the current revision and its non-null adopted relevance score; no historical-score proxy may substitute for them
- claims that are `Debunked` MUST never return to active feeds
- pool creation MUST be permissionless
- pool parameters and policy references MUST be immutable after creation
- every challenge MUST record the claim's `currentRevision`, `claimManifestCid`, and `authorBondWei` at filing time
- reserved round reward floor MUST be deducted from the pool budget at scheduling time and released only on finalization or cancellation
- queued challenge tax MUST NOT credit to the pool budget before challenge activation
- bond adjustments MUST NOT take effect while an active or queued challenge exists
- a `PendingEdit` claim MUST remain challengeable on its last finalized revision

## Failure Handling

### Non-Falsifiability

- items that fail to instantiate a falsifiable proposition MUST be challengeable with `reasonType = NonFalsifiable`
- a successful `NonFalsifiable` challenge yields the final adjudication outcome `Debunked`

### Scope Violation

- items that do not belong in the pool's declared topic domain MUST be challengeable with `reasonType = ScopeViolation`
- a successful `ScopeViolation` challenge yields the final adjudication outcome `Debunked`
- `ScopeViolation` covers topic mismatch only; template non-conformance is handled by `TemplateViolation`

### Template Violation

- items that pass on-chain structural checks but fail the pool's `ClaimTemplate` semantic requirements (missing required fields, wrong source class, etc.) MUST be challengeable with `reasonType = TemplateViolation`
- a successful `TemplateViolation` challenge yields the final adjudication outcome `Debunked`
- on-chain structural validation (non-empty CIDs, correct version pointers) is enforced at submission time; `TemplateViolation` addresses semantic template rules that can only be evaluated off-chain

### Low Participation

- if no eligible backed seat can be drawn, the round is cancelled without slashing and the assessed revision remains unscored unless it already had its own relevance score; fewer than five curator accounts does not itself prevent a round
- if valid reveals cover less than 80% of a completed draft's original weight, the round is cancelled, drafted curators who failed to commit or reveal are penalized as non-participants, and the same assessed revision keeps its previous relevance score, without assigning it to newer content; coverage and the denominator use original drawn weights before penalties
- if a pool has no meaningful reward budget, new ordinary relevance rounds pause until it is replenished; contested appeals retain the common-pot fee-funding path in Flow F-bis

### Collusion

- use commit-reveal
- use drafted curators, not self-selected per-claim curators
- escalation: a larger appeal committee may reduce a coalition's overrepresentation from a lucky draw when it broadens independent participation; any improvement in collusion resistance also depends on public funding participation and the appeal settlement rules, and has not been established by the single-round collusion sweeps
- an independent recipient of a leaked intended vote can defect by precommitting the leaked payload and proving it within the existing window to receive actual confiscated utility tokens plus the violator’s normal earned ETH fee; this does not detect tacit coordination (e.g., "we all vote 0.9"), off-chain agreements without vote exchange, or disciplined collusion where no party defects

A leaker and cooperating reporter, including two addresses controlled by one actor, can retain their combined confiscated utility tokens and diverted ETH fee, apart from transaction costs. The rule changes ownership between those addresses without establishing a net coalition penalty; it therefore MUST NOT be presented as proven coalition deterrence. No new identity exclusion is imposed. The protected-collateral cap prevents this leak transfer from releasing backing locked for another active round. It does not make transfers between a cooperating leaker and reporter an economic loss to their coalition. The enforceable token penalty may be smaller than the requested multiplier when the eligible balance is low. The fixed post-reveal proof window removes the finalizer’s ability to shrink proof acceptance by issuing early. Its duration follows the paper's provisional default; cryptographic proof validity, inclusion and processing liveness still need analysis. Delayed completion cannot admit late proofs. ETH fees remain immediately withdrawable at actual issuance after the full proof period, with qualifying recipient overrides already applied.

### Whale Concentration

- escalation: apply the conditional appeal defense in Flow F-bis; a stake minority is not by itself sufficient to ensure that an appeal is filed or succeeds
- competitive exit: rely on the conditional pool-selection hypothesis in the Relevance Round State Model; deterrence additionally requires that the attacker's loss in capital value exceed the benefit of capture, which is not guaranteed for an independently valued staking asset or an externally motivated attacker
- keep reputation decaying and pool-scoped
- keep confidence linear in bonded stake-time, but rely on relevance gating so large bonds do not automatically dominate the main feed

Per-identity weight caps were removed as security theater: Sybil adversaries bypass them by creating cheap identities. The proposed defenses against whale concentration are escalation, graduated slashing, and the conditional competitive-exit mechanism described above.

**Sybil attack cost analysis.** Creating additional Ethereum addresses is costless. The real Sybil deterrent is `pool.seatSizeWei` (L): each identity must hold at least `L` deposited tokens to be eligible for drafting (`d_i = floor(s_i / L) >= 1`). Eligibility does not guarantee drafting; the protocol uses VRF stake-weighted randomness from the full eligible set, so an attacker whose total stake is a small fraction of the pool's eligible stake will have most identities go undrafted. Even when drafted, minimum-stake identities in a well-capitalized pool carry negligible effective weight relative to high-stake honest curators.

The Sybil threat is therefore most acute in low-liquidity pools where attacker stake dominates the eligible set. In such pools, the attacker's identities are likely to be drafted and to represent a large share of effective weight. The seat size `L` sets a per-identity eligibility floor, but the effective defense depends on the pool's total honest-stake depth, the coalition's strategy and the viability of appeals, not on `L` alone; the main paper's simulation-derived collusion range is not a general security threshold.

This reveals a tension between permissionless participation and Sybil resistance. A low `L` makes curation accessible but makes Sybil eligibility cheap. A high `L` raises the eligibility floor but restricts participation to well-capitalized curators. Neither value alone resolves the tension without external identity verification or a sufficiently deep honest-stake pool that dilutes the attacker's draft probability.

Pools that cannot rely on a sufficiently deep honest-stake pool to dilute attackers SHOULD consider identity verification (proof-of-personhood, allowlisted credentials, or equivalent) as a mitigation. Pools that operate without identity verification SHOULD acknowledge that the draw-and-lock model provides proportional influence (more stake, more seats, more weight and more risk) but offers no defense against an adversary willing to split stake across multiple addresses beyond the aggregate economic deterrence of escalation and graduated slashing.

### Cold Start

- a new pool creator SHOULD fund the initial reward budget before expecting curator participation
- a new pool MAY remain outside the canonical main surfaces until enough budget and curator activity exists to produce live relevance rounds

### Challenge-Based Suppression

- a claim leaves the main feed when challenged, before merits resolution
- the challenge tax and counter-stake create an economic cost for frivolous challenges
- sequential queued challenges can extend suppression; the 24-hour cancellation window limits but does not eliminate this
- interfaces MAY choose to show challenged claims in a prominent `Under Dispute` view to mitigate suppression impact
- the design accepts this tradeoff: removing challenged claims from the main feed is the price of making the accuracy signal conservative

**Quantitative deterrence conditions.** The economic deterrent against frivolous challenges depends on the challenger losing their counter-stake when a merits-resolved challenge fails (the normal payout rule splits it between the author and pool budget). This deterrent does not apply to timeout `ChallengeFailed` outcomes, where the counter-stake is refunded in full (see Timeout And Fallback). The paper's E1 simulation characterizes the economics under stated assumptions: at juror accuracy p=0.80, jury size N=5, and stake-to-bounty ratio S/B=0.25, a legitimate challenger's expected value is approximately +0.87 times the bounty. Applying the same payout model in reverse (the challenger files against a true claim and expects to lose), the derived frivolous-challenge expected value is approximately -0.24 times the bounty. The asymmetry is notable: the frivolous-challenge penalty is much smaller than the legitimate-challenge reward, because the counter-stake (0.25B) is much smaller than the bounty (B). The frivolous-challenge penalty is real but modest relative to the legitimate-challenge reward.

Conditional on having identified a false claim, legitimate challenges remain profitable across a wide range of juror accuracy: even at p=0.60, net expected value is approximately +0.55 times the bounty, and at p=0.50, approximately +0.32 times the bounty (all figures include tax and DDR fees on the same basis as the +0.87x figure). These figures do not include the search cost of finding a false claim; the paper's Claim 2 analyzes the full search-and-challenge economics separately. The mechanism's economic viability degrades gradually with juror accuracy rather than collapsing at a sharp threshold.

The deterrent fails under specific conditions:

- **Low juror accuracy**: at the E1 default parameters (S/B=0.25, tax=0.5%, DDR fee=0.05B), frivolous challenges become profitable below approximately p=0.644 per juror. At p=0.60, frivolous-challenge EV is approximately +0.09B: the attacker profits from filing challenges they expect to lose because the jury is unreliable enough that they win often enough to compensate for the counter-stake loss. This is the most fundamental failure mode: the deterrent depends on the DDR producing correct outcomes with sufficient reliability.
- **High DDR fees relative to counter-stake**: higher arbitration fees reduce the expected return of both frivolous and legitimate challenges. They can deter frivolous challenges at the expense of viable factual correction; sufficiently high fees make both kinds unprofitable.
- **High-value suppression targets**: for claims whose removal from the main feed creates value exceeding the expected counter-stake loss (e.g., politically sensitive claims, market-moving information), the suppression cost may be acceptable to a well-funded adversary. The asymmetry between legitimate-challenge reward and frivolous-challenge penalty means suppression is cheaper than one might expect from the +0.87x figure alone.
- **Serial suppression economics**: for unsuccessful merits-resolved cycles, the cost to suppress one claim for the duration of DDR resolution is `counter-stake + challenge tax + DDR fee`. For a claim with a 0.1 ETH bond: counter-stake is 0.025 ETH (at S/B=0.25), challenge tax is 0.0005 ETH (at 0.5%), and the DDR fee is external and variable. The non-DDR cost floor is approximately 0.026 ETH per unsuccessful merits-resolved cycle. If the DDR times out with `ChallengeFailed`, the counter-stake is refunded (see Timeout And Fallback), reducing the effective suppression cost to just `challenge tax + DDR fee`. Sequential queued challenges can extend suppression at the applicable marginal cost per cycle, and the 24-hour cancellation window between cycles is the only pause.

The protocol does not attempt to eliminate suppression attacks entirely. The claim is that the cost structure makes sustained suppression expensive relative to the value of most claims. Whether this holds in practice depends on the distribution of claim values and adversary budgets, which cannot be determined analytically.

### Indexer Or Gateway Failure

- the protocol record remains canonical on-chain
- interfaces MUST degrade to claim-detail pages from chain + content manifest even if ranked feeds fail

## Operational Requirements

The complete Truth Post deployment is not considered production-ready unless all of the following are true:

- at least 2 independent indexers are live
- at least 2 independent IPFS-capable gateways are configured in the canonical frontend
- every claim manifest is pinned by at least 2 operators
- a read-only fallback client can reconstruct claim pages from chain data plus content manifests
- pool dashboards expose indexer health, gateway health, and block freshness

The canonical frontend MUST remain readable when:

- the preferred gateway fails
- one indexer fails
- the connected wallet is absent

The app MAY disable authoring and staking without a wallet, but MUST NOT disable public read access because a wallet extension is missing.

## On-Chain Module Layout

The first complete implementation SHOULD use the following contract/module split:

- `PoolRegistry`
  - pool creation, policy hashes, immutable parameter storage, optional deprecation/successor hints
- `ClaimRegistry`
  - claim creation, revisions, state, bond accounting, confidence integral
- `ChallengeManager`
  - challenge queueing, tax routing, counter-stake accounting, DDR dispute hooks
- `RelevanceEngine`
  - curator drafting, utility-token draw-and-lock seat allocation, commit-reveal, graduated slashing, distance-slash redistribution, separate ETH service-fee accounting, relevance-round escalation (appeals)
- `ReputationLedger`
  - author reputation balances, rewards, slashes, and decay
- `PoolBudgetLedger`
  - pool-local reward budgets, challenge tax routing, top-ups, reward-floor debits

These MAY be merged for gas efficiency or deployment simplicity, but the logical boundary MUST remain intact.

The initial complete build MUST use immutable contracts. Protocol changes MUST require new contract deployments and explicit migration by users and interfaces rather than in-place upgrades.

## DDR Integration Specification

The initial complete build assumes Kleros v1 as the external DDR provider. The `ChallengeManager` contract MUST implement the `IArbitrable` interface.

This blueprint does not model the market cost of capturing the external DDR token or the economics of community forking after capture. Claims about capture resistance therefore remain conditional on provider-specific liquidity, circulating float, and attacker budget, and MUST NOT be treated as protocol-level guarantees.

### Required Adapter Interface

The `ChallengeManager` MUST:

- call `IArbitrator.createDispute(numberOfRulings, extraData)` when activating a challenge, with `numberOfRulings = 2` (`ChallengeFailed` or `Debunked`)
- implement `rule(uint _disputeID, uint _ruling)` callback from the arbitrator to receive final rulings
- emit `Evidence(Arbitrator, disputeId, party, evidenceURI)` for each evidence submission
- emit `Dispute(Arbitrator, disputeId, metaEvidenceID, evidenceGroupID)` when a dispute is created
- store `metaEvidenceID` referencing the pool's evidence policy

### Phase Synchronization

The protocol MUST mirror the external dispute phase on-chain. Phase transitions are driven by the arbitrator's callbacks or by reading arbitrator state.

### Timeout And Fallback

If the external DDR does not return a ruling within `pool.ddrTimeoutSeconds` (suggested default: 365 days / 31,536,000 seconds), the protocol MUST allow either party to trigger a timeout resolution:

- if only the author has paid their share, the challenge is treated as `ChallengeFailed`
- if only the challenger has paid their share, the challenge is treated as `Debunked` with `adjudicationSource = Timeout`
- if neither or both have paid, the challenge is treated as `ChallengeFailed` and the challenger's counter-stake is refunded

All timeout resolutions MUST set `adjudicationSource = Timeout`, not `DDR`. Timeout resolutions MUST NOT apply the normal challenger-loss payout rule (80/20 split). The counter-stake is refunded in full for timeout `ChallengeFailed` outcomes. Author bond remains locked. Challenge tax remains in the pool budget.

Design note (debunked by forfeiture): the "only challenger paid" timeout path produces a `Debunked` outcome driven by fee-payment asymmetry, not by merits adjudication. The protocol labels this outcome `adjudicationSource = Timeout` so that interfaces, historical records, and downstream consumers can distinguish forfeiture from a merits-adjudicated debunking. The economic consequences (bond slash, reputation slash, feed removal) are identical to merits-Debunked: the claim is terminal.

The rationale is that an author who fails to fund their defense within the timeout period has effectively abandoned the claim. The design treats non-participation as forfeiture rather than acquittal.

This is a deliberate tradeoff with known risks:

- **False-positive debunking**: an author may fail to pay for reasons unrelated to claim accuracy (key loss, jurisdictional internet restrictions, personal emergency, or simply missing the deadline during a 365-day window). The protocol cannot distinguish genuine abandonment from involuntary absence.
- **Adversarial exploitation**: an attacker can challenge a claim by a temporarily unavailable author and obtain a Debunked ruling without any evidence evaluation.
- **365-day assumption**: the suggested default assumes one year is sufficient for any motivated author to respond. This is long relative to most dispute processes but may be inadequate for authors in prolonged adverse conditions.

The alternative (letting abandoned challenged claims remain in limbo indefinitely) is worse: it locks the challenger's counter-stake permanently, removes any deadline pressure on the author, and leaves the claim in a contested-but-unresolved state that interfaces cannot meaningfully present. Forfeiture is the least-bad resolution for claims whose authors have genuinely disappeared.

Interfaces SHOULD label forfeiture outcomes distinctly (e.g., "debunked by forfeiture" or "author did not respond") so readers can assess the provenance of the outcome.

### Appeal Handling

Appeal funding follows the DDR provider's native crowdfunding mechanism. Any address MAY fund either side. The protocol MUST NOT add its own appeal layer on top of the DDR's appeal mechanics.

The accuracy layer does not implement an internal appeal ladder; accuracy appeals are handled entirely by the external DDR's native appeal and crowdfunding mechanics. The relevance layer specifies an internal publicly crowdfunded appeal mechanism (see Flow F-bis: Relevance-Round Escalation), which is separate from and independent of DDR appeals.

## Migration And Version Coexistence

Immutability means deployments coexist. It does not mean old state disappears.

Default migration semantics:

- old contracts remain canonical and queryable for the claims, stakes, disputes, and reputation they already contain
- new deployments handle new claims, new curator stake, new challenge activity, and new reward budgets
- nothing is portable by default: claims, curator stake, and reputation remain attached to their original deployment
- interfaces aggregate across versions and SHOULD label deployment/version clearly
- if an old deployment is deprecated because of a bug or design flaw, interfaces MAY stop routing new activity there while still preserving read access to historical records

## Relationship To The Foundational Paper

The foundational paper owns the shared accuracy and relevance rules. This blueprint specializes them for news: continuous bonded publication, confidence accumulation, and the default feed formula `relevanceScore * confidencePercentile`. The 2023 deployment remains a separate historical implementation, not an alternative authority for the current mechanism.

Both documents separate utility-token staking and penalty redistribution from fixed ETH service fees and ETH appeal settlement. The single-asset analytical example and simulations examine their stated models; they do not validate the complete two-asset proposal. Shared rules, including revision pinning and earned-fee preservation, should be interpreted from the foundational paper rather than independently maintained here. The blueprint's reference news parameters are provisional and do not close the implementation questions in Flow F-bis.

## Open Questions

- What effort, coordination, concentration, token-value and appeal deviations remain profitable with fixed ETH fees for timely valid reveals and separate utility-token redistribution? The former dispersion-based ETH reward-padding example cannot increase the fixed fee for the same valid revealers and original drawn seats, but this does not establish informative reporting or a truthful equilibrium. Complete the remaining settlement rules before evaluating the revised incentives, tracked in [issue #141](https://github.com/0xferit/manuscript-decentralized-curation/issues/141).
- Can the proof validity checks, inclusion and processing be implemented with reliable liveness under the paper's provisional proof-duration default? The paper’s fixed exclusive deadline applies regardless of early readiness or delayed completion; timely proofs must be processed before issuance or drafted quorum-failure cancellation, and a bare precommit creates no extension or later claim.
- Whether the external DDR should remain Kleros v1 indefinitely or later be replaced by a custom adapter-compatible court or a newer Kleros version.
- Whether future interfaces should expose additional feed formulas beyond `relevanceScore * confidencePercentile`.
- Exact percentile algorithm, active-set definition, and tie handling for cross-indexer consistency in `confidencePercentile` computation.
- Whether linear, non-decaying confidence accumulation creates an unacceptable long-run entrenchment effect for older claims, and if so what bounded or alternative weighting scheme would preserve exposure-to-challenge semantics without freezing newcomer competition.
