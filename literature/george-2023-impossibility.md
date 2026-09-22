# George (2023): Strategic Behaviour and Manipulation Resistance in Peer-to-Peer Information Gathering

**Citation**: George, W. (2023). Strategic behaviour and manipulation resistance in Peer-to-Peer, crowdsourced information gathering. *Mathematical Social Sciences*, 124, 1-23. doi:10.1016/j.mathsocsci.2023.04.005

## Core thesis

For Schelling-style coordination games (peer-to-peer, crowdsourced information systems) with voting and payoff systems satisfying minimal attack resistance, if there are three or more **ranked** alternatives, then situations always exist where truthful reporting is not a Nash equilibrium. This is an impossibility result: no mechanism design can make truthful reporting universally incentive-compatible under these conditions.

## Key concepts

- **Impossibility theorem**: the central result. For games with >= 3 ranked alternatives and minimal attack resistance properties, truth-telling cannot always be an equilibrium. This bounds what Schelling-based mechanisms can achieve.
- **Minimal attack resistance**: the properties that any reasonable mechanism should satisfy (e.g., you cannot profit by simply copying someone else's report, the mechanism is not trivially gameable). These are weak conditions, making the impossibility strong.
- **Ranked alternatives**: applying the theorem to a proposed mechanism requires matching its alternatives, reports and payoffs to the theorem’s assumptions. A scalar reporting space alone does not establish that the mechanism falls outside its scope.

## Connection to our paper

We cite this result as a constraint on general truthful-reporting claims. The paper does not establish an escape theorem for its relevance mechanism:

### Binary accuracy (DDR disputes)
- The impossibility requires >= 3 ranked alternatives. Binary choice (Valid/Invalid) has only 2 alternatives, so the impossibility does not apply.
- `NonFalsifiable` and `TemplateViolation` identify challenge reasons adjudicated against a pool’s requirements. They are not additional truth values ranked alongside Valid/Invalid.
- This is a clean escape: the impossibility literally does not cover the binary case.

### Scalar relevance (coherence game)
- Curators report a scalar in [0,1], aggregated by weighted mean with a dispersion-dependent penalty.
- Direct application of the impossibility result requires a formal mapping between the games. Regardless of that mapping, the paper’s [Claim 3](../paper.qmd#curator-voting-strategy) demonstrates a profitable deviation under permitted relevance-reward parameters.

## Key takeaways for our paper

1. We cannot claim our mechanisms always produce truth or that every false report is more expensive than an honest one. The stated reward rule permits profitable dispersion padding.
2. The ranked-alternative theorem’s assumptions must be checked against each proposed mechanism; changing the reporting space is not a proof of incentive compatibility.
3. Analyze the actual utilities, information, reward and appeal rules before claiming a truthful equilibrium.

## Relationship to George (2023b) on griefing

Same author, different paper. The griefing paper provides the attack-cost formalization (griefing factor). The impossibility paper provides the theoretical boundary. Together they define the design space: what is impossible in general (impossibility) and how to measure security of specific designs within the feasible region (griefing factor).
