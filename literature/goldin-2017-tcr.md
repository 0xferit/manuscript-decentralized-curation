# Goldin (2017): Token-Curated Registries + Asgaonkar & Krishnamachari (2018): TCR Game Theory

**Citations**:
- Goldin, M. (2017). Token-Curated Registries (TCRs). Blog post.
- Asgaonkar, A., & Krishnamachari, B. (2018). Token Curated Registries: A Game Theoretic Approach. arXiv:1809.01756.
- Wang, Y. L., & Krishnamachari, B. (2019). Enhancing Engagement in Token-Curated Registries via an Inflationary Mechanism. ICBC 2019, 188-191. doi:10.1109/BLOC.2019.8751443

## Core thesis (Goldin)

Token-curated registries use token-weighted voting to maintain a list of items. The proposed incentive is that token holders benefit when the registry is useful and valuable. That link is an assumption to analyze, not a guarantee of informative voting. The mechanism is: apply to be listed, token holders vote to accept/reject, challengers can dispute listings.

## Core thesis (Asgaonkar & Krishnamachari)

Game-theoretic analysis of TCRs reveals multiple equilibrium problems: (1) challenges are rare because challenging is costly and risky, (2) token holders may prefer to not challenge bad entries if they hold tokens in both the listing and the registry, (3) wealth concentrates over time as early token holders accumulate voting power.

## Key concepts

- **Token-weighted voting**: voting power proportional to token holdings. Creates plutocratic dynamics.
- **Registry as quality signal**: the registry's value comes from its curation quality; token value derives from registry value. But this circular dependency can break: if quality declines, tokens lose value, quality declines further.
- **Challenge rarity**: Asgaonkar shows that rational token holders may not challenge bad entries because the expected return from challenging is negative after costs. This leads to passive acceptance of low-quality entries.
- **Inflationary mechanism** (Wang & Krishnamachari 2019): proposes token inflation to incentivize active participation, addressing the challenge rarity problem. But inflation introduces its own incentive distortions.

## Connection to our paper

TCRs are the closest prior art and the primary "what not to do" reference:

- **"This is just TCRs" is an anticipated objection**: our Q&A prep addresses this directly. The key differences:
  1. **Unit of curation**: TCRs answer "is this item in the list?" Our unit is a structured claim with proposition, scope, evidence policy, and resolution policy. This structure supplies explicit grounds for adjudication, without eliminating interpretation or policy choice.
  2. **Quality decomposition**: The basic registry membership game uses token-weighted acceptance decisions. We separate accuracy (dispute resolution) from relevance (coherence game). TCRs conflate the two.
  3. **Evidence standard**: A registry needs an application-specific evidence and listing policy. A token-voting mechanism alone does not supply one; this does not mean all registry implementations lack policies.
  4. **Challenge economics**: TCR challenges are rare because challenging is expensive with uncertain returns. Our dispute mechanism (via DDR) has concrete expected-value calculations and the bounty structure can make a challenge profitable under particular detection, cost and adjudication assumptions.

- **Documented failure modes that informed our design**:
  - Challenge rarity: challenge incentives depend on expected rewards, detection and dispute costs
  - Participation decay: pooled availability may simplify participation but its retention effect is unvalidated
  - Wealth concentration: the selected relevance draft uses utility-token stake; publisher reputation does not remove stake concentration
  - No evidence standard: addressed by explicit evidence policies per pool

## Key takeaway

Registry work exposes reasons to analyze token-weighted curation carefully; it does not prove that every such registry must fail. The contribution of our work is not "TCR but better" but a different architecture: structured claims + quality decomposition + separate mechanisms per dimension + explicit evidence standards. The surface similarity (tokens, staking, voting) masks deep structural differences.
