# Thesis Presentation Script

Approximate length: 20 minutes

## Opening

My thesis is simple to state and difficult to ignore:

most hard problems are actually curation problems.

For a long time, the bottleneck of civilization was access to information. Information was trapped in libraries, universities, archives, and institutions. The internet changed that. Today we have access to far more information than almost any generation before us. But that did not automatically make us wiser. It did not automatically make us more coordinated. It did not automatically make our institutions healthier.

Why not?

Because information is not knowledge.

Information becomes useful only after it is curated into something decision-grade: something you can rely on when you decide how to vote, what to build, what to fund, what to believe, and how to act.

And that is the core claim of my work: the internet solved access to information, but it did not solve access to knowledge. Curation, the transformation of information into knowledge, is still the bottleneck.

This matters because curation is not optional. When you search for travel destinations, you are consuming someone else’s curation. When you read a newspaper, you are consuming someone else’s curation. When you rely on rankings, reviews, feeds, summaries, or recommendations, you are outsourcing judgment.

That is useful. We cannot verify everything ourselves. We cannot sort and evaluate the entire world manually. But the moment we depend on a curator, we inherit that curator’s incentives, competence, and failure modes.

So the problem is not that curation exists. The problem is that curation is indispensable, high leverage, and usually trusted rather than mechanized.

## Why This Matters

Take news.

A newspaper is a curated set of claims about reality. People consume those claims and then make decisions. In a democracy, those decisions are collective and consequential. A functioning democracy assumes that voters are informed. But in practice, most voters are informed through third-party curation.

That creates two failure modes.

The first is incompetence. A curator may simply be wrong.

The second is weaponization. A curator may use control over the information-to-knowledge pipeline to shape the consumer’s worldview intentionally.

In both cases, the downstream damage is the same: people act on corrupted knowledge.

This is why I argue that many coordination failures are misdiagnosed. We keep trying to fix governance, voting, or collective decision-making directly. But often the deeper problem is upstream. People are trying to coordinate without a shared reality.

If two people trust that two plus two equals four, there is no coordination problem there. It scales from two people to two thousand. But if two groups inhabit different informational realities about politics, institutions, or public events, then governance becomes extremely hard. Not because humans are incapable of coordination, but because the knowledge layer underneath coordination is broken.

That is why I say governance is often a hidden curation problem.

So the contribution of this thesis is not just one protocol for one application. It is a general way of seeing a broad class of hard problems.

## The Framework

The central contribution of my thesis is a general framework for trustless decentralized curation.

It has four steps.

First, identify the hidden curation problem. Ask: what looks like a governance problem, or a coordination problem, or an allocation problem, but is actually failing because the knowledge layer is unreliable?

Second, identify the relevant quality dimensions. Information quality is not one thing. Wang and Strong made this point clearly in their work on multidimensional data quality. Depending on the use case, different dimensions matter: accuracy, relevance, timeliness, interpretability, completeness, and so on.

Third, require falsifiability. If a claim is easily verifiable, then you do not need a curation game around it. You can just verify it directly. If a claim is not falsifiable at all, then the mechanism has nothing to latch onto. The interesting middle is where verification is hard, but falsification is feasible.

Fourth, design mechanisms dimension by dimension. Different information qualities require different mechanisms. There is no single universal curation mechanism that works for all quality dimensions.

That framework is the backbone of the thesis.

It is domain-agnostic. In the thesis I instantiate it mainly for news, because news is where the problem is socially visible and the cost of failure is broadly distributed. But it is not a news-only framework.

## Why News Is The First Serious Use Case

When I apply the framework to news, two quality dimensions dominate: accuracy and relevance.

Accuracy is obvious. News should not be false.

But accuracy is not enough. A claim like “one equals one” is accurate, but it is not news. If you optimize only for accuracy, you do not solve the curation problem. You just produce a pile of correct but useless statements.

So the second crucial dimension is relevance.

Relevance is not binary in the same way. It includes importance, timeliness, and conformity to the curation goal. A perfectly accurate article about a football match may still be irrelevant in a world-politics pool. A voting result may be highly relevant today and far less relevant ten years later.

This is exactly why quality identification matters. The mechanism has to match the quality dimension. Accuracy and relevance are different problems and need different treatment.

This is also where the thesis becomes more than a complaint about media. It becomes a mechanism-design program.

## Falsifiability

Another core requirement of the framework is falsifiability.

This is where Popper is useful. Popper’s key point was that science advances not by proving universal claims exhaustively, but by making claims that could, in principle, be refuted by evidence. Falsifiability is what makes a claim operationally meaningful.

My thesis uses that insight in a practical, economic way.

I am interested in claims that are difficult to verify exhaustively, but feasible to falsify. News fits that pattern well. A claim about an event may be difficult to prove conclusively in a universal sense, but a single strong counterexample or contradiction can still falsify it.

That asymmetry is exactly what makes decentralized challenge mechanisms viable.

If a claim is non-falsifiable, the system should not pretend it can process it reliably. If a claim is trivially verifiable, the system is unnecessary. The mechanism is designed for the middle region where truth is expensive to establish but falsehood can still be attacked.

## Mechanism Design

Once you identify the relevant quality dimensions, you can stop thinking in slogans and start thinking in mechanism design.

For news, accuracy can be handled through a challenge-based dispute mechanism.

An author posts a claim together with a bond. A challenger can attack that claim by staking against it and providing evidence. The dispute is resolved through decentralized dispute resolution under an explicit policy and evidence standard.

The point is not that the protocol becomes an oracle of metaphysical truth. The point is that it creates transparent, contestable challenge outcomes and economic consequences for being wrong.

An important caveat: the mechanism makes falsehood expensive to sustain if challenged, but our simulations show the dominant bottleneck is detection coverage. At representative parameters, a false claim has about a 0.67 probability of surviving its first detection-and-challenge window. The system does not guarantee that false claims will be found; it guarantees that finding them is rewarded.

Relevance is different. Relevance is not well served by a binary yes-or-no process. Relevance is a ranking problem. It is about what matters more, not just whether something passes a threshold.

So for relevance I use a policy-guided coherence game. Curators stake into a pool, are drafted into rounds, and independently rate how strongly a claim conforms to the pool’s curation policy. Outliers are slashed. Coherent participants are rewarded.

This mechanism resists small colluding minorities, but at our reference parameters (K=1.25, 15-member committees) it degrades when a coordinated bloc exceeds roughly 15 to 20 percent of drafted stake. The threshold depends on the coherence parameter and committee size; it is not a universal constant. Below that threshold, honest reporting is the stable strategy; above it, a coordinating bloc can bend the signal. This is a known constraint, not a solved problem.

This is where Schelling-style reasoning becomes important. The mechanism does not ask curators to assert global truth. It asks them to converge on policy-grounded relevance under conditions where their incentives favor disciplined judgment.

The deeper point is this:

different information qualities require different mechanisms.

That sounds obvious once said clearly, but a lot of systems ignore it. They try to collapse everything into one signal. My thesis argues that serious decentralized curation cannot do that.

## Why This Problem Is Becoming More Urgent

I also argue that this problem is becoming structurally more important, not less.

Recent advances in AI make the curation bottleneck much worse.

Historically, the cost of producing information acted as a crude quality filter. Writing a convincing paper required understanding the topic. Writing working software required competence. The form of output and the substance behind it were coupled.

AI breaks that coupling.

Today, people can generate fluent prose, plausible structure, respectable formatting, and even working code without understanding what they produced. The form of quality has become cheap. The substance of quality has not.

That means the volume of credible-looking information is increasing faster than our ability to curate it.

So we are entering a world of information abundance and knowledge scarcity.

And that is why I say curation is not a side problem. It is becoming the bottleneck of civilization.

If we do not solve the transformation from information into knowledge, then improvements in generation, storage, and access only deepen the overload.

## Truth Post

At this point, I want to make something explicit.

This thesis is not just conceptual. It already has an implementation history.

In 2023, I launched Truth Post as a partial instantiation of this framework for news. It implemented the accuracy layer only: authors could submit staked claims, challengers could dispute them, and disputes were routed through Kleros.

That was not the full system. It was deliberately incomplete. There was no full relevance layer, no standing curator layer, no robust multi-interface architecture, and no complete economic bootstrap.

And it did not sustain participation.

That outcome is important, but its interpretation is ambiguous.

The deployment showed that the core submission-and-challenge flow can run on real infrastructure. But it did not establish why participation collapsed. My working interpretation is that accuracy alone is not enough to bootstrap sustained use: most claims are not interesting enough to challenge, and people do not come to a system just to verify boring truths. But competing explanations exist: the failure may also reflect gas costs, a narrow initial market, UX friction, or insufficient challenger incentives in a low-traffic environment. I cannot cleanly distinguish between these causes from the data available.

Truth Post also exposed the cold-start problem clearly. Without enough participants, you do not get meaningful signals. And it showed why protocol/interface separation is not optional: a decentralized protocol with a single fragile frontend is not actually robust.

So Truth Post matters in this presentation for one reason:

it shows that I am not standing here with only an abstract idea.

I pushed the framework into partial deployment, observed where it stalled, and used those observations to specify the full system more rigorously. Whether the stall reflects a flaw in the core model or only in the incomplete instantiation remains an open question.

That is what the current Truth Post blueprint represents.

In the complete design, the system is no longer just “post a claim and hope someone challenges it.” It becomes a full curation architecture:

- bonded claim submission
- explicit challenge and dispute flow
- a separate relevance layer with drafted curators
- confidence accumulation over stake and time
- pool-local reward budgets
- permissionless pool creation
- immutable contracts
- multi-interface and multi-indexer survivability

In other words, it becomes a real protocol design rather than a minimal experiment.

A necessary caveat: the design is backed by simulations at representative parameters but has not been deployed at scale. Several parameters, such as committee sizes, bond ratios, and slashing thresholds, lack formal optimality justification and are candidates for empirical calibration. The blueprint is detailed enough to constrain an implementation, but additional specification work remains before it is production-ready.

## Why I Think This Work Is Advanced

What makes this advanced is not that every piece is already deployed. It is that the field has been pushed several steps forward at once.

First, I am not presenting a single app idea. I am presenting a general framework that explains when decentralized curation is feasible and how to decompose it.

Second, I am not treating “truth” as one monolithic signal. I separate quality dimensions and assign mechanisms accordingly.

Third, I already have a real deployment retrospective. That is rare in work of this kind. Truth Post did not merely inspire the thesis; it constrained it.

Fourth, the complete protocol blueprint is no longer vague. It has concrete actors, objects, state machines, challenge flows, relevance flows, economic rules, and failure models. The design decisions are concrete enough to constrain an implementation, even though additional specification work remains.

And fifth, the framework generalizes.

## Advertising As A Second Instantiation

To show that this is a general framework rather than a news-only theory, consider advertising.

Advertising is one of the strongest second use cases because it is structurally wasteful. It is a negative-sum competition for attention. Participants keep spending resources until the contest reaches its feasibility limit.

That is why, in my own notes, I compare it to Bitcoin mining, water overconsumption, and arms races. These are different domains, but the same structure appears: participants consume slack resources until the game becomes infeasible.

Now imagine a different advertising game.

Instead of paying for attention in a way that rewards volume regardless of truth, advertisers express ads as claims and post a bond behind them.

If the claim is true, their main cost is temporary capital lockup.

If the claim is false, they lose the capital.

That inverts the current cost structure. Honest actors become cheap to accommodate. Dishonest actors become expensive to sustain.

And this is exactly why I include advertising in the thesis. It demonstrates that the framework is not tied to one political or journalistic niche. It applies wherever there is an information-to-knowledge bottleneck, public evidence, and feasible falsification.

## What This Thesis Is Actually Claiming

I want to be precise about the strength of the claim.

I am not claiming that decentralized curation solves every epistemic problem.

I am not claiming that every domain is immediately ready for this.

I am not claiming that the current full system is already live.

What I am claiming is this:

there is a general and underdeveloped field here.

That field is trustless decentralized curation.

Its central question is how to transform raw information into decision-grade knowledge without requiring trust in a central curator.

I am claiming that many problems usually described as governance failures, media failures, or coordination failures are better understood as curation failures upstream.

I am claiming that this problem can be structured rigorously.

I am claiming that the right way to structure it is:

problem definition, use case selection, quality identification, falsifiability, and mechanism design dimension by dimension.

And I am claiming that Truth Post is the most advanced implementation example of this framework so far, not because it is finished, but because it already moved from theory into deployment, failure, and redesign.

## Closing

So if I reduce the thesis to one sentence, it is this:

the bottleneck is not information access anymore; the bottleneck is curation.

And if I reduce the contribution to one sentence, it is this:

I am not just naming that bottleneck; I am proposing a general framework and a concrete protocol architecture for removing trust from it.

News is the main instantiation because it makes the problem visible. Truth Post is the implementation example because it shows this work has already passed the stage of vague speculation. Advertising is the second instantiation because it shows the framework is general.

What I want the audience to take away is not merely that I have a protocol idea.

It is that this is a serious research program around a real and growing bottleneck, that the conceptual framework is already in place, that the first implementation lessons already exist, and that the path from thesis to buildable system is now much shorter than most people assume.

That is the work.
