# Truth Post Complete Blueprint

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
| Relevance slash rate | 3% of active curator stake slice per failed round |
| Pre-reveal leak slash multiplier | Variable; suggested default `3x` incoherent slash |
| Author reputation decay | Variable; suggested default `1%` per 30-day epoch |
| Author busted-publication slash | Variable; suggested default `50%` of current author reputation |
| Author successful-defense reward | Variable; suggested default `+1` reputation unit |
| Curator reputation draft boost `alpha` | 0.25 |
| Curator reputation decay | 1% per 7-day epoch |
| Curator exit cooldown | 7 days |
| Flat-round std-dev epsilon | 0.02 |
| Per-identity effective weight cap | 10% of drafted round weight |
| Round reward floor | 0.01 ETH equivalent from pool reward budget |

## System Overview

Truth Post has two independent but connected outputs:

- **Adjudication output**: whether a claim is `Unchallenged`, `ChallengeFailed`, or `Debunked`
- **Relevance output**: how important the claim is for a specific pool right now, scored on `[0,1]`

These outputs come from different mechanisms:

- **Challenge adjudication** is resolved through challenge, evidence submission, and external decentralized dispute resolution.
- **Relevance** is resolved through an internal coherence game among drafted curators.

Truth Post does not declare claims universally true or false. It records challenge outcomes, evidence, confidence accumulation, and dispute history so readers can interpret the record for themselves.

Truth Post also maintains two separate reputation systems:

- **Author reputation**: a pool-scoped, slow-decaying credibility stock that acts as a standing non-monetary bond for publishers
- **Curator reputation**: a pool-scoped drafting signal used only for internal relevance rounds

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

## Actors

### Authors

Authors create claim blobs, upload evidence bundles, post author bonds, and may withdraw or amend claims.

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
- `curatorMinStakeWei`
- `relevanceRoundTargetSize`
- `minRevealQuorum`
- `relevanceCadenceSeconds`
- `coherenceK`
- `relevanceSlashBps`
- `preRevealLeakSlashMultiplier`
- `flatRoundStdDevMin`
- `authorReputationDecayBpsPerEpoch`
- `authorReputationDecayEpochSeconds`
- `authorBustSlashBps`
- `authorChallengeFailedRepReward`
- `curatorReputationDraftBoostAlpha`
- `curatorReputationDecayBpsPerEpoch`
- `curatorExitCooldownSeconds`
- `roundRewardFloorWei`
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
- `evidenceBundleCid`
- `revisionHistoryCid`
- `currentRevision`
- `authorBondWei`
- `operationalState`
- `adjudicationOutcome`
- `adjudicationSource`
- `confidenceIntegral`
- `lastConfidenceAccrualBlock`
- `confidenceAccrualState`
- `activeChallengeId`
- `queuedChallengeCount`
- `createdAtBlock`
- `updatedAtBlock`

Authority:

- created by author
- status changes by protocol actions

Storage plane:

- on-chain for ids, accounting, status, current CIDs, timestamps, version pointers
- content storage for manifest, article body, evidence bundle, revision history

### EvidenceBundle

Purpose: package evidence references and integrity commitments.

Required fields:

- `bundleId`
- `claimId`
- `items`
- `authorStatement`
- `submittedBy`
- `submittedAt`

Each evidence item MUST contain:

- `label`
- `sourceClass`
- `uriOrCid`
- `contentHash`
- `publishedAt`
- `retrievedAt`

Authority:

- authors or challengers submit bundles
- bundles are append-only

Storage plane:

- content storage
- on-chain by bundle hash and pointer

### Challenge

Purpose: open a formal accuracy dispute against a claim.

Required fields:

- `challengeId`
- `claimId`
- `challenger`
- `challengedProposition`
- `reasonType` (`Debunking`, `NonFalsifiable`, `ScopeViolation`)
- `counterEvidenceCid`
- `counterStakeWei`
- `challengeTaxWei`
- `arbitrationFeeWei`
- `queuePosition`
- `status` (`Queued`, `Active`, `Cancelled`, `Refunded`, `Finalized`)
- `queuedAt`
- `activatedAt`
- `cancellationWindowEndsAt`
- `linkedDisputeId`

Authority:

- created by challenger
- finalized by dispute outcome

Storage plane:

- on-chain for amounts, status, ids
- content storage for evidence bundle

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

Storage plane:

- on-chain for ids, phases, rulings, deadlines

### CuratorStake

Purpose: record a curator’s domain commitment and eligibility.

Required fields:

- `stakeId`
- `poolId`
- `curator`
- `amountWei`
- `lockedWei`
- `status` (`Pending`, `Active`, `Cooldown`, `Exited`)
- `cooldownEndsAt`
- `joinedAt`
- `lastSlashedAt`

Authority:

- created by curator
- state transitions by protocol

Storage plane:

- on-chain

### RelevanceRound

Purpose: compute a pool-local relevance score and slash incoherent curation.

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
- `flatRoundStdDevMin`
- `degeneracyReason`
- `coherentCurators`
- `preRevealLeakReports`
- `relevanceScore`
- `slashSummary`
- `rewardSummary`
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

### CuratorReputationBalance

Purpose: track topic-scoped, non-transferable curation performance.

Required fields:

- `poolId`
- `curator`
- `rep`
- `lastDecayEpoch`
- `lastUpdatedAt`

Authority:

- updated only by finalized relevance rounds and periodic decay

Storage plane:

- on-chain

### ConfidenceScore

Purpose: represent stake-at-risk over time for one claim.

Required fields:

- `claimId`
- `confidenceIntegral`
- `lastAccrualBlock`
- `accrualState` (`Active`, `Paused`, `Terminated`)
- `displayPercentile`

Authority:

- raw value is canonical protocol state
- display percentile is indexer/interface derived

Storage plane:

- raw state on-chain
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
- curator stakes and cooldowns
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
- evidence manifests
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
- `PendingEdit`: author is preparing a new revision, confidence paused, claim out of the main feed
- `WithdrawPending`: author initiated withdrawal cooldown, confidence paused, challenge still allowed
- `Challenged`: external dispute active, confidence paused
- `Closed`: final DDR outcome executed, historical only
- `Withdrawn`: author exited after cooldown

### Adjudication Outcome

- `Unchallenged`
- `ChallengeFailed`
- `Debunked`

`NonFalsifiable` remains a challenge reason, not a final adjudication label. A successful `NonFalsifiable` challenge yields the final outcome `Debunked`.

### Adjudication Source

- `None`
- `DDR`

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
- `Live -> WithdrawPending`
  - trigger: author initiates withdrawal with no active or queued challenge
- `WithdrawPending -> Withdrawn`
  - trigger: cooldown ends with no challenge
- `WithdrawPending -> Challenged`
  - trigger: challenge filed during cooldown
- `Challenged -> Live`
  - trigger: DDR final ruling is `ChallengeFailed` and no queued challenge remains
  - side effect: `adjudicationOutcome = ChallengeFailed`, `adjudicationSource = DDR`
- `Challenged -> Challenged`
  - trigger: DDR final ruling is `ChallengeFailed` and a queued challenge auto-activates after the cancellation window
  - side effect: active challenge id advances to the next queued challenge
- `Challenged -> Closed`
  - trigger: DDR final ruling is `Debunked`
  - side effect: `adjudicationOutcome = Debunked`, `adjudicationSource = DDR`, confidence terminates, queued challenges are refunded, and claim is removed from active feeds

A claim with `operationalState = Closed` and `adjudicationOutcome = Debunked` is terminal for feed purposes and remains queryable historically.

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
- If the round is drafted but revealed participation ends below `minRevealQuorum`, drafted curators who failed to commit or reveal are penalized as incoherent participants, the claim keeps its previous relevance score, and a replacement round is scheduled at the next cadence.
- If the round reaches reveal but `stdDev < pool.flatRoundStdDevMin`, the round is cancelled as degenerate, no relevance score update occurs, no round reward is paid, and no curator reputation reward is granted.

## Curator Stake State Model

- `Pending`
- `Active`
- `Cooldown`
- `Exited`

Transitions:

- `Pending -> Active` after stake finalization
- `Active -> Cooldown` when curator requests exit for stake that is not locked in unresolved rounds
- `Cooldown -> Exited` after cooldown and no unresolved slash obligations on the exiting slice
- `Active -> Active` after slash/reward events

There is no separate `Slashed` state. Slashing is an accounting event against an active stake.

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
- bad pool design should fail locally through non-use rather than through a protocol-level governance gate

### Flow B: Author Submission And Template Validation

1. The author drafts a claim manifest locally.
2. The interface lints the manifest against the pool template.
3. The author uploads:
   - claim manifest JSON
   - article body
   - evidence bundle
4. The author deposits the author bond.
5. The protocol stores current CIDs, version pointers, timestamps, revision metadata, and bond accounting on-chain.
6. The claim enters `Live`.
7. Confidence accrual starts immediately.
8. The scheduler queues the claim for its initial relevance round if the pool reward budget can fund it.

One claim blob MAY contain multiple subclaims. Truth Post does not require the author to decompose them into separate bonded on-chain units. Instead, any challenger must name the explicit natural-language proposition they are challenging inside the blob.

Posting a claim does not require pre-existing author reputation. But once the claim is live, the author's pool-scoped reputation is exposed to downside if the claim is later `Debunked`.

Claims that fail template linting MUST NOT be postable through the canonical frontend. Contracts MAY also enforce minimal field presence.

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
- confidence does not use protocol-level exponential decay in the initial complete build

Design note:

- linear bonded stake-time is intentional
- a large bond does not by itself buy main-feed dominance because main-feed ranking still multiplies confidence by curator-produced relevance

Display logic:

- indexers compute `confidencePercentile` within each active pool
- interfaces display both `C_raw` and percentile
- the default Truth Post frontend uses percentile in ranking and raw score in detail pages

### Flow D: Challenge, Dispute, Appeals, Finality

1. A challenger chooses a live claim.
2. The challenger submits:
   - `reasonType`
   - explicit natural-language `challengedProposition`
   - counter-evidence bundle
   - counter-stake `S = max(pool.minChallengeStake, 0.25 * authorBond)`
   - challenge tax `T = pool.challengeTaxBps * authorBond`
   - DDR arbitration fee
3. The challenge tax is paid by the challenger at filing and credited immediately to the challenged pool's reward budget.
4. If no challenge is active, the protocol:
   - pauses confidence
   - moves claim to `Challenged`
   - marks this challenge `Active`
   - opens a dispute through the DDR adapter
5. If another challenge is already active, the new challenge enters the FIFO queue with stake, tax, and DDR fee escrowed up front.
6. The filed `challengedProposition` MUST be a fair reading of the claim blob. That is part of what DDR evaluates.
7. The DDR adapter asks one binary question: should this filed challenge succeed under the stated `reasonType`, `challengedProposition`, pool policy, and submitted evidence?
8. The DDR process runs through evidence, voting, and possible appeals.
9. A queued challenger MAY cancel during the 24-hour cancellation window and recover their escrowed stake, tax, and DDR fee before activation.
10. Final ruling outcomes are interpreted as:
   - `ChallengeFailed`: if no queued challenge remains, the claim returns to `Live` and the author gains `pool.authorChallengeFailedRepReward`
   - `ChallengeFailed`: if a queued challenge remains, the next queued challenge auto-activates after a fixed 24-hour cancellation window
   - `Debunked`: claim moves to `Closed`, author bond is slashed, current author reputation in that pool is reduced by `pool.authorBustSlashBps`, and all queued challenges are refunded in full
11. `Debunked` covers any successful `Debunking`, `NonFalsifiable`, or `ScopeViolation` challenge.
12. Appeal funding is handled by DDR crowdfunding. The author, challenger, or any third party MAY fund either side in exchange for the underlying DDR-side reward logic. If the author's side is not funded, the author loses the appeal opportunity.

Default payout rule:

- if challenger wins:
  - challenger receives author bond
  - challenger receives their own counter-stake back
  - challenge tax remains in the pool reward budget
  - losing-side appeal reward logic is inherited from DDR
- if challenger loses:
  - author keeps author bond locked unless later withdrawn
  - 80% of challenger counter-stake is paid to author
  - 20% of challenger counter-stake is credited to the challenged pool reward budget
  - DDR fee is not refunded by Truth Post

### Flow E: Pooled Staking And Curator Eligibility

1. A curator stakes into one pool.
2. The curator’s stake becomes `Active` after confirmation.
3. While active, the curator becomes eligible for drafting into relevance rounds in that pool.
4. The protocol tracks which slice of the curator's active stake is locked in unresolved rounds.
5. A curator MAY request exit only for stake that is not currently locked.
6. The exiting amount enters `Cooldown` for `pool.curatorExitCooldownSeconds`; the suggested default for the reference news pool is 7 days.
7. During cooldown:
   - no new rounds may draft the exiting amount
   - unresolved slash liabilities still apply to any still-locked amount
8. After cooldown, the curator may withdraw the exiting amount.

Important clarification:

- pooled staking belongs only to the internal relevance layer
- authors still bond claims individually
- challengers still challenge claims individually
- external DDR jurors still resolve accuracy disputes independently of curator pools

### Flow F: Relevance Curation And Coherence Game

1. Every newly live claim gets an initial relevance round immediately after posting if the pool reward budget can fund it.
2. Every `Live` claim gets a new relevance round at the pool's configured cadence while the claim remains bonded and not withdrawn. The suggested default for the reference news deployment is one round per week.
3. If the pool reward budget cannot cover the configured round reward floor, no new round is scheduled and the claim keeps its previous relevance score if one exists.
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
7. Otherwise, the scheduler drafts `n` curators using VRF randomness. Drafting weight is:

```text
d_i = s_i + alpha * rep_i
```

where `alpha = pool.curatorReputationDraftBoostAlpha`.
8. Effective round weight is:

```text
w_i = min(s_i, 10% of total drafted round weight)
```

9. Each drafted curator commits a relevance score in `[0,1]`.
10. Each drafted curator reveals the score.
11. If the number of valid reveals is below `quorum`, the round is cancelled:
   - drafted curators who failed to commit or reveal are slashed at the same rate as incoherent participants
   - any previous relevance score remains in force
   - if the claim has no previous finalized relevance round, it remains unscored for feed purposes
   - a replacement round is scheduled at the next cadence
12. Otherwise, the protocol computes:
   - weighted mean `mu`
   - weighted standard deviation `sigma`
13. If `sigma < pool.flatRoundStdDevMin`, the round is cancelled as degenerate:
   - no new relevance score is produced
   - no round reward is paid
   - no curator reputation reward is granted
   - a replacement round is scheduled at the next cadence
14. Otherwise, a curator is coherent iff:

```text
abs(v_i - mu) <= K * sigma
```

with `K = 1.25` by default.

15. Incoherent curators lose 3% of the active stake slice used in that round.
16. Coherent curators share:
   - slashed stake from incoherent curators
   - the pool’s fixed round reward floor
17. Pre-reveal leak reporting remains open until round finalization.
18. A reporter who receives a leaked intended vote MAY precommit `hash(leakedPayload)` before reveal closes.
19. After reveal, the reporter MAY open the payload.
20. A leak report is valid only if the opened payload proves that a drafted curator disclosed their vote before their on-chain reveal and the payload later matches the curator's actual reveal and commitment for that round.
21. If a valid leak report is confirmed, the guilty curator is slashed by:

```text
preRevealLeakSlash = pool.preRevealLeakSlashMultiplier * incoherentSlashAmountForThatRound
```

22. This penalty is in addition to any incoherent-participation slash that already applies in the same round.
23. The claim’s `relevanceScore` becomes `mu`.
24. The round finalizes and updates reputation.

Non-participation rules:

- failure to commit or reveal counts as incoherent
- drafted curators who fail to commit or reveal are slashed at the same rate as incoherent participants for that round
- repeated non-participation beyond 3 missed rounds in 30 days SHOULD auto-start stake cooldown

Pre-reveal leak rules:

- a drafted curator MUST NOT disclose their intended vote or reveal preimage before their own on-chain reveal
- successful collusion requires revealing the intended vote to at least one other participant
- any recipient of that leak can defect by precommitting the leaked payload and later opening it for a slash reward
- only cryptographically verifiable reports that match the curator's later reveal and commitment count
- a confirmed leak triggers an additional slash equal to `pool.preRevealLeakSlashMultiplier` times the round's incoherent slash amount for that curator

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

- challenge tax paid by challengers at challenge filing
- 20% of failed challenger counter-stake
- direct top-ups from the pool creator, sponsors, or any third party

Pool reward budgets pay:

- round reward floors

Rules:

- the pool creator SHOULD seed the initial reward budget to bootstrap curator participation
- any address MAY replenish a pool reward budget
- a peaceful pool SHOULD assume round rewards are primarily sponsor-funded rather than financed by failed challenges
- if the budget cannot cover the configured round reward floor, new relevance rounds pause until the pool is funded again

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

Rules:

- author reputation is not portable across pools
- author reputation is not directly withdrawable
- author reputation does not replace the monetary author bond; it is an additional downside layer
- author reputation MAY be shown in interfaces as publisher credibility context, but MUST NOT bypass challengeability or dispute resolution

### Curator Reputation Model

Curator reputation is pool-scoped and non-transferable.

Curator reputation is not itself the bond. Stake is the bond. Curator reputation only biases drafting into rounds; once a curator is drafted, only slashable stake determines vote weight and penalties.

Update rule:

- each finalized coherent round adds `+1` reputation unit to the curator
- incoherent or absent participation adds nothing
- every 7-day epoch applies 1% decay to all pool-scoped curator reputation balances

Rules:

- curator reputation is not portable across pools
- curator reputation is not directly withdrawable
- curator reputation only affects drafting priority into internal relevance rounds
- curator reputation MUST NOT directly increase final vote weight inside a round unless a future version also makes the reputation component slashable
- curator reputation never affects accuracy juror selection in the external DDR

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
- author and curator reputation balances are pool-scoped and non-transferable
- no curator may exceed the per-identity round weight cap
- only slashable stake MAY determine final vote weight inside a relevance round
- a revealed relevance score must match its commitment hash
- a confirmed pre-reveal leak MUST trigger an additional slash equal to `pool.preRevealLeakSlashMultiplier * incoherentSlashAmountForThatRound`
- no amendment may start while a claim has an active or queued challenge
- main-feed inclusion MUST require non-terminal adjudication status and at least one finalized relevance round
- claims that are `Debunked` MUST never return to active feeds
- pool creation MUST be permissionless
- pool parameters and policy references MUST be immutable after creation

## Failure Handling

### Non-Falsifiability

- items that fail to instantiate a falsifiable proposition MUST be challengeable with `reasonType = NonFalsifiable`
- a successful `NonFalsifiable` challenge yields the final adjudication outcome `Debunked`

### Low Participation

- if a pool has fewer eligible curators than `minRevealQuorum`, the round is cancelled without slashing and the claim remains unscored unless it already had a previous relevance score
- if a drafted round does not get enough reveals, the round is cancelled, drafted curators who failed to commit or reveal are penalized as incoherent participants, and the claim keeps its previous relevance score
- if a pool has no meaningful reward budget, new relevance rounds pause until it is replenished

### Collusion

- use commit-reveal
- use drafted curators, not self-selected per-claim curators
- cap effective round weight per identity at 10%
- make collusion unstable by letting any recipient of a leaked intended vote precommit and later report it for a multiplicative slash tied to the round's incoherent-participation penalty

### Whale Concentration

- cap per-identity round weight
- keep reputation decaying and pool-scoped
- keep confidence linear in bonded stake-time, but rely on relevance gating so large bonds do not automatically dominate the main feed

### Cold Start

- a new pool creator SHOULD fund the initial reward budget before expecting curator participation
- a new pool MAY remain outside the canonical main surfaces until enough budget and curator activity exists to produce live relevance rounds

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
  - curator drafting, commit-reveal, degenerate-round detection, scoring, slashing, round rewards
- `ReputationLedger`
  - author and curator reputation balances, rewards, slashes, and decay
- `PoolBudgetLedger`
  - pool-local reward budgets, challenge tax routing, top-ups, reward-floor debits

These MAY be merged for gas efficiency or deployment simplicity, but the logical boundary MUST remain intact.

The initial complete build MUST use immutable contracts. Protocol changes MUST require new contract deployments and explicit migration by users and interfaces rather than in-place upgrades.

## Migration And Version Coexistence

Immutability means deployments coexist. It does not mean old state disappears.

Default migration semantics:

- old contracts remain canonical and queryable for the claims, stakes, disputes, and reputation they already contain
- new deployments handle new claims, new curator stake, new challenge activity, and new reward budgets
- nothing is portable by default: claims, curator stake, and reputation remain attached to their original deployment
- interfaces aggregate across versions and SHOULD label deployment/version clearly
- if an old deployment is deprecated because of a bug or design flaw, interfaces MAY stop routing new activity there while still preserving read access to historical records

## Differences From Current Thesis Draft

- This blueprint keeps external DDR jurors fully separate from internal curators. The initial complete build does not reuse curator pools for accuracy adjudication.
- This blueprint treats a claim as a bonded, content-addressed blob that may contain multiple subclaims. Challenges target an explicit natural-language proposition inside that blob, and a successful challenge debunks the whole blob.
- This blueprint removes protocol TTL entirely. Claims remain active while bonded and remain historically visible as `Withdrawn` after bond removal.
- This blueprint makes main-feed inclusion stricter than the paper’s broad interface discussion: only `Live` claims with non-terminal adjudication status and a finalized relevance round appear in the default main feed.
- This blueprint makes pool creation permissionless and treats bad pools as a local failure to be filtered by interfaces rather than prevented by protocol governance.
- This blueprint prefers immutable contracts and explicit redeployment over upgradeable contracts.

## Open Questions

- Whether the external DDR should remain Kleros indefinitely or later be replaced by a custom adapter-compatible court.
- Whether future interfaces should expose additional feed formulas beyond `relevanceScore * confidencePercentile`.
