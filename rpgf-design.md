# Retroactive Public Good Funding: A Curation Framework Instantiation

Status: complete design document. Ready for blueprint phase. Applies the decentralized curation framework from the thesis to retroactive public good funding (RPGF).

## Problem

Public good funding allocation is a curation problem disguised as a governance problem.

Existing RPGF systems fail at information verification:

- **Expert committees** (e.g., Optimism RPGF) are trusted, scarce, and opaque. A small group decides how millions of dollars are allocated. The bottleneck is not capital; it is the committee's ability to verify hundreds of impact claims.
- **Democratic voting** (e.g., Gitcoin Quadratic Funding) is a preference and attention aggregator, not a truth-verification mechanism. Popularity is a weak proxy for impact. The mechanism is susceptible to Sybil attacks and narrative capture.

Both systems suffer from the same upstream failure: they cannot make impact claims **legible**, **contestable**, and **comparable** at scale. Evaluators face information abundance (hundreds of project submissions) and knowledge scarcity (no trustworthy way to verify which claims are real).

The thesis argument applies directly: **curation precedes coordination**. Fix the curation layer (evaluate impact claims) and the coordination layer (allocate funds) becomes a well-defined function of the curation output.

## Framework Application

### Step 1: Identify the hidden curation problem

RPGF allocation failures are usually described as governance failures: "the committee was biased," "the voting was gamed," "the wrong projects got funded." These are symptoms. The upstream cause is that impact claims are not structured, not contestable, and not independently verifiable.

### Step 2: Identify the relevant quality dimensions

Two dimensions dominate:

- **Impact accuracy**: did the project deliver what it claims? Binary, global, challengeable. The claim is either substantiated or it is not.
- **Allocation relevance**: how important is this delivered impact for the funding pool's mission? Scalar, local, pool-dependent. A developer tool matters more to an "Ethereum infrastructure" pool than to a "climate action" pool.

Design principle: do not decompose quality further than your mechanisms can distinguish. Two mechanisms (challenge-based accuracy, coherence-based relevance) means two dimensions. Additional quality considerations (efficiency, novelty, team quality) belong inside the relevance policy as scoring criteria, not as separate protocol mechanisms.

### Step 3: Require falsifiability

Impact claims must be expressed as falsifiable assertions. This is harder than traditional text claims because impact submissions default to narrative. The **template** does the heavy lifting.

The relevant region on the falsifiability spectrum:

- **Falsifiable**: "Our tool was used by 500 developers in Q1 2026" (verifiable usage data)
- **Falsifiable**: "We deployed contract X at address Y on date Z" (on-chain evidence)
- **Not falsifiable**: "We improved the developer experience" (no measurable assertion)
- **Not falsifiable**: "This infrastructure prevented $2M in losses" (counterfactual; no observable test)

The template must reject the second category and force projects to express impact in the first category. Non-falsifiable claims are challengeable as `NonFalsifiable`.

### Step 4: Design mechanisms dimension by dimension

Two mechanisms handle the two dimensions:

- **Accuracy**: bonded publication, open challenges, external DDR (Kleros v1). Verifies whether impact claims are true.
- **Relevance**: drafted curator coherence game under a public policy. Scores how important the verified impact is for the pool's mission.

Three domain-specific adaptations are required:

1. **Tighter templates**: impact nomination templates must require measurable outputs, evidence links (on-chain transactions, usage metrics, third-party attestations), bounded time periods, and pool-specific eligibility criteria.
2. **Whole-nomination challenge unit**: the impact nomination is the atomic challengeable unit. A successful challenge debunks the entire nomination.
3. **Holdback bond model**: provisional allocation with a challenge window before final disbursement, instead of requiring large upfront bonds from capital-constrained projects.

## Impact Nomination Structure

A project submits one **impact nomination** per pool-defined project identity per funding round. The one-nomination-per-identity rule is a pool template requirement, not a protocol invariant; pools define what counts as the same project identity. A duplicate submission is challengeable as `TemplateViolation`. The nomination is the atomic challengeable unit: a successful challenge debunks the entire nomination and redirects its funding share.

The nomination contains:

- One or more falsifiable assertions about specific deliverables or outputs
- Evidence links (on-chain transactions, usage metrics, third-party attestations)
- Bounded time periods for each assertion

The pool template defines structural, semantic, and eligibility requirements. Eligibility criteria (e.g., "project must target Ethereum L1 or L2," "must be open-source") are embedded in the template, not enforced by a separate scope mechanism. A nomination that fails eligibility is challengeable as `TemplateViolation`.

The nomination is challenged as a whole. A project with one false assertion in an otherwise valid nomination risks the entire allocation. This stronger deterrent incentivizes clean, conservative submissions and is accepted as a design tradeoff for protocol simplicity. The tradeoff is precision over recall: fewer false assertions survive, but projects may underreport marginal impact to avoid risk. The materiality standard mitigates this by excluding immaterial inaccuracies from debunking grounds.

### Evidence policy

The evidence policy defines what evidence is admissible in impact nominations and challenge disputes, how conflicting evidence is weighed, and when insufficient evidence causes a challenge to fail.

Each falsifiable assertion in an impact nomination MUST cite at least one evidence item. Evidence is admissible only for the kind of fact it can directly support. For example, on-chain records can establish deployments and on-chain activity, public repositories can establish code delivery and release timing, and third-party attestations can establish independently observed integrations or usage. A source is not admissible for propositions it cannot directly substantiate.

Admissible evidence classes:

- **Direct public artifacts**: on-chain transactions and state, verified contract addresses, cryptographic proofs, public repositories, signed releases, package registry records, and other machine-verifiable public records.
- **Independent third-party evidence**: audits, independent analytics platforms, public attestations from downstream integrators, milestone sign-offs, and other records created by parties not controlled by the author.
- **Self-reported evidence**: internal analytics, team dashboards, and author-produced summaries. Self-reported evidence MAY supplement a claim but is insufficient by itself for quantitative usage, adoption, or impact assertions; such assertions MUST be corroborated by at least one direct public artifact or independent third-party source.

When multiple sources conflict, jurors SHOULD prefer the more directly verifiable, more assertion-specific, and more canonical source. Machine-readable primary records outrank screenshots, summaries, and social posts when both are available.

Evidence MUST correspond to the assertion's claimed time period. Evidence from outside the claimed period is admissible only to establish baseline facts or continuing state and is insufficient by itself to prove period-specific activity or impact.

For `Debunking`, the contested inaccuracy must be material to the assertion's claim of impact. Trivial numerical discrepancies that do not change the substance of the claimed impact are insufficient grounds for debunking. DDR jurors SHOULD dismiss challenges based on immaterial errors.

The challenger bears the burden of proof. If admissible evidence is conflicting or insufficient to establish a violation under this policy, the challenge fails and the nomination stands.

### Challenge types

Three typed challenge reasons, all yielding `Debunked` on success:

- **`Debunking`**: one or more assertions in the nomination are factually false.
- **`NonFalsifiable`**: the nomination fails to contain testable assertions under the pool's template and evidence policy.
- **`TemplateViolation`**: the nomination fails the pool's structural, semantic, or eligibility requirements (missing required fields, disallowed source classes, ineligible project type). As with `Debunking`, the violation must be material: trivial formatting defects that do not affect the substance of the nomination are insufficient grounds for debunking.

No `ScopeViolation` type. Scope is handled by eligibility criteria in the pool template (challenged as `TemplateViolation`) and by the relevance layer (curators score off-mission nominations low).

A challenge MUST provide concrete evidence for the claimed reason. For `Debunking` and `NonFalsifiable`, this means identifying the specific assertion(s) being contested and providing counter-evidence. For `TemplateViolation`, this means citing the violated template rule and providing supporting evidence (e.g., a conflicting nomination for duplicate submissions, or missing fields for structural violations). The burden of proof is on the challenger.

### Challenge payout rules

One tax event at challenge filing, paid to the pool budget. After that, the loser's stake goes to the winner in full.

| Outcome | Author bond | Challenger counter-stake | Challenge tax |
|---|---|---|---|
| Debunked | To challenger | Returned to challenger | Pool budget (paid at filing) |
| ChallengeFailed | Returned to author | To author | Pool budget (paid at filing) |
| DDR timeout | Returned to author | To author | Pool budget (paid at filing) |

## Round Phases

Each funding round proceeds through five sequential phases:

1. **Submission window** (suggested default: 30 days): projects submit impact nominations and post bonds. Nominations are editable and retractable during this phase.
2. **Evaluation period**: submission window closes. Curators score each nomination via the coherence game (one relevance round per nomination). Duration depends on the number of nominations and round scheduling.
3. **Provisional allocation**: evaluation completes. The protocol computes each nomination's funding share from relevance scores.
4. **Holdback** (suggested default: 30 days): challenge window is open. At holdback end, unchallenged nominations disburse immediately; challenged nominations' shares remain in escrow.
5. **Settlement**: challenged nominations resolve via DDR. Debunked shares are redistributed as supplementary payments to surviving projects. Cleared shares are released to authors.

## Impact Nomination Lifecycle

Each impact nomination follows a state machine from submission through disbursement or debunking, operating within the round phases above.

![RPGF impact nomination state machine. Nominations enter `Submitted` on bonded publication. Evaluation and provisional allocation produce `Scored` nominations that enter holdback. Challenges route through external DDR; successful challenges lead to `Debunked` (funds redirected), failed challenges restore the pre-challenge state. Terminal states have double borders.](diagrams/fig-rpgf-impact-states.png){#fig-rpgf-impact-states}

### Operational states

| State | Description |
|---|---|
| `Submitted` | Nomination filed during the open submission window. Bond posted. Nomination is editable and retractable while the window is open. |
| `Retracted` | Author retracted the nomination during the submission window. Bond refunded. **Terminal.** |
| `Scored` | Submission window closed, relevance evaluation complete, provisional allocation computed. The holdback period is running. The nomination is challengeable. |
| `Challenged` | An active DDR dispute has been filed against this nomination during holdback. |
| `PendingResolution` | The holdback period expired while a challenge is still active. No new challenges are accepted. The nomination's provisional funding share remains in escrow until DDR resolves. |
| `Disbursed` | Funds released to the project. **Terminal.** |
| `Debunked` | Challenge succeeded. The nomination's funding share is redistributed to surviving projects. Author reputation slashed. **Terminal.** |
| `Unscored` | Relevance round failed quorum twice. Nomination excluded from allocation. Bond refunded. No reputation change. **Terminal.** |

### Adjudication outcomes

Three adjudication outcomes, orthogonal to operational state:

- **Unchallenged**: no challenge has been resolved against this nomination.
- **ChallengeFailed**: a challenge was resolved in the author's favor (or DDR timed out).
- **Debunked**: a challenge succeeded, regardless of challenge type.

### Transitions

| From | To | Trigger | Side effects |
|---|---|---|---|
| *(initial)* | `Submitted` | Project submits impact nomination with bond | `adjudicationOutcome = Unchallenged` |
| `Submitted` | `Submitted` | Author amends nomination (window open) | Content updated; no state change |
| `Submitted` | `Retracted` | Author retracts nomination (window open) | Bond refunded. Nomination removed from round. |
| `Submitted` | `Scored` | Submission window closes; evaluation completes; provisional allocation computed | `provisionalShare` assigned. Holdback timer starts. Nomination locked (no further edits). |
| `Scored` | `Disbursed` | Holdback expires with no active challenge | Funds released. Bond returned. |
| `Scored` | `Challenged` | Challenge filed during holdback | Counter-stake escrowed. Challenge tax paid to pool budget. DDR initiated. |
| `Challenged` | `Scored` | DDR ruling: `ChallengeFailed`; holdback still active | Counter-stake transferred to author. Nomination returns to holdback; new challenges remain possible. |
| `Challenged` | `Debunked` | DDR ruling: `Debunked` | Nomination's `provisionalShare` redistributed. Author reputation slashed. Challenger receives counter-stake back and author bond. |
| `Challenged` | `PendingResolution` | Holdback expires while challenge is still active | No new challenges accepted. Nomination's `provisionalShare` remains in escrow. |
| `PendingResolution` | `Scored` | DDR ruling: `ChallengeFailed` or DDR timeout (90 days) | Counter-stake to author. Holdback reopens for 7 days. New challenges possible. |
| `PendingResolution` | `Debunked` | DDR ruling: `Debunked` | Same as `Challenged` to `Debunked`. |
| `Submitted` | `Unscored` | Relevance round fails quorum twice | Bond refunded. Nomination excluded. No reputation change. Bypasses holdback. |

### Design notes

**Round phases are the backdrop, not nomination states.** The submission window, evaluation period, holdback period, and disbursement phase are round-level phases. Nominations transition within them. There is no `InEvaluation` state; all submitted nominations are scored as a batch when the round enters the evaluation phase.

**Amendment and retraction are only possible during the submission window.** Once the window closes and evaluation begins, nominations are frozen. This is the batch model's advantage: clean phase boundaries.

**No queued challenges, but a post-resolution grace period.** In batch RPGF, the holdback window is finite. If a challenge is already active, a second challenger waits for resolution. After any challenge resolves as `ChallengeFailed`, the remaining holdback for that nomination is set to `max(currentRemaining, 7 days)`. If holdback had already expired (nomination was in `PendingResolution`), it reopens for 7 days by transitioning back to `Scored`. This guarantees a minimum window for follow-up challenges and prevents a blocker attack where a weak or collusive first challenge occupies the slot until holdback expires.

**Anti-relitigation rule.** After a challenge resolves as `ChallengeFailed`, a follow-on challenge against the same nomination in the same round MUST present materially new evidence or a distinct unadjudicated violation. Refiling substantially the same losing case is invalid; DDR jurors dismiss it as relitigation. This bounds serial challenge griefing without capping the number of challenges, imposing deadlines, or escalating costs. The attacker's viable challenges are limited by the nomination's actual vulnerability surface: a clean nomination has few plausible challenge grounds, and the attacker exhausts them quickly while burning a counter-stake on each attempt. Serial challenges are further self-limiting under partial disbursement: only the challenged nomination is escrowed, and each failed challenge transfers the counter-stake to the author, compensating delay on-chain. The residual risk is externally motivated delay attacks where off-chain benefit exceeds on-chain cost; this is acknowledged but not solvable by any economic mechanism.

**Partial disbursement.** At holdback end, unchallenged nominations disburse their shares immediately. Challenged nominations' shares remain in escrow until DDR resolves. On resolution: if `Debunked`, the freed share is redistributed as a supplementary payment to already-disbursed surviving projects, pro-rata by relevance score. If `ChallengeFailed` or DDR timeout, the share is released to the author. This scopes the delay to only the challenged nomination rather than the entire round, preventing a griefing vector where a cheap challenge against a small-share nomination delays disbursement for everyone.

**Scoring failure paths.** Degenerate rounds and quorum failure are treated differently:

- *Degenerate round* (sigma < cancellation threshold): the round's mean is accepted as a valid relevance score. Coherence slashing is skipped for that round because the band has collapsed. A degenerate round with full quorum is genuine consensus, not a failure.
- *Quorum failure* (reveals < minimum quorum): the round is retried once with a fresh draft. If the retry also fails quorum, the nomination transitions to `Unscored`: excluded from allocation, bond refunded, no reputation change, bypasses holdback. The author is not penalized for curator infrastructure failure. `Unscored` is distinct from a score of 0 (which means "judged irrelevant" under the rubric).

**DDR timeout defaults to author victory.** If DDR does not resolve within the timeout period (90 days), the nomination is treated as if the challenge failed. The author is not guilty unless proven; it is the challenger's burden to win the dispute.

## Bond Model: Provisional Allocation With Holdback

Projects seeking retroactive funding are typically capital-constrained. Requiring large upfront bonds is circular.

Instead:

1. Projects submit impact nominations with a **flat upfront bond** of `pool.submissionBondWei` (suggested default: 0.01 ETH). The bond is a spam filter; the real economic deterrent is the holdback mechanism and reputation system. The due diligence cost the system bears per submission is roughly constant, so a flat bond that covers it is the right unit.

   The number of nominations per round is capped at `pool.maxNominationsPerRound`, derived from the pool's curation budget: `maxNominationsPerRound = curationBudget / roundRewardFloor`. This ensures every nomination receives a funded relevance round with positive curator incentives. If more nominations are submitted than the pool can evaluate, excess nominations are rejected on a first-come-first-served basis with bond refunded.
2. The curation layer produces scores. Allocation is computed **provisionally** based on the curation output.
3. A **holdback period** (suggested default: 30 days) runs before final disbursement.
4. During holdback, challenges can be filed against any impact nomination.
5. At holdback end, **unchallenged nominations** disburse their shares immediately. **Challenged nominations'** shares remain in escrow until DDR resolves.
6. On challenge resolution: if `Debunked`, the freed share is redistributed as a **supplementary payment** to already-disbursed surviving projects, pro-rata by relevance score. If `ChallengeFailed` or DDR timeout, the share is released to the author.
7. **Author reputation** is the primary long-term deterrent: debunked nominations slash project reputation, affecting eligibility in future funding rounds.

## Relevance Scoring and Attribution

Each impact nomination receives a relevance score through the coherence game. Curators stake into a pool, are drafted via a stake-weighted lottery, and commit-reveal relevance scores in [0,1]. The protocol computes the weighted mean and standard deviation; curators outside the coherence band (|v_i - mu| > K * sigma) are slashed. Near-flat rounds (sigma < flat-round threshold) are cancelled as degenerate. Curators score nominations one at a time, and the protocol normalizes across all eligible nominations in the pool. Relevance round rewards are funded from the pool's curation budget, which SHOULD be reserved as a percentage of the pool's total funding budget before allocation scoring begins (suggested default: 5% of pool funding budget reserved for curation costs). The budget is split equally across all relevance rounds in the evaluation period. Round rewards are distributed among coherent curators (those within the coherence band) proportional to their effective round weight. A curator's stake slice for a given round is the portion of their total staked capital at risk in that round, equal to their effective round weight.

The pool's **relevance policy** defines the scoring question and rubric. Example:

> "Score each impact nomination from 0.0 (no value to this pool) to 1.0 (critical contribution) based on: usage scale, downstream adoption, ecosystem dependency, cost efficiency, and uniqueness of contribution."

**Double-counting and attribution**: when multiple projects claim credit for the same downstream effect, the relevance layer handles it through scoring. The relevance policy SHOULD instruct curators to consider uniqueness of contribution and discount overlapping claims across projects in the same round. No protocol enforcement of exclusive attribution. Limitation: the coherence game rewards consensus on scalar scores, not accurate causal attribution. If curators do not notice overlap, both projects may receive full credit for the same downstream effect. This is an accepted limitation.

Broad pools (covering heterogeneous project types) are allowed. The relevance policy rubric is responsible for making comparisons meaningful. If a pool's rubric is bad, curators produce bad scores, users migrate to better pools, and the bad pool loses relevance. Bad pools fail locally: users migrate to better pools rather than governance intervening.

## Challenge Incentives

Debunking a false impact nomination during holdback **redirects funds** to legitimate projects. This creates a competitive challenge incentive with two components:

- **Debunking reward**: the challenger captures the author's bond and recovers their counter-stake.
- **Competitive redirection**: funds that would have gone to a false nomination are redistributed to surviving projects, including potentially the challenger's own project.

This is a double-edged sword: competitive dynamics also enable **strategic challenges** (filing challenges to suppress rival projects). To make sabotage expensive, challenge costs SHOULD scale with the challenged nomination's allocation weight rather than with a flat symbolic bond. The counter-stake is `max(pool.minChallengeStakeWei, nominationProvisionalShare / 4)`, and the challenge tax is `pool.challengeTaxBps * nominationProvisionalShare / 10,000`. Failed challengers lose their counter-stake (transferred to author) and pay DDR arbitration fees. Repeated failed challenges from the same identity SHOULD trigger escalating costs or cooldowns at the interface level.

**Strategic challenge expected value.** Let `P` be the pool budget, `a` the challenger's share among surviving nominations, `b` the challenged nomination's provisional share, `c` the counter-stake ratio (default 0.25), and `t` the challenge tax rate (default 0.005). A challenge with DDR success probability `p` has expected value:

`EV = p * a*b/(1-b) * P - (1-p) * c*b*P - t*b*P`

The break-even success probability is:

`p* = (c + t) / (a/(1-b) + c)`

At reference parameters (`c = 0.25`, `t = 0.005`):

| Scenario | Challenger share (a) | Target share (b) | Break-even p* |
|---|---|---|---|
| Equal competitors | 0.30 | 0.30 | 37.6% |
| Small challenges large | 0.05 | 0.30 | 79.3% |
| Large challenges small | 0.30 | 0.05 | 44.7% |

Assuming DDR is unbiased but noisy (per Kahneman and Sunstein's noise framework): for a meritless challenge, DDR noise would need to exceed sigma > 1.58 on a [0,1] merit scale for the break-even to be reached, which is unrealistic for juror panels with majority aggregation. Borderline cases (true merit near the decision threshold) become positive-EV at moderate noise, but this is inherent to any adjudication system: genuinely ambiguous cases attract challenges. The counter-stake ratio is the primary safety lever; the break-even threshold rises with `c` and falls with challenger concentration `a`. Without concentration limits, an actor controlling multiple nominations could lower the effective break-even significantly. The one-nomination-per-identity rule provides the first defense; Sybil resistance remains the deeper constraint.

## Funding Distribution

Once the curation layer produces scores for all surviving impact nominations:

```
projectFunding = (nominationRelevanceScore / sum(nominationRelevanceScore for all surviving nominations)) * poolFundingBudget
```

Each project submits one nomination per round, so there is a one-to-one mapping between nominations and project allocations. The formula is straightforward proportional allocation weighted by curated relevance. If no surviving nominations exist (all debunked or Unscored), the denominator is zero and no allocation is made; the pool budget rolls over to the next funding round.

Design note: bond-time is not used for scoring. All nominations are submitted within the same round window, so time-in-system does not differentiate meaningful exposure to challenge. Relevance score alone drives allocation.

The formula is deterministic conditional on its inputs, but those inputs depend on the pool's relevance policy (a governance surface defined at pool creation) and the coherence game output. No additional governance beyond pool creation is needed for the allocation step itself.

## Author Reputation

Author reputation is a pool-scoped integer that starts at zero and tracks a project's history of honest participation.

- **Earning**: +1 per funding round in which the project's nomination survives without debunking.
- **Penalty**: -5 per debunked nomination. One debunking costs five clean rounds to recover from.
- **Decay**: absolute value reduced by 1 per epoch (suggested default: 30 days), drifting toward zero over time. Old history fades.
- **Negative reputation**: reputation can go below zero. A project with negative reputation has a worse track record than a newcomer.

Reputation does not directly weight curation scores or allocation. The framework rejects reputation-weighted curation because it grants influence not fully backed by slashable capital. Instead, reputation serves two purposes:

1. **Eligibility gating**: pools MAY set a minimum reputation threshold for submission (e.g., reputation >= 0). Projects below the threshold cannot submit to that pool. This is a binary gate, not a scoring weight.
2. **Public signal**: interfaces display author reputation alongside nominations. Curators may informally factor reputation into their relevance scores.

## Pool Creation

Pool creation is permissionless: any address can create a funding pool. The pool creator defines:

- **Pool parameters**: submission window duration, holdback period, bond amount, challenge costs, curation budget, coherence game parameters, reputation thresholds.
- **Nomination template**: structural and semantic requirements for nominations, including eligibility criteria and required evidence types.
- **Evidence policy**: admissible evidence classes, freshness rules, sufficiency standards, and tie-break logic for DDR disputes.
- **Relevance policy**: the scoring question, rubric, and any domain-specific instructions for curators.

These policy objects are versioned by content hash. Nominations submitted under one pool version remain bound to that version permanently. Pool parameters are immutable after creation; if a pool's design proves flawed, the correct response is to create a new pool with better parameters, not to upgrade the existing one. Bad pool design fails locally through non-use rather than through a protocol-level governance gate.

## Reference RPGF Pool Profile

| Parameter | Suggested Default |
|---|---|
| Domain | Retroactive public good funding for a specific ecosystem |
| Impact nomination submission window | 30 days per funding round |
| Holdback period | 30 days after provisional allocation |
| Author bond | 0.01 ETH per impact nomination (flat; `pool.submissionBondWei`) |
| Challenger counter-stake | `max(0.01 ETH, 25% of challenged nomination's provisional share)` |
| Challenge tax | 0.5% of challenged nomination's provisional share |
| Curation budget reserve | 5% of pool funding budget |
| Max nominations per round | `curationBudget / roundRewardFloor` (derived; ensures every nomination gets a funded round) |
| Relevance round cadence | One round per nomination during the evaluation period |
| Relevance draft committee size | 15 curators |
| Minimum reveal quorum | 5 curators |
| Flat-round cancellation threshold | sigma < 0.02 (degenerate; round cancelled) |
| Per-identity effective weight cap | 10% of drafted round weight |
| Round reward floor | 0.01 ETH equivalent from pool curation budget |
| Commit window | 48 hours |
| Reveal window | 48 hours |
| Relevance coherence threshold K | 1.25 |
| Relevance slash rate | 3% of curator stake slice |
| Author reputation: initial value | 0 |
| Author reputation: surviving round reward | +1 per round |
| Author reputation: debunking penalty | -5 per debunked nomination |
| Author reputation: decay | absolute value reduced by 1 per 30-day epoch (drift toward 0) |
| Curator exit cooldown | 7 days |
| DDR timeout | 90 days (funding rounds have deadlines) |

## Differences From News Instantiation

| Aspect | News | RPGF |
|---|---|---|
| Challenge unit | Whole article blob | Whole impact nomination |
| Bond model | Author-chosen (no protocol minimum) | Flat per-nomination bond (spam filter; holdback is the real deterrent) |
| Primary deterrent | Bond loss | Reputation slash + funding redirection |
| Challenge incentive | Debunking reward only | Debunking reward + competitive fund redirection |
| Challenge types | Debunking, NonFalsifiable, ScopeViolation, TemplateViolation | Debunking, NonFalsifiable, TemplateViolation (scope via template eligibility) |
| Time horizon | Continuous (claims live indefinitely) | Batch (funding rounds with submission windows) |
| Cadence | Weekly relevance rounds | Per-round evaluation period |
| Relevance question | "How important is this for the feed?" | "How valuable is this impact for the pool's mission?" |
| Attribution | Not applicable (each claim is independent) | Relevance layer handles overlapping credit |
| Comparability | Ranking only (feed position) | Budget-share allocation (proportional funding) |
| Nomination lifecycle | 6 states; continuous with edit/withdraw | 8 states; batch-phased, edits only during submission window |
| Challenge payouts | Complex payout matrix | Single tax at filing; loser's stake to winner in full |

## Open Problems

### Identity persistence

Reputation only works if project identity persists across funding rounds. If identity is cheap to reset (new address, new team name), reputation-slash is ineffective. The same identity gap limits duplicate-nomination enforcement: the one-nomination-per-identity template rule is only as strong as the pool's identity definition and evidence policy. Options include requiring identity attestations, proof-of-personhood, or minimum reputation thresholds for participation. This is not solved at the protocol level.

### Comparability limits

Relevance scoring with normalization may produce unintuitive allocation results across very different project types (a developer tool vs. a research paper vs. core infrastructure). The relevance policy must be specific enough to make these comparisons meaningful. If it is not, curators produce noisy scores and the allocation degrades gracefully rather than catastrophically (the "bad pool fails locally" dynamic).

### Competitive challenge dynamics

The competitive redirection incentive improves challenger participation but creates an adversarial surface: projects have a direct financial incentive to challenge competitors. Monitoring challenge patterns, adjusting challenge costs, and interface-level reputation signals for challenge behavior may be needed in practice.

### Counterfactual impact

The framework handles direct output claims ("we built X") but not counterfactual impact claims ("X prevented Y from happening"). Counterfactual claims fail the falsifiability requirement and would be legitimately challengeable as `NonFalsifiable`. This limits the framework to observable, measurable impact, which is a real scope constraint.

### Scoring order effects

Curators score nominations sequentially (one relevance round per nomination). Earlier-scored nominations may anchor expectations for later scores. The coherence game rewards convergence to the committee mean, but that mean shifts as the evaluation period progresses. Randomizing scoring order across curators and rounds mitigates this but does not eliminate it.

### Double-counting as strategic exploit

When multiple projects claim credit for the same downstream effect, the relevance layer handles it through scoring. However, colluding projects can strategically engineer overlapping claims to extract double allocation if curators fail to notice the overlap. The evidence policy SHOULD require explicit attribution statements that make overlap detectable, but protocol-level enforcement of exclusive attribution is not feasible.

### Reputation decay and long-term memory

Positive reputation decays toward zero over time, which means sustained good behavior is not durably rewarded. A veteran project whose reputation has decayed to zero is indistinguishable from a newcomer by the eligibility gate. Asymmetric decay (negative reputation decays slower than positive) or a persistent "peak negative" score could strengthen long-term deterrence.

### Pool migration friction

Pool-scoped reputation creates switching costs: established projects with high reputation in one pool face reputation reset if they migrate to a new pool. This friction may slow the "bad pools fail locally" dynamic, since the projects whose participation would make a new pool viable are exactly the ones with the highest switching cost.
