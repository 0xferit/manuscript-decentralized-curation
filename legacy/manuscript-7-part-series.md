# Decentralized Curation: A 7-Part Series

## Abstract

Modern systems fail downstream (governance, funding, coordination) because they fail upstream: they do not reliably transform raw information into **decision-grade knowledge**. This manuscript frames that transformation as **curation**, identifies why centralized curation predictably breaks (opacity, capture, gaming, censorship, fragility), and proposes a direction for fixing it: **trustless curation via decentralization**.

The core idea is mechanism design: make it **profitable to be right** and **expensive to be wrong**. We separate two distinct qualities of information: **accuracy** (human judgment, treated as binary classification under an evidence standard, resolved via dispute resolution) and **relevance** (non-binary importance, produced by policy-guided coherence games). The result is a protocol-level “knowledge layer” that any interface can consume, rather than a single platform’s private truth.

This is not a claim that blockchains “solve truth.” It is a claim that incentives can produce a scalable, auditable approximation: a system where falsehoods become liabilities, truth becomes an asset, and ambiguity is punished as harshly as error.

## Contributions (what is novel here)

- **Curation as the upstream bottleneck:** Treat “information → knowledge” as the failure point behind many coordination failures.
- **Separation of powers:** Split curation into **Accuracy (global, binary)** vs **Relevance (local, non-binary)**, with different mechanisms for each.
- **Attack-resilient incentive design:** Stake-to-verify, challenge bounties, pooled staking, commit-reveal voting, and appeal mechanics that reward principled minorities (“Lone Wolf payoff”).
- **Semantic precision as a security primitive:** “Vagueness = Rejection” as a first-class defense against misleading truths and legal/semantic ambiguity.
- **Sustainability story:** Funding via advertiser staking (“Proof of Truth”) plus public-good funding (“Truth Automata”) to survive both peacetime and vampire attacks.

## Threat model (what we defend against)

We assume adversaries can be rational, coordinated, well-funded, and persistent. The design explicitly targets:

- **Economic attacks:** rich liars, bribery/collusion, low-stake spam, free riding (vampires).
- **Game-theoretic attacks:** lazy majorities, herding, “consensus over correctness.”
- **Social/legal attacks:** chilling effects (liability), toxic content, interface capture.
- **Epistemic attacks:** ambiguity/context collapse, temporal decay (“frozen truth”).

Out of scope: breaking cryptography, coercion at gunpoint, and global-scale censorship of all clients at once.

## Scope and Assumptions

Before diving into mechanism design, it is worth making explicit what this paper takes as given, what it designs, and where the boundaries lie. Every system rests on assumptions. The honest thing to do is name them.

### Assumption 1: Trustless Arbitration Exists as an External Dependency

This paper does **not** design a Decentralized Dispute Resolver (DDR). It designs the **curation layer** that feeds disputes into a DDR. The DDR — we use [Kleros](https://kleros.io/whitepaper.pdf) as the reference implementation — is treated as a black box that accepts a well-formed dispute (claim, evidence, resolution criteria) and returns a verdict.

This is a meaningful dependency, and it requires a defense, because the DDR itself relies on Schelling-point coordination among jurors — and this paper's relevance mechanism **also** uses Schelling games (the coherence game in Part 5). We are building on Schelling coordination at two layers. That demands honesty about what Schelling coordination actually claims.

**What Schelling coordination does NOT claim:** It does not claim that consensus equals truth. A room full of people can coordinate on a wrong answer if the wrong answer is more obvious than the right one.

**What Schelling coordination DOES claim:** When a question is **well-posed** — falsifiable, with clear resolution criteria — then "correct" becomes the natural focal point, because it is the easiest answer to coordinate on. If I ask "Did Company X report revenue above $1B in Q3 2025, per their SEC filing?", the correct answer is the Schelling point because it is verifiable by anyone willing to look. Coordinating on the wrong answer requires explicit collusion; coordinating on the right answer requires only that each juror independently checks the evidence.

This is precisely why **Principle 3 (Semantic Precision)** exists. Semantic precision is not a stylistic preference — it is a **game-theoretic requirement**. Well-posed questions make the Schelling focal point align with correctness. Poorly-posed questions make it align with whatever is most "obvious," which may be wrong.

When a question is **not** well-posed — ambiguous, under-specified, or lacking clear resolution criteria — the correct Schelling focal point is **"Under-specified."** The system does not force jurors to guess True or False on a bad question. It gives them a third option that is itself the natural focal point for ambiguous inputs.

Two additional mechanisms bound the failure modes:

- **Infinite appeals** provide error-correction within the game. If a Schelling outcome is wrong, the appeal system allows escalation (see Section 4 below). Appeals must be theoretically infinite — no hard cap — because a known final round degrades via backward induction. Exponentially escalating costs make appeals self-limiting in practice.
- **Forking** provides the ultimate backstop **outside** the game. If the DDR itself is captured or systematically corrupted, the community can fork the protocol, taking the honest participants and their stakes to a new chain. This is covered in detail in Part 7 and formalized in Section 3 below.

The [Ohio State socio-legal case study of Kleros](https://moritzlaw.osu.edu/sites/default/files/2022-08/10-%20BERGOLLA%2055-98.pdf) (Bergolla, Seif & Eken, 2022) and the [Columbia Science and Technology Law Review analysis](https://journals.library.columbia.edu/index.php/stlr/blog/view/84) both document real limitations of Schelling-point adjudication — juror passivity, coordination failures, interface friction. We do not dismiss these findings. We argue that semantic precision and infinite appeals **mitigate** (not eliminate) the failure modes they identify.

### Assumption 2: Blockchain Liveness and Smart Contract Correctness

Standard cryptographic assumption. The protocol assumes the underlying blockchain (Ethereum or equivalent) provides liveness, finality, and correct execution of deployed smart contracts. If the base layer fails, everything above it fails. This is not unique to this design — it is shared by every DeFi protocol, every DAO, every on-chain system.

### Assumption 3: Evidence Authenticity Is Unverifiable On-Chain

The protocol can verify that evidence was **submitted** (timestamped, hashed, recorded on-chain). It **cannot** verify that the evidence is **genuine**. A challenger can submit a fabricated document. A claim author can cite a real-looking but doctored study.

This is explicitly acknowledged as a trust assumption. The protocol's defense is **adversarial**: if fabricated evidence is submitted, the opposing party has the incentive and the opportunity to submit counter-evidence exposing the fabrication. The DDR jurors evaluate both. But the protocol itself has no oracle for "is this PDF real?" — and pretending otherwise would be dishonest.

This limitation is shared by every dispute resolution system, including traditional courts. Courts rely on rules of evidence, expert testimony, and cross-examination to surface fabrication. The DDR relies on adversarial incentives and juror judgment. Neither is perfect.

### Assumption 4: Rational Actors with Bounded Information

Participants are **economically rational** — they respond to incentives, seek to maximize expected value, and avoid negative-expected-value actions. They are **not** omniscient. They have bounded information, bounded computational capacity, and bounded attention.

The system is designed for **rational adversaries**, not for irrational ones. An attacker who is willing to burn $10M to destroy a $1M protocol cannot be stopped by mechanism design — only by making the protocol not worth attacking in the first place. The threat model (Section 1.3) makes this explicit.

This assumption also means the system does **not** require altruism. Curators do not need to care about truth for its own sake. They need to find it profitable to curate honestly. If the incentives are right, honest behavior emerges from self-interest. That is the entire point.

## Stress tests (attacks & where addressed)

|   # | Attack vector                                                     | Where it is addressed                                            |
| --: | ----------------------------------------------------------------- | ---------------------------------------------------------------- |
|   1 | Lazy majority equilibrium                                         | Part 4 (Flow 3) + Part 5 (“Attack 2: The Lazy Curator”)          |
|   2 | “Subreddit war” / echo chambers                                   | Part 5 (Accuracy vs Relevance) + Part 6 (“Echo chambers”)        |
|   3 | Post-truth apathy                                                 | Part 6 (“Post-truth apathy”)                                     |
|   4 | Low-stake lies survive (“Boring dystopia”)                        | Part 4 (Flow 1: Low Stake = Low Signal)                          |
|   5 | Oracle capture (51% attack)                                       | Part 7 (Challenge 1)                                             |
|   6 | Rich get richer                                                   | Part 5 (Reputation as Capital) + Part 6 (Human factors)          |
|   7 | Chilling effect / liability                                       | Part 4 (Flow 2: pooled staking)                                  |
|   8 | Meta-curation / interface capture                                 | Part 6 (“Meta-Curation trap”)                                    |
|   9 | No yield in peacetime                                             | Part 7 (“Advertising as Proof of Truth” + peacetime yield)       |
|  10 | Toxic/illegal content                                             | Part 6 (Protocol vs Interface)                                   |
|  11 | Mediocrity / consensus-as-truth                                   | Part 5 (“Attack 3” + Lone Wolf payoff)                           |
|  12 | Context collapse / vagueness                                      | Part 3 (Principle 3: Semantic Precision)                         |
|  13 | Frozen truth / temporal decay                                     | Part 7 (Challenge 3)                                             |
|  14 | Vampire attack / free riding                                      | Part 7 (Challenge 2)                                             |
|  15 | Ambiguous questions / legal semantics (“Consensus ≠ correctness”) | Part 3 (Semantic Precision) + Part 5 (“Consensus ≠ correctness”) |

## Table of Contents

**Front Matter:** Abstract, Contributions, Threat Model, Scope and Assumptions, Stress Tests

1. **The Problem: Curation as the Bottleneck**
2. **What's Broken: Framework, Failure Modes, and Better Curation**
   - Related Work
3. **The Solution: Principles of Decentralized Curation**
   - Why This Is Not a TCR
4. **Architecture: How Decentralized Curation Works**
   - The Truth Post: Lessons from an MVP
5. **Game Theory: Making Honesty Profitable**
   - Infinite Appeals and Backward Induction
6. **Governance & UX: Making It Actually Work**
7. **The Future: Beyond News, Beyond Trust**
   - Advertising as Proof of Truth
   - The Economics of Forking

---

# Part 1: The Problem - Curation as the Bottleneck

## Why Information Curation Is Broken (and Why It Matters)

---

### 0. The simple idea that explains a lot

Uncoordinated actions cancel out. Coordinated actions compound.

But coordination is not where things usually break.

To coordinate, people first need to share a picture of reality: what is happening, what matters, what might work. That shared picture does not magically appear. It's produced by **curation**—by what we pay attention to, believe, and ignore.

**Curation transforms raw information into knowledge.**

So you can think of most hard problems as two-phase:

1. **Curation:** Transform information into knowledge—converge on "what is true and important enough to act on"
2. **Coordination:** Align actions, given that shared knowledge

The claim in this piece is blunt: **the bottleneck is almost always phase one.** We keep trying to fix coordination with better governance, better voting, better funding mechanisms, while standing on a broken knowledge layer.

### 1. The age of information abundance, but knowledge scarcity

For most of history, the hard part was getting information at all.

Books were scarce. Universities gatekept knowledge. If you weren't physically near the right libraries, people, or institutions, you were out of luck.

The internet blew that bottleneck apart. Now, anyone with a phone has access to more _information_ than the average professor did a generation ago. Information in the technical sense: raw signals, data points, claims. That sounds like victory—until you notice what actually changed:

**Access to information is solved.**
**Access to knowledge is not.**

We need to be precise about terms here:

- **Information** is a signal—data, a claim, a data point. Raw and unverified.
- **Knowledge** is information that has been verified, contextualized, and integrated into a coherent understanding.

Curation is what transforms information into knowledge.

Before the internet, this transformation happened through institutions: newspapers selected which stories mattered, academic journals peer-reviewed claims, universities taught frameworks for understanding. The process was slow and imperfect, but it produced knowledge: information you could trust and act on.

Now, we have vastly more _information_. But we're drowning in signals without the structural processes to turn them into knowledge.

A good way to visualize this:

- A **pile of data** on the floor: huge, impressive, and almost useless. Terabytes of information.
- A **library**: the same information, but organized, indexed, verified, contextualized. Transformed into knowledge.

The difference is not the information. It's the **curation structure** that turns information into knowledge.

### 2. When common knowledge fails

When coordination fails, it often doesn't look like a coordination problem. It looks like stubbornness, polarization, or bad faith.

But underneath, something more fundamental is breaking: **the collapse of shared knowledge.**

In game theory, **common knowledge** means not just that I know X, but that you know X, and we both know that we both know X, and so on infinitely. This infinite loop of mutual understanding is what lets us coordinate safely.

Experimental research shows that people routinely treat shallow shared understanding as rock-solid when they actually lack this infinite loop of common knowledge. In situations requiring true common knowledge, they take risky actions and suffer real penalties when coordination breaks. The result: **an illusion of shared knowledge that masks incompatible understanding** [@bolander2020common].

That is what modern life feels like, scaled up:

- "Everyone" saw the same information… except they didn't. But they _feel_ like they did because their curated feeds showed similar things.
- "Everyone" knows the same facts about the election… except their feeds presented completely different information.
- "We all agree on the science"… except half the population was shown different information that led them to different knowledge.

On the surface, the failures look like stubbornness or polarization or bad faith. Underneath, they are very often **curation failures**: people are trying to coordinate from different knowledge slices—built from different information, curated by different systems, trusting different sources.

They have the _feeling_ of shared knowledge. But the actual knowledge is incompatible.

### 3. Who loses, who wins

When curation breaks, the damage is not evenly distributed.

**Users lose twice:**
First in time—endless filtering through information, constant uncertainty, decision paralysis.
Then in knowledge quality—beliefs built on corrupted information, leading to bad decisions.

**Honest creators lose:**
Journalists, researchers, and creators who invest in rigorous information verification compete against those who produce sensational signals. The sensational information often wins distribution, because attention is the currency that platforms reward.

**Platforms win engagement, but lose trust:**
Short-term metrics go up (clicks, shares, time-on-site). Long-term legitimacy erodes. Global trust in news hovers around 40% [@reuters2024digitalnews], with lower figures in many developed markets. Once trust drops below a threshold, "just trust us" stops working as a strategy.

**Society loses knowledge coherence:**
When groups operate from incompatible curated information, they build incompatible knowledge. Climate, vaccines, election integrity, economic policy: these become not debates but collisions between separate knowledge systems. You cannot coordinate action when you don't share knowledge of what's real.

---

## Part 2: What's Broken - Framework, Failure Modes, and Better Curation

### A framework for understanding curation systems

To diagnose failures precisely, we need a framework for decomposing any curation system into its core components.

Every curation system contains:

**Actors:**

- **Creators:** produce information
- **Curators:** decide what information gets verified and elevated to "knowledge"
- **Consumers:** consume the curated knowledge
- **Challengers/Validators:** dispute curation decisions
- **Attackers:** try to game the system

**Information flow:**

1. Creation (someone produces a claim)
2. Submission (enters the curation system)
3. Verification (system decides whether to elevate to "knowledge")
4. Consumption (users see the curated knowledge)
5. Feedback (users react; does this loop back to improve curation?)

**Incentives:**

- Economic (money, revenue, ad income)
- Reputational (credibility, followers, citations)
- Ideological (mission, values)
- Social (belonging, recognition)

**Critical insight:** A system's actual behavior is determined by its incentive structure, not by its stated goals.

If a platform says "we care about knowledge quality" but pays curators based on engagement, the system will optimize for engagement—not knowledge reliability.

### The five failure modes of centralized curation

When one entity controls the transformation of information into knowledge, failure becomes inevitable:

**Failure Mode 1: Opacity**
Rules for what becomes knowledge are hidden. Users don't know why decisions were made.

- _Example:_ Twitter shadowbanning—users noticed their tweets weren't appearing in search results, but Twitter denied the practice. Later, investigation showed it was partly algorithmic error and partly deliberate filtering—but the original opacity destroyed trust.

**Failure Mode 2: Capture**
The curation system is nominally independent, but actually serves interests other than knowledge quality.

- _Example:_ Facebook optimized for engagement (likes, comments, shares). This rewarded outrage, misinformation, and divisive content. Internal research (the "Facebook Papers") showed the algorithm amplified polarizing information, but the company continued because engagement drives ad revenue.

**Failure Mode 3: Gaming**
Actors figure out the curation rules and exploit them to elevate false information to "knowledge" status.

- _Example:_ Review systems (Amazon, Yelp, Airbnb): Fake reviews are cheap to create and profitable to scale. If the curation system can't distinguish them, fake reviews dominate what becomes "known" about products.

**Failure Mode 4: Censorship**
One entity can unilaterally suppress information from becoming "known."

- _Example:_ Platform moderation asymmetry—information from one person is removed; similar content from another person stays up. Rules exist but are applied inconsistently.

**Failure Mode 5: Fragility**
The system has single points of failure. One algorithm change, policy shift, or acquisition can destroy the entire knowledge-production system.

- _Example:_ When Elon Musk acquired Twitter and changed the algorithm, what counted as "visible knowledge" changed unpredictably. Creators who built livelihoods on the old algorithm faced collapse. No warning, no appeal, no participation.

**The common pattern:** Each failure mode traces back to the same root: **Centralized curation concentrates power over knowledge production in one entity, and power + misaligned incentives = inevitable failure.**

### What good curation actually means

Now that we've diagnosed the failures, what should we be optimizing for?

Any curation system transforms raw information into knowledge. But what makes that transformation successful? We must ground our answer in two complementary frameworks: **epistemology** (the philosophy of knowledge) and **data quality standards** (industry-proven measurement systems).

**If you want the punchline (and want to skip the deep dive):** good curation means claims are (1) **well-posed** (falsifiable, not vague), (2) **evidence-backed** under an explicit standard, (3) **internally consistent** with other validated claims, (4) **current** (truth decays), and (5) **auditable** (who said what, why, and with what evidence).

The rest of this section gives a rigorous grounding for those requirements. If you're reading for the mechanism design, you can skip directly to **Part 3** and come back later.

## The Epistemological Foundations: What Makes Knowledge "Good"?

Traditional epistemology holds that **knowledge is justified true belief (JTB)**. To understand what curation should produce, we need to unpack what each component means:

### 1. **Truth (The Correspondence Condition)**

**Definition:** A claim corresponds to reality. It is "what is the case," not what is false.

**Why it matters:** False information doesn't just mislead—it cascades. One false belief can corrupt downstream decisions and understandings.

**How it's tested:**

- Can the claim be verified against evidence?
- Does it match observable reality?
- Do multiple independent methods confirm it?

**Examples:**

- ✓ "Paris temperatures on 2024-01-31 were X°C" (can be verified against weather station data)
- ✓ "The FDA approved drug X in 2023" (can be verified against regulatory records)
- ✗ "This product is amazing" (not a truth claim; subjective preference)

**The challenge:** Some claims are hard to verify—complex systems, future predictions, or historical events with limited records. The curation system must distinguish between **unverified** (might be true, insufficient evidence) and **false** (contradicted by evidence).

---

### 2. **Justification (The Rational Support Condition)**

**Definition:** A belief is held for good reasons. The claim has adequate rational support to warrant acceptance.

Epistemology identifies several sources of justification:

#### **A. Foundationalism: Basic Beliefs & Evidence**

Some beliefs are self-justifying or directly grounded in evidence (foundational beliefs). Others derive justification from these foundations through inference.

- **Basic beliefs (foundational):** Direct observations. "I observe rain falling."
- **Inferred beliefs (non-basic):** "It rained last night" (inferred from wet pavement).

For a claim to be justified, there must be a chain of reasoning back to solid evidence.

**Good justification:**

- "This phenomenon was observed in 50 replicated studies" (strong foundational support)
- "The historical record shows this event occurred" (primary source evidence)

**Weak justification:**

- "Everyone knows this" (vague, no foundational support)
- "A celebrity said it" (appeals to authority, not evidence)

#### **B. Coherentism: Internal Consistency**

Beliefs are justified when they **cohere** with other accepted beliefs and don't contradict them.

- **Logical consistency:** Does the claim contradict other validated claims?
- **Explanatory relations:** Does it fit into a coherent system of understanding?
- **Inductive support:** Do other beliefs support this one?

**Good coherence:**

- A new study fits with prior research in the field
- Historical evidence doesn't contradict the claim

**Bad coherence:**

- "X happened in 2020" but "X was first discovered in 2025" (direct contradiction)
- A claim contradicts established scientific consensus without adequate explanation

#### **C. Reliabilism: Source Reliability**

A belief is justified if it's produced by a reliable process—one that tends to produce true beliefs.

- **Reliable sources:** Peer-reviewed journals, regulatory agencies, established researchers
- **Unreliable sources:** Anonymous forums, heavily partisan media, sources with financial incentives to lie

**Examples of reliability:**

- ✓ Data from peer-reviewed experiment (reliable process = scientific method)
- ✓ Historical record from archival sources (reliable process = documentary evidence)
- ✗ Rumor from an acquaintance (unreliable process = unverified transmission)

---

### 3. **Belief (The Conviction Condition)**

**Definition:** The claim is not merely entertained—it is actually believed/asserted as true.

**Why it matters:** A claim you don't actually believe is not knowledge, even if it's true and justified. This prevents "lucky guesses" from counting as knowledge.

**How it's tested:**

- Is the claim explicitly asserted as true?
- Or is it hedged ("might be," "possibly")?
- Does the author stand behind it?

**Examples:**

- ✓ "The Earth orbits the Sun" (asserted as fact)
- ✗ "The Earth might orbit the Sun" (hedged, not a full belief claim)

---

### 4. **No False Lemmas (Internal Coherence)**

A belief should not depend on false premises. Even if your conclusion is true, if you arrived at it through false reasoning, it may not count as knowledge.

**Example (Gettier case):**

- You look at a clock that is stopped at 3:00 PM
- You believe it's 3:00 PM (your belief is true—it actually is 3:00 PM)
- Your belief is justified (you have good reason to trust the clock)
- But you don't have knowledge, because your justification depends on the false premise that "this clock is working"

**For curation:** This means validators must examine not just whether a conclusion is true, but whether the reasoning leading to it is sound.

---

### 5. **Appropriate Causal Connection (Externalist Condition)**

A belief should be causally connected to its truth in the right way. Your belief should arise from a process that reliably produces true beliefs about that domain.

**Good causal chain:**

- Scientist performs experiment → observes results → forms belief based on results
- Historical researcher examines primary documents → reads them → forms belief about what happened

**Bad causal chain:**

- You flip a coin (heads = believe X, tails = don't believe X) → it lands heads → you form belief X
- Even if X happens to be true, your belief didn't arise from a process that tracks truth

**For curation:** This means the system must audit how claims were formed, not just whether they're currently supported.

---

### 6. **Testimony as Evidence (Social Epistemology)**

Modern epistemology recognizes that much of what we know comes through testimony—we rely on others' assertions.

For testimony to generate knowledge (not just belief), three conditions typically apply:

- **Speaker reliability:** Is the speaker trustworthy and knowledgeable?
- **Hearer reasonableness:** Is the hearer in a position to evaluate the testimony?
- **Proper function:** Is the testimonial context normal (not adversarial, deceptive)?

**Good testimony:**

- "According to the peer-reviewed study [authors, year, journal]..." (speaker is transparent about source)
- "The historical record shows..." (speaker cites primary evidence)

**Bad testimony:**

- "Scientists say..." (vague; can't evaluate speaker reliability)
- "Everyone knows..." (no source; anonymous)

**For curation:** The system must track the chain of testimony and flag when sources are unclear.

---

## Data Quality Standards: Industrial Measurement Frameworks

Beyond epistemology, the data quality industry has developed **measurable dimensions** to assess information quality. These are grounded in decades of work across databases, analytics, and information systems (ISO 8000 standard).

The **Six Core Data Quality Dimensions** are:

### **1. Accuracy**

How well does the data represent reality? Does it match ground truth?

**How measured:** Percentage of records verified against ground truth, discrepancy detection rates

**Examples:**

- ✓ "Customer address verified against postal database (95% match)"
- ✗ "Product weight listed as 500kg when actual is 5kg"

### **2. Completeness**

Is all required information present? Are there gaps or missing values?

**How measured:** Percentage of non-NULL values, coverage rate across required fields

**Examples:**

- ✓ "Customer record has name, address, phone, email (100% complete)"
- ✗ "Dataset missing 40% of temperature readings"

### **3. Consistency**

Does information match across systems, databases, or time periods? Are there conflicting versions?

**How measured:** Cross-system reconciliation checks, format conformity, structural alignment

**Examples:**

- ✓ "Customer name 'John Smith' in CRM, 'Smith, John' in billing (different format, same person)"
- ✗ "Sales database $100, Finance database $150 for same transaction"

### **4. Timeliness**

Is the information current? When was it last updated? Available when needed?

**How measured:** Data age/freshness, latency, meeting user expectations

**Examples:**

- ✓ "Real-time stock feeds update every millisecond"
- ✗ "Weather forecast from 3 days ago used for today's planning"

### **5. Validity**

Does the data conform to specified formats and business rules?

**How measured:** Percentage conforming to schema, format compliance, business rule violations

**Examples:**

- ✓ "All phone numbers stored as valid 10-digit format"
- ✗ "Salary negative, age > 150 years old"

### **6. Uniqueness**

Are there duplicate or redundant records? Is each piece represented only once?

**How measured:** Duplicate detection rates, primary key collision rates

**Examples:**

- ✓ "Each customer ID is unique across system"
- ✗ "Customer 'John Smith' appears 47 times with different IDs"

---

## Information Credibility Framework

The **Five-Component Credibility Checklist** (used in digital literacy):

### **1. Accuracy**

- Is content free from errors?
- Can information be verified elsewhere?
- Has it been fact-checked?

### **2. Authority**

- Who is the author/creator?
- What are their credentials?
- Does source provide contact/affiliation?
- Is it recommended by trusted institutions?

### **3. Objectivity**

- Is there stated purpose/bias?
- Is content balanced or one-sided?
- Are multiple perspectives presented?
- Are sources cited?

### **4. Currency**

- When was it last updated?
- Still relevant/valid?
- Are links current or broken?
- Does it account for recent developments?

### **5. Coverage/Scope**

- What is included and excluded?
- Are limitations acknowledged?
- Who is intended audience?
- What is depth of treatment?

---

## Integrated Quality Standards

A claim passes the quality test when it satisfies:

| Category            | Standard               | How to Test                      | Connection                |
| ------------------- | ---------------------- | -------------------------------- | ------------------------- |
| **Epistemological** | Truth                  | Verifiable against evidence      | Correspondence to reality |
| **Epistemological** | Justified (Foundation) | Traceable to solid evidence      | Rational support          |
| **Epistemological** | Justified (Coherent)   | No contradictions                | Internal consistency      |
| **Epistemological** | Justified (Reliable)   | From trustworthy source          | Reliable process          |
| **Epistemological** | Testimony              | Sources identified, trackable    | Social verification       |
| **Data Quality**    | Accuracy               | % match vs. ground truth         | Matches reality           |
| **Data Quality**    | Completeness           | All required info present        | No critical gaps          |
| **Data Quality**    | Consistency            | Matches across systems           | No conflicting versions   |
| **Data Quality**    | Timeliness             | Current, available when needed   | Reflects present state    |
| **Data Quality**    | Validity               | Conforms to format/rules         | Usable and verifiable     |
| **Data Quality**    | Uniqueness             | No duplicates                    | Evidence not multiplied   |
| **Credibility**     | Authority              | Identifiable, credible source    | Source evaluable          |
| **Credibility**     | Objectivity            | Balanced, biases disclosed       | Context understood        |
| **Credibility**     | Currency               | Recent, updated, valid           | Not obsolete              |
| **Credibility**     | Coverage               | Scope clear, limits acknowledged | Appropriate for use       |

---

## The Seven Curation Objectives

### **1. Epistemic Justification & Evidence Standards**

Claims must be true, justified, from reliable sources, and internally coherent. They must also be accurate, complete, consistent, valid, and unique.

### **2. Credibility & Authority**

Information from identifiable, credible sources whose expertise and bias can be evaluated. Anonymous or untraced claims deprioritized.

### **3. Timeliness & Currency**

Information current and delivered when needed. System tracks when claims become superseded by newer evidence.

### **4. Diversity**

Multiple perspectives surface; minority views not suppressed. However, diversity ≠ false balance. All views must meet epistemological standards.

### **5. Integrity**

System resists manipulation. Validators have skin in the game (staked capital), making dishonest validation expensive.

### **6. Transparency**

Rules for justified belief are explicit and auditable. Users see why claims were accepted/rejected based on which criteria passed.

### **7. Accessibility**

System usable by diverse participants. Expertise required should be domain-specific, not technical curation knowledge.

---

## The Fundamental Trade-Off

These objectives conflict fundamentally:

- **Justification vs. Speed:** High rigor takes time. Speed sacrifices verification.
- **Completeness vs. Novelty:** Waiting for complete info means late publication. Incomplete early info speeds response but risks errors.
- **Consistency vs. Innovation:** Contradicting established knowledge gets downranked but may represent breakthroughs.
- **Authority vs. Diversity:** Privileging experts reduces noise but suppresses novel voices.
- **Transparency vs. Security:** Public rules are exploitable. Secret rules can't be audited.

**No centralized system excels across all dimensions.**

- Academic journals: Quality, integrity; fail at speed, accessibility
- Twitter: Relevance, timeliness; fail at quality, integrity, transparency
- Social media: Engagement; fail at epistemological standards

**Fundamental constraint:** Centralized control forces trade-offs because one entity decides. That entity has incentives favoring some objectives over others.

**Solution:** Distribute power. Let competing validators optimize for different objectives using transparent standards.

## Related Work

This section positions the design relative to the existing literature. The goal is not comprehensiveness but clarity: where does this work sit, what does it borrow, and where does it diverge?

### Mechanism Design for Public Goods

The idea that self-interest can be harnessed for socially optimal outcomes in public goods provision was formalized by [Groves & Ledyard (1977)](https://www.jstor.org/stable/1914085). Their paper solved the classical free rider problem — the assumption, dominant since [Samuelson (1954)](https://www.jstor.org/stable/1925895), that public goods would always be undersupplied because rational agents conceal their true preferences. Groves-Ledyard constructed a class of allocation-and-tax mechanisms where truthful preference revelation is the Nash equilibrium: each consumer's tax includes a penalty proportional to how much their reported valuation deviates from the mean of the others' reports. Lying costs more than truth-telling. Both Welfare Theorems hold.

Curated knowledge is a public good. It is non-excludable (anyone can consume it once produced) and non-rivalrous (one person's use does not diminish another's). The classical prediction applies: without intervention, curation will be undersupplied. Rational agents will consume curated knowledge without contributing to its production — the "lazy curator" problem this protocol explicitly addresses.

This protocol applies the Groves-Ledyard insight to knowledge production. The coherence game penalizes curators whose relevance assessments deviate excessively from the group mean — structurally analogous to the quadratic deviation penalty in the Groves-Ledyard tax rule. The bounty-and-challenge mechanism for accuracy makes it individually rational to verify rather than free-ride, because challengers capture the stakes of those who curate dishonestly. In both cases, the mechanism designer does not need to observe truth directly. The mechanism makes truth-telling the cheapest strategy.

The key difference: Groves-Ledyard assume a single, well-defined public good with cardinal preferences. Curation operates over a high-dimensional claim space with two distinct quality dimensions (accuracy and relevance), adversarial participants, and no central allocator. The mechanism design challenge is correspondingly harder — but the foundational insight is the same.

### Token-Curated Registries

[TCRs (Goldin, 2017)](https://medium.com/@ilovebagels/token-curated-registries-1-0-61a232f8dac7) are the most direct ancestor. They proposed stake-weighted curation for maintaining quality lists — a powerful idea that struggled in practice. The [Gitcoin mechanism analysis](https://gitcoin.co/mechanisms/token-curated-registry) provides a comprehensive overview of TCR mechanics and deployment history. adChain, the first live TCR (2018), suffered from low participation and curator apathy. [Kosmarski & Gordiychuk (2020)](https://onlinelibrary.wiley.com/doi/10.1002/leap.1302) proposed TCRs for scholarly journals, identifying real problems in peer review incentives but inheriting TCR structural limitations.

This work generalizes TCRs from binary list inclusion to **structured claims with evidence**, separates accuracy from relevance, replaces fixed deposits with variable bounties, and introduces pooled staking to address the participation problem (see Section 2 above for the full comparison).

### Kleros and Decentralized Dispute Resolution

The protocol uses Kleros-style DDR as a building block. The [Kleros whitepaper](https://kleros.io/whitepaper.pdf) (Lesaege, Ast & George, 2019) describes the Schelling-point jury mechanism, commit-reveal voting, and the appeal system. The [Ohio State socio-legal case study](https://moritzlaw.osu.edu/sites/default/files/2022-08/10-%20BERGOLLA%2055-98.pdf) (Bergolla, Seif & Eken, 2022) provides the most rigorous empirical analysis of Kleros to date — introducing the concept of the "decentralized sheriff" while documenting adoption barriers including juror interface friction, PNK token economics, and trust formation challenges. The [Columbia STLR analysis](https://journals.library.columbia.edu/index.php/stlr/blog/view/84) evaluates Kleros through a legal lens, questioning whether game-theoretic incentives can substitute for procedural safeguards.

We take these critiques seriously. The curation protocol is designed to **mitigate** known DDR failure modes: Semantic Precision (Principle 3) constrains the input quality so jurors receive well-posed questions rather than ambiguous ones. Infinite appeals provide error-correction. Forking provides an exit if the DDR itself is captured. But we do not claim these mitigations are complete — the DDR remains a trust assumption (see Section 1, Assumption 1).

### Peer Prediction Mechanisms

Peer prediction ([Jurca & Faltings, 2014](https://arxiv.org/abs/1401.3451)) elicits truthful reports **without verification** by comparing agents' reports against each other. The core idea: if your report about X is statistically consistent with another independent reporter's observation of X, you are probably telling the truth.

Peer prediction works best when ground truth **exists** but is **unobservable** by the mechanism designer — e.g., rating a product you actually used, where the platform cannot directly observe your experience but can compare your rating to other buyers'.

Decentralized curation faces a harder problem. Ground truth is sometimes genuinely **contested** — two honest people examining the same evidence may disagree. And some claims require evaluating external evidence, not just reporting private observations. This is why the protocol needs the evidence-and-dispute layer (claim → challenge → DDR adjudication) rather than purely statistical comparison between curators. The relevance dimension, however, is closer to a peer-prediction setting — curators' relevance assessments are compared against each other in the coherence game, which borrows the core peer-prediction insight.

### The Verifier's Dilemma

[Zhao et al. (2025)](https://arxiv.org/html/2406.01794v2) formalize Byzantine-robust peer prediction for decentralized verification — addressing the same core question: **how do you incentivize honest verification when skipping verification is cheaper?** Their framework shows that combining capture-the-flag designs with peer prediction techniques can resolve the Verifier's Dilemma even when cheating provers are extremely rare.

The key difference: their framework assumes verification is a **technical/computational task** with a well-defined correct output (valid proof or invalid proof). Curation involves **human judgment** — evaluating evidence quality, assessing claim specificity, weighing relevance. This requires the separation into accuracy (where judgment is constrained by evidence and adjudicated by a DDR) and relevance (where judgment is explicitly subjective and resolved by coherence games). The Verifier's Dilemma literature informs our design but does not directly solve our problem.

### Decentralized Science (DeSci)

The DeSci movement ([Weidener & Spreckelsen, 2024](https://www.frontiersin.org/journals/blockchain/articles/10.3389/fbloc.2024.1375763/full), Frontiers in Blockchain) has explored blockchain-based scientific infrastructure — funding (VitaDAO), publishing, data sharing, and peer review. Their comprehensive survey defines DeSci's shared values: transparency, accessibility, reproducibility, and community governance.

Most DeSci projects, however, focus on **access and funding** rather than **epistemic quality**. They solve "who gets to publish?" and "who gets funded?" but not "is this claim actually true?" The incentive-compatible verification layer — the part that makes honest evaluation profitable and dishonest evaluation costly — is largely absent from current DeSci infrastructure. This work directly addresses that gap. A decentralized curation protocol could serve as the **verification layer** for DeSci, providing the incentive-aligned quality signal that DeSci's access and funding mechanisms currently lack.

### Prediction Markets

Prediction markets (Augur, Polymarket, Metaculus) aggregate information through price discovery. They work brilliantly for events with **clear resolution criteria** and a **future resolution date** — elections, sports outcomes, ship arrival times.

This work addresses a different problem: curating claims about **the present and past**, where resolution requires evidence evaluation rather than waiting for an outcome. "Did Company X dump toxic waste in River Y in 2024?" cannot be resolved by waiting — it requires someone to investigate, produce evidence, and have that evidence evaluated.

The **relevance dimension** has no prediction-market analog at all. Prediction markets do not ask "is this question important?" — they only ask "what is the probability of this outcome?" A curation protocol must handle both dimensions: what is true, and what matters.

---

# Part 3: The Solution - Principles of Decentralized Curation

### From gatekeepers to distributed validators

The shift from centralized to decentralized curation is a shift in **who gets to decide** what information becomes knowledge.

**Centralized:** One entity controls what becomes "knowledge." Users are passive. Rules are hidden.

**Decentralized:** Many entities participate. Users can be validators or curators. Rules are visible and auditable.

**Critical mechanism:** Distributing the power to validate information reduces the opportunity and incentive for any single actor to corrupt knowledge production.

This builds on Token-Curated Registries (TCRs) [@goldin2017tcr], but generalizes from “is this in the list?” to claims, evidence, and disputes, and separates accuracy from relevance.

### Seven core principles

**Principle 1: Transparency**
Rules for what becomes knowledge are explicit and auditable. Validators (and everyone else) can see what information gets validated, why it was validated, who made the decision, and what evidence was used.

**Principle 2: Open Participation**
Anyone can participate in validating information and contributing to knowledge production. Multiple independent validators can operate simultaneously. No single entity can unilaterally suppress information.

**Principle 3: Verifiable Claims & Semantic Precision**
Information is validated through explicit, verifiable criteria.

- **Claims must be falsifiable.** "God exists" cannot be curated. "The Pope visited Brazil" can be.
- **Vagueness = Rejection.** If a claim lacks context ("Prices rose 5%" without dates/indexes), it is rejected as "Non-Falsifiable." The protocol enforces rigorous definition.
- **Evidence is public.** Verification logic is transparent. This makes gaming harder—it's expensive to fake evidence.

**Claim templates (ambiguity is a first-class attack surface)**
A jury can only resolve what is actually specified. If the claim is ambiguous, jurors will rationally coordinate on a _shared interpretation_—which can be wrong.

So a claim must carry enough structure that “correct” is not a matter of vibes:

- **Statement:** a single proposition (no bundled claims).
- **Scope:** timeframe, geography/jurisdiction, and any necessary definitions (units, indices, thresholds).
- **Resolution policy:** what sources/procedures count as authoritative evidence for this claim in this domain.

If these are missing, the correct verdict is not “True/False.” It is “Under-specified,” and that failure is slashable: ambiguity is punished like error.

_Example (bad → good):_

- Bad: “Did it snow in Portugal on Jan 31?”
- Better: “Between 2024-01-31T00:00Z and 2024-01-31T23:59Z, did Portuguese Met Office station **X** report snowfall $> 0$ cm? Source: station dataset **Y**.”

**Principle 4: Aligned Incentives**
Validators are rewarded for producing reliable knowledge and penalized for validating false claims. Validators stake resources on their judgments. Correct judgments are rewarded. Wrong judgments are penalized. This converts the incentive from "maximize engagement" to "maximize accuracy."

**Principle 5: No Censorship by Design**
No single actor can suppress information from becoming part of the knowledge base. Even if one validator rejects information, others can accept it. Censorship requires capturing a majority of validators—much harder than capturing one.

**Principle 6: Contestability**
Users can challenge, appeal, or dispute knowledge-validation decisions. Anyone can formally challenge a piece of knowledge. The challenge is resolved through transparent rules. No single person can permanently silence a dispute.

**Principle 7: Composability**
Knowledge produced by one curation system can feed into and integrate with other systems. Validators can build on each other's work. Users can combine ratings from multiple validators. Systems can fork or customize without starting from scratch.

### How this solves the five failure modes

| Failure Mode   | Problem                                           | Decentralized Solution                                                             |
| -------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Opacity**    | Rules for knowledge are hidden                    | All validation rules are explicit and auditable                                    |
| **Capture**    | Curator incentives diverge from knowledge quality | Validators are rewarded for accuracy, penalized for false claims                   |
| **Gaming**     | Single optimizable metric is exploitable          | Multiple independent validators use diverse criteria—expensive to fool all of them |
| **Censorship** | One entity can suppress information               | Censorship requires consensus; very hard at scale                                  |
| **Fragility**  | One algorithm change destroys the system          | No single point of failure; changes require consensus                              |

### Why This Is Not a TCR

Token-Curated Registries are the most direct ancestor of this design. [Mike Goldin's 2017 whitepaper](https://medium.com/@ilovebagels/token-curated-registries-1-0-61a232f8dac7) proposed using stake-weighted curation to maintain quality lists without centralized gatekeepers. The idea was elegant: token holders stake to list items, challengers stake to dispute them, and the market for the token reflects the registry's quality.

TCRs were supposed to be the decentralized replacement for curated lists — ad networks ([adChain](https://adtoken.com)), token directories, even [scholarly journals](https://onlinelibrary.wiley.com/doi/abs/10.1002/leap.1302) (Kosmarski & Gordiychuk, 2020). Most of them failed. The [Gitcoin analysis of TCR mechanisms](https://gitcoin.co/mechanisms/token-curated-registry) documents the structural issues. [ChainScore Labs](https://www.chainscorelabs.com/en/blog/prediction-markets-and-information-theory/decentralized-information-markets/why-token-curated-registries-incentivize-mediocrity-not-excellence) has argued convincingly that TCRs "incentivize mediocrity, not excellence."

This design shares DNA with TCRs but addresses their known failure modes. Here is how.

#### Variable Bounties vs. Fixed Deposits

In a classic TCR, the entry deposit is **protocol-fixed**. Every item costs the same to list, regardless of how important or contested it is. This creates a flat signal: a $100 deposit on "the sky is blue" looks identical to a $100 deposit on "this experimental drug cures cancer."

In this design, the author's **bounty is variable** and directly signals conviction. A $10 bounty on a trivially true claim carries almost no weight. A $10,000 bounty on a contested claim carries enormous weight — because the author is putting real money behind their assertion. The **Confidence Score** reflects this: `f(bounty, time uncontested, validator signal)`. Low bounties never mature into high-confidence claims regardless of how long they sit unchallenged. The bounty is not just an entry fee — it is a **credibility signal**.

#### No "Listed by Default" Problem

In TCRs, entries are **added unless challenged** — challenge-based exclusion. This creates a toxic default: if no one bothers to challenge a low-quality entry, it becomes "listed," and listing implies endorsement. The result is that low-stakes lists fill with garbage that no one has the incentive to clean up, as early TCR experiments like adChain demonstrated.

Here, claims **start with no confidence**. They must **earn** confidence through bounty size, time surviving challenges, and validator attention. An unchallenged low-stake claim does not silently become "truth" — it remains low-confidence noise. The system's default state is **skepticism**, not endorsement.

#### Pooled Staking vs. Per-Item Staking

TCR curators must individually evaluate and stake on **every item**. This creates a participation bottleneck: as the registry grows, the cost (in time and attention) of evaluating every entry exceeds the expected reward. The result is the **low-participation equilibrium** that killed adChain — rational curators stop paying attention, and the registry degrades.

In this design, curators stake on **pools** (topics, domains, subject areas), and the protocol randomly drafts them for specific claims within those pools. Curators are performing **portfolio-level duty**, not per-claim research. You do not need every curator to care about every claim — you need enough curators in each pool to staff the claims that arise in that pool. This directly addresses the participation problem by making curation economically viable as a sustained activity rather than a per-item chore.

#### Separation of Accuracy and Relevance

TCRs conflate "should this be in the list?" into a **single binary vote**. This forces curators to simultaneously evaluate truthfulness, importance, and appropriateness — all in one up-or-down decision. The result, as [ChainScore Labs argues](https://www.chainscorelabs.com/en/blog/prediction-markets-and-information-theory/decentralized-information-markets/why-token-curated-registries-incentivize-mediocrity-not-excellence), is that safe, mediocre entries pass while genuinely important but controversial entries get challenged for the wrong reasons.

This design **separates** the two questions:

- **"Is it true?"** — Global, binary, resolved by evidence and DDR adjudication. This has a ground truth anchor.
- **"Is it important?"** — Local, non-binary, resolved by the coherence game within specific curation pools. This is explicitly subjective and pool-specific.

A claim can be true but irrelevant to a specific pool (accurate but boring). A claim can be highly relevant but contested on accuracy (important and wrong). By separating these dimensions, curators can do their actual job — surface what matters — without being forced to play amateur fact-checker on every entry.

Kosmarski & Gordiychuk (2020) [proposed TCRs for scholarly journals](https://onlinelibrary.wiley.com/doi/10.1002/leap.1302) with similar intuitions about decentralizing peer review. Their framework identified the right problems — editorial bias, reviewer incentive misalignment, lack of rewards — but inherited the structural limitations of the TCR model. This work builds on their insights while addressing the failure modes they identified: variable stakes replace fixed deposits, pooled curation replaces per-item voting, and the accuracy/relevance separation gives the mechanism enough dimensionality to handle scholarly claims.

### Building blocks

To make decentralized curation work, you need:

1. **Claims and Evidence:** Information structured as explicit, falsifiable claims supported by transparent evidence
2. **Validators and Reputation:** Independent actors who assess claims; their accuracy is publicly tracked
3. **Challenges and Disputes:** Anyone can formally dispute a claim; disputes are resolved through clear procedures
4. **Rewards and Penalties:** Validators who produce accurate knowledge get rewarded; those who promote false claims get penalized
5. **Governance and Rule-Making:** Community can propose and vote on rules; changes require consensus, not unilateral decree
6. **Interoperability:** Validators can integrate with each other; reputation and knowledge portable across systems

---

# Part 4: Architecture - How Decentralized Curation Works

### Design: A three-actor model

The system needs three kinds of participants:

**Authors:** Submit information with a stake (bounty) at risk. If challenged and proven wrong, they lose their stake.

**Curators:** Stake resources to validate information as accurate/relevant. Correct votes are rewarded. Incorrect votes lose their stake.

**Readers:** Consume curated knowledge. Can optionally become validators by staking.

### Data model: claims, evidence, and verdicts

The unit of curation is not “a post.” It is a **claim** with enough structure to be adjudicated:

- **Claim:** statement + scope (timeframe, definitions, jurisdiction) + resolution policy (what sources/procedures count) + selected pool.
- **Evidence bundle:** public references (links, documents, datasets) plus integrity commitments (hashes) so evidence can’t be silently swapped after the fact.
- **Verdict:** at minimum **Valid / Invalid / Under-specified**. “Under-specified” is critical: ambiguity is treated as a failure, not something jurors should guess.

**Evidence standards (policy, not vibes)**
For each pool/domain, participants need a shared standard for what counts as “good enough” evidence. So every pool must publish an **evidence policy** (and can update it via governance):

- Accepted evidence types (datasets, primary documents, expert testimony, etc.)
- Canonical sources and tie-break rules (what wins when sources disagree)
- What threshold is required for “Valid” vs “Insufficient/Under-specified”

This converts “legal definition disputes” into _policy compliance disputes_ with explicit rules.

### Confidence Score (a signal, not a guarantee)

The interface displays a **Confidence Score** $C$ to guide attention. Conceptually:

$$
C = f(\text{bounty at risk},\ \text{time uncontested},\ \text{validator signal})
$$

Where “validator signal” can include reputation-weighted agreement and challenge history. The details can evolve, but the invariants are:

- **Monotone:** higher bounty / more uncontested time / stronger validator signal → higher confidence.
- **Gated:** low bounty or zero validator attention never becomes “high confidence” just by aging.

### The core flows

**Flow 1: Submission & Trust Building**
Author submits information, selects a curation pool (topic area), and stakes a bounty.

The system assigns a **Confidence Score**, which guides user attention:

- **Low bounty = Low Signal:** If the bounty at risk is tiny, the claim is treated as noise by default.
- **High bounty + time uncontested:** If a meaningful bounty remains uncontested, confidence increases.
- **Validator attention matters:** Explicit validator participation (and their historical accuracy) can raise or lower confidence faster than time alone.
- **Result:** Low-signal claims do not “mature into truth” by neglect.

**Flow 2: Validation (Pooled Staking)**
Validators don't just stake on single items (which exposes them to liability). They stake on **Curation Pools** (e.g., "Science Validators"). The protocol randomly drafts validators from the pool to judge specific claims. This creates "Herd Immunity"—validators are performing a neutral, randomized duty, protecting them from being targeted as individual publishers.

**Flow 3: Challenge & Dispute**
Any user can challenge what's been validated by staking resources and submitting evidence (or by asserting the claim is **under-specified**).

The dispute is delegated to a decentralized dispute resolver (DDR) which:

- **Selects jurors randomly from an eligible pool** (self-selected via staking; optionally topic-scoped), rather than “random people on the internet.”
- Uses **commit–reveal voting** (commit hash first, reveal later) to reduce copy-the-majority dynamics and simple vote-buying.
- Supports **appeals**: later rounds require higher stake and can overturn earlier lazy consensus.

The verdict updates the claim state and redistributes stakes on-chain.

**Flow 4: Relevance**
Beyond accuracy, validators vote on relevance. A true statement can have low relevance. This separates "boring facts" from "important news."

### On-chain vs. off-chain

**On-chain (transparent, tamper-proof, trustless):**

- Registry: All claims and metadata
- Staking: Manages validator stakes, rewards, penalties
- Dispute Resolution: Records challenges, jury selection, vote tallying
- Governance: Tracks rule changes, community voting

**Off-chain (fast, usable, can be run by many providers):**

- Indexing & Discovery: Indexes on-chain data for searching
- User Interface: Makes the system usable for non-technical users
- Reputation System: Tracks validator accuracy over time
- Evidence Storage: Stores full text of evidence on IPFS/decentralized storage
- Integration APIs: External systems can read curated knowledge

**Critical mechanism:** On-chain ensures transparency and trustlessness. Off-chain ensures usability and scalability. No single point of control exists because multiple providers can run each off-chain component.

### Trust assumptions

**What we minimize:**
✅ Validation results (we trust the aggregate, not any single validator)
✅ Dispute outcomes (we trust randomized juries + commit-reveal voting, not individual arbiters)
✅ Protocol logic (we trust the code—smart contracts are deterministic)
✅ History (everything on-chain is immutable and auditable)

**What we still require:**
⚠️ Evidence authenticity (submitted evidence is genuine, not fabricated)
⚠️ Off-chain data integrity (indexing, UIs can be run by third parties—multiple providers reduce risk)
⚠️ Community agreement on standards (what counts as "valid evidence"?)
⚠️ Participant honesty (we can't prevent someone from voting dishonestly, but we make it expensive—they lose their stake)

**Why this matters:** We don't eliminate the need for trust. We **make honesty profitable**. If you validate accurately, you get rewarded. If you validate dishonestly, you lose money. Over time, dishonest validators get poor reputation and are chosen less often.

### The Truth Post: Lessons from an MVP

The Truth Post launched in 2023 as a minimal viable implementation of the core submission-and-challenge flow. It is worth being honest about what happened.

#### What Was Built

The Truth Post implemented:

- **Author submission with staked bounties.** Users could submit claims and attach a token bounty as a credibility signal.
- **Challenger disputes routed to Kleros.** Anyone could challenge a claim by staking tokens, triggering a dispute in the Kleros court system.

This was the **bare minimum** of the protocol — the accuracy layer without the relevance layer.

#### What Was NOT Built

The MVP did not implement:

- **Relevance curation** (the coherence game described in Part 5)
- **Author rewards** from a protocol treasury
- **The Confidence Score** system
- **Pooled staking** for curators
- **Multiple frontends** or interface redundancy

#### What Happened

The MVP did not achieve sustained usage. Activity was sparse — a handful of claims, fewer challenges. The web frontend eventually stopped loading, likely due to a subgraph indexing failure (a common failure mode for dApps that depend on The Graph for on-chain data). The project was abandoned due to maintenance overhead.

This is not a comfortable admission in a whitepaper. But the alternative — pretending the MVP validated the design — would be dishonest, and this paper is about building systems that are hostile to dishonesty.

#### Lessons Learned

**1. The cold-start problem is real.** Without a critical mass of curators and challengers, the system lacks the economic activity needed to generate meaningful confidence signals. A claim with zero challenges and zero validators has a confidence score of approximately zero — which is correct, but useless. The system needs enough participants to generate signal before it becomes useful, and it needs to be useful to attract participants. This is a classic two-sided marketplace problem, and "build it and they will come" does not solve it.

**2. Relevance curation may be the engagement driver.** Accuracy alone — "is this true or false?" — generates a trickle of activity. Most claims are not interesting enough to challenge. The relevance layer — which turns the system into something users actively interact with, ranking and surfacing what matters — may be **necessary for bootstrapping**. People do not visit a site to verify boring truths. They visit to find out what is important. The relevance layer is what makes the protocol useful as a **product**, not just a verification mechanism.

**3. Infrastructure maintenance matters.** A decentralized protocol is only as good as its off-chain infrastructure — indexers, frontends, APIs. The Truth Post had a single frontend operated by the development team. When the subgraph broke, the entire user-facing product went down. This is a single point of failure that contradicts the protocol's own design philosophy. The lesson: the protocol must be designed so that **anyone** can deploy a frontend, and no single frontend failure kills the system. Protocol-vs-interface separation is not optional — it is a survival requirement.

These lessons directly inform the full design in this manuscript:

- **Pooled staking** reduces cold-start friction by letting curators commit to domains rather than individual claims.
- **The Confidence Score** makes the system useful even with thin participation — a single unchallenged claim with a large bounty still provides a meaningful (if incomplete) signal.
- **Protocol-vs-interface separation** ensures that the protocol survives any individual frontend's failure. If one explorer goes down, others continue operating.

---

# Part 5: Game Theory - Making Honesty Profitable

### The basic game

In centralized systems, lying is free. You type it, it spreads, and there's no cost if you're wrong.

In decentralized curation, **lying has a price.**

Here's the game:

**Author publishes: "X is true" and stakes $100.**

**Two scenarios:**

**Scenario 1: The Statement stands unchallenged**

- Author publishes and stakes $100.
- Time passes. No one challenges it.
- The **Confidence Score** rises as $f(\text{bounty}, \text{time uncontested}, \text{validator signal})$.
- Users see: "High Confidence (historically hard to debunk at this stake/time/profile)."
- Result: Knowledge is validated passively by the absence of successful attacks.

**Scenario 2: The Statement is False**

- A Challenger finds evidence that contradicts it
- Challenger stakes $50 to formally dispute it
- Kleros jurors are selected
- Jurors vote based on evidence
- If Challenger wins: Challenger gets the Author's $100 bounty (minus fees)
- Author loses their initial $100 stake
- Curators who voted "True" lose their stakes
- Everyone who validated dishonest information is punished

**The result:** Honesty becomes the equilibrium strategy. It's cheaper to be right than to be wrong.

### Incentives 2.0: Reputation as Capital

Financial staking is just the start. The system also tracks **Reputation**:

- **Authors** who consistently post valid information earn Reputation (R) = f(stake × accuracy over time).
- **Utility:** Reputation can be used in place of capital to stake on new claims. This lowers the barrier to entry for honest but cash-poor journalists. It turns "Truth" into a form of credit score.
- **Protection:** Reputation is non-transferable and decays if unused, preventing Sybil attacks (creating 100 accounts and coordinating them).
- **Reward:** The protocol treasury distributes inflation rewards pro-rata to Reputation holders, creating a constant income stream for truth-tellers.

### Why attacks fail

**Defense: The Competence Filter**
The crypto-economic game forces a binary choice: **Be competent or be gone.**

- If you curate a topic you don't understand, your chance of being coherent with expert consensus drops.
- A lazy curator voting randomly will be incoherent on average, losing stake gradually until exit becomes rational.
- Result: The system naturally purges incompetent or lazy actors. The dominant strategy for a non-expert is **not to play**. This creates a "Competence Filter" where only those who actually do the work survive.

**Attack 1: The Rich Liar**
Attacker stakes $1M, hoping to scare off challengers.

Why it fails: A large bounty is a honeypot. If the lie is provable, jurors happily vote against the rich liar to claim their share of that $1M. The richer the liar, the bigger the reward for telling the truth.

**Attack 2: The Lazy Curator**
Curators just vote "Yes" on everything without reading.

Why it fails: This creates an opportunity for a "Shark" (a diligent Challenger) who spots the pattern, finds the false article, and challenges it. Lazy curators lose their stakes. The threat of the Shark forces actual work.

**Attack 3: The "Self-Fulfilling Prophecy" Loop**
Critics argue that jurors don't vote for "Truth," but for "Predictable Consensus" (Mediocrity). If a truth is complex or counter-intuitive, jurors might vote "False" just to stay safe with the herd.

**Defense: The "Lone Wolf" Payoff**

- Jurors are incentivized to coordinate with the **final** ruling, not the current one.
- If 1,000 lazy jurors vote "False" on a nuanced truth, a single **Lone Wolf** expert can appeal.
- **Appeal Mechanics:** Appeals require a higher stake (e.g., 2x the original). If the appeal succeeds, the appellant receives the slashed stakes from all dissenting jurors from prior rounds. This creates exponential payoff for being right when everyone else is wrong.
- **Preventive Effect:** Each appeal raises the stakes and draws more expertise. This creates incentive for jurors to "do their homework" initially, knowing that a future Lone Wolf expert can punish sloppy consensus. The _threat_ of the future creates honesty in the present.

**Common criticism: “Consensus ≠ Correctness”**
It’s true that Schelling-style juries reward **coherence**. Voters try to guess what other voters will do.

The point is not to deny this—it’s to design around it:

- **Make “correct” the coordination point** by enforcing semantic precision. If the question is ambiguous, the right outcome is **Under-specified**, not a forced True/False guess.
- **Decentralized pre-selection:** jurors are not “random people.” They are drawn from staking pools, shaped by the competence filter and reputation over time. That is the non-centralized version of “quality criteria.”
- **High-court effect via appeals:** when the stakes are low, nobody will spend an hour parsing edge cases. Appeals make that economically rational: higher stakes attract higher effort and expertise, and expert minorities are rewarded for overturning lazy majorities.
- **Legal/contract semantics are policy questions:** many “prediction market resolution” disputes are really about what the resolution policy means. The system must treat that policy as part of the claim, and jurors adjudicate **policy compliance** under an explicit standard—not metaphysical truth.

This is also why parameterization matters: these mechanisms are sensitive to claim templates, stake sizes, and appeal economics. If you set them poorly, you don’t get “decentralized truth”—you get expensive noise.

### Infinite Appeals and Backward Induction

Why can’t we just set a maximum number of appeal rounds — say, 5 — and call it done?

Because of **backward induction**.

#### The Problem with a Known Final Round

Suppose there are exactly **N** appeal rounds, and everyone knows it.

In round N, jurors know their verdict is **definitive**. There is no future appeal. No Lone Wolf can overturn them later. The economic pressure that keeps jurors honest — “if I vote incorrectly, someone will appeal and I’ll lose my stake” — **disappears** on the last round.

Round N degenerates. Jurors in round N face weaker incentives to research carefully, because their only risk is intra-round (being in the minority of this round), not inter-round (being overturned on appeal). The error-correction mechanism is disabled.

Now consider round N−1. Participants in round N−1 know that round N is degenerate. They know that an appeal to round N will not reliably correct errors. So the threat of appeal is weaker in round N−1 too. And round N−2 participants know round N−1 is degraded. The degradation **cascades backward** through every round.

This is the standard backward induction problem from game theory. If the end of the game is known, strategic behavior unravels from the end.

#### The Solution: Theoretically Infinite Appeals

Appeals must always be **possible** — there must never be a round that participants know is final.

In practice, exponentially escalating costs make the process self-limiting:

| Round | Stake Required |
| ----- | -------------- |
| 1     | S              |
| 2     | 2S             |
| 3     | 4S             |
| k     | 2^(k−1) × S    |

At some point, no rational actor is willing to escalate further. A dispute over a $100 claim will not see a round requiring $10,000 in stakes. The process terminates **economically**, not structurally.

The key insight: **economic termination preserves incentives; structural termination destroys them.** When the game might always continue, every round’s jurors face the threat of being overturned. When the game has a known endpoint, that threat evaporates at the boundary and the damage propagates inward.

This is directly analogous to the **iterated prisoner’s dilemma** with an uncertain end date. Cooperation is sustainable when the game might continue indefinitely. Cooperation collapses when the end is known. Robert Axelrod demonstrated this decades ago — we are applying the same logic to dispute resolution.

The practical implication for protocol design: **never hard-code a maximum appeal count.** Let the staking schedule do the work. The game ends when no one is willing to pay — not when the protocol says “time’s up.”

### Separation of powers: Accuracy vs. Relevance

This is crucial. In centralized platforms, these are mashed into a single "Engagement" metric. We separate them into two distinct dimensions.

**Accuracy (Binary classification):**

- Question: "Is this claim supported by evidence?"
- Nature: **Binary Classification.**
- Mechanism: Bounty + Challenge + Jury.
- Scope: **Global.** Pools can vary on _relevance_ policy, but they cannot mint their own “accurate-for-us” labels. If a pool tries to tag falsehoods as “Accurate,” it becomes slashable via the shared dispute process (e.g., a cross-pool court like Kleros).
- Logic: Accuracy requires human judgment, but it can be treated as binary (Valid vs. Invalid). A jury can look at evidence and make a definitive decision under an evidence standard.

**Relevance (Subjective):**

- Question: "Is this important to this community?"
- Nature: **Non-binary Spectrum.**
- Mechanism: **Schelling-Point Coherence Game.**
- Logic:
  1.  **Policy:** Each pool has a specific "Relevance Policy" (e.g., "What counts as Tech News").
  2.  **Vote:** Curators stake tokens to rate an item (e.g., 0-10).
  3.  **Aggregate:** Let curator $i$ submit rating $v_i$ with weight $w_i$ (stake and/or reputation). Compute:
      - $\mu = \frac{\sum_i w_i v_i}{\sum_i w_i}$ (weighted mean)
      - $\sigma = \sqrt{\frac{\sum_i w_i (v_i - \mu)^2}{\sum_i w_i}}$ (weighted std. dev.)
  4.  **Coherence rule:** Choose a pool parameter $K$. Curator $i$ is **Coherent** iff $|v_i - \mu| \le K\sigma$. Otherwise they are **Incoherent**.
  5.  **Incentive:** Incoherent stakers are slashed; their stake is redistributed to coherent stakers (and/or the pool treasury). Voting uses commit–reveal to reduce copying.
  6.  **Result:** Participants maximize expected reward by reading the policy, doing real work, and predicting what other competent curators will conclude under that policy.

This solves the "Boring Truth" problem. An accurate article about paint drying passes accuracy checks (Valid) but scores low on relevance (users vote 1/10). Users see it marked "Accurate but irrelevant."

---

# Part 6: Governance & UX - Making It Actually Work

### The gap between theory and practice

We have a robust engine. But systems fail because they ignore the human element.

A curation system isn't just code. It's a **socio-technical system** involving real people with limited attention, biases, and varying technical literacy.

### Governance: Who updates the rules?

In centralized systems, an engineer fixes the code. In decentralized systems, code is immutable. But the world changes.

**What needs governing:**

- Economic parameters (minimum stakes, bounty amounts)
- Protocol upgrades (fixing bugs, adding features)
- Community values (defining what counts as "valid evidence")

**Pluralism: The Market for Curation Policies**
How do we decide what the "best" curation policy is? We don't. We let the market decide.

Think of it like **Reddit, but with stakes:**

- On Reddit, `r/science` has strict rules. `r/futurology` has different rules.
- In Trustless Curation, anyone can spin up a **Curation Pool** for a topic.
- Each pool has its own policy, enforced by crypto-economics.

**Why "Echo Chambers" Aren't the Problem**
Critics worry this creates echo chambers (e.g., a "Conspiracy Pool"). But this misunderstands the market.

- You can't compare the "Science Pool" to the "Conspiracy Pool" any more than you compare a Michelin guide to a fast-food blog. They are different products.
- Competition happens _within_ a niche. Multiple "Science Pools" compete to be the most reliable source of science news.
- If a pool's policy is bad (e.g., allows spam), users leave. The best policy for a given goal wins by natural selection.
- Relevance is local, but accuracy is global: you can curate “relevant conspiracy theories,” but you cannot safely tag them as “Accurate.”

**Post-truth apathy (and why this is not a bug)**
Some users will prefer dopamine over accuracy. This protocol is middleware: it produces verifiable labels and incentives, but it does not force people to consume truth. A truth-first interface can foreground high-confidence claims; an entertainment-first interface can ignore the signal—but the signal remains available for any user (or competing app) that wants it.

**The mechanism:** Decentralized Autonomous Organization (DAO)

- Token holders vote on proposals for the _base protocol_.
- Individual pools govern their own _local policies_.
- Approved changes have a timelock (e.g., 48 hours) allowing users to exit if they disagree.
- Governance votes on _rules_, not individual curation decisions (separating legislative from judicial power).

### UX: Hiding the machinery

The biggest barrier to decentralized tech is friction. Wallets, gas fees, staking—non-starters for mass audiences.

**Progressive disclosure UX:** Conventional interface up front, crypto complexity behind the scenes.

- **For Readers:** Identical to Web2. Open an app, read news, see a "Confidence Score." No wallet needed. No need to understand blockchain.
- **For Authors/Curators:** Complexity exposed only as needed.

**Interface vs. Protocol: Solving the "Toxic Content" Problem**
Critics argue that a permissionless protocol will inevitably host illegal or toxic content (e.g., hate speech).

- **The Protocol** is neutral and uncensorable (like the Internet). It stores everything, preserving censorship resistance (including adversarial/whistleblowing use cases).
- **The Interface** is opinionated (like a Browser). `TruthPost.com` can choose to filter out toxic pools or illegal content to comply with local laws.
- **Result:** Users get the best of both worlds: censorship resistance at the infrastructure layer, but safety and compliance at the user experience layer.

**The "Meta-Curation" trap (Interface capture)**
Even if the protocol is neutral, distribution power can re-centralize at the interface layer (apps can hide, downrank, or “editorialize” reality). The defense is that interfaces are replaceable while the protocol is not: claims, stakes, and verdicts are public and auditable, so other clients can independently index the chain and reproduce the same Confidence Scores. Interfaces can filter; they can’t silently rewrite what the protocol committed to.

**UX patterns:**

- Instead of "Stake 50 DAI," ask "How confident are you?" ("I'm sure" → triggers a stake)
- Use Account Abstraction (log in with Google, protocol pays gas fees)
- Users can delegate voting power to trusted curators

### Human factors: Safety and fairness

**The Rich Validator Problem**
Money doesn't change facts. A billionaire who stakes on a lie loses their money to thousands of regular people who stake on the truth. The mechanism extracts wealth from dishonest rich actors and redistributes it to honest observers.

Related concern: **"Rich get richer."** Competent curators will tend to compound stake and influence over time. This is partly intended selection pressure (we optimize for knowledge quality, not curator equality), but we can still reduce barriers with low minimum stakes and **Reputation as Capital**, so cash-poor domain experts can participate and compete.

But we must ensure minimum stakes are low enough that diverse validators can participate.

**Appeal Safety Valves**
Humans make mistakes. Solution: Progressive Decentralization. Initially, the protocol might have longer time windows or a "Security Council." As it matures, training wheels are removed.

**Cognitive Load**
We cannot expect every user to verify every fact. Solution: Users can "follow" curators they trust. Liquid Democracy: delegate voting power to experts by topic, revoke instantly if they mess up.

---

# Part 7: The Future - Beyond News, Beyond Trust

### The journey so far

We started with a diagnosis: **Information is abundant, but knowledge is scarce.** Centralized curation failed because gatekeepers with misaligned incentives control what becomes "truth."

We proposed a solution: **Trustless Curation**—a system where honesty is profitable, truth is verifiable, and no single entity controls knowledge production.

We built the architecture, designed the incentives, and created a working MVP (The Truth Post).

Now: What's next?

### Beyond news: The universal verification layer

The stake-to-verify model is generic. It applies to any domain where **truth is valuable but verification is costly.**

### Advertising as Proof of Truth

Here is an observation: advertisers already make claims about their products. "Longest battery life in its class." "Zero sugar." "Clinically proven." These claims are currently verified (if at all) by regulatory agencies operating at glacial speed, or by journalists who may or may not bother.

What if the verification mechanism was **built into the advertising itself**?

#### The Mechanism

1. An advertiser makes a **verifiable claim** about their product: _"Battery lasts 48 hours under standard use conditions (ISO 12345)."_
2. The advertiser **stakes tokens** on this claim. The stake amount signals conviction — a $50,000 stake on a product claim is a very different signal than a $50 stake.
3. **Anyone can challenge** the claim. If the challenge succeeds (independent testing shows the battery does not last 48 hours under ISO 12345 conditions), the advertiser **loses their stake** — distributed to the challenger and the protocol.
4. If the claim stands unchallenged or **survives challenges**, the advertiser recovers their stake minus a small protocol fee.

#### Why This Works

**Honest advertisers pay almost nothing.** Their stake is returned. The protocol fee is the cost of verified credibility — far cheaper than a Super Bowl ad, and far more durable. A staked claim that has survived multiple challenges is worth more than any amount of traditional advertising spend, because it carries **adversarially-tested credibility**.

**Dishonest advertisers are punished.** False claims become bounties for challengers. The more extravagant the lie, the larger the bounty. The system creates a **market for debunking** — anyone with testing equipment and a financial incentive can challenge dishonest advertising. The advertiser is literally funding their own exposure.

**Trivially true claims are possible but useless.** An advertiser could stake on "our product contains atoms" — technically true, economically unchallenged, completely meaningless. The market naturally selects for claims that are both **true AND informative**, because those are the only claims worth staking on. No one gains marketing value from proving their product contains atoms. The incentive is to stake on the strongest true claim you can defend — which is exactly the kind of claim consumers want to see.

#### Temporal Validity

Claims are staked with a **validity window**. "Battery lasts 48 hours" applies to the current product version, identified by model number and firmware version. If the product changes — new model, updated firmware, different manufacturing process — the advertiser must **withdraw or update the claim**. An outdated claim on a changed product becomes a target for challengers, because the original claim may no longer be true of the current product.

This handles the temporal decay problem: product claims do not become eternal truths. They are living assertions, maintained by the advertiser's continued stake and validated by the ongoing threat of challenge.

#### Caveats and Alternatives

This mechanism is **speculative**. It requires market validation. Several open questions remain:

- **Will advertisers actually participate?** The mechanism requires a cultural shift from "advertising as persuasion" to "advertising as verifiable assertion." This may happen in some markets (consumer electronics, supplements) faster than others (luxury goods, entertainment).
- **Will challengers emerge?** The mechanism depends on a functioning market for challenge — people willing to invest in testing and verification for the expected bounty. Consumer protection organizations, testing labs, and investigative journalists are natural participants, but their willingness to engage with on-chain mechanisms is untested.
- **Regulatory interaction.** How does staked advertising interact with existing advertising regulations (FTC in the US, ASA in the UK)? Does a staked claim provide legal cover, or does it create additional liability?

Advertising-as-proof-of-truth is presented as **one possible sustainability path**, not the sole funding model. Other paths include:

- **Public-good funding:** Grants from protocol treasuries, Gitcoin rounds, or ecosystem funds that value the knowledge layer as infrastructure.
- **Integration fees:** Downstream consumers of the curated knowledge layer — news aggregators, research platforms, AI training pipelines — pay fees for access to the curated, confidence-scored dataset.
- **Protocol fees:** Small fees on every claim submission, challenge, and appeal that accumulate in a protocol treasury for ongoing development.

The honest assessment: the protocol needs **at least one** of these revenue streams to be sustainable. Advertising-as-proof-of-truth is the most novel and potentially the most lucrative. But it is also the most uncertain. Building the protocol to support multiple funding models is the prudent approach.

**Core Applications:**

**Science: Decentralized Peer Review**

- Researchers submit papers with bounties
- Scientists stake on reproducibility
- Invalid work is profitably debunked
- Result: "Living journals" where valid research rises instantly

**Code: Decentralized Security Audits**

- Protocols post security bounties
- Security researchers stake on specific code being safe
- If bugs are found later, "Safe" stakers lose their stakes
- Result: Continuous security as a market

**History: The Immutable Record**

- Historical claims are staked and challenged
- Contested history isn't erased—marked "Disputed" with evidence forever on IPFS
- Result: History that resists revisionism

### The AI elephant in the room

Generative AI has reduced the cost of producing plausible text to zero. Traditional spam filters can't work—spam is trained to beat filters.

**Decentralized Curation is the immune system for the AI age.**

The problem: If AI models train on internet data flooded with AI-generated garbage, they collapse (“model collapse”) and lose fidelity over generations [@shumailov2023recursion]. They need **human-verified truth** as their foundation.

The solution: A decentralized curation protocol produces a dataset that is **expensive to forge** because every "True" label is backed by real money and real risk. This becomes the gold standard for training truth-seeking AIs.

### Open challenges

### The Economics of Forking: Why Capture Destroys the Prize

Forking is the nuclear option. It is expensive, disruptive, and destroys network effects. **That is the point.** Its existence as a credible threat is what makes the attack economically irrational.

#### The Simple Model

Let:

- **V** = total value of the protocol (token market cap + utility value from integrations, users, curated knowledge)
- **C** = cost of acquiring 51% of governance/arbitration tokens
- **V_post** = value of the captured chain after the community forks away

The attacker's expected payoff:

> **E[attacker] = V_post − C**

#### Why V_post ≈ 0

The protocol's value does not live in the code. The code is open source and forkable — anyone can copy it in an afternoon. The value lives in:

- **Users** who submit and consume curated claims
- **Curators** who stake, validate, and maintain knowledge pools
- **Applications** that integrate the curated knowledge layer
- **Network effects** — the accumulated history of adjudicated claims, confidence scores, and reputation

Upon capture, honest participants fork to a new chain. The curators migrate. The applications re-point their integrations. The users follow the curators and the applications. The attacker is left controlling the code and the captured chain — but with no users, no curators, no integrations. An empty protocol with a captured governance token.

Therefore **V_post << V**, and for most realistic scenarios, **V_post ≈ 0**.

So **E[attacker] = 0 − C = −C**. The attack is pure economic loss.

#### Empirical Precedent: Ethereum / Ethereum Classic (2016)

After the DAO hack, the Ethereum community faced exactly this choice. They forked. The result, as documented on [Arkham Research](https://info.arkm.com/research/ethereum-vs-ethereum-classic):

- **ETH** (the fork with community support): market cap >$280B.
- **ETC** (the "original" chain the community abandoned): market cap <$3.5B — roughly **1.2%** of ETH's value.

ETC subsequently suffered [multiple 51% attacks](https://info.arkm.com/research/ethereum-vs-ethereum-classic) — in January 2019 ($1.1M in double-spends) and three more in August 2020 ($5.6M+ in losses) — confirming that a chain without its community becomes a security liability, not an asset.

The lesson is stark: **the value lives in the community, not the chain.** Capturing the chain without the community is buying an empty castle and then watching it get looted.

#### The Triple Threat

Three forces compound to make capture irrational:

1. **Economic suicide.** The attacker spends C to control something worth ≈ 0 post-fork. This is not a profitable trade under any realistic assumption about V_post.

2. **Acquisition slippage.** Acquiring 51% of governance tokens on open markets triggers massive price increases due to thin order books. The actual cost C is far higher than `0.51 × spot_price × total_supply` would suggest. Illiquidity is a feature, not a bug — it makes the attack progressively more expensive as the attacker buys.

3. **Community coordination advantage.** The honest majority has a natural Schelling point for coordination: "fork away from the attacker." This is **easier** to coordinate on than the attack itself, because the attack requires secrecy (to avoid front-running) while the defense is public and obvious.

#### Caveat: Forking Is Not Free

Forking destroys network effects temporarily. It splits liquidity. It requires community coordination — someone has to deploy the fork, someone has to build or re-deploy the frontend, applications need to update their integrations. It creates confusion about which chain is "real" (for a while).

Forking is a **nuclear option**, not a routine defense. The protocol's first line of defense is the economic incentives within the game (honest curation is profitable, dishonest curation is punished). The second line is the appeal system. Forking is the third line — the backstop that exists to deter the attacks that the first two lines cannot handle.

The point is not that forking is painless. The point is that its existence as a **credible threat** makes the attack irrational. The attacker must believe that the community will **not** fork — and given the Ethereum/ETC precedent, that belief is hard to sustain.

**Challenge 2: The Vampire Attack (Free Riding)**
Competitors can scrape our verified data for free and monetize it.

**Response: Feature, not Bug.** We are building Public Infrastructure, not a walled garden.

- If a "Vampire" site distributes our verified truth to millions, we are winning the information war.
- **Funding:** The system is funded by a mix of "Advertiser Staking" (commercial utility) and "Public Funding" (NGOs/States funding the "Truth Automata"). Just as society funds Wikipedia and roads, it will fund the machine that verifies reality.
- **Why Wikipedia is Different:** Wikipedia works well for encyclopedic knowledge but fails for real-time news and contested claims—where rapid verification and incentive alignment matter most. Our design targets those gaps while Wikipedia's governance is centralized and doesn't reward accuracy directly.

**Challenge 3: The "Frozen Truth" (Temporal Decay)**
Knowledge can become false later. An immutable ledger risks accumulating stale, misleading, or superseded claims.

**Response:** Validation is not a lifetime warranty. Claims can be **withdrawn** (un-staked) by authors when they become obsolete—otherwise they become profitable targets for challengers who can debunk them for reward. Authors are incentivized to withdraw stale claims before a hostile takedown. The repository self-cleans: dead truths are either withdrawn or eaten; only living truths remain staked.

**Challenge 4: Governance Capture**
If token distribution is centralized, the protocol becomes a plutocracy.

**Solution:** Wide distribution, reputation-based voting, and minimizing governance surface (make the protocol rigid).

### The closing vision

Imagine a world where truth isn't determined by an algorithm owner's mood or an advertiser's budget.

Every claim has a **Confidence Score**. You hover over it:

**"High Confidence."**

Why? "Because the author staked $500, and it has stood uncontested for 72 hours. Historically, claims with this stake/time/profile are rarely overturned."

You don't trust the curators. You trust the incentives. You know **people don't like losing money.**

This is the shift from **Institutional Truth** (Trust Us) to **Incentive Truth** (Verify Us).

It's a world where lying is expensive, truth is profitable, and shared knowledge is a public good that no one owns but everyone protects.

This is what we're building.
