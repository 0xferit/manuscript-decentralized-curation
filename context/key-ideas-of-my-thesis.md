# Key Ideas of My Thesis

Cleaned transcript from the spoken draft in `transcription-me-explaining-my-core-ideas-for-this-thesis.txt`. The wording has been refined for readability, but the substance, examples, and argument order are preserved.

## Core Thesis

My thesis is that most hard coordination problems are actually curation problems.

Throughout human history, we built better and faster information systems. For most of history, the bottleneck was access to information. Information was gated in libraries, universities, and similar institutions, and the internet largely solved that problem. Today we have access to far more information than the average researcher had in the past. But that does not automatically make us smarter. Information is not useful by itself. It becomes useful only after it is curated.

For example, when you want to travel somewhere for vacation, what do you do? You search for the best travel destinations. That is an attempt to tap into someone else's knowledge, someone else's curated information about what the best destinations are. By consuming that curated information, you place trust in the curator's competence and good intentions.

That is not inherently wrong. We cannot curate everything by ourselves. We cannot verify, sort, categorize, and evaluate everything ourselves. By relying on other people's curation work, we increase our productivity. It is convenient and helpful. But trusting a curator comes with drawbacks.

## Why Curation Matters

Take news as an example. What is a newspaper? It is a collection of news articles curated by some entity. What do we do with the information we consume from newspapers? We make decisions. We make important decisions based on it. We may decide how to vote in a democratic setting based on the news we consume and the worldview that follows from it.

A well-functioning democracy assumes that voters are rational and informed. That means voters need to consume quality knowledge. If people are consuming newspapers curated by third parties, those third parties have the opportunity to weaponize that privilege by intentionally poisoning the consumer with disinformation. Even without malicious intent, incompetence can still produce bad knowledge. In one case the corruption is intentional; in the other it is accidental. Either way, the consumer is harmed.

My point is that curation is useful, but it carries costs because of its trust assumptions. Over centuries, despite making bigger and faster information systems, we did not make comparable progress in information quality, or more precisely, knowledge quality.

In this thesis I argue that many hard problems are actually curation-borne problems, and I propose a decentralized curation system in which you do not have to place trust in curators. The goal is to produce high-quality information through mechanism design rather than trust.

## High-Level Framework

I have a high-level framework for approaching these problems.

The first step is to identify a problem that looks like something else, but is actually a curation problem. Governance is a good example. Governance is notoriously hard: people make proposals, people vote, and the process often becomes a mess. Why is that? Why can stakeholders not converge on what is good for the entity they jointly own or govern?

Imagine a shared asset owned by one hundred people who collectively decide what to do with it. They all want to benefit from it, yet governance still fails. Or imagine an apartment building with many residents trying to make collective decisions. It is hard to take action. Is that because people simply cannot coordinate? I argue no. I argue that governance is often a curation problem.

To take action as a collective, people need a shared reality. If you and I share the same worldview, it becomes straightforward to converge on the same decision and take action together. But how do we arrive at a shared reality? We consume information, especially news. When news is unreliable or untrusted, people choose what they want to believe. That is why we do not argue about whether two plus two equals four, but we do argue about which political party to vote for. Two plus two equals four is trusted knowledge. It creates no coordination problem, whether there are two people or two thousand. But political judgment is difficult because people operate with different constructed realities, each shaped by incomplete and sometimes inaccurate information. In that sense, governance is actually a curation problem.

So the first step of the framework is to identify the hidden curation problem inside what appears to be some other hard problem.

The second step is to identify the nature of the curation problem. Information does not have a single universal quality. It has distinct qualities, and this is something Wang and Strong discuss in their 1996 paper, "Beyond Accuracy." Their core thesis is that data quality is multidimensional. Through empirical research and surveys of data consumers, they argue that data quality decomposes into multiple dimensions grouped into four categories: intrinsic dimensions such as accuracy, objectivity, believability, and reputation; contextual dimensions such as relevance, timeliness, completeness, and value-added amount; representational dimensions such as interpretability, ease of understanding, conciseness, and consistency; and accessibility dimensions such as accessibility and security.

The implication for my framework is that the second step is to identify which qualities of information matter for the particular curation problem you are trying to solve.

## News as a Use Case

In the news use case, which I studied extensively, I identified two especially important qualities: accuracy and relevance.

Accuracy is obvious. We want the news we consume to be accurate, not fake, not incorrect, not wrong. But accuracy alone is not enough. A statement like one equals one is accurate, but it is not news. So if you curate only for accuracy, you still fail to solve the problem.

The second quality is relevance. If you publish a newspaper about world politics and include a perfectly accurate article about a football game, that article may still be irrelevant to the curation goal. Relevance also includes importance and timeliness. A voting result may be very relevant the next day, but much less relevant ten years later. At that point it is old news.

That is what I mean by identifying the relevant quality dimensions for a specific use case.

## Falsifiability

I may have mixed up the numbering of the steps while speaking, but another necessary part of the framework is this: for the system to work, the information, or the claims, or the statements being processed need to be falsifiable.

If something is easily verifiable, there is no need to design games around it. You can simply present the proof and the matter is settled. We do not need elaborate curation mechanisms to determine whether one equals one or whether two plus two equals four, because those claims can be directly verified.

The kinds of claims I care about are those that are difficult to verify but easy to falsify. News is a good example. A claim that something happened can be hard to verify conclusively, but later evidence may emerge that falsifies it. That asymmetry is useful.

At this point in the original recording I paused to add Popper to my literature notes. Popper's core thesis in *The Logic of Scientific Discovery* is that a statement is scientific if and only if it is falsifiable. There must exist some possible observation that would contradict it. Verification is logically asymmetric with falsification: no finite set of observations can prove a universal claim, but a single counterexample can refute it. That asymmetry is the demarcation criterion between science and non-science.

My system taps into that concept. It cannot process non-falsifiable claims, such as claims about God. And it has no reason to process easily verifiable claims, because those can simply be verified directly.

## Mechanism Design

The final step is to craft a mechanism. In other words, the framework ends in mechanism design: distinct mechanisms for each identified dimension of information quality.

Using news again as the example, accuracy can plausibly be handled with a binary classification mechanism. A claim can be judged accurate or inaccurate. But relevance is not well served by a binary mechanism. Asking only "is this relevant?" does not help enough, because the real task is often to sort, rank, and weight relevance.

Public goods allocation makes this clearer. You do not just want to know whether funding a project is relevant or not. You want to identify which candidates are most relevant, and eventually assign weights. If you think of beneficiaries as a vector of weights between zero and one, where all weights sum to one, the goal is to arrive at a normalized weight vector that maximizes public benefit.

That is one of the core ideas in the thesis: different dimensions of curation require different mechanisms.

## Why This Problem Is Becoming More Urgent

I also argue that curation is the bottleneck of our civilization because we keep getting better at information access, creation, and storage.

Recent advances in AI make the curation problem much worse. It is now far cheaper to create information. People can produce well-structured papers, fluent prose, and working code without understanding what they have produced. The form of quality, such as proper formatting, confident language, and plausible presentation, has become trivially cheap to generate. The substance of quality, such as correctness, coherence, and domain understanding, has not.

The flood of machine-generated content that looks credible but lacks grounding makes the curation bottleneck not just important, but urgent. The volume of information that must be filtered, verified, and organized is growing faster and faster, while our curation capabilities are not becoming comparably more sophisticated.

Historically, the cost of producing information functioned as a crude quality filter, almost like a proof of work. Writing a convincing academic paper required understanding the subject. Writing functional software required knowing how to program. Competence and output were coupled, because producing the signal required the same effort that made it credible. AI breaks that coupling. People can now produce without understanding.

That leaves us, as a civilization, in a condition of information abundance but knowledge scarcity.

## Advertising as Another Use Case

I also want to mention another use case, and I think it is one of the strongest ones: advertising.

Advertising may be one of the most wasteful industries of all. What is produced in advertising? Nothing, in the usual sense. The industry is largely a competition for attention, and that competition escalates until it becomes infeasible. In game-theoretic terms, all participants spend as many resources as they can justify until the contest reaches its limit.

I see this as structurally similar to Bitcoin mining. Competing miners spend resources up to the point where the activity is just barely feasible. If you think about Bitcoin's electricity usage, people consume electricity until the marginal slack is exhausted. My claim is that advertisers do something similar with broader resources.

I used water as an analogy in the recording. If households reduce water usage, that may simply create slack that industry will absorb anyway, because industry also expands consumption up to the point of feasibility. In that framing, changing your own usage habits does not necessarily reduce total consumption; it can simply shift slack from one sector to another.

I also used the example of an arms race. One nation builds one unit of firepower, the rival builds two, then the first builds three, then the rival builds five. The process keeps escalating until it becomes infeasible. At that point everyone stops, which means all slack resources have already been consumed.

From this perspective, these are all similar negative-sum games. Everyone involved loses. Advertising is one instance of that broader pattern.

## A Different Advertising Game

Now imagine a different advertising game. Advertisements are expressed as claims: my product does this, my product does that, or my product is the best in some respect. On top of that claim, the advertiser posts a bounty.

If the claim is true, the advertiser's main cost is only that their capital is locked for some period of time. That is almost negligible compared with the current structure of advertising spend. But if the claim is false, the advertiser loses the capital.

This shifts cost away from honest actors with correct claims and toward bad actors making false claims. The result is that advertisements become negligibly cheap for honest producers, while consumers receive advertisements that function as quality knowledge. They learn what the best products actually are. In that sense the system benefits consumers and producers alike. The only actors who lose are the bad actors, and that is the intended behavior.

## Closing Note on Mechanisms

To come back to mechanism design: in this thesis I am using Schelling games extensively to design these mechanisms. I mentioned the mechanisms only vaguely in this recording, and I did not really explain how they work yet. I will go into mechanism design in a later recording.
