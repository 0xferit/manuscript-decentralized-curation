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

A project submits an **impact report** containing multiple **impact claims**. Each claim is:

- A bonded, falsifiable assertion about a specific deliverable or output
- Independently challengeable on its own evidence
- Scored for relevance as part of the project's contribution to the pool

If one claim is debunked, the others survive. The project's funding allocation is computed over surviving claims only. Whole-report debunking is reserved for `TemplateViolation` (the report itself fails template requirements) or `NonFalsifiable` (the entire report lacks testable assertions).

This is a deliberate departure from the news instantiation, where whole-blob debunking is accepted because the proportionality tradeoff is less severe (removing a news article from a feed is less consequential than zeroing out a project's funding).

## Bond Model: Provisional Allocation With Holdback

Projects seeking retroactive funding are typically capital-constrained. Requiring large upfront bonds is circular.

Instead:

1. Projects submit impact reports with a **small symbolic bond** (spam filter; e.g., 0.01 ETH).
2. The curation layer produces scores. Allocation is computed **provisionally** based on the curation output.
3. A **holdback period** (suggested default: 30 days) runs before final disbursement.
4. During holdback, challenges can be filed against any impact claim.
5. If a claim is debunked during holdback, the corresponding funding share is withheld and **redistributed** to surviving projects.
6. After holdback, remaining funds are disbursed.
7. **Author reputation** is the primary long-term deterrent: debunked claims slash project reputation, reducing allocation in future funding rounds.

## Relevance Scoring and Attribution

Each impact claim receives an independent relevance score through the standard coherence game (same mechanism as news). Curators score claims one at a time, and the protocol normalizes across all eligible claims in the pool.

The pool's **relevance policy** defines the scoring question and rubric. Example:

> "Score each impact claim from 0.0 (no value to this pool) to 1.0 (critical contribution) based on: usage scale, downstream adoption, ecosystem dependency, cost efficiency, and uniqueness of contribution."

**Double-counting and attribution**: when multiple projects claim credit for the same downstream effect, the relevance layer handles it. Curators score contribution shares through relevance scoring. No protocol enforcement of exclusive attribution. This keeps the template simple and avoids forcing projects to negotiate credit splits before submitting claims.

Broad pools (covering heterogeneous project types) are allowed. The relevance policy rubric is responsible for making comparisons meaningful. If a pool's rubric is bad, curators produce bad scores, users migrate to better pools, and the bad pool loses relevance. Same "bad pools fail locally" philosophy as news.

## Challenge Incentives

Debunking a false impact claim during holdback **redirects funds** to legitimate projects. This creates a competitive challenge incentive that is structurally stronger than news:

- In news, challengers are motivated by the debunking reward (counter-stake payout).
- In RPGF, challengers are also motivated by **competitive redirection**: funds that would have gone to a false claim are redistributed to deserving projects, including potentially the challenger's own project.

This is a double-edged sword: competitive dynamics also enable **strategic challenges** (filing challenges to suppress rival projects). The challenge tax and counter-stake create economic barriers, but the adversarial surface is larger than in news. Pool operators and interfaces should monitor challenge patterns for abuse.

## Funding Distribution

Once the curation layer produces scores for all surviving impact claims:

```
claimScore = relevanceScore * confidencePercentile

projectScore = sum(claimScore for surviving claims by this project)

projectFunding = (projectScore / sum(projectScore for all eligible projects)) * poolFundingBudget
```

This is proportional allocation weighted by curated quality. Simple, deterministic, no governance needed.

## Reference RPGF Pool Profile

| Parameter | Suggested Default |
|---|---|
| Domain | Retroactive public good funding for a specific ecosystem |
| Impact report submission window | 30 days per funding round |
| Holdback period | 30 days after provisional allocation |
| Author symbolic bond | 0.01 ETH per impact report |
| Challenger counter-stake | `max(0.01 ETH, 25% of symbolic bond)` |
| Challenge tax | 0.5% of symbolic bond |
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
| Bond model | Author locks substantial bond | Small symbolic bond + holdback on provisional allocation |
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
