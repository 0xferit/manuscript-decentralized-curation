# Retroactive Public Good Funding: A Curation Framework Instantiation

Status: working design document. Applies the decentralized curation framework from the thesis to retroactive public good funding (RPGF).

## Problem

Public good funding allocation is a curation problem disguised as a governance problem.

Existing RPGF systems fail at information verification:

- **Expert committees** (e.g., Optimism RPGF) are trusted, scarce, and opaque. A small group decides how millions of dollars are allocated. The bottleneck is not capital; it is the committee's ability to verify hundreds of impact claims.
- **Democratic voting** (e.g., Gitcoin Quadratic Funding) is a preference and attention aggregator, not a truth-verification mechanism. Popularity is a weak proxy for impact. The mechanism is susceptible to Sybil attacks and narrative capture.

Both systems suffer from the same upstream failure: they cannot make impact claims **legible**, **contestable**, and **comparable** at scale. Evaluators face information abundance (hundreds of project reports) and knowledge scarcity (no trustworthy way to verify which claims are real).

The thesis argument applies directly: **curation precedes coordination**. Fix the curation layer (evaluate impact claims) and the coordination layer (allocate funds) becomes a simple function of the curation output.

## Framework Application

### Step 1: Identify the hidden curation problem

RPGF allocation failures are usually described as governance failures: "the committee was biased," "the voting was gamed," "the wrong projects got funded." These are symptoms. The upstream cause is that impact claims are not structured, not contestable, and not independently verifiable.

### Step 2: Identify the relevant quality dimensions

Two dimensions dominate, the same structure as news:

- **Impact accuracy**: did the project deliver what it claims? Binary, global, challengeable. The claim is either substantiated or it is not.
- **Allocation relevance**: how important is this delivered impact for the funding pool's mission? Scalar, local, pool-dependent. A developer tool matters more to an "Ethereum infrastructure" pool than to a "climate action" pool.

Design principle: do not decompose quality further than your mechanisms can distinguish. Two mechanisms (challenge-based accuracy, coherence-based relevance) means two dimensions. Additional quality considerations (efficiency, novelty, team quality) belong inside the relevance policy as scoring criteria, not as separate protocol mechanisms.

### Step 3: Require falsifiability

Impact claims must be expressed as falsifiable assertions. This is harder than news because impact reports default to narrative. The **template** does the heavy lifting.

The relevant region on the falsifiability spectrum:

- **Falsifiable**: "Our tool was used by 500 developers in Q1 2026" (verifiable usage data)
- **Falsifiable**: "We deployed contract X at address Y on date Z" (on-chain evidence)
- **Not falsifiable**: "We improved the developer experience" (no measurable assertion)
- **Not falsifiable**: "This infrastructure prevented $2M in losses" (counterfactual; no observable test)

The template must reject the second category and force projects to express impact in the first category. Non-falsifiable claims are challengeable as `NonFalsifiable`, exactly as in news.

### Step 4: Design mechanisms dimension by dimension

The same two mechanisms as news carry over:

- **Accuracy**: bonded publication, open challenges, external DDR (Kleros v1). Verifies whether impact claims are true.
- **Relevance**: drafted curator coherence game under a public policy. Scores how important the verified impact is for the pool's mission.

Three domain-specific adaptations are required:

1. **Tighter templates**: impact report templates must require measurable outputs, evidence links (on-chain transactions, usage metrics, third-party attestations), and bounded time periods.
2. **Finer debunking granularity**: atomic impact claims are the challenge unit, not whole project reports. Debunking one claim does not debunk the others.
3. **Holdback bond model**: provisional allocation with a challenge window before final disbursement, instead of requiring large upfront bonds from capital-constrained projects.

## Claim Structure: Atomic Impact Claims

A project submits an **impact report** containing multiple **impact claims**. The bond is posted at the **report level**, not per claim. Each claim within the report is:

- A falsifiable assertion about a specific deliverable or output
- Independently challengeable on its own evidence
- Scored for relevance as part of the project's contribution to the pool

If one claim is debunked, the others survive. The project's funding allocation is computed over surviving claims only. Whole-report debunking is reserved for `TemplateViolation` (the report itself fails template requirements) or `NonFalsifiable` (the entire report lacks testable assertions).

Challenge queue semantics (FIFO ordering, 24-hour cancellation window, escrowed amounts until activation) are inherited from the Truth Post blueprint (see `truth-post-complete-blueprint.md`, Flow D: Challenge). At most one challenge is active per impact claim at any time; additional challenges enter the queue.

**Bond apportionment**: the report-level bond covers all claims in the report. When a single claim is debunked, the fraction of the bond at risk is proportional to the debunked claim's relevance score share within the report (using the frozen scoring snapshot): `claimBondAtRisk = reportBond * (claimRelevanceScore / sumOfClaimScoresInReport)`. When the entire report is debunked (via `TemplateViolation` or `NonFalsifiable`), the full report bond is forfeited.

This is a deliberate departure from the news instantiation, where whole-blob debunking is accepted because the proportionality tradeoff is less severe (removing a news article from a feed is less consequential than zeroing out a project's funding).

## Bond Model: Provisional Allocation With Holdback

Projects seeking retroactive funding are typically capital-constrained. Requiring large upfront bonds is circular.

Instead:

1. Projects submit impact reports with an **initial bond** of `pool.baseBondWei` (suggested default: 0.01 ETH). For first-time applicants with no reputation history, the bond floor SHOULD be higher.
2. The curation layer produces scores. The protocol computes a **scoring snapshot** (defined in the "Scoring snapshot" subsection below) that freezes all derived quantities simultaneously. The required bond per report is recalculated as `max(pool.baseBondWei, pool.bondProvisionalShareBps * provisionalAllocation / 10,000)` (suggested provisional-share rate: 5%). The protocol **automatically withholds** the required bond from each project's provisional allocation before the holdback period begins. No voluntary top-up step exists. This prevents selective top-up attacks where an author submits many reports at floor bond, observes scores, and tops up only the winners.
3. A **holdback period** (suggested default: 30 days) runs before final disbursement.
4. During holdback, challenges can be filed against any impact claim.
5. If a claim is debunked during holdback, the corresponding funding share is withheld and **redistributed pro rata** to surviving projects (proportional to each surviving project's score share in the frozen scoring snapshot). Redistribution is batched at holdback end, not after each individual debunking, to avoid cascading recalculations.
6. At holdback end, **uncontested shares** (claims with no active challenge) are disbursed. **Contested shares** (claims with an active, unresolved challenge) remain escrowed until DDR resolution or timeout. On resolution: if `ChallengeFailed`, the share is disbursed to the project; if `Debunked`, the share is redistributed pro rata to surviving projects. The successful challenger additionally receives the debunked project's forfeited bond (minus challenge tax and DDR fees), consistent with the framework's challenge payout model.
7. **Author reputation** is the primary long-term deterrent: debunked claims slash project reputation, reducing allocation in future funding rounds.

**Scoring snapshot**: at the end of the evaluation period, the protocol computes and freezes a single snapshot containing all derived quantities:

- `provisionalAllocation` per project
- `claimRelevanceScore` per claim
- `challengeCostBase` per claim (= claim's provisional share)
- `reportBondTarget` per report (= `max(pool.baseBondWei, pool.bondProvisionalShareBps * provisionalAllocation / 10,000)`)
- `claimBondAtRisk` per claim (= `reportBond * claimRelevanceScore / sumOfClaimScoresInReport`)

All challenge filings, bond withholding, and redistribution calculations MUST reference this frozen snapshot. No quantity is recomputed mid-holdback.

## Relevance Scoring and Attribution

Each impact claim receives an independent relevance score through the standard coherence game (same mechanism as news). Curators score claims one at a time, and the protocol normalizes across all eligible claims in the pool. Relevance round rewards are funded from the pool's curation budget, which SHOULD be reserved as a percentage of the pool's total funding budget before allocation scoring begins (suggested default: 5% of pool funding budget reserved for curation costs).

The pool's **relevance policy** defines the scoring question and rubric. Example:

> "Score each impact claim from 0.0 (no value to this pool) to 1.0 (critical contribution) based on: usage scale, downstream adoption, ecosystem dependency, cost efficiency, and uniqueness of contribution."

**Double-counting and attribution**: when multiple projects claim credit for the same downstream effect, the relevance layer handles it through scoring. The relevance policy SHOULD instruct curators to consider uniqueness of contribution and discount claims that overlap with other projects' claims in the same round. No protocol enforcement of exclusive attribution. This keeps the template simple and avoids forcing projects to negotiate credit splits before submitting claims. Limitation: the coherence game rewards consensus on scalar scores, not accurate causal attribution. If curators do not notice overlap, both projects may receive full credit for the same downstream effect. This is an accepted limitation of the per-claim independent scoring model.

Broad pools (covering heterogeneous project types) are allowed. The relevance policy rubric is responsible for making comparisons meaningful. If a pool's rubric is bad, curators produce bad scores, users migrate to better pools, and the bad pool loses relevance. Same "bad pools fail locally" philosophy as news.

## Challenge Incentives

Debunking a false impact claim during holdback **redirects funds** to legitimate projects. This creates a competitive challenge incentive that is structurally stronger than news:

- In news, challengers are motivated by the debunking reward (they receive the author's forfeited bond on successful challenge).
- In RPGF, challengers are also motivated by **competitive redirection**: funds that would have gone to a false claim are redistributed to deserving projects, including potentially the challenger's own project.

The challenger's private reward is the forfeited bond, which is small relative to the total redirected funds. Most of the economic benefit of a successful challenge is a positive externality shared across all surviving projects. This is the RPGF analogue of the challenger free-rider problem identified in the thesis (Proposition 2: challenger entry is rational only when the false-claim base rate exceeds a threshold; below it, no rational agent searches). The competitive redirection incentive partially mitigates this (challengers who are also applicants benefit from redirection), but the first-mover disadvantage remains. Pools MAY supplement challenger rewards from the curation budget to strengthen the private incentive.

This is a double-edged sword: competitive dynamics also enable **strategic challenges** (filing challenges to suppress rival projects). To make sabotage expensive, challenge costs SHOULD scale with the challenged claim's allocation weight rather than with a flat symbolic bond.

**Departure from framework:** In the framework's news instantiation, challenge costs scale with the author's *bond* (counter-stake = `max(pool minimum, B/4)`, challenge tax = % of pinned bond). In RPGF, challenge costs scale with the challenged claim's *provisional allocation share* instead. Rationale: in news, the bond is the primary capital at risk and the natural scaling anchor. In RPGF with holdback, the primary capital at risk is the provisional allocation (which may far exceed the bond). Scaling challenge costs to the allocation makes challenges proportionally expensive relative to the funds being contested, preventing cheap strategic challenges against high-value claims.

The challenger pays three costs:

1. **Counter-stake**: `max(pool.minChallengeStakeWei, challengedClaimProvisionalShare / 4)`. Forfeited if the challenge fails.
2. **Challenge tax**: `pool.challengeTaxBps * challengedClaimProvisionalShare / 10,000`. Credited to the pool's curation budget. Non-refundable.
3. **DDR fee**: the external dispute resolution provider cost (e.g., Kleros arbitration fee). Non-refundable regardless of outcome.

Failed challengers lose their counter-stake and have already paid the challenge tax and DDR fee. Repeated failed challenges from the same identity SHOULD trigger escalating costs or cooldowns at the interface level.

**Cost pinning**: challenge costs reference the **frozen scoring snapshot** computed at the end of the evaluation period. All challenge filings during holdback use the same snapshot values for counter-stake, challenge tax, and payout calculations. Subsequent debunkings during the same holdback period do not reprice already-filed or future challenges. This ensures challengers can compute their expected costs and rewards at filing time without exposure to repricing risk.

## Funding Distribution

Once the curation layer produces scores for all surviving impact claims:

```
claimScore = relevanceScore

projectScore = sum(claimScore for surviving claims by this project)

projectFunding = (projectScore / sum(projectScore for all eligible projects)) * poolFundingBudget
```

Design note: confidence (bond-time accumulation) from the news instantiation is **not used** in RPGF scoring. In news, the feed score formula `relevanceScore * confidencePercentile` uses bond-time to distinguish long-lived, well-scrutinized claims from new ones. In batch RPGF, all reports are submitted within the same round window, so bond-time would merely reward earlier submission within the window rather than measuring meaningful exposure to challenge. Relevance score alone drives allocation.

**Claim-splitting defense**: the additive formula creates an incentive to split impact into many small claims to inflate total score. Two mitigations:

1. **Per-report claim cap**: pools SHOULD set a maximum number of impact claims per report (suggested default: 10). Claims beyond the cap are rejected.
2. **Curator awareness**: the relevance policy SHOULD instruct curators to score the marginal contribution of each claim, not its standalone importance. Redundant or trivially granular claims should receive low relevance scores. The coherence game penalizes curators who inflate scores out of line with the committee.

These mitigations do not eliminate the incentive entirely, but they raise the cost and reduce the payoff of claim-splitting. If claim-splitting becomes a practical problem, a future version can introduce sublinear aggregation (e.g., square root of claim count) or project-level portfolio scoring.

This is proportional allocation weighted by curated relevance. The formula is deterministic conditional on its inputs, but those inputs depend on the pool's relevance policy (a governance surface defined at pool creation) and the coherence game output. No additional governance beyond pool creation is needed for the allocation step itself.

## Reference RPGF Pool Profile

| Parameter | Suggested Default |
|---|---|
| Domain | Retroactive public good funding for a specific ecosystem |
| Impact report submission window | 30 days per funding round |
| Holdback period | 30 days after provisional allocation |
| Author bond | `max(0.01 ETH, 5% of provisional allocation)` per impact report; automatically withheld from provisional allocation |
| Max claims per report | 10 |
| Challenger counter-stake | `max(0.01 ETH, 25% of challenged claim's provisional share)` |
| Challenge tax | 0.5% of challenged claim's provisional share |
| DDR fee | External provider cost (e.g., Kleros arbitration fee); paid by challenger |
| Curation budget reserve | 5% of pool funding budget |
| Relevance round cadence | One round per claim during the evaluation period |
| Relevance coherence threshold K | 1.25 |
| Relevance slash rate | 3% of curator stake slice |
| Author reputation decay | 1% per 30-day epoch |
| Author debunking slash | 50% of current reputation |
| Curator exit cooldown | 7 days |
| DDR timeout | 90 days (shorter than news; funding rounds have deadlines) |

## Differences From News Instantiation

| Aspect | News | RPGF |
|---|---|---|
| Claim unit | Whole article blob | Atomic impact claims within a report |
| Debunking scope | Whole blob debunked | Per-claim; surviving claims keep their score |
| Bond model | Author-bonded (no protocol minimum) | Scaled bond + holdback on provisional allocation |
| Challenge cost base | Scales with author's bond | Scales with challenged claim's provisional share |
| Primary deterrent | Bond loss | Reputation slash + funding redirection |
| Challenge incentive | Debunking reward only | Debunking reward + competitive fund redirection |
| Time horizon | Continuous (claims live indefinitely) | Batch (funding rounds with submission windows) |
| Cadence | Weekly relevance rounds | Per-round evaluation period |
| Relevance question | "How important is this for the feed?" | "How valuable is this impact for the pool's mission?" |
| Attribution | Not applicable (each claim is independent) | Relevance layer handles overlapping credit |
| Comparability | Ranking only (feed position) | Budget-share allocation (proportional funding) |

## Open Problems

### Identity persistence

Reputation only works if project identity persists across funding rounds. If identity is cheap to reset (new address, new team name), reputation-slash is ineffective. Options include requiring identity attestations, proof-of-personhood, or minimum reputation thresholds for participation. This is not solved at the protocol level.

### Comparability limits

Independent per-claim relevance scoring with normalization may produce unintuitive allocation results across very different project types (a developer tool vs. a research paper vs. core infrastructure). The relevance policy must be specific enough to make these comparisons meaningful. If it is not, curators produce noisy scores and the allocation degrades gracefully rather than catastrophically (the same "bad pool" dynamic as news).

### Competitive challenge dynamics

The competitive redirection incentive improves challenger participation but creates an adversarial surface: projects have a direct financial incentive to challenge competitors. Monitoring challenge patterns, adjusting challenge costs, and interface-level reputation signals for challenge behavior may be needed in practice.

### Counterfactual impact

The framework handles direct output claims ("we built X") but not counterfactual impact claims ("X prevented Y from happening"). Counterfactual claims fail the falsifiability requirement and would be legitimately challengeable as `NonFalsifiable`. This limits the framework to observable, measurable impact, which is a real scope constraint.

### Claim lifecycle during holdback

The framework defines explicit claim lifecycle states (`Live`, `PendingEdit`, `WithdrawPending`, `Challenged`, `Closed`, `Withdrawn`). This RPGF design does not specify lifecycle states for impact claims during holdback. Open questions: can a project amend a claim during holdback (e.g., correct a factual error before it is challenged)? Can a project voluntarily withdraw a claim to avoid debunking reputational damage? If amendment is allowed, does it reset the holdback window for that claim? The news instantiation allows amendment (which resets confidence to zero) and withdrawal (with a cooldown period); the RPGF adaptation should specify equivalent rules.

### Post-holdback fraud discovery

Challenges are limited to the holdback period. Once funds are disbursed, there is no protocol-level mechanism to recover funds if fraud is discovered later. The deterrent after disbursement is limited to reputation slashing (reducing future allocations). This is an accepted tradeoff for disbursement finality, but it means the holdback window is the sole challenge opportunity. Pools that require stronger post-disbursement accountability must rely on external mechanisms (e.g., legal recourse, off-chain reputation systems).

### Curation budget sustainability

The curation budget (suggested 5% of pool funding) is drawn from the pool's total funding, reducing funds available to projects. Whether this budget is sufficient to incentivize curator participation depends on pool size and claim volume. Small pools may need higher curation budget percentages, while large pools may attract curators at lower rates. The current flat percentage suggestion may need per-pool calibration.
