---
title: "Decentralized Curation for Public Goods"
subtitle: "A blueprint for contestable assessment and funding"
author: "Ferit Tunçer"
orcid: "0009-0004-1449-9348"
date: 2026-10-25
version: 0.2.0
bibliography: ../../../references.bib
lang: en
status: preprint
papersize: a4
fontsize: 11pt
geometry: margin=24mm
mainfont: Georgia
colorlinks: true
urlcolor: blue
citecolor: black
header-includes:
  - |
    ```{=latex}
    \clubpenalty=10000
    \widowpenalty=10000
    \AtBeginDocument{\hypersetup{linkcolor=black}}
    ```
---

> This preprint presents a proposed design and evaluation agenda, not a completed experiment or a validated deployment.

## Abstract

Public-goods funding requires judgments about what was contributed, which claims are credible and how contributions serve a stated goal. Decentralized Curation proposes using private incentives to support useful information production, assessment and correction. This paper develops an application blueprint in which nominators publish bonded nominations, challengers can earn rewards for establishing false claims or other specified violations, and paid jurors assess relevance under a public policy. It separates factual contestability from policy-relative judgment, and both from the later use of assessment in funding. The main profile supports ongoing curation: relative weights can exist before a beneficiary budget arrives, while subsequent funding follows eligible weights and preserves amounts already earned. We distinguish honesty, care and competence, explain the intended role of private reports and coherence incentives, and identify the conditions under which repeated competition could select for informed judgment. A worked example connects nomination, assessment, appeal, reassessment and funding. The contribution is an application architecture and evaluation agenda. Truthful best responses, reliable competence selection, affordable correction and improved public outcomes remain questions for analysis and testing. <!-- [claim:C048] [evidence:E001,E002,E003] -->

## 1. From a funding decision to a curation problem

A public-goods funder needs answers to different questions. Did the nominated contribution exist? What evidence supports its claimed use? How important is it to the funder's purpose? How should the available money be distributed? A persuasive narrative can influence all these judgments at once, but they need not be settled by the same procedure.

The parent paper, *Decentralized Curation: Trustless Transformation of Information into Knowledge*, proposes a framework for identifying an information problem, selecting the relevant dimensions of quality and designing incentives for each dimension [@tuncer2026decentralizedcuration]. Its central ambition is to make useful assessment and correction privately worthwhile. Public-goods funding is an application of that framework, not its definition. <!-- [claim:C001] [evidence:E001] -->

This paper concentrates on openly usable contributions with diffuse beneficiaries, such as research software, shared standards and maintained infrastructure. Its reference question is how to sustain a credible, revisable assessment of completed and maintained work. Funding can then use that assessment. Whether another grant would produce the greatest additional benefit is a different question and requires a policy and evidence designed for that purpose. <!-- [claim:C002] [evidence:E003,E005] -->

The proposed application separates three operations:

- **Contest a nomination's claims.** A bonded nomination states testable claims and supplies evidence. A successful challenge establishes a false claim or another specified violation and carries a financial consequence for the nominator.
- **Assess relevance.** Jurors judge the contribution against a public goal and rubric. Their reports enter a competitive scoring mechanism.
- **Use the assessment.** A specified allocation rule maps eligible weights to a budget or funding flow. This step need not occur when the weights are first produced. <!-- [claim:C003] [evidence:E001,E003] -->

The contribution is a blueprint connecting these operations while keeping their responsibilities separate. It specifies the information a pool must publish, the participant roles, the lifecycle of an ongoing nomination and the boundaries of its funding claims. It also states an evaluation agenda that can distinguish attractive arithmetic from useful behavior.

### Scope and status

This paper develops the author's current ongoing-funding design. The parent paper, version 1.3.0, establishes the framework's research context and supplies the shared accuracy, jury and appeal rules. This is a design specification and evaluation agenda, not evidence that historical contracts implement every rule. Detailed provenance and remaining implementation questions are in [the source record](https://github.com/0xferit/manuscript-decentralized-curation/blob/public-goods-v0.2.0/projects/rpgf/companion-paper/source-and-open-questions.md). <!-- [claim:C004] [evidence:E001,E002,E003,E010] -->

## 2. What the application must configure

A **pool** is a curation context with a stated purpose, rules, participant balances and, when funded, a distribution budget. A pool does not make its purpose legitimate merely by publishing it. The application must identify whose needs the goal serves and how affected people can question it. A faithfully executed rule can still pursue a poor objective. <!-- [claim:C005] [evidence:E001,E003] -->

The parent framework supplies the decomposition and candidate mechanisms. The public-goods application must supply the following domain choices. These must be readable before anyone commits capital or effort.

| Configuration | Question the application must answer |
| ------------------------- | --------------------------------------------------------------------------- |
| Goal and scope | Which contribution, beneficiaries and time horizon are being assessed? |
| Nomination template | What work is nominated, which claims are testable and which evidence is required? |
| Attribution | How are shared work, overlapping nominations and beneficiary identity handled? |
| Relevance rubric | What does a score mean, including its intended use as a relative weight? |
| Accuracy process | Which violations can be challenged, who bears the burden and which Kleros-like court decides? |
| Participation economics | What capital, service funding, costs and penalties apply to each role? |
| Lifecycle | When are changes permitted, when may challenges begin and when can a new assessment occur? |
| Funding adapter | Which nominations may earn, how are weights normalized and when do entitlements arise? |
| Dependencies and authority | Which assets, registries, contracts and exceptional powers are relied upon? |

These configuration responsibilities synthesize the parent framework and current application decisions; the table is not a claim that all choices have been implemented. <!-- [claim:C006] [evidence:E001,E002,E003,E005,E010] -->

### A concrete goal and rubric

For a research-infrastructure pool, the workshop's example asks how much completed and maintained work underpins how research is done, shared and preserved now. Its prompts concern reliance, the role in research and available alternatives. These are one pool's criteria. A climate-adaptation pool or a pool funding future experiments would need different questions. The workshop's named projects and scores are illustrations, not measured assessments to reuse as ground truth. <!-- [claim:C007] [evidence:E005] -->

The rubric must say whether it evaluates current reliance, unmet funding need, expected additional benefit or another objective. Combining these without a stated tradeoff leaves jurors answering different questions. If the output becomes a funding weight, the numerical interpretation also matters: a score twice as large produces twice the relative weight under direct proportional allocation only while the requested cap does not bind. That is a policy choice, not a measurement showing twice the public benefit. <!-- [claim:C008] [evidence:E002,E003] -->

Attribution needs comparable clarity. The reference policy assesses the nominated work and avoids counting the same work twice across nominations. It does not exclude distinct contributions merely because they share a beneficiary. The application must identify where money should go, but beneficiary identity alone cannot establish that two descriptions refer to distinct work. Semantic overlap remains an assessment and policy problem. <!-- [claim:C009] [evidence:E005,E010] -->

## 3. Publish contributions as contestable nominations

A **nomination** identifies the contribution, its beneficiary and the factual claims on which its assessment relies. The pool's template states what evidence those claims require. A time-bounded claim should identify its period, but this is not a universal requirement that every nomination cover one fixed interval. The template should also distinguish direct observations from causal interpretation: a release record can support a software release's existence and date, without establishing how much research depended on it or what would have happened without it. <!-- [claim:C010] [evidence:E002,E003] -->

An illustrative nomination for a maintained data library could contain:

| Field | Illustrative content |
| --- | --- |
| Work | Maintenance and release of a named library version |
| Period | The interval covered by the nomination |
| Claims | Release existence, specified delivered features and documented downstream integrations |
| Evidence | Release artifacts, change records and independent integration records |
| Beneficiary | The eligible recipient identified under the pool's rules |
| Boundaries | Work shared with other nominations; claims the evidence does not establish |

This is a template example, not a factual claim about an existing project or a universal list of required fields. A pool must publish the evidence and challenge standards its participants will be asked to apply.

Publication is **optimistic**: satisfying the structural submission rules and posting the required deposit do not certify the claims as true. The claims become exposed to challenges. A violation of an evidence requirement may be challengeable under a template rule, but a missing document does not automatically prove a factual claim false. Testability, evidence sufficiency and truth are related questions with distinct burdens. <!-- [claim:C011] [evidence:E001,E002,E003] -->

### Why put a deposit at risk?

The nomination deposit makes an adverse accuracy ruling financially consequential. A successful challenge closes that nomination, ends its future funding eligibility and transfers the deposit to the successful fact-checker, who also recovers the counter-stake. This is the incentive: someone who establishes a qualifying problem can be paid from capital the nominator risked. It is not merely an invitation to provide unpaid feedback. <!-- [claim:C012] [evidence:E002,E003,E010] -->

The inherited accuracy rules require the challenger to post the greater of the pool minimum and one quarter of the bond pinned to the challenge, pay a challenge tax set as a pool-configured percentage of that pinned bond and cover the external arbitrator's fee. If the challenge fails, the nomination retains its bond and the counter-stake is divided between the nominator and the pool at the configured ratio. The challenge tax and arbitration fee are sunk costs in either outcome. For a queued challenge, the tax stays in escrow until activation, when it enters the pool budget. These are the shared accuracy-layer cashflows. The pool must publish its parameter values and specify any unresolved arbitrator-timeout behavior. <!-- [claim:C051] [evidence:E002] -->

The expected return still depends on detection, admissible evidence, adjudication, fees and investigation cost. A bounty can be too small to justify scrutiny; a profitable successful case can still have an unattractive expected return before investigation. Defined cashflows create an opportunity for fact-checking, not a guarantee that enough scrutiny will occur. <!-- [claim:C013] [evidence:E001,E002] -->

An accuracy challenge may begin while the nomination is active, including before its first relevance assessment and during a relevance appeal. An external arbitrator decides the challenge; the relevance jury does not decide whether a factual assertion is false. As in the parent, that arbitrator is a decentralized court reached through the `IArbitrable` interface, with Kleros v1 as the modeled provider. The design commits to a Kleros-like court, not to Kleros's implementation: an improved or patched Kleros, or a fork that redistributes the court's tokens away from concentrated holders, would also serve. The shared grounds cover factual falsification, lack of testability, violation of the declared topic scope and semantic template violations. A successful ruling closes the nomination rather than banning the person or project. A new nomination requires its own identity and deposit and does not reopen the closed nomination's entitlements. <!-- [claim:C014] [evidence:E001,E002,E003,E013] -->

This design makes correction possible, not inevitable. A nomination that nobody successfully challenges has survived the process so far. That is different from independent confirmation that all its claims are true. <!-- [claim:C015] [evidence:E001,E003] -->

## 4. Incentives for honesty, care and competence

Accuracy does not settle importance. Two contributions can both be real and still serve a pool's goal differently. Relevance jurors apply the published rubric to the nominated work and evidence. The selected mechanism draws seats from participants who commit a dedicated utility token, locks the capital backing those seats and collects private score commitments before revelation. Several seats held by one participant increase that participant's weight; they do not create several independent minds. <!-- [claim:C016] [evidence:E002] -->

The parent design uses a weighted mean for the relevance score and a dispersion-dependent band for coherence penalties. The band is centered on the last jury score in the appeal chain, so every committee is graded against the chain's final adjudicated outcome, and locked tokens stay locked until that chain is final. A report outside the band can lose part of its locked tokens. Actual distance-based penalties fund utility-token rewards to coherent participants; there is no independent base token reward in this selected rule. A configured dispersion floor keeps the band from collapsing when reports nearly agree, so tiny differences are not penalized. Agreement is penalized only when an appeal moves the final score away from it; without an appeal, the design cannot distinguish informed agreement from coordinated or uninformed agreement. The parent specification owns the exact formulas and rounding rules. <!-- [claim:C017] [evidence:E002,E003] -->

Service compensation is separate. In the parent design, a timely valid reveal generates the configured ether (ETH) service fee per represented seat when a valid ruling issues, independently of coherence. The fee belongs to the juror unless a successful premature-disclosure report redirects it to the reporter. It becomes withdrawable at issuance and is not clawed back when an appeal changes the score. A failed-quorum attempt produces no service fee. The fee pays for service; it does not prove that evidence was examined or that the participant understood it. The ETH ledger and utility-token ledger must remain distinct, and their quantities cannot be added as if they were the same asset. <!-- [claim:C018] [evidence:E002,E003] -->

Quorum requires timely valid reveals representing at least 80% of the originally drawn positive weight. An empty draw fails, and there is no minimum number of distinct jurors. One participant controlling sufficient drawn weight can satisfy this coverage rule alone. A drafted attempt also completes a fixed post-reveal period for opening qualifying premature-disclosure proofs before a ruling or quorum-failure settlement. This provides an enforcement opportunity for private reporting, not a guarantee that collusion is detectable. Proof validation and reporting incentives require further evaluation. <!-- [claim:C046] [evidence:E002,E003] -->

### Three requirements, three different questions

| Requirement | Meaning here | What the mechanism must make worthwhile |
| -------------------- | ---------------------------------------- | ---------------------------------------- |
| Honesty | Reporting one's actual assessment rather than deliberately misrepresenting it | Applying the public rubric sincerely instead of coordinating a convenient answer |
| Care | Exerting the effort needed to examine the available evidence rigorously | Doing useful assessment work rather than collecting fees for a guess |
| Competence | Having the knowledge and ability to interpret the task and evidence | Entering tasks one can judge well and improving, specializing or leaving when one cannot |

An honest and careful juror can still lack competence. A competent juror can choose to be dishonest. These distinctions motivate separate evaluation of effort, information and strategic reporting; they are not three independently verified qualities certified by a coherent score. <!-- [claim:C019] [evidence:E002,E003] -->

### What the Schelling-point argument does and does not establish

A **Schelling point** is a focal answer people expect others to select without reliable coordination. A clear policy and shared evidence are intended to make a sincere, informed assessment such a focal point. Buterin's SchellingCoin proposal describes an early cryptoeconomic oracle built on this idea, paying the participants whose revealed values fall between the 25th and 75th percentiles on the premise that the truth is “arguably the most powerful Schelling point” [@buterin2014schellingcoin]. The Kleros design carries it into arbitration, using private reports and economic consequences for incoherence [@kleros2019shortpaper]. These ideas motivate the mechanism; they do not prove that the honest answer is each participant's best response in this application. <!-- [claim:C020] [evidence:E001,E002,E006,E011] -->

The distinction matters because simple agreement incentives can suppress informative minority reports. Miller, Resnick and Zeckhauser illustrate this problem and develop a different peer-prediction mechanism using proper scoring rules and beliefs about others' reports [@miller2005peerprediction]. Their result cannot be transferred to the present weighted-mean game merely because both mechanisms compare reports. A relevant evaluation must inspect this game's complete payoffs and the information participants possess. <!-- [claim:C021] [evidence:E007] -->

Repeated competition supplies a possible competence-selection mechanism. If informed participants tend to retain or gain utility tokens while uninformed participants lose them, the latter's relative stake and future selection chances can fall. Anticipated losses could deter entry by participants who recognize their own disadvantage. But lacking an informational edge is not sufficient to establish negative total expected return. Service fees, token value, effort cost, correlated mistakes and outside incentives may reverse that conclusion. Competence selection requires a demonstrated payoff advantage for informed assessment after these costs and benefits, not a label attached to whoever won a round. <!-- [claim:C022] [evidence:E001,E002,E003] -->

## 5. Separate appeals from reassessment

An **appeal** contests an issued relevance ruling about a fixed nomination revision under its policy. A **reassessment** produces a later judgment as reliance, alternatives or evidence change. Reassessment does not imply the earlier ruling was procedurally wrong. An appeal does not by itself update the subject to newly edited content. <!-- [claim:C023] [evidence:E002,E003] -->

The parent's appeal design allows public backing of fixed-score positions. Two or more distinct, fully funded positions lead to one shared jury with a larger planned seat count, after admission closes and every admitted funding outcome is known. Reaching two funded positions cannot close admission early. The positions oppose one another; neither must defend the existing ruling. The jury can issue a score different from all proposed positions. Funding comes from the defined combination of available pool service funds and appeal capital; several positions do not create several independent juries or fee bills. Adjudicated backer funds settle against the appeal chain's terminal score under the parent's scalar payout rule. <!-- [claim:C024] [evidence:E002,E003] -->

Bounded admission and funding windows have different outcomes. If no position funds, the issued score becomes final under the specified timing rule. If exactly one position fully funds, its score can become final by forfeiture without a jury. That is a procedural outcome, not evidence of consensus. Multiple funded positions require adjudication; a valid appeal ruling can itself be appealed with fresh funds. Failed-quorum retries and repeated appeals create a real risk of prolonged capital commitment. A larger planned jury helps only if it brings useful additional information and sufficiently dispersed control. <!-- [claim:C025] [evidence:E002,E003] -->

Routine reassessment should occur at a published cadence, with funding and eligibility requirements. The parent's rules prevent it from bypassing an active same-item appeal hold. The next ordinary assessment becomes eligible one full configured cadence after the last applicable hold ends, rather than replaying missed assessments as a backlog; actual execution still requires funding and eligibility. Public interfaces should distinguish a currently adopted score, an appealed ruling, a later pending assessment and a nomination with no score. Missing assessment is not equivalent to a relevance score of zero. <!-- [claim:C026] [evidence:E002,E003] -->

Revision identity is important for both procedures. A later edit cannot change what an earlier jury judged or erase its capital commitments. Each assessment and appeal refers to its pinned content; a new revision needs its own assessment before that score can support new score-dependent funding. The scope and timing of permitted edits must be made explicit by the application. <!-- [claim:C027] [evidence:E002,E003] -->

Nomination closure and appeal settlement are also distinct. A previously funded contested appeal chain continues against the historical revision after debunking or permitted withdrawal, without restoring funding eligibility. If closure instead occurs during the initial appeal process before any level was fully contested and funded, that process stops and accepted contributions become refundable; a lone proposed score does not win by forfeiture. An ordinary attempt whose nonempty draw completed before closure also finishes under its existing rules: valid issuance earns the normal service fee and opens its normal first appeal process. If that attempt fails quorum, it produces no score, fee or new appeal window, and no fresh ordinary retry may be drawn for the closed nomination. These distinctions preserve prior commitments without allowing a historical assessment to reactivate a closed nomination. <!-- [claim:C047] [evidence:E002,E003] -->

## 6. Turn curated weights into funding, when funding exists

The curation output is a set of policy-relative weights. Producing that output requires resources for nomination, assessment and correction, but it does not require a budget already committed to beneficiaries. Keeping the **curation budget** separate from the **beneficiary budget** allows a funder to inspect an existing assessment or supply money later. It does not make curation costless. <!-- [claim:C028] [evidence:E003] -->

Let \(r_i\) be nomination \(i\)'s adopted relevance score and \(a_i\) its requested relative-weight cap, both on the pool's common scale. The reference ongoing profile computes an effective weight \(w_i=\min(a_i,r_i)\). For the set \(E\) currently eligible for a particular allocation, the total effective weight is \(W=\sum_{j\in E}w_j\). When \(W>0\), each eligible nomination \(i\in E\) receives share \(p_i=w_i/W\). <!-- [claim:C049] [evidence:E003] -->

The shares sum to one. A beneficiary budget \(B\) allocates \(Bp_i\); a flow rate \(F\) implies an earning rate \(Fp_i\), while the eligibility set and weights remain in force. These formulas describe the reference profile rather than a universal requirement of Decentralized Curation. <!-- [claim:C029] [evidence:E002,E003] -->

The cap limits relative weight, not absolute payment. A sole eligible nomination with positive weight receives the full distributable share even if its score is low. If the total eligible weight is zero, the formula supplies no allocation vector; it does not authorize an equal split. Setting the beneficiary budget to zero preserves existing weights and shares for an otherwise unchanged eligibility set, while producing no earnings. <!-- [claim:C030] [evidence:E002,E003] -->

A nomination can be assessed before it is eligible to earn. A new nomination serves its initial holdback before earning begins. Later adopted increases or decreases change future earning without a fresh holdback. The allocation interface must expose the earning conditions rather than present every curated score as an immediately payable entitlement. <!-- [claim:C031] [evidence:E003,E010] -->

### Preserve the distinction between earned and prospective funding

Already-earned funding remains owed to the nomination's beneficiary, whether paid or unclaimed. It is immediately claimable during an accuracy dispute or relevance appeal, after revision and after final debunking. Successful debunking ends future eligibility and forfeits the nomination deposit separately; it does not seize past earnings. A later revision or lower score likewise cannot rewrite an earlier beneficiary entitlement. <!-- [claim:C032] [evidence:E003,E010] -->

The application should display the following separately:

| Quantity or event | Meaning |
| ----------------------------------- | ----------------------------------------------------------------- |
| Adopted weight | The current assessment used when the relevant allocation conditions hold |
| Prospective earning rate | A rate conditional on available funds, current weights and eligibility |
| Earned balance | A recorded entitlement belonging to the beneficiary |
| Claim or payment | Collection or transfer that satisfies an earned entitlement |
| Nomination closure | An end to future participation under that nomination |

Claiming earnings and withdrawing a nomination are different operations. Under the intended ongoing rules, a nomination-withdrawal request made after an accuracy dispute waits behind it; debunking closes the nomination and cancels that now-unnecessary request. The existence of an accuracy dispute does not freeze collection of amounts already earned. Appeal backers' capital, by contrast, follows its own refund and chain-finality rules. <!-- [claim:C033] [evidence:E003] -->

This separation is a substantive design choice. It trades the possibility of later recovery of incorrectly awarded money for stability of earned entitlements. Initial holdback and continuing scrutiny must therefore be evaluated against the cost of errors that are discovered only after earnings have accumulated. No claim that the chosen balance is optimal follows from deterministic accounting. <!-- [claim:C034] [evidence:E003] -->

## 7. An illustrative lifecycle

Consider a pool assessing research infrastructure. Three fictional nominations, A, B and C, have completed their initial earning conditions. Their requested caps are each 1, and their adopted scores are 0.6, 0.3 and 0.1. These stipulated scores are inputs for an accounting example, not observations or a quality benchmark. <!-- [claim:C035] [evidence:E009] -->

Their effective weights total 1, so their shares are 60%, 30% and 10%. With no beneficiary budget, those weights can still be recorded and reviewed. If an available flow later supplies 100 accounting units per day and conditions remain unchanged, their earning rates become 60, 30 and 10 units per day. “Accounting units” here avoids assuming a market exchange rate or a deployed payment schedule. <!-- [claim:C036] [evidence:E003,E009] -->

Suppose a funded relevance appeal revises A's adopted score to 0.4. Once adopted, the weights total 0.8 and the shares become 50%, 37.5% and 12.5%. At the same flow, future rates become 50, 37.5 and 12.5 units per day. This branch illustrates a changed judgment of relevance; it does not allege that A made a false claim. <!-- [claim:C037] [evidence:E003,E009] -->

Suppose a later routine reassessment lowers B's adopted score to 0.2 because its role under the policy has changed. With A at 0.4 and C at 0.1, weights now total 0.7. Shares become \(4/7\), \(2/7\) and \(1/7\). That change concerns present relevance and creates no retrospective liability for earlier earnings. <!-- [claim:C038] [evidence:E003,E009] -->

Now suppose an accuracy challenge establishes a false claim in C's nomination. C closes and its deposit goes to the successful challenger under the selected accuracy rule. Among the remaining eligible weights, A receives \(2/3\) and B receives \(1/3\). Any amount C earned before closure remains owed to C's beneficiary. This final branch is accuracy adjudication, distinct from both the appeal and reassessment. <!-- [claim:C039] [evidence:E003,E009] -->

The example holds the other eligibility and funding conditions fixed and does not compute fee transfers or elapsed-time balances. Its purpose is to show how different events affect different outputs: a score, a future share, a deposit or an existing entitlement. It does not assume that funds already earned become unavailable during a dispute.

## 8. Governance and operational boundaries

The mechanism does not eliminate judgment by moving arithmetic into a contract. The goal, eligible evidence, scoring rubric, arbitrator and beneficiary mapping remain consequential choices. The parent favors published rules, permissionless pool creation and explicit protocol boundaries. Consistent with its commitments to immutable contracts and minimal governance, the design gives no actor a power to pause, upgrade or override execution outside the published rules. A deployment that adds such an exceptional-intervention authority must make that authority and its duration visible; an interface cannot safely imply that an intervention is impossible merely because ordinary execution is automatic. <!-- [claim:C040] [evidence:E001,E002,E003,E012] -->

Competition among pools is a possible discipline on poor choices only when users can recognize a better alternative, that alternative has resources, and migration is feasible. Public access to rules does not establish those conditions. Nor does permissionless entry make influence equal: stake-based selection explicitly gives more draw weight to more committed capital. <!-- [claim:C041] [evidence:E001,E002] -->

A deployment must bind the decided rules to concrete pool parameters, beneficiary controls, content references and eligibility checks. Initial holdback, later score adoption and treatment of earned balances are different operations; choosing parameter values must not change those relationships. The implementation must preserve separate accounting for nomination deposits, juror collateral, service funds, appeal contributions and beneficiary entitlements. Earned obligations remain reserved for their recipients. Unused reservations return to their original funding sources under the explicit cancellation rules. These are accounting obligations of the design, not evidence that an existing deployment already meets them. <!-- [claim:C042] [evidence:E002,E003,E010] -->

## 9. Failure modes and evaluation priorities

The decisive question is not whether participants can submit scores. It is whether the incentives make them obtain and use evidence, report informative judgments and correct mistakes at a sustainable cost. The following agenda is proposed future work; no study results are reported here.

| Failure mode | Why the design remains exposed | Evaluation that would inform the decision |
| ------------------------- | ----------------------------------- | ---------------------------------------- |
| Weak factual scrutiny | Investigating a claim may cost more than its expected reward | Measure detection, challenge entry, total costs and adjudication quality across claim types |
| Shared but mistaken judgment | Coherent reports may reflect the same misconception | Compare reports with independently justified task-specific reference assessments and trace evidence use |
| Paid guessing | Service fees may exceed expected losses from low-effort reporting | Estimate complete net returns under different effort choices and asset valuations |
| Expertise mismatch | Honest effort does not supply missing domain knowledge | Compare relevant expertise and task performance separately from coherence and self-confidence |
| Coordinated distortion | A coalition can target the mean and make outsiders look incoherent | Analyze best responses, concentrated stake, correlated signals, bribes and delayed coalition formation |
| Unaffordable or delayed appeals | Correction requires capital and participation, and may remain unresolved | Measure entry costs, funding failure, capital lock duration and outcome sensitivity to wealth |
| Double-counted contributions | Separate plausible claims can credit overlapping work | Audit cross-nomination attribution using structured overlap cases |
| Poor public purpose | Faithful scoring can reward the wrong objective | Examine affected users' needs and compare feasible policies and downstream outcomes |

These are design-specific risks and proposed tests, drawn from the parent's limitations and the application boundaries above. Listing a defense does not demonstrate its effectiveness. <!-- [claim:C043] [evidence:E001,E002,E003] -->

A staged evaluation should first establish that participants understand the goal, score scale, deposit risk and distinction between accuracy and relevance. Next, controlled tasks should vary evidence quality, participant expertise and incentive terms while retaining independently assessable outcomes where possible. Field work can then measure actual challenge supply, assessment costs, participation concentration and beneficiary consequences. Agreement and participant profit should be reported as process outcomes, not substituted for evidence quality or public benefit. These are proposed evaluation choices, not procedures already performed.

The strategic analysis must model the selected two-asset mechanism and the complete appeal process. Simulations that prescribe informative or random reports can reveal consequences of those assumptions, but cannot establish that self-interested participants will choose those strategies. Any competence-selection claim should compare net returns and subsequent selection weight, including fees, losses, effort, capital cost and outside benefits. <!-- [claim:C044] [evidence:E001,E002] -->

Finally, improved curation and improved funding outcomes require separate evidence. Better-supported judgments could still be used under a poor goal, and a desirable contribution need not be the best recipient of additional money. Evaluation should state the public outcome sought, whose interests count and which feasible alternative allocation process supplies the comparison.

## 10. Conclusion

Applying Decentralized Curation to public goods requires more than attaching incentives to a vote. It requires a clear goal, contestable nominations, an explicit relevance rubric, financially meaningful correction, and accounting that distinguishes an assessment from a funding entitlement. The proposed ongoing profile permits curation before beneficiary funding and revision of future shares without rewriting what has already been earned.

The strongest claim of this blueprint is architectural: these responsibilities can be specified separately and connected through explicit interfaces. Its economic ambition is conditional. Honest reporting, rigorous effort and competent judgment must each become worthwhile under the complete rules. Establishing that result, and showing that it improves outcomes for affected people, is the work the blueprint makes possible to test.

## Preparation note

Scientific Agent Skills informed the drafting and evidence workflow [@kassis2026scientificagentskills]. This identifies a preparation tool, not evidence for the mechanism. Agent assistance was used to draft and revise prose, inspect sources, and check citations and arithmetic. These checks do not establish the truth of claims or validate the mechanism. <!-- [claim:C045] [evidence:E008] -->

## References

The parent paper establishes the framework context [@tuncer2026decentralizedcuration]. Kleros and peer prediction supply related mechanism literature [@kleros2019shortpaper; @miller2005peerprediction]. Source identifiers and inspection scope appear in the [source record](https://github.com/0xferit/manuscript-decentralized-curation/blob/public-goods-v0.2.0/projects/rpgf/companion-paper/source-and-open-questions.md). <!-- [claim:C050] [evidence:E001,E006,E007] -->

::: {#refs}
:::
