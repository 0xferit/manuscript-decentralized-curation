# George (2023): Strategic Behaviour and Manipulation Resistance in Peer-to-Peer Information Gathering

**Citation**: George, W. (2023). Strategic behaviour and manipulation resistance in Peer-to-Peer, crowdsourced information gathering. *Mathematical Social Sciences*, 124, 1-23. doi:10.1016/j.mathsocsci.2023.04.005

## Core thesis

For Schelling-style coordination games (peer-to-peer, crowdsourced information systems) with voting and payoff systems satisfying minimal attack resistance, if there are three or more **ranked** alternatives, then situations always exist where truthful reporting is not a Nash equilibrium. This is an impossibility result: no mechanism design can make truthful reporting universally incentive-compatible under these conditions.

## Key concepts

- **Impossibility theorem**: the central result. For games with >= 3 ranked alternatives and minimal attack resistance properties, truth-telling cannot always be an equilibrium. This bounds what Schelling-based mechanisms can achieve.
- **Minimal attack resistance**: the properties that any reasonable mechanism should satisfy (e.g., you cannot profit by simply copying someone else's report, the mechanism is not trivially gameable). These are weak conditions, making the impossibility strong.
- **Ranked alternatives**: the impossibility requires that the alternatives can be ranked (ordered). This is the key technical condition our paper exploits: binary choice and scalar aggregation are not "ranked alternatives" in the required sense.

## Connection to our paper

This is the primary constraint our mechanism design must navigate. We cite it as the reason we cannot claim truthful reporting is always an equilibrium in the general case. Our contribution is identifying **restricted conditions** where the impossibility does not bind:

### Binary accuracy (DDR disputes)
- The impossibility requires >= 3 ranked alternatives. Binary choice (Valid/Invalid) has only 2 alternatives, so the impossibility does not apply.
- Under-specified is a structural rejection (claim fails template validation), not a third ranked alternative that jurors compare against Valid/Invalid.
- This is a clean escape: the impossibility literally does not cover the binary case.

### Scalar relevance (coherence game)
- Curators report on [0,1] (continuous scalar), aggregated by weighted mean with K-sigma threshold.
- George's impossibility applies to **rankings** over discrete alternatives. Scalar aggregation with a coherence band is a different game structure.
- The escape here is less clean than the binary case: we argue the game structure is sufficiently different that the impossibility does not "directly bind," but we should be careful about overclaiming. The impossibility is about ranked discrete alternatives; our game is about distance from a continuous mean. These are structurally different, but proving they are formally outside the impossibility's scope requires care.

## Key takeaways for our paper

1. We cannot claim our mechanisms always produce truth. We should not try. The mechanisms produce signals that are more expensive to fake than to verify honestly.
2. The binary restriction for accuracy is well-justified and clean.
3. The scalar restriction for relevance is defensible but less airtight. We should frame it as "the impossibility does not directly bind" rather than "the impossibility does not apply."
4. This paper is also useful for explaining why simpler approaches (e.g., voting on quality with 3+ categories) would fail: the impossibility directly applies.

## Relationship to George (2023b) on griefing

Same author, different paper. The griefing paper provides the attack-cost formalization (griefing factor). The impossibility paper provides the theoretical boundary. Together they define the design space: what is impossible in general (impossibility) and how to measure security of specific designs within the feasible region (griefing factor).
