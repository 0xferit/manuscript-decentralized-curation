Status: end-state design blueprint. This document describes the **complete Truth Post system that should exist**, not the 2023 MVP that was partially deployed.

Normative language: **MUST**, **SHOULD**, and **MAY** are used in their usual engineering sense.

## Purpose

Truth Post is a trust-minimized news-curation protocol that separates **accuracy** from **relevance** and makes both outputs contestable.

The protocol curates **claims**, not vague posts. Interfaces may render those claims as article pages, feeds, newsletters, or dashboards, but the canonical protocol unit is always one bonded, content-addressed claim blob.

The complete system exists to solve three failures that the original Truth Post MVP did not solve:

- the MVP could punish false claims, but could not surface what matters
- the MVP had a trust/confidence metric, but no standing curator layer
- the MVP depended too heavily on a single frontend and off-chain dependencies

This blueprint fixes those gaps by specifying the full end-state protocol, including:

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

This blueprint defines one default pool profile for the initial complete Truth Post deployment. Other pools may change parameters, but this profile is the reference implementation target.

There is no protocol-level minimum author bond in the initial complete build. Authors may post claims with very small bonds. The consequence is not rejection, but weak economic weight: such claims accumulate confidence slowly and are less likely to matter in ranking or attract challenge attention.

Challenge tax is a pool-configurable parameter, not a single global constant. The suggested starting default for the reference news deployment is `0.5%` of the author bond.

| Parameter | Default |
|---|---|
| Domain | General news, subdivided into topic pools |
| Author withdrawal cooldown | 7 days |
| Claim lifetime | Infinite while bonded; historical after withdrawal |
| Challenger counter-stake | `max(0.0125 ETH, 25% of author bond)` |
| Challenge tax | Variable; suggested default `0.5%` of author bond |
| Relevance round target size | 15 drafted curators |
| Minimum reveal quorum | 5 curators |
| Relevance cadence | Variable; suggested default one round per week while claim is live |
| Relevance coherence threshold `K` | 1.25 |
| Seat size `L` | Pool-configurable; `L > 0`, measured in smallest on-chain token unit |
| Dispersion floor `epsilon_sigma` | 0.02 |
| Minimum reward fraction `rho` | Pool-configurable; `rho in [0, 1]` |
| Pre-reveal leak slash multiplier | Variable; suggested default `3x` locked tokens (`w_i`); capped at deposited balance |
| Appeal window (`appealWindowSeconds`) | Suggested default 7 days (604,800 seconds) after round finalization |
| Sigma-ref window size | Suggested default 50 rounds; `sigma_ref = epsilon_sigma` until populated |
| Author reputation decay | Variable; suggested default `1%` per 30-day epoch |
| Author busted-publication slash | Variable; suggested default `50%` of current author reputation |
| Author successful-defense reward | Variable; suggested default `+1` reputation unit |
| Appeal stake | Pool-configurable; separate from drafting eligibility |
| Appeal mean-difference threshold | Pool-configurable |
| Maximum escalation depth | Pool-configurable |
| Round reward floor | 0.01 ETH equivalent from pool reward budget |
| Protocol grace period | 7 days (604,800 seconds) |

### Parameter Status And Calibration Limits

These defaults are reference-deployment starting points, not empirically validated optima. The table above exists so an initial Truth Post news pool can be implemented and analyzed end to end. It should not be read as claiming that the listed values have already passed formal calibration or joint sensitivity analysis.

The parameter families also have different justification levels. Challenge-friction parameters such as the counter-stake, challenge tax, and failed-challenge payout split are partially grounded by the later deterrence arithmetic in this blueprint: under the stated assumptions, raising challenger cost improves frivolous-challenge deterrence but also makes legitimate correction harder, while lowering challenger cost does the reverse. That supports only directional claims under those assumptions. It does not identify a robust optimum across heterogeneous claim values, bond sizes, or DDR fee regimes.

Relevance-game parameters such as coherence threshold `K`, seat size `L`, dispersion floor `epsilon_sigma`, minimum reward fraction `rho`, the leak multiplier, appeal stake, appeal threshold, maximum escalation depth, and the round reward floor are currently calibration placeholders. Their intended role is clear: values that are too low weaken discipline against incoherent, concentrated, or low-effort curation, while values that are too high risk curator non-participation, excessive round cancellation, or overly conservative scoring. The blueprint does not yet provide a formal equilibrium analysis or simulation sweep for this parameter family.

Reputation parameters such as decay, successful-defense reward, and bust slash are likewise placeholders for how much long-run publisher history should matter relative to single-claim outcomes. If set too low, reputation becomes mostly cosmetic; if set too high, a small number of outcomes can dominate future participation. Their interaction with posting frequency, pool migration, and heterogeneous author quality remains unvalidated.

Accordingly, the strongest justified claim at present is narrow: these are coherent starting defaults for a reference Truth Post news pool, sufficient to specify an implementable mechanism and to support the later illustrative calculations, but not sufficient to claim robustness or optimality. Before treating them as validated economics, the design still needs at least three kinds of sensitivity work: one-at-a-time sweeps for the challenge, relevance, and reputation parameter families; joint sweeps for coupled parameters such as counter-stake/tax/payout split, `K`/`L`/`epsilon_sigma`/`rho`/appeal parameters, and reputation decay/reward/slash size; and adversarial tests covering suppression, low-participation rounds, escalation dynamics, and stake concentration.

## System Overview

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
- `seatSizeWei` (L; the fixed token amount locked per drawn seat)
- `relevanceRoundTargetSize`
- `minRevealQuorum`
- `relevanceCadenceSeconds`
- `coherenceK`
- `epsilonSigma` (dispersion floor)
- `rho` (minimum reward fraction for zero-dispersion rounds)
- `preRevealLeakSlashMultiplier`
- `appealStakeWei`
- `appealMeanDiffThreshold`
- `maxEscalationDepth`
- `authorReputationDecayBpsPerEpoch`
- `authorReputationDecayEpochSeconds`
- `authorBustSlashBps`
- `authorChallengeFailedRepReward`
- `roundRewardFloorWei`
- `protocolGracePeriodSeconds`
- `ddrTimeoutSeconds`
- `ddrProviderId`
- `successorPoolId` (nullable)
- `createdBy`
- `createdAt`

Authority:

- created permissionlessly by any address
- immutable after creation, except for discovery metadata: the creator MAY mark the pool `Deprecated` or publish a successor reference for interface discovery

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
- `relevanceScore` (nullable)
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
- `depositedWei` (total deposited balance)
- `lockedWei` (tokens locked in active rounds; not withdrawable)
- `appealExposureWei` (tokens reserved against pending appeal windows; not withdrawable)
- `status` (`Pending`, `Active`, `Exited`)
- `joinedAt`
- `lastSlashedAt`

Authority:

- created by curator
- state transitions by protocol

Storage plane:

- on-chain

### RelevanceRound

Purpose: compute a pool-local relevance score via draw-and-lock staking, graduated slashing, and smooth reward scaling.

Required fields:

- `roundId`
- `poolId`
- `claimId`
- `snapshotBlock`
- `targetRoundSize`
- `actualDraftSize`
- `minRevealQuorum`
- `draftedCurators`
- `commitClosesAt`
- `revealClosesAt`
- `finalizedAt`
- `revealedScores`
- `effectiveWeights`
- `meanScore`
- `stdDev`
- `epsilonSigma`
- `sigmaRef`
- `rewardFactor`
- `slashingSkipped` (boolean; true when sigma < epsilonSigma)
- `coherentCurators`
- `preRevealLeakReports`
- `relevanceScore`
- `slashSummary`
- `rewardSummary`
- `reservedRoundRewardWei`
- `status`

Authority:

- created by protocol scheduler
- finalized by protocol after reveal window

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

Purpose: track reward funding for one pool.

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
- curator deposits, locks, and appeal exposure
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
  - trigger: author initiates amendment with no active or queued challenge
  - side effect: confidence pauses and claim leaves the main feed
- `PendingEdit -> Live`
  - trigger: author finalizes new revision
  - side effect: current CID pointers update, revision history updates, confidence resets to zero, `adjudicationOutcome = Unchallenged`, and a fresh relevance round is queued subject to pool funding
  - design note: the claim's previous relevance score remains in effect until a new relevance round produces a replacement; because confidence resets to zero, `feedScore` will be near zero regardless, so the old relevance score preserves main-feed eligibility (not placement) during the transition period
- `PendingEdit -> Challenged`
  - trigger: challenge filed targeting the last finalized revision
  - side effect: edit finalization is blocked, confidence remains paused, `preChallengeOperationalState = PendingEdit`
- `Live -> WithdrawPending`
  - trigger: author initiates withdrawal with no active or queued challenge
- `WithdrawPending -> Withdrawn`
  - trigger: cooldown ends with no challenge
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

A claim with `operationalState = Closed` and `adjudicationOutcome = Debunked` is terminal for feed purposes and remains queryable historically. Interfaces SHOULD distinguish `adjudicationSource = Timeout` (debunked by forfeiture) from `adjudicationSource = DDR` (debunked on merits).

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

- `Scheduled`
- `CommitOpen`
- `RevealOpen`
- `Scoring`
- `Finalized`
- `Cancelled`

`Cancelled` is allowed whenever a round cannot safely produce a relevance score. In that case:

- If the eligible curator set is smaller than `minRevealQuorum`, the round is cancelled before drafting, nobody is slashed, and the claim keeps its previous relevance score if one exists.
- If the round is drafted but revealed participation ends below `minRevealQuorum`, drafted curators who failed to commit or reveal MUST be slashed as non-participants, but no curator reward MUST be paid and no new relevance score MUST be produced. Non-participation slashes from such a cancelled round MUST be credited to the pool reward budget. Pre-reveal leak slashes, if any, MUST still be paid to the reporter per the leak-report payout rules and MUST NOT be redirected to the pool budget. A replacement round is scheduled at the next cadence.
- Low-dispersion rounds are no longer cancelled as degenerate. Instead, rewards scale smoothly with sigma. Let `R` denote the base round reward, `rho` the minimum reward fraction, `epsilon_sigma` the dispersion floor, and `sigma_ref = max(epsilon_sigma, median(sigma over rolling window of recent rounds))`. The reward factor is `f_reward = rho + (1 - rho) * min(1, sigma / sigma_ref)`. At `sigma = 0` the reward is `rho * R` (minimum); at `sigma >= sigma_ref` the full `R` is paid; between them the transition is linear. When `sigma < epsilon_sigma`, graduated slashing is skipped (`p_i = 0` for all curators, all locked tokens returned from finalization), but the weighted mean is still accepted as a valid relevance score. Released tokens remain slashable during the appeal window: withdrawals during the appeal window are allowed only to the extent that they do not reduce the deposited balance below the curator's outstanding appeal exposure. If a subsequent appeal succeeds, the protocol debits the slash from that reserved balance; if no appeal is filed before the window closes, the reserve is removed and the balance becomes fully withdrawable. Design note: smooth reward scaling eliminates the cliff that degenerate-round cancellation created. A step function that switched from zero to full rewards at a fixed cutoff would incentivize curators to inject artificial variance to cross the threshold, producing systematic bias. The smooth curve removes that discontinuity. More broadly, the coherence mechanism assumes that a pool's relevance policy is specific enough to anchor curator signals near a defensible ground truth. If all curators share the same bias, they will converge on a wrong answer and be rewarded. The hypothesized defense is competitive pool selection: if biased curation produces bad feeds, users migrate to better pools, and the biased pool loses relevance. The protocol does not prevent bad curation within a pool; the design intention is that bad curation remains pool-local rather than protocol-global. The additional defense is escalation: a dissenting minority that believes the first-round score is wrong can appeal, and if the appeal committee agrees with the minority, the original majority is slashed (see Flow F-bis: Relevance-Round Escalation).

This hypothesis has not been empirically validated. Several well-documented dynamics in platform economics could prevent pool competition from functioning as described:

- **Information asymmetry**: users cannot easily evaluate curation quality without independently verifying claims, which defeats the purpose of the protocol. Biased curation produces outputs that look normal to users who share the bias, making quality differences difficult to observe.
- **Network effects**: the first pool with sufficient curators and content may dominate regardless of quality, because authors go where curators are and curators go where claims are. This winner-take-most dynamic is common in two-sided platforms and does not require the winning pool to be the highest-quality one.
- **Switching costs**: curators who have tokens locked in active rounds or reserved against pending appeal windows cannot withdraw immediately; authors who have accumulated confidence on claims in one pool lose that history if they repost in another. These frictions slow migration even when quality differences are recognized.
- **Coordination failure**: migration requires multiple actors (curators, authors, sponsors) to move roughly simultaneously for a new pool to be viable. Individual exit does not automatically solve this collective action problem (see the analogous analysis of pool migration friction in the RPGF design document).

Competitive pool selection should therefore be read as a conditional hypothesis, not as an intrinsic correction mechanism. It can discipline within-pool bias only if users can observe persistent quality differences, at least one funded alternative pool for the same domain exists, and authors, curators, and sponsors can coordinate migration before incumbency and network effects entrench the biased pool. If those conditions do not hold, the coherence game remains a consensus mechanism without an internal path from consensus to correctness.

Empirical signals that would indicate whether pool competition is functioning: measurable user migration from pools with demonstrably biased feeds, successful bootstrapping of competing pools in the same topic domain, and declining curator participation in pools whose feeds diverge from verifiable ground truth. Until these signals are observed, the protocol should be understood as relying on an untested market mechanism for its primary defense against within-pool bias.

## Curator Stake State Model

- `Pending`
- `Active`
- `Exited`

Transitions:

- `Pending -> Active` after stake finalization
- `Active -> Exited` when curator requests exit and no tokens are locked in unresolved rounds or reserved against pending appeal windows
- `Active -> Active` after slash/reward events, deposit top-ups, or partial withdrawals of unlocked balance

There is no separate `Slashed` state. Slashing is an accounting event against an active stake. There is no curator exit cooldown: curators may withdraw any tokens that are not locked in active rounds and not reserved against pending appeal windows at any time.

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
2. The interface lints the manifest against the pool template.
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

Posting a claim does not require pre-existing author reputation. But once the claim is live, the author's pool-scoped reputation is exposed to downside if the claim is later `Debunked`.

Claims that fail template linting MUST NOT be postable through the canonical frontend. Contracts MUST enforce minimal structural field presence: non-empty `articleBodyCid`, `claimManifestCid`, and `initialEvidenceCids`; valid `claimTemplateVersion` and `evidencePolicyVersion` matching the pool's current versions. Semantic template validation (field content quality, source class conformance, falsifiability) remains an interface-layer concern and is enforceable post-publication via `TemplateViolation` challenges.

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
   - `Debunked`: claim moves to `Closed`, author bond is slashed (using `bondAtChallengeOpenWei`), current author reputation in that pool is reduced by `pool.authorBustSlashBps`, and all queued challenges are refunded in full
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
  - challenger counter-stake is split between author reward and pool reward budget at a pool-configurable ratio (suggested default: 80% author / 20% pool)
  - DDR fee is not refunded by Truth Post

The counter-stake split ratio is a pool-configurable parameter. The suggested 80/20 default is a starting point. No sensitivity analysis has been conducted on this ratio; see Parameter Status And Calibration Limits above for the current epistemic status of this default.

### Flow E: Draw-And-Lock Staking And Curator Eligibility

1. A curator deposits tokens into a pool contract. Let `s_i` denote curator `i`’s deposited balance, with both `s_i` and the seat size `L` (`pool.seatSizeWei`) measured in the token’s smallest on-chain unit.
2. The curator’s stake becomes `Active` after confirmation.
3. Only curators with `s_i >= L` are eligible for drafting. The draft weight is the integer number of full seat-tickets the curator holds: `d_i = floor(s_i / L)`.
4. When drafted, each drawn ticket locks `L` tokens from the curator’s deposited balance. Let `n_i` denote the number of seats drawn for curator `i`. The curator’s round weight is `w_i = n_i * L`. Locked tokens are simultaneously the curator’s influence on the weighted mean and their maximum loss.
5. The unlocked remainder (`s_i - n_i * L`) stays in the pool contract but is not at risk in that round and is withdrawable, subject to appeal-window reserves (see Flow F-bis).
6. Each curator submits one score weighted by `w_i`. Multiple seats increase the curator’s weight on that single score, not the number of independent votes.
7. A curator MAY withdraw any tokens that are not locked in active rounds and not reserved against pending appeal windows at any time. There is no exit cooldown.
8. A curator MAY exit fully when no tokens are locked and no appeal-window reserves remain.

Important clarification:

- draw-and-lock staking belongs only to the internal relevance layer
- authors still bond claims individually
- challengers still challenge claims individually
- external DDR jurors still resolve accuracy disputes independently of curator pools

### Flow F: Relevance Curation And Coherence Game

1. Every newly live claim gets an initial relevance round immediately after posting if the pool reward budget can fund it.
2. Every `Live` claim gets a new relevance round at the pool's configured cadence while the claim remains bonded and not withdrawn. The suggested default for the reference news deployment is one round per week. `Claim` MUST include `nextRelevanceRoundAt`. When multiple claims in the same pool are simultaneously due for scheduling, the protocol MUST process them in ascending `(nextRelevanceRoundAt, claimId)` order.
3. If the pool reward budget cannot cover the configured round reward floor, no new round is scheduled and the claim keeps its previous relevance score if one exists. When a round enters `Scheduled`, the protocol MUST reserve `pool.roundRewardFloorWei` from the pool reward budget immediately. Reserved reward floor MUST be unavailable to later rounds, MUST be released if the round is cancelled, and MUST be paid only when the round finalizes. A round MUST NOT enter `CommitOpen` unless its reward floor is reserved in full.
4. The scheduler snapshots the eligible curator set for the claim's pool.
5. Let:

```text
target = pool.relevanceRoundTargetSize
quorum = pool.minRevealQuorum
n = min(target, eligibleCuratorCount)
```

6. If `n < quorum`, the round is cancelled as underpopulated:
   - no new relevance score is produced
   - any previous relevance score remains in force
   - claims with no prior finalized relevance round remain out of the default main feed
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

Locked tokens are simultaneously the curator’s influence on the weighted mean and their maximum loss. The unlocked remainder (`s_i - n_i * L`) stays in the pool contract but is not at risk in this round and is withdrawable (subject to appeal-window reserves). A curator MUST NOT be finalized as drafted unless `availableDepositedWei_i >= w_i = n_i * L` at the time seats are locked; if this condition fails (e.g., a withdrawal between snapshot and drafting reduced the balance), the protocol MUST discard that curator’s unfunded seats and continue drawing replacement seats using the same round seed until all `n` seats are fully backed or the round is cancelled. Only `w_i` MAY determine vote weight or slash exposure for that round.

9. Each drafted curator commits a single relevance score in `[0,1]`, weighted by `w_i`. Multiple seats increase the curator’s weight on that single score, not the number of independent votes.
10. Each drafted curator reveals the score.
11. If the number of valid reveals is below `quorum`, the round is cancelled:
   - drafted curators who failed to commit or reveal are slashed as non-participants (graduated slashing applies using a penalty fraction of 1, i.e., total loss of locked tokens)
   - any previous relevance score remains in force
   - if the claim has no previous finalized relevance round, it remains unscored for feed purposes
   - a replacement round is scheduled at the next cadence
12. Otherwise, the protocol computes weighted mean and standard deviation. For a round with valid reveal set `V`, let `W = sum(w_i for i in V)`. If no curators reveal (`W = 0`), the round is cancelled: no score is produced, the claim retains its previous relevance score if one exists, and all locked tokens are returned. Otherwise the protocol MUST compute:

```text
mu = sum(w_i * v_i for i in V) / W
sigma = sqrt(sum(w_i * (v_i - mu)^2 for i in V) / W)
```

`mu` and `sigma` MUST be computed over valid reveals only.

13. Round rewards scale linearly with `sigma` rather than switching at a threshold. Let `epsilon_sigma = pool.epsilonSigma` denote the dispersion floor, and define the reference dispersion level:

```text
sigma_ref = max(epsilon_sigma, median(sigma over rolling window of recent rounds))
```

The rolling window length is a pool parameter (`pool.sigmaRefWindowSize`, suggested default: 50 rounds). Until the window is populated (fewer historical rounds than the window size), `sigma_ref = epsilon_sigma`. This preserves adaptation without governance while guaranteeing `sigma_ref > 0` even during sustained consensus or at bootstrap. Let `R` denote the base round reward drawn from the pool’s reward budget, and `rho = pool.rho` the minimum reward fraction for zero-dispersion rounds. The reward factor is:

```text
f_reward = rho + (1 - rho) * min(1, sigma / sigma_ref)
```

At `sigma = 0` the reward is `rho * R` (minimum). At `sigma >= sigma_ref` the reward is full `R`. Between them the transition is linear.

14. Slashing guard: if `sigma < epsilon_sigma`, graduated slashing is skipped (`p_i = 0` for all curators, `delta_i = 0`), and all locked tokens are released from finalization. The mean is still accepted as a valid relevance score. Released tokens remain slashable during the appeal window: withdrawals during the appeal window are allowed only to the extent that they do not reduce the deposited balance below the curator’s outstanding appeal exposure.

15. If `sigma >= epsilon_sigma`, graduated slashing applies. Let `v_i` denote curator `i`’s revealed score and `K = pool.coherenceK` the coherence-threshold multiplier. Curators inside the coherence band (`abs(v_i - mu) <= K * sigma`) are not penalized. Curators outside the band lose a fraction of their locked tokens that scales linearly with distance:

```text
p_i = min(1, max(0, (abs(v_i - mu) / sigma - K) / K))
```

At the band boundary the penalty is zero; at twice the boundary distance (`2 * K * sigma` from the mean) the penalty is total loss of locked tokens. Since `w_i` is measured in smallest on-chain units (integers), the slashed amount is rounded down:

```text
delta_i = floor(p_i * w_i)
q_i = w_i - delta_i
```

The protocol slashes `delta_i` tokens and returns the remainder `q_i`. This graduated slashing replaces binary slashing: near-boundary deviations incur small losses, while extreme deviations incur total loss.

16. Each coherent curator (those with `p_i = 0`) MUST receive `(w_i / sum(w_j for j in coherent)) * (sum(delta_j) + f_reward * R)`. If the coherent set is empty (all curators slashed), the slashed tokens and the round reward remain in the pool budget; no curator receives a payout. The pool MUST enforce `K > 0` and `epsilon_sigma > 0` to prevent degenerate parameter configurations that could produce an empty coherent set under normal conditions.
17. Pre-reveal leak reporting remains open until round finalization.
18. A reporter who receives a leaked intended vote MAY precommit `hash(leakedPayload)` before reveal closes.
19. After reveal, the reporter MAY open the payload.
20. A leak report is valid only if the opened payload proves that a drafted curator disclosed their vote before their on-chain reveal and the payload later matches the curator’s actual reveal and commitment for that round.
21. If a valid leak report is confirmed, the guilty curator is slashed. For every drafted curator `i`, define `baseLeakSlashWei_i = w_i` (total locked tokens for that curator) regardless of whether curator `i` is later coherent or incoherent. A confirmed pre-reveal leak by curator `i` MUST trigger:

```text
preRevealLeakSlashWei_i = min(pool.preRevealLeakSlashMultiplier * baseLeakSlashWei_i, availableDepositedWei_i)
```

The leak penalty may exceed the curator's locked tokens (`w_i`) and is drawn from the curator's full deposited balance. It is capped at `availableDepositedWei_i` (the deposited balance minus any other outstanding lock obligations) to prevent the protocol from slashing more than the curator holds. The successful reporter MUST receive the full `preRevealLeakSlashWei_i`. If multiple valid reports exist for the same leak, the earliest valid precommit MUST win. `preRevealLeakSlashWei_i` MUST NOT be added to the coherent-curator reward pool.

22. This penalty is in addition to any graduated slashing that already applies in the same round.
23. The claim’s `relevanceScore` becomes `mu`.
24. The round finalizes. An appeal window opens (see Flow F-bis).

Non-participation rules:

- failure to commit or reveal counts as maximum-penalty incoherence (`p_i = 1`, total loss of locked tokens)
- repeated non-participation beyond 3 missed rounds in 30 days SHOULD auto-exit the curator

Pre-reveal leak rules:

- a drafted curator MUST NOT disclose their intended vote or reveal preimage before their own on-chain reveal
- successful collusion requires revealing the intended vote to at least one other participant
- any recipient of that leak can defect by precommitting the leaked payload and later opening it for a slash reward
- only cryptographically verifiable reports that match the curator’s later reveal and commitment count
- a confirmed leak triggers an additional slash equal to `pool.preRevealLeakSlashMultiplier` times the curator’s locked tokens for that round

### Flow F-bis: Relevance-Round Escalation (Appeals)

1. Any curator with a deposited balance in the pool MAY appeal a finalized relevance round by posting an appeal stake (`pool.appealStakeWei`). A curator with `s_i < L` who cannot be drafted MAY still appeal. The appeal MUST be filed within `pool.appealWindowSeconds` (suggested default: 7 days) after round finalization.
2. The appeal triggers a new round with a larger drafted committee at higher stakes. The appeal committee independently scores the same claim under the same pool relevance policy.
3. If the appeal committee’s weighted mean differs from the original round’s mean by more than `pool.appealMeanDiffThreshold`, the appeal succeeds: the appeal score replaces the original, and original-round curators whose scores were closer to the overturned mean than to the appeal mean are slashed via the same graduated slashing formula applied against the appeal committee’s mean.
4. If the difference is within the threshold, the appeal fails and the appellant’s stake is slashed.
5. Multiple escalation rounds MAY occur, each with a larger committee and higher cost, up to `pool.maxEscalationDepth`.
6. The threat of appeal is the primary disciplining force: first-round curators converge on "what would survive appeal by a larger committee" rather than "what the current committee will vote." Under continuous-signal assumptions (unbiased, independent, finite-variance signals), the appeal-round mean concentrates more tightly around the latent relevance target as the number of distinct drafted curators grows. Additional seats assigned to the same curator do not create new independent observations; the defense is effective when escalation increases independent participation.
7. Escalation replaces per-identity weight caps as the defense against whale manipulation: a dishonest whale who dominates round 1 by locking many seats faces proportionally larger losses on appeal when the appeal round broadens independent participation enough to reduce the weighted mean’s variance and overturn the original score. This defense is effective when the whale is a stake minority; a majority-stake whale dominates any committee size. The residual defense is economic rather than mechanical: distorting a pool’s output degrades its utility and the attacker’s locked capital with it, which deters profit-seeking attackers but not externally motivated ones.

### Flow G: Rewards, Slashing, And Withdrawals

#### Authors

- earn no direct protocol reward by default
- benefit by keeping bond intact and accumulating confidence
- may later withdraw after cooldown if claim remains live

#### Challengers

- profit when they correctly debunk or flag non-falsifiable claims
- lose counter-stake when they challenge incorrectly

#### Curators

- earn rewards only when drafted and coherent
- do not earn passive yield merely for sitting in a pool

#### Pool Reward Budget

Each pool has its own reward budget. This is not a discretionary governance treasury.

Pool reward budgets receive:

- challenge tax paid by challengers at challenge activation (not at filing for queued challenges)
- 20% of failed challenger counter-stake
- direct top-ups from the pool creator, sponsors, or any third party

Pool reward budgets pay:

- round reward floors

Rules:

- the pool creator SHOULD seed the initial reward budget to bootstrap curator participation
- any address MAY replenish a pool reward budget
- a peaceful pool SHOULD assume round rewards are primarily sponsor-funded rather than financed by failed challenges
- if the budget cannot cover the configured round reward floor, new relevance rounds pause until the pool is funded again
- no protocol mechanism creates a sponsorship incentive; pool economics depend on external actors (pool creators, sponsors, or third parties) voluntarily funding the reward budget; if funding does not materialize, the relevance layer pauses but the accuracy layer remains fully functional; this is a critical bootstrapping dependency

**Sustainability and the free-rider problem.** The relevance layer exhibits a classic public-goods free-rider problem: curated feeds benefit all readers, but only sponsors bear the cost. Rational sponsors have an incentive to let others fund the pool while still consuming its outputs. A well-functioning pool with few challenges generates negligible self-funding because challenge-tax and failed-challenge inflows are inherently tied to dispute volume: a peaceful pool (the desired outcome) produces the least endogenous revenue.

When funding dries up, the degradation is partial but significant: relevance rounds pause, new claims receive no relevance score and cannot enter the main feed (which requires at least one finalized relevance round for inclusion), and existing claims retain their last finalized relevance scores but receive no refreshes. Ranking among existing scored claims continues to shift as confidence accrues, but the feed becomes increasingly stale as new content is excluded and relevance scores age. The user-facing product degrades toward an accuracy dispute system where existing rankings drift on confidence alone without relevance recalibration. The protocol's competitive pool selection hypothesis (see Relevance Round State Model) also depends on funded competitors existing; if no pool in a given topic domain is funded, there is no competitive alternative for users to migrate toward.

The current design accepts this as a limitation. The protocol intentionally avoids endogenous funding mechanisms (token inflation, mandatory protocol fees, or automated treasury management) because each introduces governance surfaces that conflict with the design ordering `NoNeedForGovernance > GoodGovernance`. Whether exogenous sponsorship can sustain a pool long-term is an open empirical question. Possible external funding models (advertising revenue sharing, subscription access, grant funding, or interface-operator subsidies) exist but are outside the protocol's scope and have not been analyzed for incentive compatibility with the curation mechanism.

### Flow H: Withdrawal, Historical Persistence, And No TTL

Truth Post claims do not expire by protocol TTL.

Default rules:

- a claim remains active as long as its author bond remains locked and there is no terminal accuracy ruling
- withdrawal is the only ordinary author-controlled path from active history into inactive history
- amendments are allowed only when there is no active or queued challenge
- when an author initiates an amendment, the claim enters `PendingEdit`, current confidence pauses, and the claim leaves the main feed
- when the amendment finalizes, the same claim id points to new content CIDs, revision history is preserved, and confidence resets to zero
- when an author initiates withdrawal, the claim enters `WithdrawPending` for the pool cooldown
- if no challenge arrives during the cooldown, the bond is returned and the claim becomes `Withdrawn`
- `Withdrawn` claims remain visible in historical interfaces
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
  - require at least one finalized relevance round
- `Under Dispute`
  - include claims with `operationalState = Challenged`
- `Archive`
  - include claims with `operationalState in {Withdrawn, Closed}`
  - interfaces SHOULD surface `Debunked` claims with the winning challenge reason, including `NonFalsifiable` where applicable
  - interfaces SHOULD distinguish `adjudicationSource = Timeout` (debunked by forfeiture) from `adjudicationSource = DDR` (debunked on merits) so readers can assess outcome provenance

Claims with no finalized relevance round MAY still be reachable through direct links or pool-level pending views, but they MUST NOT be given synthetic relevance scores.

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
- every challenge MUST name an explicit challenged proposition in natural language
- claim policy versions are immutable after posting
- author bond cannot become negative
- author reputation cannot become negative
- challenger counter-stake cannot become negative
- pool reward budgets cannot become negative
- confidence is monotone while active, paused during dispute/withdraw cooldown, terminated on terminal exit
- withdrawn claims MUST remain queryable as historical records with their last finalized confidence value
- author reputation balances are pool-scoped and non-transferable
- only locked tokens MAY determine vote weight or slash exposure inside a relevance round
- a revealed relevance score must match its commitment hash
- a confirmed pre-reveal leak MUST trigger an additional slash equal to `pool.preRevealLeakSlashMultiplier * lockedTokensForThatRound`
- no amendment may start while a claim has an active or queued challenge
- main-feed inclusion MUST require non-terminal adjudication status and at least one finalized relevance round
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

- if a pool has fewer eligible curators than `minRevealQuorum`, the round is cancelled without slashing and the claim remains unscored unless it already had a previous relevance score
- if a drafted round does not get enough reveals, the round is cancelled, drafted curators who failed to commit or reveal are penalized as incoherent participants, and the claim keeps its previous relevance score
- if a pool has no meaningful reward budget, new relevance rounds pause until it is replenished

### Collusion

- use commit-reveal
- use drafted curators, not self-selected per-claim curators
- escalation: a coordinated coalition that shifts the mean in round 1 faces a larger appeal committee where sampling variance is reduced, making overrepresentation from lucky draws less likely and the committee mean more reflective of the pool's true stake-weighted distribution; the effective collusion threshold phi* rises because a colluding bloc must survive not only the current round but also a potential appeal round with a larger committee
- destabilize collusion modes that require explicit pre-reveal vote disclosure: any recipient of a leaked intended vote can defect by precommitting the leaked payload and later reporting it for a multiplicative slash; this does not detect tacit coordination (e.g., "we all vote 0.9"), off-chain agreements without vote exchange, or disciplined collusion where no party defects

### Whale Concentration

- escalation: a dishonest whale who dominates round 1 by locking many seats faces proportionally larger losses on appeal when the appeal round broadens independent participation enough to reduce the weighted mean's variance and overturn the original score; this defense is effective when the whale is a stake minority
- economic self-destruction: a majority-stake whale that distorts a pool's curation output degrades the pool's utility, driving users and curators to competing pools and reducing the value of the attacker's locked position; this argument holds for profit-seeking attackers whose locked capital exceeds the external value of capturing the pool but does not hold for externally motivated attackers (state actors, competitors) who treat the stake as an operational expense
- keep reputation decaying and pool-scoped
- keep confidence linear in bonded stake-time, but rely on relevance gating so large bonds do not automatically dominate the main feed

Per-identity weight caps were removed as security theater: Sybil adversaries bypass them by creating cheap identities. The defense against whale concentration is the combination of escalation, graduated slashing, and economic self-destruction described above.

**Sybil attack cost analysis.** Creating additional Ethereum addresses is costless. The real Sybil deterrent is `pool.seatSizeWei` (L): each identity must hold at least `L` deposited tokens to be eligible for drafting (`d_i = floor(s_i / L) >= 1`). Eligibility does not guarantee drafting; the protocol uses VRF stake-weighted randomness from the full eligible set, so an attacker whose total stake is a small fraction of the pool's eligible stake will have most identities go undrafted. Even when drafted, minimum-stake identities in a well-capitalized pool carry negligible effective weight relative to high-stake honest curators.

The Sybil threat is therefore most acute in low-liquidity pools where attacker stake dominates the eligible set. In such pools, the attacker's identities are likely to be drafted and to represent a large share of effective weight. The seat size `L` sets a per-identity eligibility floor, but the effective defense depends on the pool's total honest-stake depth, the aggregate collusion threshold phi*, and the threat of escalation, not on `L` alone.

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

**Quantitative deterrence conditions.** The economic deterrent against frivolous challenges depends on the challenger losing their counter-stake when a merits-resolved challenge fails (the normal payout rule transfers the counter-stake to the author). This deterrent does not apply to timeout `ChallengeFailed` outcomes, where the counter-stake is refunded in full (see Timeout And Fallback). The paper's E1 simulation characterizes the economics under stated assumptions: at juror accuracy p=0.80, jury size N=5, and stake-to-bounty ratio S/B=0.25, a legitimate challenger's expected value is approximately +0.87 times the bounty. Applying the same payout model in reverse (the challenger files against a true claim and expects to lose), the derived frivolous-challenge expected value is approximately -0.24 times the bounty. The asymmetry is notable: the frivolous-challenge penalty is much smaller than the legitimate-challenge reward, because the counter-stake (0.25B) is much smaller than the bounty (B). The frivolous-challenge penalty is real but modest relative to the legitimate-challenge reward.

Conditional on having identified a false claim, legitimate challenges remain profitable across a wide range of juror accuracy: even at p=0.60, net expected value is approximately +0.55 times the bounty, and at p=0.50, approximately +0.32 times the bounty (all figures include tax and DDR fees on the same basis as the +0.87x figure). These figures do not include the search cost of finding a false claim; the paper's Proposition 2 analyzes the full search-and-challenge economics separately. The mechanism's economic viability degrades gradually with juror accuracy rather than collapsing at a sharp threshold.

The deterrent fails under specific conditions:

- **Low juror accuracy**: at the E1 default parameters (S/B=0.25, tax=0.5%, DDR fee=0.05B), frivolous challenges become profitable below approximately p=0.644 per juror. At p=0.60, frivolous-challenge EV is approximately +0.09B: the attacker profits from filing challenges they expect to lose because the jury is unreliable enough that they win often enough to compensate for the counter-stake loss. This is the most fundamental failure mode: the deterrent depends on the DDR producing correct outcomes with sufficient reliability.
- **High DDR fees relative to counter-stake**: if arbitration fees dominate the challenger's cost structure, the counter-stake loss becomes a secondary concern and the deterrent weakens. At sufficiently high fees, both frivolous and legitimate challenges become unprofitable.
- **High-value suppression targets**: for claims whose removal from the main feed creates value exceeding the expected counter-stake loss (e.g., politically sensitive claims, market-moving information), the suppression cost may be acceptable to a well-funded adversary. The asymmetry between legitimate-challenge reward and frivolous-challenge penalty means suppression is cheaper than one might expect from the +0.87x figure alone.
- **Serial suppression economics**: for merits-resolved cycles, the cost to suppress one claim for the duration of DDR resolution is `counter-stake + challenge tax + DDR fee`. For a claim with a 0.1 ETH bond: counter-stake is 0.025 ETH (at S/B=0.25), challenge tax is 0.0005 ETH (at 0.5%), and the DDR fee is external and variable. The non-DDR cost floor is approximately 0.026 ETH per merits-resolved cycle. If the DDR times out with `ChallengeFailed`, the counter-stake is refunded (see Timeout And Fallback), reducing the effective suppression cost to just `challenge tax + DDR fee`. Sequential queued challenges can extend suppression at the applicable marginal cost per cycle, and the 24-hour cancellation window between cycles is the only pause.

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
  - curator drafting, draw-and-lock seat allocation, commit-reveal, graduated slashing, smooth reward scaling, relevance-round escalation (appeals)
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

The accuracy layer does not implement an internal appeal ladder; accuracy appeals are handled entirely by the external DDR's native appeal and crowdfunding mechanics. The relevance layer does implement an internal escalating-stakes appeal mechanism (see Flow F-bis: Relevance-Round Escalation), which is separate from and independent of DDR appeals.

## Migration And Version Coexistence

Immutability means deployments coexist. It does not mean old state disappears.

Default migration semantics:

- old contracts remain canonical and queryable for the claims, stakes, disputes, and reputation they already contain
- new deployments handle new claims, new curator stake, new challenge activity, and new reward budgets
- nothing is portable by default: claims, curator stake, and reputation remain attached to their original deployment
- interfaces aggregate across versions and SHOULD label deployment/version clearly
- if an old deployment is deprecated because of a bug or design flaw, interfaces MAY stop routing new activity there while still preserving read access to historical records

## Differences From Current Thesis Draft

The blueprint’s relevance-layer mechanism design now matches the paper: draw-and-lock staking, graduated slashing, smooth reward scaling, and relevance-round escalation are shared between both documents. The remaining differences are implementation-level specifics that the paper does not address:

- This blueprint keeps external DDR jurors fully separate from internal curators. The initial complete build does not reuse curator pools for accuracy adjudication.
- This blueprint treats a claim as a bonded, content-addressed blob that may contain multiple subclaims. Challenges target an explicit natural-language proposition inside that blob, and a successful challenge debunks the whole blob.
- This blueprint removes protocol TTL entirely. Claims remain active while bonded and remain historically visible as `Withdrawn` after bond removal.
- This blueprint makes main-feed inclusion stricter than the paper’s broad interface discussion: only `Live` claims with non-terminal adjudication status and a finalized relevance round appear in the default main feed.
- This blueprint makes pool creation permissionless and treats bad pools as a local failure to be filtered by interfaces rather than prevented by protocol governance.
- This blueprint prefers immutable contracts and explicit redeployment over upgradeable contracts.
- This blueprint adds author bond adjustment with a pool-scoped grace period.
- This blueprint makes `PendingEdit` claims challengeable on their last finalized revision.
- This blueprint replaces evidence bundles with flat per-item evidence aligned with Kleros v1’s native evidence model.
- This blueprint adds `TemplateViolation` as a fourth challenge reason for semantic template non-conformance.
- This blueprint pins challenges to the exact claim revision and bond at filing time.
- This blueprint includes a full DDR Integration Specification assuming Kleros v1 as the external provider.

## Open Questions

- Whether the external DDR should remain Kleros v1 indefinitely or later be replaced by a custom adapter-compatible court or a newer Kleros version.
- Whether future interfaces should expose additional feed formulas beyond `relevanceScore * confidencePercentile`.
- Exact percentile algorithm, active-set definition, and tie handling for cross-indexer consistency in `confidencePercentile` computation.
- Whether linear, non-decaying confidence accumulation creates an unacceptable long-run entrenchment effect for older claims, and if so what bounded or alternative weighting scheme would preserve exposure-to-challenge semantics without freezing newcomer competition.
