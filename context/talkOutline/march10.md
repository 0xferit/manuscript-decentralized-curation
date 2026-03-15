# Talk Outline: Decentralized Curation (March 10)

Three chapters. Each section is a talking point with enough detail to speak from directly.

## Chapter 1: The Curation Bottleneck

### 1.1. Information needs curation to be useful; curation is everywhere

- Raw information is an endless pile of books. Curated information is a library. The difference is not the content; it is the transformation: filtering, ordering, contextualizing, prioritizing.
- Curation is not a niche activity. Every search result, every news feed, every recommendation, every review system, every editorial decision is curation. We are all downstream of curation systems we did not choose and cannot inspect.
- Ackoff's DIKW hierarchy (1989) names the levels: data, information, knowledge, wisdom. Each transition requires a different kind of processing. The bottleneck is in the transitions, not in the raw material. "An ounce of knowledge is worth a pound of information." DIKW is useful as a positioning reference: it maps the landscape of transformations. But the paper diverges from Ackoff's definition of "knowledge," which is procedural (know-how). Here, "knowledge" means propositional: decision-grade verified claims. DIKW is also purely descriptive; it names the levels without specifying how to perform or verify the transformations. The paper fills that gap with mechanisms.

### 1.2. Historical arc: access solved, quality not

- For most of history, the bottleneck was access. Information lived in libraries, archives, universities. The internet solved access dramatically.
- But information abundance did not produce knowledge abundance. The internet gave everyone a voice without giving anyone a filter. The transformation from information into decision-grade knowledge remains unsolved at scale.
- This is not a new observation: the quality gap has been visible since the early web. What is new is how the gap is widening.
- The consequence is not just noise; it is adverse selection. Akerlof's "lemons" problem applies directly: when buyers cannot distinguish quality, low-quality goods drive out high-quality ones. In information markets, high-quality content is expensive to produce and low-quality content is cheap. If no curation layer makes quality legible, low-quality content captures distribution and high-quality producers are punished for their costs. A badly curated information environment does not merely misinform; it selects against excellence.

### 1.3. Quality is multidimensional (Wang & Strong 1996)

- Wang and Strong's empirical finding: data quality decomposes into multiple dimensions grouped into four categories: intrinsic (accuracy, objectivity, believability), contextual (relevance, timeliness, completeness), representational (interpretability, consistency), and accessibility.
- The structural insight: accuracy is intrinsic (independent of use context); relevance is contextual (depends on who uses it, when, and for what). This distinction is not preference; it is structural.
- The design consequence: collapsing all quality into a single engagement metric is a systematic design flaw. Single-metric compression loses information about which dimensions are failing and creates incentives that trade off dimensions against each other in uncontrolled ways. A system that compresses accuracy and relevance into one score will systematically confuse different properties that need different incentive structures.

### 1.4. AI breaks the proof-of-work coupling

- Historically, the cost of producing information acted as a weak quality filter. Producing convincing output usually required some underlying understanding, so form and substance were at least partly coupled.
- AI weakens that coupling. The form of quality is now cheap: fluent prose, plausible references, polished tone. The substance of quality is still expensive: correctness, coherence, domain understanding, grounded judgment.
- This is not an AI-specific thesis. The curation problem predates AI. But AI accelerates the pressure: cheaper generation without better curation produces overload, not understanding.

### 1.5. Traditional curation: useful but dangerous, domain-dependent

- Traditional curation works through trusted intermediaries: editors, reviewers, platforms, algorithms, institutions. These are useful. They often produce good results.
- The danger: every trusted intermediary is a capture surface. The curator's competence, incentives, and failure modes become the consumer's failure modes. We inherit judgment we cannot audit.
- Domain dependence: different domains need different quality dimensions. A curation system that works for academic peer review does not transfer to news, product reviews, or public goods funding. There is no universal curator.

### 1.6. Many coordination failures are curation failures

- The thesis claim: before people can coordinate well, they usually need a sufficiently shared picture of reality. If the upstream curation layer is weak, captured, or opaque, then downstream coordination looks broken even when the formal governance mechanism is not the main problem.
- Examples: a building association, a DAO, a city council. The voting rule may be procedurally fine, yet outcomes are dysfunctional because participants disagree about what reality looks like. The failure is upstream.
- Falsifiability boundary: the claim does not apply to pure preference conflicts where all parties share verified facts but disagree on what to do: distributional tradeoffs, risk appetite differences, value pluralism. These are genuine coordination problems, not curation problems. If the audience asks "what would refute this?", that is the concrete answer.

---

## Chapter 2: Curating Without Trust

### 2.1. The goal: trustless curation via mechanism design

- If curation is upstream of coordination, and trusted curators are capture surfaces, then the design goal is: can we build curation systems that do not require trusting the curator?
- "Trustless" means: the system's outputs are reliable not because we trust the participants, but because the incentive structure makes honest behavior the rational strategy. Honesty is a best response, not a virtue requirement.
- This is mechanism design applied to the information-to-knowledge transformation.

### 2.2. The four-step framework

- Present the framework first so the audience has the conceptual skeleton before the instantiation.
- **Step 1: Problem definition.** Identify the hidden curation problem inside what is usually described as a downstream failure (governance failure, market failure, coordination failure).
  - Diagnostic test: if participants share the same verified knowledge and still cannot coordinate, the failure is downstream (preferences, incentives, power), not upstream (curation). This test guards against confirmation bias in problem selection.
- **Step 2: Quality identification.** Determine which dimensions of information quality matter in the target domain. Different domains care about different dimensions. No universal curation mechanism exists.
- **Step 3: Falsifiability requirement.** Use challenge-based mechanisms only in the middle region: where verification is expensive but falsification is feasible. Trivially verifiable claims need no mechanism. Non-falsifiable claims cannot be processed by a challenge-based system.
- **Step 4: Mechanism design by dimension.** Design distinct mechanisms for each quality dimension instead of collapsing all quality into one score. Different dimensions need different games.
- One-line summary: find the hidden curation problem, decompose the quality dimensions, require falsifiability where needed, then match each dimension to the right mechanism.

### 2.3. News instantiation: two quality dimensions

- Applying the framework to news yields two dominant dimensions: accuracy and relevance.
- **Accuracy** is global and binary. A claim either withstands a debunking challenge or it does not. The answer does not depend on the pool or the reader. Binary treatment is an engineering decision: the simplest focal point structure for jurors, not an ontological claim that accuracy is inherently binary. Some claims are partially true or context-dependent; the protocol handles this by requiring explicit, scoped propositions that can be challenged on their specific terms.
- **Relevance** is local and scalar. What matters depends on the pool's public curation policy, its scope, and current context. "1=1" is accurate but not news. A football article can be perfectly true and irrelevant in a world-politics pool.
- The mechanism must respect this decomposition. Forcing both into one system is a category error.

### 2.4. Accuracy layer: bonded publication, challenge, DDR, state machine

- An author submits a claim blob and locks a bond. The item enters `Live` status immediately. The protocol is not saying "this is true." It is saying: this item is publicly posted, capital is at risk, and it is open to challenge.
- A challenger identifies a specific proposition, posts counter-stake plus a challenge tax, and specifies the challenge reason (falsehood or non-falsifiability under the pool's rules).
- The dispute routes to external decentralized dispute resolution (DDR). Jurors answer a narrow binary question. If the challenge succeeds: `Debunked`, bond transferred. If it fails: back to `Live`.
- State machine: `Live` -> `Challenged` -> `Debunked` or back to `Live`. Author can also initiate `RetractPending` -> `Retracted` (cooldown during which challenges still accepted).
- The Popperian asymmetry: the system makes falsehood attackable but does not certify truth. Surviving challenge is undefeated exposure to scrutiny, not proof. Institutional modesty matters.

### 2.5. Relevance layer: drafted curators, coherence game, policy as focal point

- Curators stake into a pool. Relevance rounds are scheduled at a pool-defined cadence for `Live` items.
- Curators are drafted using a stake-weighted lottery. No reputation weighting: purely stake-driven.
- Drafted curators commit and reveal relevance scores. The protocol computes a consensus estimate. Curators whose scores deviate too far from the group are slashed; those within the coherence band are rewarded.
- The curation policy is the focal point (Schelling). Without a specific, public policy, there is no salient coordination target and the game degenerates. Policy specificity is not a UX concern; it is a game-theoretic requirement for equilibrium existence.
- The curation policy functions as the law of the pool. The pool creator defines what "relevant" means; the coherence game turns curators into enforcers of that definition through slashing and rewards. If the policy is bad, curation will be bad. But that is a policy-level problem, not a system flaw, just as a bad law is not a failure of the concept of law enforcement.
- The mechanism's information content depends on curators having genuine expertise about the policy domain. If curators lack domain knowledge and are simply guessing what others will say, the game degenerates into pure coordination with no information content: consensus without knowledge. Stake-weighted drafting selects for capital, not competence; the defense is that the slashing mechanism converts this into a competence filter over repeated rounds. Incompetent curators produce noisy scores, fall outside the coherence band, and lose stake. The game eliminates incompetent curators over time.
- Near-flat rounds are cancelled as degenerate. Weight capping limits whale influence.

### 2.6. Confidence and author reputation

- **Confidence** is accumulated bond-time: the longer a claim survives with more capital at risk, the higher the confidence score. Challenge pauses accumulation; retraction freezes the score. Confidence is not a truth certificate; it is a signal of accumulated capital risk exposure.
- Distributional concern: confidence is a function of bond size and time, so well-capitalized authors accumulate it faster. The partial defense is that larger bonds attract more scrutiny (higher challenger rewards), making the exposure genuine, not performative. But the system does not correct for differences in capital access. It structurally advantages well-capitalized participants.
- **Author reputation** is a pool-scoped, slowly decaying credibility stock. Not escrowed per claim, but each new claim exposes the author's standing reputation to large downside on debunking. Separates honest from dishonest authors over time.
- No curator reputation. Earlier iterations allowed reputation to weight curation; current design rejects that entirely because it grants influence not fully backed by slashable capital.

### 2.7. Equilibrium properties (concise)

- **Author honesty**: false publication has negative expected value when the bond is large enough relative to what the author stands to gain. The required bond size depends mainly on how likely detection is.
- **Challenger entry**: rational only when the false-claim base rate is high enough to justify the search cost. Below that threshold, no one searches. This is not a failure when the base rate is genuinely low; the risk is that it rises undetected.
- **Curator honesty**: under commit-reveal, honest reporting is an equilibrium when: (i) the policy is specific enough, (ii) the coherence threshold is permissive enough, and (iii) the colluding fraction stays below a critical threshold. Beyond that threshold, dishonest reporters survive and honest reporters get slashed.
- **Most fragile condition**: challenger entry. If challengers exit, the false-claim rate can rise, creating a cyclical dynamic. The system dramatically reduces the required trust surface but does not fully eliminate it: during low-fraud periods, some non-economic motivation for challenge activity may be needed. The honest label is "trust-minimized," not "trustless" in the absolute sense.
- Note on parameter sensitivity: the required bond is sensitive to detection probability, which is the least controllable parameter. At low detection rates, the bond requirement rises sharply.

### 2.8. Architectural commitments

- **Permissionless pools.** Anyone can create a pool with domain, claim template, evidence policy, relevance policy. Bad pools are ignored, not governed away. This is the same dynamic as newspapers and subreddits: creating a newspaper is permissionless, but if you publish poorly, no one reads it and it falls into irrelevance. Multiple subreddits can exist on the same topic; users gravitate to the best-curated one and the rest are outselected naturally. People vote with their feet. The protocol does not need to prevent bad pools; it needs to make pool creation cheap and switching costless, so competitive selection does the filtering.
- **Immutable contracts.** Protocol changes require new deployments and cross-version aggregation, not in-place upgrades. This eliminates the governance surface of protocol upgrades.
  - Tradeoff: bugs cannot be patched in place; the only option is a new deployment and voluntary migration. This is a conscious tradeoff: governance capture risk versus operational fragility.
- **Minimal governance.** Preference ordering: NoNeedForGovernance > Good Governance > Bad Governance > No Governance. If a design can eliminate a governance surface, it should.
- Three-layer architecture: canonical protocol state (on-chain), content and indexing, interfaces. A protocol with one fragile frontend is not practically decentralized.

### 2.9. Advertising as second instantiation

- Advertising is largely a competition for attention: participants keep spending until the game hits its feasibility limit. A negative-sum escalation game.
- A different advertising game: advertisers express ads as claims and bond them. If the claim is true, cost is mainly temporary capital lockup. If the claim is false, capital is lost to challengers. This inverts the cost structure: honest advertisers are cheap, dishonest advertisers are expensive.
- Advertising demonstrates that the framework is not news-specific. It also provides a plausible funding source for curation labor.
- Caveat: for capital-constrained advertisers, the bond lockup cost is real even if the bond is returned. The system's cost advantage applies most clearly to well-capitalized honest advertisers.

---

## Chapter 3: Public Goods Funding as Curation Problem

### 3.1. Resource allocation formalization

- Public goods funding is a resource allocation problem. Before we allocate money, we need upstream answers: which projects matter, for whom, under what objective, by how much relative to alternatives?
- The target is not a binary label on each project. The target is closer to an allocation vector: each entry represents how much of the pool should go to a beneficiary, each weight is in [0,1], and all weights sum to 1.
- This makes the object being curated an allocation vector, not an article feed. The curation problem is the same in structure; the object and the policy differ.

### 3.2. Applying the four-step framework to public goods

- **Step 1: Problem definition.** The hidden curation problem: funding allocation failures are typically diagnosed as governance failures or voting design failures. But the upstream question is whether the knowledge about project impact is reliable, shared, and auditable. If not, even a perfect voting mechanism operates on corrupted inputs.
- **Step 2: Quality identification.** Two dimensions emerge, analogous to news. Accuracy: do the project's factual claims hold up (deliverables, impact metrics, team qualifications)? Priority/relevance: given the pool's stated objective, how much relative weight should this project receive?
- **Step 3: Falsifiability requirement.** Output claims ("we shipped X," "we served Y users") are falsifiable and sit squarely in the middle region. Impact claims ("X improved Y by Z%") often are not, because they involve counterfactuals and long time horizons. The accuracy layer is strongest on verifiable outputs and weakest on impact attribution. The hard part of evaluation falls primarily on the relevance layer.
- **Step 4: Mechanism design by dimension.** Accuracy of project claims can use the same bonded publication and challenge system. Priority/relevance uses the coherence game, but the policy definition becomes even more critical: what does "public benefit" mean for this specific pool?

### 3.3. What changes from news

- **The object**: instead of curating an article feed, the system curates an allocation vector over projects.
- **Policy importance**: in news, a vague policy weakens the focal point. In public goods, a vague objective is worse: "fund good projects" is not a curation policy. The pool must define what "good" means, for whom, over what time horizon.
- **Cadence**: news relevance changes rapidly. Project evaluation may have longer cycles tied to milestones and reporting periods.
- **Stakes**: project teams have direct financial interest in their own allocation. This concentrates incentives in ways that news authors may not face.
- **Adversarial selection**: the projects most incentivized to game the system are those with the most to gain from inflated allocation. If gaming is cheaper than genuine impact, the same lemons dynamic from Chapter 1 applies with greater force: quality is driven out by strategically inflated claims, and the attack surface is larger because the incentive to game is concentrated and direct.

### 3.4. Why quadratic voting is the wrong tool

- QV elicits willingness-to-pay as a proxy for preference intensity: it lets participants express how much they are willing to sacrifice, not just what they prefer. This is genuinely useful for aggregating preferences under the assumption that marginal utility of money is comparable across voters.
- The critique is not that QV fails at what it does. The critique is that preferences are the wrong input when the goal is optimal impact allocation. The question "how much do you care about project X?" is different from "how much impact does project X actually deliver per dollar under this pool's stated objective?"
- QV aggregates what people want. Curation aggregates what is true and important relative to a defined standard. These are different operations. If the goal is knowledge about impact rather than preference aggregation, the mechanism must be designed for knowledge, not preference.
- QV and the Keynesian beauty contest are orthogonal problems. QV achieves incentive compatibility (voters express true valuations rather than voting strategically), but the beauty contest is an epistemic problem (predicting others' predictions about an external state), not a preference-weighting problem. The actual contrast: QV sidesteps coordination games entirely through direct preference revelation; the coherence game deliberately uses a beauty contest structure but anchors the focal point to a substantive curation policy. In Kleros, beautiful = just. Here, beautiful = relevant under the pool's stated policy. The beauty contest is pathological only when the focal point is arbitrary.
- Caveat: the distinction between preference aggregation and impact evaluation is real, but impact evaluation itself involves value judgments (impact for whom, over what time horizon, relative to what counterfactual). Curation under a specific policy is more constrained than raw preference, but it is not purely factual. The framework relocates value judgments into pool policy definition rather than eliminating them.

### 3.5. Where the framework is strong

- **Project claim accuracy.** Bonded publication and challenge works well when projects make falsifiable claims: deliverables shipped, users served, metrics achieved. The same incentive structure that makes false news articles attackable makes false project reports attackable.
- **Relative priority.** The coherence game with a specific curation policy can produce a meaningful priority signal. If the pool defines its objective precisely, drafted curators can evaluate relative impact under that objective.
- **Transparency and auditability.** The entire curation history is public: who claimed what, who challenged what, what survived, what was debunked. This is a structural improvement over opaque committee-based funding decisions.

### 3.6. Where the framework faces genuine difficulty

- **Value-laden objectives.** Determining "optimal public benefit" is inherently value-laden, not purely factual. The framework does not eliminate this value judgment; it relocates it into pool policy definition. Pool policy definition is relocated governance: transparent, competing, auditable, which is better governance, but still governance. The framework makes the value question more legible; it does not dissolve it.
- **Collusion risk.** In news, authors and curators are typically different people with different incentives. In public goods, project teams have strong incentives to collude with curators to inflate their own allocation. Commit-reveal (anti-prerevelation) mitigates pre-coordination among colluders, but the attack surface is larger because the incentive to collude is concentrated and direct.
- **Long-horizon impact.** Some public goods produce value over years or decades. Falsifiability depends on evidence surfacing within the challenge window. Long-horizon impact claims are harder to falsify and may sit near the edge of the feasible region.
- **Curator competence.** In news, evaluating relevance requires broadly distributed judgment. In public goods, evaluating project impact per dollar requires domain expertise (engineering, economics, context-specific knowledge) that stake-weighted curators may lack. The competence gap is wider here than in news, but the coherence game eliminates incompetent curators over time through slashing: noisy scores fall outside the coherence band and lose stake.
- **Disclosure-harmful domains.** The framework presupposes that truthful public claims are safe to publish. The accuracy layer requires public claims and public challenges; the game theory depends on this transparency. But in domains where the act of disclosure itself causes harm, the mechanism hits a hard boundary. Security vulnerabilities are the clearest case: publishing "this contract has vulnerability X" as a bonded claim exposes the vulnerability before anyone can patch it. Responsible disclosure requires confidentiality, which is structurally incompatible with bonded publication. The same tension applies to trade secrets and proprietary information, where publication destroys the owner's competitive advantage regardless of whether the claim is true. The framework works where public truth is net-positive; it does not extend to domains where truthful publication has negative externalities.

### 3.7. The argument in one paragraph (speaker internalization)

- Internalize this for fluency: many public goods funding failures are better understood as curation failures upstream. Before we can allocate well, we need reliable, shared, auditable knowledge about what each project delivers. The decentralized curation framework provides a mechanism-design route into this problem by treating allocation as curation over weights. It does not solve the value question of what "good" means, but it relocates that question from opaque committees to public, competing pool policies. Where project claims are falsifiable, the accuracy layer applies directly. Where relative priority must be judged, the coherence game produces a signal that is defensible, auditable, and resistant to collusion up to known thresholds.

### 3.8. Scope and modesty

- Not claiming that one protocol solves every public goods funding problem.
- Not claiming that governance disappears. The design preference is to eliminate governance surfaces where possible, not to pretend policy choices vanish.
- Not claiming the system has been validated for public goods allocation in production.
- What is claimed: the decentralized curation framework, instantiated in detail for news, provides a plausible and principled mechanism-design route into public goods funding by treating allocation as a curation problem over weights. The framework generalizes; whether the specific parameter choices transfer requires empirical work.
- The thesis is intentionally upstream. Downstream coordination (how to distribute funds once weights are determined, how to enforce accountability after allocation) is a separate problem.
- The 2023 partial deployment validated the accuracy layer flow but failed to bootstrap sustained usage. The full system has never been tested end-to-end. Bootstrapping remains an unsolved operational problem.
