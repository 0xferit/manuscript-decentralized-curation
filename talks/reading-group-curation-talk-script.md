# Reading Group Talk Script

Approximate length: 20 to 25 minutes

Audience: technical reading group

Delivery note: aim for a measured pace, not a rushed one. If you speak at roughly 120 to 135 words per minute and leave brief pauses after the big claims, this version should land in the target range.

## Slide 1: Title

Today I want to present the core argument of my thesis, which is about decentralized curation.

The shortest version is this:

many hard coordination problems are better understood as curation problems upstream.

I want to be careful about what I mean by that, because I am not saying governance does not matter, voting does not matter, or institutions do not matter. My claim is narrower and, I think, more useful.

The claim is that before people can coordinate well, they usually need a sufficiently shared picture of reality. They need a decent knowledge layer underneath the coordination layer. If that upstream layer is weak, captured, or opaque, then the downstream coordination process will often look broken even when the formal governance mechanism is not the main problem.

So this talk is really about a diagnostic shift.

Instead of asking only, "Why can people not coordinate?", I am asking, "What kind of curation system produced the knowledge they are coordinating on?"

That shift is the backbone of the thesis.

## Slide 2: The Core Claim

For most of history, the bottleneck was access to information.

Information lived in libraries, archives, universities, and institutions. The internet changed that dramatically. We now have access to much more information than most people in earlier periods could reasonably reach.

But information abundance did not automatically produce knowledge abundance.

Information becomes useful only after it is filtered, interpreted, prioritized, contextualized, and made actionable. That transformation is what I mean by curation.

A simple everyday example is travel. If I want to decide where to go on vacation, I do not read every raw fact about every place on earth. I search for the best destinations, or I read recommendations, reviews, and rankings. In other words, I rely on someone else's curation work. I am borrowing their judgment.

That is not a defect. It is unavoidable. None of us can verify and sort everything ourselves.

In fact, relying on curation is one of the main ways we become more productive. We save time by standing on other people's filtering and evaluation work.

But the moment we rely on curation, we also inherit the curator's competence, incentives, and failure modes.

So the core claim of the talk is:

the internet solved access to information, but it did not solve access to knowledge. And because coordination depends on shared trusted knowledge, many hard coordination failures are really curation failures upstream.

## Slide 3: Why This Matters Now

Curation was always important, but I think it is becoming structurally more important.

Historically, the cost of producing information acted as a weak quality filter. Producing convincing software, papers, or articles usually required some underlying understanding, so form and substance were at least partly coupled.

AI weakens that coupling.

The form of quality is now cheap: fluent prose, good formatting, respectable structure, plausible references, working-looking code, polished tone. The substance of quality is still expensive: correctness, coherence, domain understanding, and grounded judgment.

So we are entering a regime where information is abundant, but knowledge is scarce.

Concretely, if the marginal cost of generating plausible output keeps collapsing, then the burden of filtering, checking, and ranking that output grows. Better generation systems without better curation systems can easily produce overload instead of understanding.

That is why I think curation is becoming a bottleneck rather than remaining a side issue.

## Slide 4: Why Curation Matters For Coordination

The main example in the thesis is governance, because governance is where the hidden curation problem becomes especially visible.

We often say governance is hard because people cannot coordinate. But in many real settings, coordination fails earlier than that. People are not choosing from the same knowledge base.

Imagine a shared asset with one hundred stakeholders. Or an apartment building where many residents need to decide how to allocate resources. Or a DAO deciding whether to fund a proposal. In all of those cases, the voting rule may be fine in a narrow procedural sense, yet the outcome can still be dysfunctional because people disagree about what reality even looks like.

The news example helps here. People consume a curated picture of the world and then make decisions from it, including political decisions. A democracy assumes that voters are informed in some meaningful sense. But if the curation layer feeding voters is incompetent, captured, or actively manipulative, then the downstream democratic process is forced to operate on corrupted inputs.

If two people trust that two plus two equals four, there is no governance problem there. The shared fact scales cleanly.

But if stakeholders inhabit different informational realities about a proposal, a budget, a public event, or a strategic risk, then governance looks broken even if the formal decision rule is not the main source of failure.

So one of the main claims of the thesis is diagnostic:

many things that look like governance problems are more usefully understood as curation problems upstream.

I am not saying all governance problems reduce to curation. I am saying that more of them begin there than is commonly recognized.

## Slide 5: The Framework

The thesis proposes a four-step framework for trustless decentralized curation.

First, identify the hidden curation problem inside an apparent downstream failure.

Second, identify the relevant quality dimensions. Information quality is not one thing. Depending on the domain, the relevant dimensions may include accuracy, relevance, timeliness, completeness, interpretability, accessibility, and so on.

This point matters because if quality is multidimensional, then there is no universal curation mechanism. A system that tries to compress all quality into one score will often confuse very different properties.

This is one reason I found the Wang and Strong data-quality framing useful. It gives a vocabulary for saying that different users and different domains care about different aspects of quality, and that mechanism design has to respect that decomposition.

Third, require falsifiability. A challenge-based mechanism only makes sense in the middle region where exhaustive verification is expensive, but falsification is still feasible.

Fourth, design mechanisms dimension by dimension. Different qualities require different games. There is no reason to expect one incentive structure to handle everything equally well.

If I had to summarize the framework in one line, it would be this:

find the hidden curation problem, decompose the quality dimensions, require falsifiability where needed, and then match each dimension to the right mechanism.

## Slide 6: News As The Main Use Case

The domain I use most heavily in the thesis is news.

News is a good use case because the curation problem is socially visible, politically consequential, and broadly distributed. A newspaper is not just a pile of articles. It is a curated set of claims about reality. People consume those claims and then make decisions with them.

That is why news matters so much for the broader thesis. It is one of the clearest domains where the transformation from information into knowledge directly affects collective behavior.

In the news case, two quality dimensions dominate: accuracy and relevance.

Accuracy is obvious. We do not want false claims.

But accuracy alone is not enough. A statement like one equals one is accurate, but it is not news. A perfectly true article about a football match can still be irrelevant in a world-politics pool.

So if you optimize only for accuracy, you can produce something that is technically correct but practically useless.

That is why the thesis insists that relevance is not a cosmetic add-on. It is a separate dimension with a different structure and therefore different incentive requirements.

This is also where the broader curation argument becomes clearer: the question is not only "Is this true?" but also "Does this matter here, for this pool, under this policy, at this time?"

## Slide 7: The Falsification Asymmetry

This is the slide I most want to make precise, because a lot of the mechanism depends on it.

The system I am describing can make falsehood expensive to sustain if challenged, but it cannot certify truth in any absolute sense. An important nuance: our simulations show the dominant bottleneck is detection coverage, not the dispute mechanism itself. The system does not guarantee that false claims will be found; it creates economic incentives for finding them at representative parameters.

That is the Popperian asymmetry.

Some claims are easy to verify. Those do not need an elaborate curation game.

Some claims are not falsifiable at all. A challenge-based mechanism cannot safely process those either, because there is nothing operational to contest.

The interesting region is in the middle: claims that are costly to verify exhaustively, but still falsifiable through later evidence or contradiction.

News often fits that structure. A claim that an event happened may be difficult to verify conclusively at first, but later evidence may still debunk it.

So the public signal is not "this system proved the claim true."

It is closer to:

- `Debunked`
- or still `Live`, meaning bonded, exposed to challenge, and not yet defeated

That distinction matters a lot. Surviving challenge is not proof of truth. It is only undefeated exposure to scrutiny.

I think that institutional modesty is important. Otherwise these systems start pretending to be oracles, and that is exactly the wrong mental model.

## Slide 8: Mechanism Split

Once that asymmetry is clear, the mechanism design becomes cleaner.

Truth Post is not one big voting system. It is two distinct but connected games around the same item.

The first game is the accuracy game.

That game asks a narrow question: can a specific proposition inside this item be successfully challenged?

The actors there are the author, the challenger, and external jurors. The output is not a relevance score. The output is a status transition such as `Live`, `Challenged`, or `Debunked`.

The second game is the relevance game.

That game asks a different question: assuming the item is still live, how much does it matter for this particular pool under this public policy?

The actors there are staked curators drafted into rounds. The output is not a truth verdict. The output is a pool-local relevance signal.

And that generalizes beyond news. In a funding context, the same basic problem becomes: how should weight be assigned across a set of candidate beneficiaries under a public objective?

That split is the core design choice.

Accuracy and relevance are different questions, with different evidence structures, different incentives, and different failure modes. If I force both questions into one mechanism, I either get bad truth adjudication or bad curation of importance.

So the protocol separates jurisdiction.

Accuracy disputes go outward to external dispute resolution.

Relevance stays inside the pool and is judged by drafted curators under the pool policy.

This is also where I rely on Schelling-style reasoning, but with caution. The system does not assume that people coordinate directly on truth. It assumes they coordinate on expected defensible judgment under explicit rules. That is a weaker claim, but I think it is the more realistic one.

A known limitation: the mechanism resists small colluding minorities, but at our reference parameters (K=1.25, 15-member committees) it degrades when a coordinated bloc exceeds roughly 15 to 20 percent of drafted stake. The threshold depends on the coherence parameter, committee size, and policy specificity. Below that threshold, honest reporting is stable; above it, a coordinating bloc can bend the relevance signal. This constraint is quantified in the paper but not yet solved.

The deeper point is that mechanism design begins only after the conceptual decomposition is done. If we start with mechanism design too early, we usually end up solving the wrong problem.

## Slide 9: How Truth Post Works

Let me walk through one item moving through the system.

Suppose the pool is world politics, and the item contains a claim like: "Country X imposed export controls this week."

First, there is a pool. A pool defines topic scope, a claim template, an evidence policy, and a relevance policy. So before any content appears, the rules of the local game are already public.

Second, an author submits an item into that pool and locks a bond behind it. The item becomes `Live` immediately.

At that moment, the protocol is not saying "this is true." It is saying: this item is publicly posted, capital is at risk, and the item is open to challenge.

Third, if someone sees a problem, they do not need to attack the whole article in a vague way. They challenge a specific proposition inside it. They put up counter-stake and specify the challenge reason, for example falsehood or non-falsifiability under the pool's own rules.

Fourth, that challenge pauses the item's normal life cycle and sends the accuracy question to the external juror layer. The jurors answer a narrow binary question about that challenge.

If the challenger wins, the item is `Debunked`.

If the challenger loses, the item returns to `Live`.

So accuracy is handled through explicit attackability, not through editorial blessing.

Fifth, while an item is live, the pool can run drafted relevance rounds. Curators who have staked into that pool can be drawn into a committee. They score how relevant the item is for that pool's purpose, then the mechanism rewards coherent judgments and slashes strong outliers.

That means the protocol does not ask jurors to decide what is important, and it does not ask curators to decide universal truth. Each group does one job.

Sixth, the item can accumulate confidence over time, but that confidence is not a truth certificate. It is closer to bonded survival. An item that has kept more capital at risk for longer while remaining exposed to public challenge sends a stronger signal than a fresh item that has barely been tested.

Finally, interfaces sit on top of the canonical protocol state. They can index the same underlying pools and disputes and render different views, but they do not own the underlying curation history.

So the mechanism in one sentence is this:

public pool rules define the local game, authors post bonded claims, challengers attack explicit propositions, jurors resolve accuracy disputes, drafted curators score relevance, and interfaces render the shared state for readers.

## Slide 10: This Problem Predates AI

I want to keep the AI point in proportion.

This problem existed before AI. The internet had already given us information abundance without solving the harder transformation from information into knowledge.

AI matters mainly because it accelerates an older pressure. It makes plausible output cheaper and increases the filtering burden, but it did not create the basic curation problem.

So even if we set AI aside entirely, I think the thesis still stands.

## Slide 11: Public Good Funding As Another Instantiation

I also want to connect this directly to public good funding, because I think that is one of the most important extensions.

An important caveat upfront: the thesis itself does not cover public good funding. What I am describing here is developed in a separate design document and is not covered by the simulations or formal analysis in the paper. I include it because it illustrates the framework's generality, but it should be understood as ongoing work, not a validated result.

The reason is that funding public goods is also a curation problem.

Before we allocate money, we need to answer upstream questions such as: which projects matter, for whom, under what objective, and by how much relative to the alternatives?

That is already a relevance problem. It is not primarily a binary truth problem.

If there are ten candidate public good beneficiaries, the target is not just a yes-or-no label on each one. The target is closer to a weight vector, where each entry represents how much of the pool should go to that beneficiary, each weight is between zero and one, and all the weights sum to one.

So in the public-goods setting, the object being curated is not only an article feed. It is an allocation vector.

That is why I think the framework transfers.

The same general logic still applies:

first identify the quality dimensions that matter, then choose mechanisms that match those dimensions.

Accuracy may still matter if projects make factual claims. But the harder question is usually relevance or priority: among many plausible beneficiaries, what relative weight should this system assign?

That is exactly the kind of problem a local, scalar, policy-dependent curation mechanism is meant to handle.

So my claim to this audience is not that I built a complete public-goods funding protocol inside this thesis.

My claim is that the decentralized curation framework, which I instantiate in detail for news, plausibly extends to public good funding by treating allocation as a curation problem over weights. That extension is sketched in a separate design document; the thesis provides the conceptual route but not the formal validation.

## Slide 12: What I Am And Am Not Claiming

I want to end with scope and modesty, because I do not think this thesis is strongest when it sounds sweeping.

I am not claiming that one protocol solves every epistemic problem, that every domain is ready for this immediately, or that the complete system has already been validated in production.

I am not claiming that governance disappears either. The design preference is to eliminate governance surfaces where possible, not to pretend policy choices vanish entirely.

I am also not claiming to solve everything downstream of shared knowledge. The thesis is intentionally upstream. And in the public-goods context, I am not claiming that curation alone is the full funding solution.

What I am claiming is narrower:

trustless decentralized curation is a serious research program, many failures described as governance or coordination failures are better diagnosed as upstream curation failures, and the framework provides a plausible path from news curation toward public good funding.

## Slide 13: Questions For The Room

The questions I most want help with are these.

First, where does the framework genuinely generalize, and where am I overextending from news?

Second, is the falsification asymmetry enough to ground a robust accuracy layer, or does it become too fragile once adversaries become strategic, well-funded, and patient?

Third, at what point does relevance policy design quietly reintroduce governance through the back door?

Fourth, what is the right empirical path from the current blueprint to a credible live validation of the full system?

And fifth, does the relevance mechanism actually generalize from ranking news inside a pool to producing useful funding weights over public good beneficiaries?

And sixth, if you think the main diagnosis is wrong, where exactly does it break? Is the failure in the claim that curation is upstream, in the mechanism assumptions, or in the jump from diagnosis to protocol design?

If the room leaves with those questions in mind, then the talk will have done what I need it to do.
