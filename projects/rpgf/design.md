> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Copyright (c) 2026 Ferit Tunçer.

Status: reference batch profile for retroactive public goods funding (RPGF). This proposed application covers nomination lifecycle, challenges, relevance scoring, funding distribution, and historical reputation. It is not a deployed system or a complete implementation specification. The [foundational paper](../../) owns shared relevance and appeal rules; the [companion paper](https://github.com/0xferit/manuscript-decentralized-curation/blob/main/projects/rpgf/companion-paper/manuscript.md) develops ongoing funding, which has a different lifecycle from the batch profile here. Neither application is evidence that the full mechanism has been validated.

## Problem

Public goods funding combines allocation choices with an information problem: participants must assess what a project delivered and how those results matter under a funding objective. Expert assessment and preference aggregation can help with allocation, but neither alone establishes the accuracy or comparability of impact claims. Preferences, objectives, budgets and beneficiary eligibility remain governance choices even when evidence improves.

This profile applies the thesis's curation framework to that information problem. It separates challenges to factual assertions from policy-relative relevance assessment, then uses eligible relevance scores as proportional funding weights. The resulting allocation is deterministic given its inputs; the quality of those inputs and the incentives that produce them remain research questions.

## Framework Application

### Step 1: Identify the hidden curation problem

RPGF allocation failures are usually described as governance failures: "the committee was biased," "the voting was gamed," "the wrong projects got funded." Some such failures may originate in poorly structured claims, limited contestability or weak evidence. Others arise from conflicting objectives or power even when participants agree on the facts; the curation mechanism does not eliminate those causes.

### Step 2: Identify the relevant quality dimensions

Two dimensions dominate:

- **Impact accuracy**: did the project deliver what the nomination claims? The nomination is open to a binary challenge outcome. Remaining unchallenged, or surviving a challenge whose burden was not met, does not establish prior substantiation or certify truth.
- **Allocation relevance**: how important is this delivered impact for the funding pool's mission? Scalar, local, pool-dependent. A developer tool matters more to an "Ethereum infrastructure" pool than to a "climate action" pool.

Design principle: do not decompose quality further than your mechanisms can distinguish. Two mechanisms (challenge-based accuracy, coherence-based relevance) mean two dimensions. Additional quality considerations (efficiency, novelty, team quality) belong inside the relevance policy as scoring criteria, not as separate protocol mechanisms.

### Step 3: Define challengeable testability requirements

In this RPGF profile, impact nominations must express their impact claims as testable assertions under the pool's template and evidence policy. This is harder than traditional text claims because impact submissions default to narrative. The **template** does the heavy lifting.

The relevant region on the falsifiability spectrum:

- **Falsifiable**: "Our tool was used by 500 developers in Q1 2026" (verifiable usage data)
- **Falsifiable**: "We deployed contract X at address Y on date Z" (on-chain evidence)
- **Not falsifiable**: "We improved the developer experience" (no measurable assertion)
- **Not falsifiable as stated**: "This infrastructure prevented $2M in losses" (without a specified causal comparison or possible evidentiary test)

The template states the testability requirements against which a posted nomination may be challenged; it does not require prior substantive verification before bonded publication. Nominations that fail to contain testable assertions under the pool’s template and evidence policy are challengeable as `NonFalsifiable`. A successful challenge debunks that nomination, rather than the person who submitted it.

### Step 4: Design mechanisms dimension by dimension

Two mechanisms handle the two dimensions:

- **Accuracy**: bonded publication, open challenges, external decentralized dispute resolution (DDR; reference provider: Kleros v1). Adjudicates challenges to a nomination’s factual assertions or compliance with testability requirements; publication does not mean prior verification.
- **Relevance**: drafted curator coherence game (a Schelling-point mechanism where curators independently score items and are rewarded for convergence) under a public policy. Scores the submitted impact claims and available evidence under the pool’s mission; the impact need not have been verified in advance.

The asset boundary follows the paper's [relevance layer](../../#relevance-layer): a dedicated utility asset backs curator availability, drafted voting weight, coherence penalties and coherence rewards. Utility-token coherence rewards redistribute only actual integer distance-based incoherence penalties. Each coherent curator’s complete original round weight is aggregated before its reward is rounded down under the paper’s rule, and the remainder goes once to this same pool’s separate utility-token balance when valid-round rewards are allocated. There is no base utility-token reward reserve or minting, and no such reward when no eligible penalty is collected. Author bonds, challenger counter-stakes, challenge taxes, beneficiary funding, jury service fees and relevance-appeal contributions and payouts use ether (ETH). ETH service fees and utility-token redistribution are separate transfers with separate accounting; neither is converted into the other. For a valid issued ruling, timely valid revealers earn the fixed gross ETH service fee per represented originally drawn seat, independent of coherence, score and dispersion, under the paper's fee rule. The explicit recipient exception is a successful pre-reveal leak report: the reporter directly receives the utility tokens actually confiscated from the violating curator and that curator's otherwise-earned gross ETH service fee for the same round, if any. This uses separate transfers in the two assets, without conversion, an independent subsidy or an increase in the round's fee.

Three domain-specific adaptations are required:

1. **Tighter templates**: impact nomination templates must require measurable outputs, evidence links (on-chain transactions, usage metrics, third-party attestations), bounded time periods, and pool-specific eligibility criteria.
2. **Whole-nomination challenge unit**: the impact nomination is the atomic challengeable unit. A successful challenge debunks the entire nomination.
3. **Holdback bond model**: provisional allocation with a challenge window before final disbursement, instead of requiring large upfront bonds from capital-constrained projects.

## Impact Nomination Structure

Each funding pool references an external curated **project-beneficiary registry**. Every impact nomination MUST reference exactly one registry entry from that registry. Each registry entry defines the beneficiary record for disbursement and the claimant policy for who may activate a nomination under that entry. Each registry entry may have at most one active impact nomination per funding round in a pool. A duplicate active nomination against the same registry entry is challengeable as `TemplateViolation`. The nomination remains the atomic challengeable unit: a successful challenge debunks the entire nomination, forfeits its bond under the challenge payout rules and removes its right to pool-beneficiary funding. The failed nomination stays closed. Its nominator may submit a fresh bonded nomination under the ordinary submission windows, registry-claimant rules and one-active-nomination-per-entry rule. A prior debunking creates no person- or registry-entry-based ban, reputation threshold or additional cooldown, and a fresh nomination does not resurrect the old one.

The nomination contains:

- One or more falsifiable assertions about specific deliverables or outputs
- Evidence links (on-chain transactions, usage metrics, third-party attestations)
- Bounded time periods for each assertion

The pool template defines structural, semantic, and eligibility requirements. Eligibility criteria (e.g., "project must target Ethereum L1 or L2," "must be open-source") are embedded in the template, not enforced by a separate scope mechanism. A nomination that fails eligibility, references an invalid registry entry, or violates the claimant policy attached to that entry is challengeable as `TemplateViolation`.

The nomination is challenged as a whole. A nomination with one materially false assertion risks its bond and entire allocation through the existing challenge process; it is not rejected merely because no advance verifier has substantiated it. Whole-nomination exposure is intended to encourage conservative submissions, but its effect depends on challenge detection, costs and adjudication. It may also discourage accurate but difficult-to-defend assertions. This trades finer attribution of errors for protocol simplicity; it does not establish a measured improvement in precision or recall. The materiality standard mitigates this by excluding immaterial inaccuracies from debunking grounds.

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

A challenge MUST provide concrete evidence or argument for the claimed reason. For `Debunking`, this means identifying the specific assertion(s) being contested and providing counter-evidence. For `NonFalsifiable`, this means identifying the purported assertion(s) and showing why they are not testable under the pool's template and evidence policy. For `TemplateViolation`, this means citing the violated template rule and providing supporting evidence (e.g., a conflicting nomination for duplicate registry-entry submissions, or missing fields for structural violations). The burden of proof is on the challenger.

### Challenge payout rules

Challenge cashflows are defined entirely in this section. At challenge filing, the challenger escrows the counter-stake, pays the challenge tax to the pool budget, and pays the external DDR fee. The DDR fee is a sunk challenger cost and is never refunded by the protocol, even if the challenge succeeds. After filing, the loser's stake goes to the winner in full.

| Outcome | Author bond | Challenger counter-stake | Challenge tax | DDR fee |
|---|---|---|---|---|
| Debunked | To challenger | Returned to challenger | Pool budget (paid at filing) | Paid by challenger; not refunded |
| ChallengeFailed | Returned to author | To author | Pool budget (paid at filing) | Paid by challenger; not refunded |
| DDR timeout | Returned to author | To author | Pool budget (paid at filing) | Paid by challenger; not refunded |

## Round Timeline

Each funding round has three shared phases, one batch computation, and one nomination-specific resolution path:

1. **Submission window** (suggested default: 30 days): claimants submit impact nominations referencing registry entries and post bonds. Nominations are editable and retractable during this phase.
2. **Evaluation period**: the submission window closes. Curators score each nomination via the coherence game (one initial relevance round per nomination, with one retry on quorum failure). Duration depends on the number of nominations and round scheduling.
3. **Provisional allocation** (batch computation): once evaluation completes, the protocol computes each nomination's provisional funding share from relevance scores.
4. **Holdback** (suggested default: 30 days): nominations with provisional shares are challengeable. At holdback end, unchallenged nominations disburse immediately. Disputed nominations' shares remain in escrow.
5. **Settlement** (nomination-specific): disputed nominations resolve via DDR. If debunked, the provisional share is redistributed as a supplementary payment to the beneficiaries referenced by already-disbursed surviving nominations. If the challenge fails or DDR times out, the nomination returns to holdback for a 7-day grace period; if no new challenge is filed, the share is released to the referenced beneficiary record.

## Impact Nomination Lifecycle

Each impact nomination follows a state machine from submission through disbursement or debunking, operating within the round timeline above.

![RPGF impact nomination state machine. Nominations enter `Submitted` on bonded publication. Evaluation produces `Scored` nominations that enter holdback. Challenges create `Disputed` state, resolved by external DDR: successful challenges lead to `Debunked` (funds redirected), failed challenges return to `Scored` with a grace period. Quorum failure after retry leads to `Unscored` (excluded, bond refunded). Terminal states have double borders.](../../diagrams/fig-rpgf-impact-states.png){#fig-rpgf-impact-states}

### Operational states

| State | Description |
|---|---|
| `Submitted` | Nomination filed during the open submission window. Bond posted. Nomination is editable and retractable while the window is open. |
| `Retracted` | Author retracted the nomination during the submission window. Bond refunded. **Terminal.** |
| `Scored` | Submission window closed, relevance evaluation complete, provisional allocation computed. The holdback period is running. The nomination is challengeable. |
| `Disputed` | An active DDR dispute is in progress. The nomination's provisional funding share remains in escrow until DDR resolves. |
| `Disbursed` | Funds released to the referenced registry entry's beneficiary record. **Terminal.** |
| `Debunked` | Challenge succeeded. The nomination's funding share is redistributed to the beneficiaries referenced by surviving nominations. Registry-entry reputation records the outcome. **Terminal.** |
| `Unscored` | Relevance round failed quorum twice. Nomination excluded from allocation. Bond refunded. No reputation change. **Terminal.** |

A terminal `Debunked` nomination remains ineligible for beneficiary funding. If an ongoing relevance-appeal chain already had a fully funded contested level before that accuracy closure, it continues under the paper’s [Public appeal funding](../../#sec-appeal-funding) rule and the relevance section below. Its continued scoring and backer settlement do not restore the nomination’s state or funding. If the initial appeal process is still open and no contested level was fully funded before accuracy closure, the paper’s pre-contest closure rule instead ends initial appeal funding and creates full refund entitlements as described below.

### Adjudication outcomes

Three adjudication outcomes, orthogonal to operational state:

- **Unchallenged**: no challenge has been resolved against this nomination.
- **ChallengeFailed**: a challenge was resolved in the author's favor (or DDR timed out).
- **Debunked**: a challenge succeeded, regardless of challenge type.

### Transitions

| From | To | Trigger | Side effects |
|---|---|---|---|
| *(initial)* | `Submitted` | Claimant submits impact nomination referencing a registry entry with bond | `adjudicationOutcome = Unchallenged` |
| `Submitted` | `Submitted` | Author amends nomination (window open) | Content updated; no state change |
| `Submitted` | `Retracted` | Author retracts nomination (window open) | Bond refunded. Nomination removed from round. |
| `Submitted` | `Scored` | Submission window closes; evaluation completes; provisional allocation computed | `provisionalShare` assigned. Holdback timer starts. Nomination locked (no further edits). |
| `Scored` | `Disbursed` | Holdback expires with no active challenge | Funds released. Bond returned. |
| `Scored` | `Disputed` | Challenge filed during holdback | Counter-stake escrowed. Challenge tax paid to pool budget. DDR initiated. |
| `Disputed` | `Scored` | DDR ruling: `ChallengeFailed` or DDR timeout (90 days) | Counter-stake transferred to author. Holdback set to `max(remaining, 7 days)`. New challenges possible. |
| `Disputed` | `Debunked` | DDR ruling: `Debunked` | Nomination's `provisionalShare` redistributed. Registry-entry reputation records the outcome. Challenger receives counter-stake back and author bond. |
| `Submitted` | `Unscored` | Relevance round fails quorum twice | Bond refunded. Nomination excluded. No reputation change. Bypasses holdback. |

### Design notes

**Round timeline stages are the backdrop, not nomination states.** The shared round phases are the submission window, evaluation period, and holdback. Provisional allocation is a batch computation between evaluation and holdback. After holdback, unchallenged nominations disburse, while disputed nominations enter settlement via DDR. There is no `InEvaluation` state; all submitted nominations are scored as a batch during the evaluation period.

**Amendment and retraction are only possible during the submission window.** Once the window closes and evaluation begins, nominations are frozen. This is the batch model's advantage: clean phase boundaries.

**No queued challenges, but a post-resolution grace period.** In batch RPGF, the holdback window is finite. If a challenge is already active, a second challenger waits for resolution. After any challenge resolves as `ChallengeFailed`, the remaining holdback for that nomination is set to `max(currentRemaining, 7 days)`. This guarantees a minimum window for follow-up challenges regardless of how much holdback time remained (or whether it had already expired). It prevents a blocker attack where a weak or collusive first challenge occupies the slot until holdback expires.

**Anti-relitigation rule.** After a challenge resolves as `ChallengeFailed`, a follow-on challenge against the same nomination in the same round MUST present materially new evidence or a distinct unadjudicated violation. Refiling substantially the same losing case is invalid; DDR jurors dismiss it as relitigation. This is intended to discourage repeated losing challenges. It supplies no numerical bound on challenge count or delay: distinct evidence and arguments need not form a finite enumerated set, and even a rejected filing can occupy the dispute process. Limiting the number of assertions may reduce the material to examine but does not by itself bound the number of admissible challenges. The rule's effectiveness also depends on DDR juror accuracy in distinguishing relitigation from genuinely novel challenges; borderline cases impose defense costs on the nominee even when ultimately dismissed. Serial challenges are further self-limiting under partial disbursement: only the challenged nomination is escrowed, and each failed challenge transfers the counter-stake to the author, compensating delay on-chain. The residual risk is externally motivated delay attacks where off-chain benefit exceeds on-chain cost; this remains unresolved by the present cost rules.

**Partial disbursement.** At holdback end, unchallenged nominations disburse their shares immediately to the beneficiary records referenced by those nominations. Disputed nominations' shares remain in escrow until DDR resolves. On resolution: if `Debunked`, the freed share is redistributed as a supplementary payment to already-disbursed surviving nominations' referenced beneficiaries, pro-rata by relevance score. If `ChallengeFailed` or DDR timeout, the nomination re-enters `Scored` with a grace period. This scopes the delay to only the disputed nomination rather than the entire round, preventing a griefing vector where a cheap challenge against a small-share nomination delays disbursement for everyone. An already-funded contested relevance-appeal chain continues separately under the paper’s rule after `Debunked`; it cannot undo this beneficiary-share redistribution or restore the nomination’s funding eligibility.

**Scoring failure paths.** Low-dispersion rounds and quorum failure are treated differently:

- *Low-dispersion round* (sigma below the dispersion floor): the round's mean is accepted as a valid relevance score. Distance-based slashing is skipped because the band has collapsed; non-participation penalties remain applicable. With no distance-based penalty collected, the round distributes no utility-token coherence reward. Timely valid revealers still earn the fixed ETH service fee per represented seat when the ruling is issued; low dispersion does not reduce it. In a batch model, cancelling low-dispersion rounds is counterproductive: if a nomination genuinely deserves a consensus score, every retry will also produce low dispersion, eventually excluding a nomination that curators unanimously evaluated.
- *Quorum failure* (valid reveals represent less than 80% of originally drawn seat weight): a nonempty drafted round completes the paper's fixed post-reveal leak-proof period before cancellation. The profile retains its cap of one ordinary retry with a fresh draft for otherwise eligible active nominations; final accuracy closure or completed permitted withdrawal bars a fresh ordinary retry draw even when an allowance remains. For a still-active nomination, if an eligible retry also fails quorum, the nomination transitions to `Unscored` after its proof period and cancellation: excluded from allocation, bond refunded, no reputation change, bypasses holdback. The author is not penalized for curator infrastructure failure. `Unscored` is distinct from a score of 0 (which means "judged irrelevant" under the rubric).

**DDR timeout defaults to author victory.** If DDR does not resolve within the timeout period (90 days), the nomination is treated as if the challenge failed. The author is not guilty unless proven; it is the challenger's burden to win the dispute.

## Bond Model: Provisional Allocation With Holdback

Projects seeking retroactive funding are typically capital-constrained. Requiring large upfront bonds is circular.

Instead:

1. Claimants submit impact nominations referencing registry entries with a **flat upfront bond** of `pool.submissionBondWei` (suggested default: 0.01 ETH). The bond is a spam filter and capital at risk; holdback and the challenge payout rules provide the nomination-level financial consequences. Reputation records history without restricting future nomination rights. The due diligence cost the system bears per submission is roughly constant, so a flat bond that covers it is the right unit.

   The number of nominations per round is capped at `pool.maxNominationsPerRound`, derived from the pool's curation budget: `maxNominationsPerRound = curationBudget / roundRewardFloor`. This bounds the planned initial ordinary-round liability at budgeting time; it does not itself reserve those funds against competing eligible commitments. Availability is secured only by an actual fee reservation under the paper’s shared-budget rule. The cap also does not guarantee positive utility-token rewards or sufficient incentives to participate. Because each scheduled round reserves one `roundRewardFloor` and unused reservations are released on no-reward outcomes, a single quorum retry does not require pre-funding two rounds per nomination. If more nominations are submitted than the pool can evaluate, excess nominations are rejected on a first-come-first-served basis with bond refunded.
2. The curation layer produces scores. Allocation is computed **provisionally** based on the curation output.
3. A **holdback** (suggested default: 30 days) runs before final disbursement.
4. During holdback, challenges can be filed against any impact nomination.
5. At holdback end, **unchallenged nominations** disburse their shares immediately. **Disputed nominations'** shares remain in escrow until DDR resolves.
6. On challenge resolution: if `Debunked`, the freed share is redistributed as a **supplementary payment** to already-disbursed surviving nominations' referenced beneficiaries, pro-rata by relevance score. If `ChallengeFailed` or DDR timeout, the nomination re-enters holdback for a 7-day grace period; if no new challenge is filed during the grace period, the share is released to the referenced beneficiary record.
7. **Registry-entry reputation** records nomination outcomes for public information. Its existing numerical updates do not bar the nominator or registry entry from submitting a fresh nomination under the ordinary rules.

## Relevance Scoring and Attribution

Each impact nomination receives a relevance score through the coherence game.

Under the paper’s continuation rule, an ordinary attempt with a successfully completed nonempty jury draw before final accuracy closure, or before completed author withdrawal where withdrawal is already permitted, continues that current attempt against its pinned revision and policy. Its existing commitment, reveal, quorum, proof, penalties, service-fee and reserve rules continue. A scheduled attempt or incomplete draw alone does not qualify; protocol execution order determines whether the draw completed before exit. A valid ruling earns the normal ETH fee and opens the normal first appeal window even though the nomination is inactive. That window and its chain use ordinary appeal rules, and the earlier exit is not replayed to cancel them for lacking funded positions. No unrelated chain or new independent ordinary round is authorized. The item remains inactive with its existing funding and bond consequences, and authorship alone creates no party role.

The qualifying current attempt may itself be an ordinary retry whose nonempty draw completed before exit. If it fails quorum after exit, it completes its existing proof period and normal fee-free, no-score failure settlement, releases its unused ordinary ETH service-fee reservation through the normal cancellation path, and opens no new appeal window. No fresh ordinary retry may be drawn for an item finally closed by an accuracy outcome or withdrawn under an existing right, even if an ordinary retry allowance remains. Proof timing, applicable penalties and normal lock settlement remain unchanged; this failure cannot refund already-earned fees, reactivate the item or reverse its bond or funding consequences. Still-active nominations retain the batch profile’s ordinary-retry rules and limit. Protected appeal-chain retries remain separate and unchanged, and this continuation introduces no new withdrawal right for the batch profile.

At most one ordinary relevance round per nomination and pool may be scheduled or running at a time, across revisions. Admission and ordinary jury-budget reservation follow the paper's atomic single-round rule; concurrent attempts cannot reserve a second round. Ordinary-round exclusivity includes the paper's post-reveal leak-proof period. Issuance transfers directly to the appeal hold, while cancellation and any permitted retry follow the existing timing and funding rules. This does not limit concurrent evaluation of different nominations or pools, add batch rounds, or change the batch profile's ordinary retry limit or the appeal retry rules. The RPGF relevance mechanism inherits draw-and-lock utility staking, graduated slashing, utility-token redistribution and relevance-round escalation (appeals) from the paper's coherence game design. The paper is the canonical specification for these mechanisms; this section summarizes the operational flow without re-specifying the full formalism.

Curators deposit the dedicated utility asset into a pool and receive seat-tickets proportional to their deposited balance. The protocol draws seats via a stake-weighted lottery; each drawn seat locks L utility tokens from the corresponding curator. Drafted curators commit-reveal relevance scores in [0,1], weighted by their total locked tokens. The paper's fixed 80% reveal-weight quorum applies to both initial and appeal rounds, with no minimum number of distinct curators. Coverage uses weights fixed when the nonempty draft succeeds, before penalties; exact 80% passes, and an empty draft fails. A single curator can satisfy quorum if its reveal represents enough of the drawn weight. Each retry uses its own completed draw without altering the frozen appeal target or fee reserve. The protocol computes the weighted mean and standard deviation; curators outside the coherence band are subject to graduated slashing (near-boundary deviations incur small losses; extreme deviations incur total loss). Low-dispersion rounds (sigma below the dispersion floor) keep the round mean as the nomination's relevance score, but distance-based slashing is skipped. Utility-token coherence rewards consist only of the actual integer eligible distance-based penalties redistributed under the paper’s per-curator round-down rule. Each coherent curator’s entire original round weight is counted once, rather than rounding by seat. The rounding remainder is credited exactly once to this same pool’s separate utility-token balance when the valid round’s rewards are allocated under existing timing, without an additional appeal-chain-finality wait. Some or all coherent rewards may round to zero. With no eligible penalties, rewards and the remainder are zero; with no coherent recipients, all collected eligible penalties follow the paper’s existing fallback into the separate token balance. The residual bound follows the number of coherent recipients under the paper, not the limit on appeal positions. Unclaimed integer rewards remain assigned to their curators and cannot be swept as rounding dust. None of these token amounts can pay ETH obligations, require conversion or create a new reward subsidy. Non-participation penalties remain applicable and do not finance this coherence reward. ETH service fees follow the paper's separate fixed payment rule for timely valid revealers, regardless of coherence, subject to its successful leak-reporter recipient override.

A nonempty drafted round follows the paper's fixed post-reveal leak-proof period before issuing a ruling or completing a quorum-failure cancellation. The positive duration is frozen for that round and measured from its fixed reveal deadline; its provisional default follows the paper's Relevance layer. The existing precommit deadline is unchanged, and qualifying proofs opened early after the corresponding on-chain reveal remain valid. A proof must be included and validated strictly before the proof cutoff. Neither all votes being ready nor all known proofs being opened permits early issuance or cancellation. At or after the cutoff, the appropriate transition is allowed but is not assumed to execute automatically; unopened or invalid precommits cannot extend the period. The round's remaining own collateral stays locked through the period, without a new freeze on currently unlocked deposits or a change to other active rounds' locks. Pre-draw and empty-draft cancellation rules remain unchanged. ETH fee availability and the appeal admission clock begin at actual valid-ruling issuance after this phase, not at reveal closure.

Relevance appeals use the paper’s [Public appeal funding](../../#sec-appeal-funding) rules, including its common terminal-exit treatment. Final accuracy closure uses that rule here. Where an application already permits voluntary author withdrawal, the same rule applies only on completed withdrawal, not on its request or pending cooldown. This does not create a new withdrawal right for this batch profile or change its retraction rules. The rule is scoped to the same pool, claim instance and appeal chain.

Before either exit branch is chosen, existing logical finality under the deadlines or outcomes must be resolved at the effective exit time, even without a recording transaction. It takes precedence when exit coincides with a cutoff. An already-final score, including an unopposed forfeiture score, and its settlement entitlements cannot be replaced, reopened or refunded again by a later exit.

If any contested level in that ongoing chain had at least two distinct positions fully funded before the terminal exit, the chain continues. This includes exit during a later level’s admission or fundraising even when that later level is not yet contested. Its pinned revision, terms, reserves and deadlines remain unchanged; open admission and funding continue, juries retain the common quorum and proof-period rules, and appeal quorum failures retain unlimited retries. Valid rulings earn normal fees and open normal further windows for fresh funding within the same chain until normal finality.

The exit cannot force a zero score, early finality, immediate adjudicated-capital refunds, reserve release or an extra exit from that protected chain. Already-earned fees remain earned. Accuracy outcomes retain their bond, reputation and beneficiary-funding consequences; an application’s completed withdrawal retains its existing inactive status, bond return and confidence consequences. Continued relevance outcomes cannot reactivate the feed or beneficiary funding, relock a returned author bond or make authorship alone a party. No appeal-finality condition is added to otherwise eligible withdrawal. The qualifying already-drawn ordinary attempt above may finish and start its normal first appeal chain, but no new independent ordinary round or unrelated chain for the inactive item is authorized.

If initial appeal funding is still open and no contested level in the same chain was fully funded before the effective terminal exit, the paper’s pre-contest terminal-exit rule cancels that process atomically. Admission and contributions stop immediately without waiting for scheduled deadlines. The already-issued referenced score becomes terminal, without forced zero, a new jury ruling or an unopposed proposal’s forfeiture win. All accepted contributions become refundable in full, including a fully funded lone position, and remain assigned independently of collection. This covers no positions, partial funding, one fully funded position and multiple positions without a funded contest. No appeal jury is drawn or fee earned for that cancelled process, and already-earned ordinary jury fees remain earned.

Unused fee reservations return to their original sources. The pool recovers only its own unused pool-funded reservation; contribution-backed amounts remain reserved for contributor refunds and cannot also become free pool funds. No new refund funding is created. Refunds use the existing permissionless claim and current receiving-address rule. Only this process’s hold ends, without affecting another claim’s or pool’s holds, reserves or proceedings or permitting a new ordinary round for the inactive item. Once existing logical finality has been respected, valid state-transition order decides the funding race: acceptance completing a second distinct fully funded position before exit protects the chain; exit first rejects later funding and proposals, which cannot restore it. The deadline and forfeiture rules below are subject to this explicit terminal-exit exception, with jury voting, proof and other deadlines unchanged. The qualifying already-drawn ordinary attempt follows the continuation rule above; final accuracy closure or completed permitted withdrawal bars any fresh ordinary retry for that inactive item.

Every round and appeal chain assesses a pinned content revision and retains that target and its outcomes. In an application permitting later revisions, an edit does not cancel or retarget the older revision's appeal, reset its clocks, alter its funding terms or release its capital; its own final score still settles its own pots. New content requires its own assessment, and the older outcome must not be relabeled as a judgment of it. An unassessed amended revision MUST NOT inherit an earlier revision's score, including as a provisional proxy, for ranking or new score-dependent funding. It remains accessible through direct links or pending views and becomes score-eligible only when it receives its own adopted score under the ordinary adoption rules, with no additional chain-finality wait. An absent score is distinct from an adopted 0.00. Existing state, allocation and holdback requirements still apply. Older appeal settlements remain separate. Where an application has already accrued beneficiary funding before an amendment, the balance remains attributed to its original revision and follows its existing beneficiary, claim, holdback and accuracy-challenge conditions; the edit alone cannot erase, return, transfer or immediately release it. This does not turn the batch profile's provisional allocation into an accrued or unconditional entitlement: its existing escrow, cancellation and redistribution rules remain in force. This binding keeps the subject of the funded contest fixed for the appellant and opposing score backers. Authorship alone neither makes the author a party nor places the author bond at stake; an author backing a position participates under the ordinary backer rules. The reference batch profile still freezes nominations after the submission window and gains no new amendment right from this general rule. Anyone, including the nominator, may propose or fund a fixed relevance score without approval or role-based exclusion. Each position fixes its score and referenced ruling before accepting contributions. Proposed appeal scores must equal `k / 100` for an integer `k` from 0 through 100 inclusive, giving 101 allowed values. Off-grid proposals such as 0.599 or 0.705 are rejected before contributions rather than silently rounded. The restriction applies only to proposed appeal positions; it does not restrict juror reports, the existing ruling or its weighted mean. A different proposed score requires a different allowed position. Any two distinct fully funded scores oppose each other directly, even when neither equals the current ruling. The existing score may be proposed and funded if it is on the allowed grid, but has no automatic funded defense. More than two funded positions are permitted. Each referenced ruling and numeric score has at most one position. Another submission of that score is not admitted as a new position; backers contribute to the existing position while its funding is open and within the same shared cap. A duplicate cannot create a new target, payout weight or funding clock. Numerically equal values such as 0.70 and 0.700 identify the same position. Distinct allowed scores are at least 0.01 apart; neighboring scores such as 0.59 and 0.60 remain permitted. The grid limits proposal resolution but does not establish resistance to capital-based influence or strategic use of neighboring scores. An appellant or backer drawn as a curator may serve under the ordinary rules.

Every valid issued ruling, including an appeal ruling, immediately opens one bounded admission window. Its positive pool-configured admission duration and positive pool-configured common funding duration are frozen at issuance. Both durations provisionally default to 72 elapsed hours under the paper. The admission deadline is issuance time plus the admission duration, and the one shared funding deadline is admission closure plus the common funding duration. Both cutoffs are exclusive under the paper’s protocol inclusion-timestamp rule: new positions must arrive before the admission deadline and funding before the funding deadline. At or after a cutoff, the respective phase is closed even without a transaction recording closure. An earlier signature or broadcast does not rescue late inclusion, and same-timestamp transaction ordering cannot extend acceptance. Existing positions can still receive capped contributions at or after admission closure, strictly before their funding cutoff. This does not change juror or external-court deadlines. No new positions enter after admission closes; all admitted positions have the full common funding duration after the complete slate is visible, while earlier positions have more total funding time. There are no per-position fundraising or matching clocks. Party actions, contributions, fee collection, claims and later configuration changes cannot alter or restart either deadline. The explicit pre-contest terminal-exit exception ends the process immediately without resetting or extending those deadlines. Reaching two distinct fully funded scores makes the group contested but does not close admission or start the jury early. Once admission has closed and every admitted funding outcome is known, a contested group’s shared jury may proceed. If all positions are fully funded, no wait for unused funding time is required; partially funded positions remain eligible to fund strictly before the common deadline and cannot expire earlier except under the explicit pre-contest terminal-exit cancellation and full-refund rule. Timeout recognition does not require refund collection. At the funding cutoff, no further contribution may alter the expired funding outcome.

Each position uses the paper's common ETH target, contribution cap and immediate lock. These ETH funds are separate from utility-token curator deposits and cannot count toward a utility-token seat lock. The pinned rule and input snapshot freeze the target, contribution multiplier, planned jury size, per-seat rate and fee ceiling before admission opens. These do not vary by proposer, score or admission time. Accepted contributions cannot be withdrawn or reused for another position, appeal level or ordinary-round seat; the lock survives curator exit without encumbering unrelated balances. Penalties outside the appeal cannot consume accepted contributions. Excess above the target is not locked. Under the paper’s contribution-interval rule, each positive acceptance atomically records its backer, accepted amount and immutable place in that position’s cumulative funding order. Repeated contributions by one address remain separate intervals; zero acceptance creates none. Records cannot be merged, reordered or reassigned after acceptance. Positions below their target at the common funding deadline are cancelled, refund accepted contributions in full and have no fee or score-setting right. Principal refunds remain the exact accepted amounts, unaffected by adjudicated-payout rounding. For a process not cancelled by the pre-contest terminal-exit rule, a fully funded unopposed distinct score, after admission closes and all funding outcomes resolve, becomes final by procedural forfeiture, with full refund and no fee or profit on its own position. This is not a jury finding or evidence of consensus and opens no new window. Two distinct fully funded scores require adjudication. If that process remains active and proposals were admitted but none is fully funded at the common funding deadline, the referenced ruling becomes final at that deadline and its issued score becomes the chain's terminal score. No appeal jury is drawn and no new jury fee is charged; all accepted partial contributions become refundable in full. Earlier earned fees remain charged and earlier adjudicated pots settle using that terminal score, with payouts claimable at finality. Recording closure or collecting refunds or payouts is not required for finality. This creates no new ruling or appeal window and ends only this group's hold; any other applicable window or active appeal still blocks new ordinary rounds. Failed fundraising provides no additional evidence of the ruling's correctness.

A contested group uses one jury scoring the nomination over the full scale, under the same commitment, reveal, aggregation, reward and penalty rules as an initial round. All fully funded opposing positions against that ruling contribute their accepted funds to one common pot, retaining each position's score and each backer's contribution record. No separate pairwise pots or per-position jury fees arise. The next appeal's planned seat target is twice the planned target of the valid round that issued the referenced ruling, under the paper's jury-sizing rule. A smaller actual draw does not reduce that baseline: a round planned for 20 seats but drawing 12 gives the next appeal a target of 40 seats. This target does not guarantee filled seats or independent curators. Additional positions and retries do not multiply the frozen target again. One shared fee is earned only on a valid issued ruling and is bounded by the frozen ceiling, derived from planned seats and base pay per seat. The paper’s shared-budget reservation rule assigns available ETH subsidy in successful fee-commitment execution order, after the group meets its existing admission and funding-readiness conditions. Earlier obligations cannot be preempted, and later deposits or returned reserves do not resnapshot that commitment. The paper's common-pot accounting applies to every contested group: reserve the maximum liability before drawing or seating, use pool funds first and deduct only the actual shortfall once from the common pot, without an additional replenishment wait. Unused pool reserves return to the pool when the fee is determined, while unused common-pot reserves remain locked until chain finality. The paper’s [Public appeal funding](../../#sec-appeal-funding) governs the ideal inverse-absolute-error allocations and actual whole-wei payouts for all fully funded distinct positions against the actual ultimate final score of the same chain. Each ideal position amount is rounded down to whole wei under that rule. At chain finality, the resulting aggregate rounding residual is credited exactly once to this same pool’s ETH jury-service budget, without waiting for payout claims; it is not spendable pool funding before finality. Each rounded position amount remains assigned to its backers and cannot be swept into the budget merely because it is unclaimed. Backer entitlements follow the paper’s cumulative rounded-interval rule in fixed funding-acceptance order. A funded position’s intervals partition its full accepted target and distribute its entire rounded position payout without a second residual or another pool credit. Each record retains its own integer entitlement regardless of claim order, can be claimed only once, and remains assigned if unclaimed; an address’s entitlement is the sum across its records. Anyone may trigger an already-claimable payout under the paper’s standing receiving-address rule. Each transfer uses the current receiver for the original recorded backer and paying contract. Ownership and the calculated amount do not change; a failed transfer leaves the unpaid entitlement reserved and retryable, with the current receiver resolved again on retry. The authenticated update interface, cryptographic format if used, replay-protection representation, transfer isolation, batching and record representation remain open. That final score is not rounded to the appeal grid for settlement. When all errors are positive, each weight is the reciprocal of its absolute error, normalized across positions without adding an artificial error floor. A unique exact prediction receives the entire net pot. The existing two-position formula follows as a special case. When all errors are positive, a closer position has a larger ideal unrounded allocation and equal errors have equal ideal allocations. Whole-wei round-down can make unequal ideal allocations pay equally or a small positive allocation pay zero; a closer position can still lose principal after fees. One position per numeric score precludes separate exact-match positions. The exact-match branch allocates the entire net pot to that position with no position-rounding residual; the same cumulative contribution-interval rule distributes that entire allocated payout among its backers. Its discrepancy from ideal proportional allocation is less than one wei per accepted contribution, not per person or address. Adjacent splitting is neutral, while interleaved contributions and funding order can change rounding outcomes; no identity-splitting resistance is established.

A quorum-failed appeal attempt produces no new score, jury fee or curator reward subsidy. A nonempty drafted attempt must complete the full post-reveal leak-proof period and retain its own round collateral until that period ends before cancellation and retry. The contested level then retries with a fresh draw at the existing cadence without a retry-count or elapsed-time limit, keeping its membership, fixed scores, funding terms and reservations. Failed quorum neither spends nor releases reserves, reopens admission or fundraising, resets either deadline nor requires top-ups. Ordinary non-participation penalties, pre-reveal leak handling and release of valid participants' utility-token round locks still apply after the proof period under the existing cancellation rules. A successful leak reporter still receives the utility tokens actually confiscated under the paper's rule; failed quorum creates no ETH service fee to redirect. These unlimited appeal retries do not alter the reference profile's separate initial-round retry limit.

Issuance and ruling finality are distinct. An issued ruling opens its appeal window and may be appealed again without a fixed depth limit using fresh funds. After the earned jury fee is deducted, the remaining adjudicated backer capital stays locked until the whole chain ends; the terminal score determines payouts at every adjudicated level using that level's own common pot, recorded positions and contribution records. Funds from different levels are not combined. Intermediate scores create no fixed or withdrawable backer entitlement. Payouts become claimable immediately at chain finality, and later ordinary rounds or separate chains cannot reopen that terminal reference. A later jury cannot charge earlier funds. Absent the explicit pre-contest terminal-exit exception, with no admitted proposals a ruling becomes final at admission closure. The admitted-but-zero-funded case follows the funding-outcome rule above.

The paper’s [Public appeal funding](../../#sec-appeal-funding) owns the common claim-execution and standing receiving-address rules for internal ETH jury-service fees, including successful leak-reporter fee redirects, and relevance-appeal backer payouts and refunds. Anyone may trigger an already-claimable payment without new per-payment approval or signature. There is one current receiving address for each original recorded recipient and paying contract, defaulting to the original recipient and applying to every currently unpaid and future entitlement within this scope. The original recipient remains the owner.

Only that original recipient may authentically update the receiver or reset it to itself, without a prior failed transfer. The receiving address gains neither ownership nor authority over future routing; a caller, operator or prior receiver cannot authorize or select a replacement. If the original recipient is a contract, only the contract through its authorized mechanism may update routing, with no authority inferred for a supposed human controller or recovery administrator. Superseded update instructions are rejected, and instructions cannot be reused for another original recipient, paying contract or chain.

Every payment resolves the current receiver at transfer time, not at accrual. Atomic on-chain execution order resolves races: payment before update uses the old receiver, while update before payment uses the new one. A stale destination or per-claim grant cannot override current routing. A later update cannot redirect an already successful settlement. The rules preserve ownership, amount, unlock time, funding, finality, refund eligibility and rounding and create no caller fee or reimbursement entitlement. A successful transfer satisfies the entitlement once. A failed transfer does not satisfy it, release the unpaid reservation or charge the source again; the unpaid entitlement remains reserved and retryable, and retry resolves the then-current receiver. Automatic distribution is not required. These rules do not apply to author bonds, beneficiary or registry claims, utility-token rewards or stake withdrawals. The authenticated update interface, cryptographic message format if used, nonce or other replay-protection representation, transfer isolation, batching and record representation remain open; no batch atomicity is selected.

From issuance, any open admission window or active appeal blocks new ordinary rounds for that nomination, even before a proposal is filed. The hold does not cancel an already-started round or block an appeal jury or another nomination; it does not authorize a second ordinary round for the same nomination and pool. The current score retains its funding role until a valid new jury score or qualifying final forfeiture score exists; mere retention does not establish finality or release adjudicated capital; the explicit finality conditions above govern, including the zero-funded outcome. Independent accuracy, eligibility, withdrawal and other funding rules still apply. Repeated appeals or quorum failures can lock capital and ordinary scheduling indefinitely. Where a profile specifies recurring ordinary reassessment, the paper's post-hold rule makes the next ordinary round eligible one full pool cadence after the last applicable hold ends. It discards missed occurrences rather than replaying a backlog, remains subject to ordinary funding and eligibility, and restarts from the end of any subsequent applicable hold. Closure recognition and refund or payout collection cannot move its protocol-time anchor. The reference batch profile still specifies only one initial relevance round per nomination and its allowed quorum retry for an otherwise eligible active nomination; no fresh ordinary retry may be drawn after terminal exit, and this resumption rule does not add recurring rounds to it or change appeal-retry timing. Target rounding, numerical representation of the defined formulas, the authenticated update interface, cryptographic format if used, replay-protection representation, transfer isolation, batching, record representation and other exceptional cancellation rules must still be specified before implementation is complete. Position-level whole-wei rounding, its same-pool ETH residual destination, cumulative contribution-interval backer payouts and per-curator utility-token reward rounding with its separate same-pool token residual follow the paper.

The paper’s [Public appeal funding](../../#sec-appeal-funding) owns shared ETH budget allocation: each otherwise eligible fresh ordinary or appeal fee commitment atomically checks unencumbered funds and reserves its pool-funded portion. Successful reservation execution order determines who obtains the available subsidy. Earlier reservations, earned unclaimed fees and other obligations are excluded and cannot be preempted. Filing, readiness, due time, off-chain intent and broadcast alone create no reservation. Existing relative scheduler order for ordinary rounds and appeal admission and funding-readiness requirements remain unchanged. Insufficiently funded ordinary work still follows its existing rules; an appeal instead covers its shortfall from its own common pot without waiting for replenishment. Later deposits or released reserves do not replace completed funding snapshots, and existing appeal-retry reservations and source-specific release rules remain intact. Faster inclusion can capture subsidy and leave unreserved ordinary work waiting; this is not a fairness or security guarantee.

Each ordinary scheduled relevance round reserves one `roundRewardFloor` in ETH from the pool's curation budget. This maximum service-fee reservation follows the paper's planned-seat and per-seat-rate rule; it is not an independent total-budget parameter or a utility-token reserve. The actual service-fee ceiling uses the drawn count, which may be lower, and unused seat capacity is returned under the round's finalization or cancellation rule. When a valid ruling is issued, every timely valid revealer has a fixed gross ETH fee for each originally drawn seat that its report represents, regardless of its score, coherence or the round's dispersion. A successful leak claim included and validated before the paper's exclusive proof cutoff overrides the violating curator as recipient before issuance fixes the allocation: the reporter receives that curator's whole otherwise-earned ETH fee for the round, across all of its represented seats, together with the utility tokens actually confiscated. No fee is created when the violating curator otherwise earns none. The override changes the recipient, not the total charge, and cannot create a duplicate payment or a refund to the funding source. Multiple seats multiply the service fee even though the curator submits one report. Nonparticipants and late or invalid revealers earn no fee, and no fee is earned on a quorum-failed attempt. Unpaid seat fees are not redistributed to other jurors. Unused ordinary-round ETH reservation returns to the pool curation budget; unused appeal funding follows its existing source-specific reservation and pot rules, with any remainder in the appeal pot staying there until chain finality. Earned ETH service fees become claimable for their original recorded recipients and payable to their current configured receiving addresses, after the proof period has ended and any successful leak-reporter override has been applied, in the same valid-ruling issuance transition under the paper's Relevance layer, without waiting for an appeal window, chain finality or another participant. A later appeal score change does not reduce or claw back the earned fee. Unclaimed fees remain committed to their assigned juror or reporter recipients outside the fee-adjusted backer pot; collection does not charge the funding source again. Anyone may trigger an already-claimable fee payment under the paper’s standing receiving-address rule. It resolves the current receiver for the original recipient and paying contract without changing ownership, amount or unlock time. A failed transfer leaves the unpaid entitlement reserved and retryable using the receiver current on retry. The authenticated update interface, cryptographic format if used, replay-protection representation, transfer isolation, batching and record representation remain open, and immediate withdrawability does not mandate an automatic transfer. If an ordinary round fails quorum and is cancelled, its ETH reservation is released back to the curation budget before any retry or later round is scheduled. Curators score nominations one at a time, and the protocol normalizes across all eligible nominations in the pool. Ordinary scheduled relevance-round service fees are funded from the pool's ETH curation budget, which SHOULD be reserved as a percentage of the pool's total funding budget before allocation scoring begins (suggested default: 5% of pool funding budget reserved for curation costs). Under the reference profile, the nomination cap and curation budget bound planned initial ordinary-round liability using one `roundRewardFloor` per nomination. The cap is not a reservation: competing eligible commitments may consume unencumbered budget before an ordinary round reserves it. This does not create a separate allocation priority. Utility-token coherence rewards follow the paper's separate redistribution rule and have no base subsidy or minting. A curator's stake slice is its utility-token capital at risk in the round, equal to its effective voting weight, and cannot be added to an ETH service fee. Appeal-jury fees use available ETH pool budget first and deduct only the ETH shortfall once from the common pot of fully funded opposing positions, as specified in [Public appeal funding](../../#sec-appeal-funding). A depleted pool does not impose an additional replenishment wait on those appeals. The ordinary-round reserve amount and cancellation rule do not calibrate the appeal contribution multiplier or per-seat rate, or determine the remaining transfer mechanics. Shared-budget subsidy allocation instead follows successful reservation execution order under the paper. The paper's score-retention rule applies while awaiting a valid new score and after a group ends without one.

The pool's **relevance policy** defines the scoring question and rubric. Example:

> "Score each impact nomination from 0.0 (no value to this pool) to 1.0 (critical contribution) based on: usage scale, downstream adoption, ecosystem dependency, cost efficiency, and uniqueness of contribution."

**Double-counting and attribution**: when multiple nominations claim credit for the same downstream effect, the relevance layer handles it through scoring. The relevance policy SHOULD instruct curators to consider uniqueness of contribution and discount overlapping claims across nominations in the same round. No protocol enforcement of exclusive attribution. Limitation: the coherence game rewards consensus on scalar scores, not accurate causal attribution. If curators do not notice overlap, multiple nominations may receive overlapping credit for the same downstream effect. This is an accepted limitation.

Broad pools (covering heterogeneous project types) are allowed. The relevance policy rubric is responsible for making comparisons meaningful. A poor rubric can produce poor scores. The design hypothesis is that users who recognize persistent quality differences can migrate to funded alternatives with better curation, allowing bad pools to lose participation. Public policies and outcomes make inspection possible but do not establish that users can identify better curation. Exit can face historical-record comparison costs, funder coordination costs and round-cycle capital commitment (see Open Problems: Pool migration friction); the reputation score creates no eligibility lock.

## Challenge Incentives

Debunking a false impact nomination during holdback **redirects funds** to legitimate nominations. Under the payout rules above, a successful challenger also captures the author's fixed bond, while the challenge tax and external DDR fee remain sunk challenger costs. This creates a competitive challenge incentive with two components:

- **Fixed debunking bounty**: the challenger receives the author's bond `B` if the nomination is debunked.
- **Competitive redirection**: funds that would have gone to a false nomination are redistributed to surviving nominations, including potentially the challenger's own nomination.

This is a double-edged sword: competitive dynamics also enable **strategic challenges** (filing challenges to suppress rival nominations). To reason about that incentive, define:

- `P`: pool funding budget
- `a`: challenger's provisional funding share before debunking
- `b`: challenged nomination's provisional funding share
- `B`: fixed author bond
- `c`: counter-stake ratio
- `S_min`: minimum challenge stake
- `S = max(S_min, c*b*P)`: challenger counter-stake
- `t`: challenge tax rate
- `T = t*b*P`: challenge tax
- `F`: external DDR fee paid by challenger and not refunded by the protocol
- `p`: probability that DDR debunks the challenged nomination

The calculation assumes `P > 0`, `0 < b < 1`, `0 <= a <= 1-b`, nonnegative costs, fixed relative scores among survivors, and a challenger nomination eligible to receive the supplementary redistribution. It ignores delay, opportunity costs and external payoffs. If the target is the sole funded nomination, the `1-b` denominator vanishes and this example does not apply. The zero-survivor rollover rule governs that case instead.

If the challenge succeeds, the challenger's incremental upside is the fixed bond plus the redirection gain from removing the challenged nomination:

`U_success = B + a*b/(1-b) * P - T - F`

If the challenge fails, the challenger loses the counter-stake and still bears the tax and DDR fee:

`U_fail = -S - T - F`

The full expected value is therefore:

`EV = p * (B + a*b/(1-b) * P - T - F) + (1-p) * (-S - T - F)`

The break-even success probability is piecewise because the minimum challenge stake may bind:

- If `c*b*P >= S_min`, then `S = c*b*P` and `p* = (c*b*P + t*b*P + F) / (B + a*b/(1-b) * P + c*b*P)`.
- If `c*b*P < S_min`, then `S = S_min` and `p* = (S_min + t*b*P + F) / (B + a*b/(1-b) * P + S_min)`.

Worked reference example: let `P = 100 ETH`, `a = 0.30`, `b = 0.30`, `B = 0.01 ETH`, `c = 0.25`, `S_min = 0.01 ETH`, and `t = 0.005`. The proportional branch binds because `c*b*P = 7.5 ETH > S_min`. The challenge tax is `T = 0.15 ETH`, and the redirection gain on success is `a*b/(1-b) * P = 12.857 ETH`. Therefore:

- `U_success = 12.717 ETH - F`
- `U_fail = -7.650 ETH - F`
- `EV = p * (12.717 - F) + (1-p) * (-7.650 - F)`
- `p* = (7.650 + F) / 20.367`

The strategic result is local, not universal. Challenge profitability depends on absolute pool size `P`, concentration `a`, target share `b`, fixed bond `B`, fee burden `F`, and whether the minimum-stake floor binds. Small pools and small nominations are dominated by fixed costs; large concentrated nominations are more exposed to strategic challenge. The one-active-nomination-per-registry-entry rule limits direct fragmentation, but an actor controlling many registry entries can still lower the effective break-even. Registry quality and Sybil resistance remain the deeper constraints.

**Limitation: pure challengers face negative expected value in this example.** The competitive redirection term `a*b/(1-b)*P` requires `a > 0`: the challenger must hold a nomination in the same pool. A pure third-party challenger with no nomination (`a = 0`) reduces to `U_success = B - T - F`. Under reference parameters, `B = 0.01 ETH` and `T = 0.15 ETH`, so `U_success = -0.14 ETH - F`: negative even on a winning challenge. This means challenge incentives under reference parameters are operative only for competing nominees, not for independent watchdogs. Under these parameters and the modeled monetary payoffs, profitable challenge depends on an eligible competing nominee with sufficient expected redirection gain. An independent watchdog may still act for external reasons, but the model supplies it no profitable protocol-funded path in this example.

Three levers could widen the challenger base if empirical deployment shows the nominee-only incentive is insufficient: (1) raising the fixed bond `B` above `T + F` so pure challengers at least break even on success; (2) refunding the challenge tax on successful challenges so the sunk cost is only the DDR fee; (3) introducing an explicit bounty funded from the pool budget for successful debunkings. Each trades off differently against the risk of frivolous challenges. The reference parameters leave this dependence unresolved. Whether a funded pool attracts independent competitors able and willing to challenge requires evidence; it is not established here.

## Funding Distribution

Once the curation layer produces scores for all surviving impact nominations:

```
nominationFunding = (nominationRelevanceScore / sum(nominationRelevanceScore for all surviving nominations)) * poolFundingBudget
```

Allocation is computed per surviving nomination. Because each active nomination references exactly one registry entry in the pool's external project-beneficiary registry, nomination-level allocation induces beneficiary-level allocation through that entry. The formula is straightforward proportional allocation weighted by curated relevance. If no surviving nominations exist, or if all surviving nominations have relevance score `0` so the denominator is zero, no allocation is made and the pool budget rolls over to the next funding round.

Under the master paper's funding-weight interpretation, these relevance numbers express relative funding weights, beyond merely ranking nominations. Among surviving nominations, scores of 0.75 and 0.25 receive a 3:1 allocation ratio under this formula; this does not establish three times the public benefit, causal impact or value of another grant. Each pool creator crafts the rubric to explain its intended numeric meaning, with no protocol-wide default policy. This interpretation concerns nomination funding, separately from curator voting weights and inverse-distance appeal payouts. The surviving-nomination, zero-denominator and holdback rules remain unchanged.

As in the [master paper](../../), full proportional allocation is intentional: if the sole eligible surviving nomination with a positive score has a score of 0.01, it receives the full distributable budget under this formula. The low absolute score does not by itself withhold part of that budget. This creates an intended opportunity for additional eligible nominations to enter and compete under the pool’s rubric, not a guarantee that entrants, better nominations or effective competition will appear. Existing submission windows, registry-entry conditions, challenges and holdbacks still apply; an allocation is not an immediate unconditional payment.

Design note: bond-time is not used for scoring. All nominations are submitted within the same round window, so time-in-system does not differentiate meaningful exposure to challenge. Relevance score alone drives allocation.

The formula is deterministic conditional on its inputs, but those inputs depend on the pool's relevance policy (a governance surface defined at pool creation) and the coherence game output. No additional governance beyond pool creation is needed for the allocation step itself.

## Registry Entry Reputation

Registry-entry reputation is a pool-scoped integer that starts at zero and summarizes recorded nomination outcomes. It attaches to the external registry entry rather than to the transient submitting account. It is historical information, not a finding that a person is honest or dishonest, and does not determine submission or funding eligibility.

- **Earning**: +1 per funding round in which the entry's nomination survives without debunking.
- **Debunking record update**: -5 per debunked nomination.
- **Decay**: absolute value reduced by 1 per epoch (suggested default: 30 days), drifting toward zero over time. Old history fades.
- **Negative reputation**: the recorded score can go below zero; that value does not restrict a fresh nomination or substitute for adjudication of its claims.

The existing earning, debunking and decay updates remain accounting rules for that historical score. Returning to zero is not a prerequisite for submitting a new nomination: there is no reputation-based exclusion or recovery cooldown. Whether the displayed history influences participants is an empirical question, not a guaranteed economic deterrent.

Reputation does not weight curation scores or allocation and MUST NOT impose a minimum threshold, ban or cooldown for a new nomination. Interfaces may display it as historical context alongside the nomination; it does not replace assessment of that nomination’s claims and evidence. The same nominator may submit again under the ordinary window and active-entry rules, while the previously debunked nomination remains closed.

## Pool Creation

Pool creation is permissionless: any address can create a funding pool. The pool creator defines:

- **Pool parameters**: submission window duration, holdback period, bond amount, challenge costs, curation budget, coherence game parameters.
- **Project-beneficiary registry reference**: an external curated registry whose entries define eligible beneficiaries and claimant policy for nominations.
- **Nomination template**: structural and semantic requirements for nominations, including eligibility criteria and required evidence types.
- **Evidence policy**: admissible evidence classes, freshness rules, sufficiency standards, and tie-break logic for DDR disputes.
- **Relevance policy**: the scoring question, rubric, and any domain-specific instructions for curators.

These policy objects and dependency references are versioned by content hash. Nominations submitted under one pool version remain bound to that version permanently. Pool parameters are immutable after creation; if a pool's design proves flawed, the correct response is to create a new pool with better parameters, not to upgrade the existing one. Pool design is not screened by a protocol-level governance gate; whether poor designs lose participation is the conditional exit hypothesis discussed below.

## Reference RPGF Pool Profile

| Parameter | Suggested Default |
|---|---|
| Domain | Retroactive public good funding for a specific ecosystem |
| Project-beneficiary registry | External curated registry referenced by the pool |
| Impact nomination submission window | 30 days per funding round |
| Holdback period | 30 days after provisional allocation |
| Author bond | 0.01 ETH per impact nomination (flat; `pool.submissionBondWei`) |
| Challenger counter-stake | `max(0.01 ETH, 25% of challenged nomination's provisional share)` |
| Challenge tax | 0.5% of challenged nomination's provisional share |
| Curation budget reserve | 5% of pool funding budget |
| Max nominations per round | `curationBudget / roundRewardFloor` (derived initial-liability bound; actual fee reservations secure funding against other commitments) |
| Relevance round cadence | One initial round per nomination during the evaluation period; one retry on quorum failure |
| Relevance round target size | 15 seat-tickets drawn |
| Reveal quorum | At least 80% of originally drawn seat weight; no curator-count minimum |
| Dispersion floor (epsilon_sigma) | 0.02 (below this: mean accepted, no distance-based slashing or resulting utility-token coherence reward; fixed ETH service fees are still earned for a valid issued ruling) |
| Seat size (L) | L units of the dedicated utility asset; each drafted seat locks L utility tokens; no ETH conversion or numerical calibration is specified |
| Utility-token coherence reward | Actual integer distance-based penalties only, redistributed with per-curator round-down and a remainder to the same pool’s separate utility-token balance under the paper; no base reserve or minting |
| ETH service-fee allocation | Fixed gross fee per originally drawn seat represented by a timely valid reveal in a valid issued ruling; successful leak reports redirect the violating curator's fee to the reporter under the paper's rule; unpaid seat fees are not redistributed |
| Reference ETH service fee per seat | Provisional reference rate defined in the paper’s [Relevance layer](../../#relevance-layer); positive pool-specific rates are fixed at creation |
| Ordinary round service-fee reservation | Planned ordinary jury size multiplied by configured ETH base pay per seat; funded from pool curation budget |
| Commit window | 48 hours |
| Reveal window | 48 hours |
| Leak-proof opening period | Positive duration frozen for the round, following its fixed reveal deadline under the paper's rule; provisional default defined in the paper's Relevance layer |
| Relevance coherence threshold K | 1.25 (also governs graduated slashing gradient) |
| Registry-entry reputation: initial value | 0 |
| Registry-entry reputation: surviving round reward | +1 per round |
| Registry-entry reputation: debunking record update | -5 per debunked nomination; historical information only |
| Registry-entry reputation: decay | absolute value reduced by 1 per 30-day epoch (drift toward 0) |
| Curator exit | No cooldown for utility-token curator balance not committed to active rounds; separate ETH appeal contributions retain their lock after curator exit |
| DDR timeout | 90 days (funding rounds have deadlines) |

### Parameter Calibration Status

These defaults are reference-pool starting points, not empirically validated optima. The table above specifies starting parameters for the ordinary-round rules of an initial RPGF pool. Public appeal crowdfunding still requires the settlement terms identified in the paper before the complete mechanism can be implemented and analyzed end to end. It should not be read as claiming that the listed values have already passed formal calibration or sensitivity analysis.

Challenge-cost parameters (counter-stake ratio, challenge tax, author bond) are partially grounded by the challenge incentive analysis above: the worked example shows how they interact to determine break-even success probabilities. But the analysis is local to one parameter configuration and does not identify robust optima across heterogeneous pool sizes, DDR fee regimes, or nomination value distributions.

Relevance-game parameters are inherited from the paper's coherence game design. Fee planning uses the paper’s provisional active-assessment workload for one juror representing one seat on one item, without treating it as measured effort or quality or adding a deadline, evidence, logging or payment condition. The provisional reference ETH rate follows the paper’s [Relevance layer](../../#relevance-layer); a pool may choose another positive rate fixed at creation. Initial and appeal service use the same rate, and a reference-default change neither retrofits existing pools nor establishes a fiat peg. Multiple represented seats still multiply pay without implying proportional additional work. Seat size L controls utility-token eligibility granularity and capital locked per seat: a high L excludes small curators, but no choice of L alone caps a curator's share of seats. It has no specified ETH conversion. K governs both the coherence threshold and the graduated penalty slope. Weight concentration depends on the eligible utility stake distribution and the draft; draw-and-lock bounds each curator's coherence-slashing exposure by its funded seats but does not prevent one curator from holding all drafted seats. The dispersion floor determines when distance-based slashing is skipped. Utility-token coherence rewards redistribute those penalties only, without a base reserve or minting. The single-asset analytical reward model uses `rho` and `f_reward` for smooth reward scaling; those parameters do not govern the selected fixed ETH service fee or validate the two-asset design. Paying a timely valid report does not verify research effort or accuracy. Utility-token exposure must remain economically meaningful relative to the fixed ETH fee; no robust calibration or equilibrium result is established here. The public-crowdfunding appeal layer is inherited from the paper. Its independent score positions, bounded admission, common ETH pot and inverse-absolute-error payout rule are summarized above. Target rounding, numerical representation of the defined formulas, non-default multiplier calibration, the authenticated update interface, cryptographic format if used, replay-protection representation, transfer isolation, batching, record representation and settlement for other cancellations are not settled by this reference profile. Shared-budget subsidy allocation follows the paper’s successful-reservation execution-order rule. The paper specifies position rounding, cumulative contribution-interval backer payouts and per-curator utility-token reward rounding with its separate same-pool token remainder; permissionless triggering, original-recipient-controlled standing receiving addresses and retryable unpaid entitlements after failed transfers are specified, while the remaining update and transfer mechanics and record representation remain implementation work. The profile table therefore does not supply a complete appeal implementation checklist. No RPGF-specific equilibrium analysis has been conducted for these parameters or the two-asset design.

The existing reputation update and decay parameters determine how nomination outcomes appear in the historical summary. They do not impose exclusion or a recovery period before a fresh nomination. Whether this presentation of history helps participants assess later claims, and how it interacts with round frequency and heterogeneous projects, remain unvalidated.

Accordingly, these are starting defaults for the specified ordinary-round rules of a reference RPGF pool and support the illustrative calculations. They do not complete the appeal settlement specification or establish robustness or optimality. The same three categories of sensitivity work identified for the news instantiation apply here: one-at-a-time sweeps, joint sweeps for coupled parameters, and adversarial tests.

## Differences From News Instantiation

The following table compares the RPGF instantiation with the thesis's other instantiation (a continuous news-curation protocol) to highlight domain-specific adaptations.

| Aspect | News | RPGF |
|---|---|---|
| Challenge unit | Whole article blob | Whole impact nomination |
| Bond model | Author-chosen (no protocol minimum) | Flat per-nomination bond (spam filter; holdback is the real deterrent) |
| Direct adverse consequence of debunking | Bond loss | Bond loss and removal of the nomination's funding share |
| Challenge incentive | Debunking reward only | Debunking reward + competitive fund redirection |
| Challenge types | Debunking, NonFalsifiable, ScopeViolation, TemplateViolation | Debunking, NonFalsifiable, TemplateViolation (scope via template eligibility) |
| Time horizon | Continuous (claims live indefinitely) | Batch (funding rounds with submission windows) |
| Cadence | Pool-defined; weekly in the reference profile | Per-round evaluation period |
| Relevance question | "How important is this for the feed?" | "How valuable is this impact for the pool's mission?" |
| Attribution | Not applicable (each claim is independent) | Relevance layer handles overlapping credit |
| Comparability | Ranking only (feed position) | Budget-share allocation (proportional funding) |
| Nomination lifecycle | 6 states; continuous with edit/withdraw | 7 states; batch-phased, edits only during submission window |
| Challenge payouts | Complex payout matrix | Single tax at filing; loser's stake to winner in full; challenger-paid DDR fee remains sunk |

## Open Problems

### Reward padding

The main paper's Curator voting strategy section demonstrates reward padding in a single-asset analytical model with a dispersion-scaled base subsidy. The illustrated gain is absent under the selected two-asset rules: that example collects no eligible utility-token penalty, and changing the reported score while keeping the same timely valid reports and represented seats cannot increase the fixed ETH service fee. This closes that specific subsidy-padding channel; it does not establish truthful reporting, meaningful research effort or an honest equilibrium. The example also does not calculate net returns after public crowdfunding and appeal settlement. A complete two-asset incentive analysis, including the economic value of utility-token exposure relative to ETH compensation, remains necessary, tracked in [issue #141](https://github.com/0xferit/manuscript-decentralized-curation/issues/141).

### Leak-reporter incentive boundary

The paper's successful-report rule transfers the actual confiscated utility tokens and the violating curator's otherwise-earned ETH fee to the reporter. Denomination and recipient assignment are therefore specified, but they do not establish an effective deterrent. The paper caps confiscation at remaining collateral for the offending round plus unlocked utility-token deposits, excluding all other active-round locks and amounts already confiscated or transferred. A lower available balance reduces the collected penalty rather than creating debt, requiring a top-up or removing another round's backing. Self-reporting or collusion between leaker and reporter remains an incentive risk. The selected fixed proof-opening period supplies a minimum opportunity after reveal closure, with the provisional duration defined by the paper. Reliable proof validation, inclusion before the cutoff, transaction censorship and delayed execution of the post-cutoff transition remain implementation risks. This profile introduces no identity restriction or additional proof extension to resolve them.

### Registry quality and beneficiary mapping

The RPGF mechanism assumes an upstream curated project-beneficiary registry. If that registry misidentifies beneficiaries, allows duplicate or captured entries, or applies weak claimant policy, the funding layer inherits those errors. Duplicate suppression, beneficiary routing, and cross-round reputation are only as strong as the registry's curation quality. This file treats the registry as a prerequisite abstraction rather than specifying its governance or dispute system.

### Comparability limits

Relevance scoring with normalization may produce unintuitive allocation results across very different project types (a developer tool vs. a research paper vs. core infrastructure). The relevance policy must be specific enough to make these comparisons meaningful. If it is not, scores may be noisy or systematically misleading. Pool scoping limits the direct allocation effects to that pool, but does not establish graceful degradation or prompt migration to better pools.

### Competitive challenge dynamics

The competitive redirection incentive is intended to improve challenger participation, but its effect is unvalidated and it creates an adversarial surface: projects have a direct financial incentive to challenge competitors. Monitoring challenge patterns, adjusting challenge costs, and interface-level reputation signals for challenge behavior may be needed in practice.

### Counterfactual impact

This profile supports documented output claims ("we built X"). A narrative such as "X prevented Y from happening", without a specified causal comparison or evidentiary test, is not testable as stated. A nomination that contains no testable assertions under the template and evidence policy is challengeable as `NonFalsifiable`. Counterfactual quantities can sometimes be identified and estimated from observed data under explicit assumptions. For example, Dahabreh et al. identify population counterfactual outcome means using randomized trials nested in cohorts [@dahabreh2019generalizing]. Identification under assumptions does not establish that those assumptions are empirically testable, or that a particular RPGF claim meets this profile's evidence rules. The profile does not specify standards for adjudicating such causal estimates; absence of supporting evidence alone does not make an assertion unfalsifiable.

Curators can score submitted output claims and their available evidence under the mission policy without establishing counterfactual impact in advance. Template and evidence requirements remain grounds for the existing challenge process. Scoring occurs before holdback challenges; successful adjudication then removes that nomination’s provisional allocation and forfeits its bond under the payout rules. Thus the scoring mechanism can operate without prior causal verification, while non-falsifiability remains challengeable. Relevance scores express policy-conditioned valuation and do not establish incremental causal benefit.

### Scoring order effects

Curators score nominations sequentially (one relevance round per nomination). Earlier-scored nominations may anchor expectations for later scores. The coherence game rewards convergence to the committee mean, but that mean shifts as the evaluation period progresses. Randomizing scoring order is a possible mitigation to test, not an established remedy or an additional scheduling rule selected here.

### Double-counting as strategic exploit

When multiple nominations claim credit for the same downstream effect, the relevance layer handles it through scoring. However, colluding actors can strategically engineer overlapping claims to extract double allocation if curators fail to notice the overlap. The evidence policy SHOULD require explicit attribution statements that make overlap detectable, but protocol-level enforcement of exclusive attribution is not feasible.

### Reputation decay and long-term memory

The numeric reputation score decays toward zero and therefore compresses distinctions between past nomination outcomes. Interfaces should not present a zero score as proof of no adverse history or proof of trustworthiness. This is a limitation of the historical summary, not a reason to block future nominations; no additional reputation formula or eligibility gate is selected here.

### Pool migration friction

The "bad pools fail locally" dynamic depends on participants exiting bad pools at a pace that limits misallocation. Three compounding friction sources slow this exit:

1. **Historical-record comparison**: the reputation summary is pool-scoped, so participants may find records from different pools difficult to compare. Any effect on willingness to migrate is social and unmeasured; the score itself imposes no submission restriction or loss of nomination rights.
2. **Funder coordination failure**: a better pool with no funding is useless. Funders must collectively migrate for a new pool to be viable, which is a coordination problem that individual exit does not automatically solve. A critical mass of funders must move roughly simultaneously, and each funder's incentive to move depends on whether others have already moved.
3. **Round-cycle lock-in**: pool parameters are immutable and rounds last ~60+ days (submission window + holdback). Capital committed to a round cannot move to a competing pool until that round completes. This temporal lock-in means that even if participants recognize a pool is bad, funds already in-flight are irrecoverable for the current round.

These frictions leave exit possible but limit the claim that it selects better curation. "Bad pools fail locally" is a design aspiration that depends on recognizable quality differences, short rounds, low minimum viable pool sizes, and sufficient funder coordination. Deployments should monitor pool concentration and exit rates as empirical signals of whether the dynamic functions as hypothesized.

### DDR dependency

The accuracy layer delegates adjudication to an external DDR provider (Kleros v1). If the external court is captured, lazy, or inaccurate, the accuracy layer inherits that degradation. In the RPGF context, this risk is amplified relative to the news instantiation because challenge outcomes directly redirect funding: a single corrupted DDR ruling can redirect a nomination's entire provisional share. The main paper's analysis of inherited DDR dependency applies here with higher stakes per ruling. The 90-day timeout fallback addresses only DDR liveness (non-resolution); it does not mitigate capture or inaccuracy and actually defaults unresolved disputes to author victory, converting stalled challenges into false negatives. This design does not independently model DDR capture cost or correctness-layer mitigation.

### Pool bootstrapping

A new RPGF pool requires curators staked and ready before the first evaluation period, a funded curation budget before nominations can be scored, and enough nominations to justify curator participation. These three dependencies create a bootstrapping coordination problem: curators may be reluctant to stake without content, nominees may be reluctant to submit without curators, and funders may wait for both. The design does not specify a bootstrapping mechanism. Whether the permissionless pool creation model can produce viable pools without external coordination (e.g., a foundation seeding the initial pool) is an open empirical question.

## FAQ

### Why not use Gitcoin or Optimism RPGF directly?

This proposal is an alternative to preference-based allocation when a funder wants contestable claims and a public relevance rubric. Preference aggregation and coherence scoring can both diverge from public benefit. The proposal must therefore be evaluated against a specified alternative on evidence quality, participation cost and funding outcomes; the mechanism alone does not establish superiority over existing programs. Whether policy-faithful judgments are individually optimal under the full reward and appeal rules also remains unresolved.

### Isn't asking voters to judge public benefit paternalistic?

No. Voters are not forbidden from having preferences. The mechanism simply does not reward them for expressing preferences. It rewards them for making judgments that are coherent with others applying the same public rubric. The claim is not that voters are ignorant; it is that standard voting structures incentivize strategic or self-serving behavior even when voters know better.

### What is a coherence game and why does it help?

A coherence game rewards agreement among independently committed reports. A specific public rubric can supply a substantive focal point: curators seek to anticipate judgments based on the same criteria. Claim 3 in the main paper demonstrates a unilateral reward-increasing report in its single-asset analytical model. That particular gain does not carry over to the selected utility-token redistribution and fixed ETH service fee: the example collects no eligible token penalty, and the same represented seats retain the same service fee. This observation is not a test of the two-asset design's full incentives. Signal concentration and truthful best responses are distinct questions.

The main paper's simulated collusion results concern specified single-asset models, not the two-asset design. They provide no proven boundary for honest equilibrium and have not been calibrated for RPGF. Here, allocation incentives can create additional reasons to distort scores; an RPGF-specific strategic analysis remains necessary.

### How does the design address beauty-contest incentives?

The mechanism retains beauty-contest incentives: participants are rewarded for anticipating other curators' judgments, including those of an appeal committee. The public, versioned rubric is intended to make policy-based judgment a focal point and reduce arbitrary coordination. It does not eliminate higher-order beliefs or establish that participants select a policy-faithful equilibrium. Even establishing one truthful equilibrium would not establish its uniqueness or selection; peer-prediction research treats these as separate problems [@kong2016peerprediction]. Strategic reporting and coordination failures remain possible; the main paper's single-asset simulation results do not establish a security threshold for this two-asset design.

### Who controls the scoring rubric?

No one exclusively. Any address can create a pool with its own public relevance policy. Pool parameters are immutable after creation. Pool scoping contains the direct effects of a bad rubric. Whether poor pools lose participation depends on users recognizing quality differences and coordinating migration; adoption alone does not establish rubric quality.

### Why is permissionless pool creation better than governance?

Governance centralizes value disputes. Every disagreement about what counts as a public good becomes a political fight over control of a shared mechanism. Permissionless pools let participants choose among explicit, auditable rubrics without changing a shared policy. A bad pool's direct allocation decisions remain local, and participants can seek alternatives. The further claim that competition selects better curation is a conditional hypothesis: it requires recognizable quality differences, funded alternatives and feasible migration.

### What prevents the most marketed pool from winning over the best one?

The design does not prevent this. Permissionless creation keeps alternatives possible, and public, versioned policies support inspection. Those features do not establish that users can identify higher-quality curation or coordinate migration to a funded alternative. Marketing, network effects and switching costs can still sustain a poorly curated pool.

### How are nominations kept honest?

Nominators may publish bonded claims without prior factual approval, subject to the existing submission window, registry and one-active-nomination rules. Any participant can file typed challenges: `Debunking`, `NonFalsifiable`, or `TemplateViolation`. Disputed nominations are escalated to external decentralized dispute resolution (Kleros). Falsification or non-falsifiability established through a successful challenge debunks that nomination, forfeits its bond and removes its pool-beneficiary right. The nomination stays closed, but its nominator may submit a fresh one under the ordinary rules. Surviving without a successful challenge does not certify truth. The existing evidence requirements govern the challenge process rather than serving as advance factual verification.

### Is this trustless?

The coherence game and nomination layer are designed to be trust-minimized on-chain. The dispute resolution layer relies on an external arbitration system (Kleros v1). The design is explicit about where trust assumptions remain rather than hiding them.

### What is the relationship to the broader curation manuscript?

This RPGF design is a concrete application of the general framework developed in the main manuscript. The manuscript argues that public goods funding is a curation problem, and that curation is better solved by incentive design than by preference aggregation. The RPGF proposal operationalizes that argument.
