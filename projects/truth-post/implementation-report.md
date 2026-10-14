> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Copyright (c) 2026 Ferit Tunçer.

# Truth Post Implementation Report

Historical analysis: March 9, 2026. Usage snapshot: April 9, 2026. Source-link and repair verification: October 14, 2026.

This retrospective describes the 2023 partial deployment and later observations of it. It is not the specification of the current proposed protocol. The [blueprint](https://manuscript-decentralized-curation.pages.dev/truth-post/blueprint/) describes that proposal; the [foundational paper](https://manuscript-decentralized-curation.pages.dev/) owns the shared mechanism rules.

## Summary

Truth Post is a partial implementation of the thesis design for decentralized news curation. It implemented an **accuracy-layer bonded dispute mechanism** on-chain and a **Trust Score** confidence metric in the webapp/subgraph layer. It does **not** implement the full protocol described in the thesis. In particular, it omits the relevance layer, and therefore also has no internal curator role, no pooled staking layer, no reputation layer and no interface redundancy. Both the deployment and the current proposal use binary accuracy challenges; the proposal handles non-falsifiability through a typed challenge reason, not a separate ambiguity verdict.

**Trust Score was implemented** in the webapp and indexing layer. It was not a Solidity contract primitive or an empirically validated probability of accuracy.

## Sources Reviewed

- Thesis section on Truth Post in the [foundational paper](https://manuscript-decentralized-curation.pages.dev/)
- [Historical contract source](https://github.com/proveuswrong/contracts-tp/tree/9cf886989bad1dfd5df476c5607ef8d9b403a7dd): the last contract-file revision before the April 2026 repair; the observations below are reproducible in this source, without asserting deployed-bytecode identity.
- [Webapp source](https://github.com/proveuswrong/webapp-tp/tree/38400a5a08a8d7a28aeb15dfcb599d8fef6ed7d9): March 9, 2026 snapshot used for the source permalinks below.
- Observed site: [landing page](https://truthpost.news/) and [application route](https://truthpost.news/0x1/). Site availability statements below describe the dated observation, not a current uptime check.
- Legacy deployed News dispute policy: `https://bafybeihfbyagmbt5ilixqtoj2ga3pxv77gnpwquyr5usq6yhdzxvi3w354.ipfs.dweb.link/`

## Mechanism Design

Truth Post implements a narrow but real mechanism:

1. An author publishes a claim and locks ether (ETH) as a bounty.
2. The claim remains live unless challenged.
3. Anyone can challenge by paying Kleros arbitration cost plus a tax.
4. Kleros adjudicates the binary accuracy dispute.
5. If the challenger wins, the author's bounty is transferred to the challenger.
6. If the author wins or the ruling ties, the bounty remains and the article can continue accumulating trust.
7. Appeal funding is crowdfunded, and contributors on the ultimately winning side can claim rewards.

In compact form, the mechanism is:

- **Accuracy game**: "prove this claim wrong if it is false"
- **Confidence metric**: "how much bonded value has remained exposed, for how long, without successful debunking"

## What Is Implemented On-Chain

The Solidity contract in [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L16) implements:

- Author submission with a bonded bounty via `initializeArticle(...)` in [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L71)
- Bounty increases via `increaseBounty(...)` in [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L103)
- Withdrawal timelock and withdrawal via [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L117) and [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L127)
- Open challenges routed to Kleros via [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L147)
- Appeal crowdfunding via [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L177)
- Distribution of bounty to the challenger on successful debunking via [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L282)
- Basic admin controls for challenge tax, treasury, and dispute parameters

The deploy script configures a single `News` category and asks a binary policy question:

- "Is this article accurate according to the policy of this curation pool?"

This is defined in [`1_deploy_truthpost.js`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/deploy/1_deploy_truthpost.js#L24).

The deployed system also references one fixed `News` dispute policy document through the Kleros metaevidence URI. That document is the juror policy surface used by the minimum viable product (MVP). It is thin, but real. In substance it says:

- submissions must be understandable in English
- submissions must actually pertain to news
- challengers should provide a reason and supporting evidence
- if any part of the article is inaccurate, the article is inaccurate
- time-sensitive claims should be judged within the article's stated timeframe
- evidence should be submitted in open file formats

So the MVP did not use a naked true/false question with no surrounding policy. It used one static pool-level dispute policy. What it lacked was the richer, versioned policy stack described in the complete blueprint: structured claim templates, explicit evidence-policy versions, and typed challenge reasons. The current blueprint also resolves each accuracy challenge with a binary outcome.

## What Is Implemented In The Webapp

The Trust Score confidence mechanism exists in the webapp and subgraph layer.

The app fetches the following article fields from the subgraph in [`fragments.js`](https://github.com/proveuswrong/webapp-tp/blob/38400a5a08a8d7a28aeb15dfcb599d8fef6ed7d9/src/data/graphql/fragments.js#L1):

- `bounty`
- `lastCalculatedScore`
- `lastBalanceUpdate`

The Trust Score is computed in [`getTrustScore.js`](https://github.com/proveuswrong/webapp-tp/blob/38400a5a08a8d7a28aeb15dfcb599d8fef6ed7d9/src/businessLogic/getTrustScore.js#L1) as:

```text
TrustScore = lastCalculatedScore + (currentBlockNumber - lastBalanceUpdate) * bounty
```

This is the raw accumulated score. The display divides the raw wei-block value by $10^{18}$ and truncates to whole ether-blocks. The block delta is computed in [`getTimePastSinceLastBountyUpdate.js`](https://github.com/proveuswrong/webapp-tp/blob/38400a5a08a8d7a28aeb15dfcb599d8fef6ed7d9/src/businessLogic/getTimePastSinceLastBountyUpdate.js#L1).

The app then uses this score to:

- sort articles in browse view in [`listArticles/index.jsx`](https://github.com/proveuswrong/webapp-tp/blob/38400a5a08a8d7a28aeb15dfcb599d8fef6ed7d9/src/components/others/listArticles/index.jsx#L1)
- display Trust Score on article pages in [`keyMetrics/index.jsx`](https://github.com/proveuswrong/webapp-tp/blob/38400a5a08a8d7a28aeb15dfcb599d8fef6ed7d9/src/components/others/route_article/keyMetrics/index.jsx#L1)
- explain the intended semantics in the FAQ in [`faq/index.jsx`](https://github.com/proveuswrong/webapp-tp/blob/38400a5a08a8d7a28aeb15dfcb599d8fef6ed7d9/src/routes/faq/index.jsx#L10)

The article UI explicitly labels the unit as `Etherblocks`, which is accurate to the implementation.

**Validation caveat.** Trust Score was implemented and displayed, but never empirically validated. No correlation analysis was performed between Trust Score rankings and actual article accuracy, and no comparison was made against a baseline (e.g., unweighted chronological ordering). The formula also differs from the blueprint's `confidenceIntegral` design, which specifies pause/resume semantics during challenges and withdrawals; the MVP formula lacks these pause/freeze semantics.

Validating Trust Score as a meaningful confidence metric would require at minimum: correlation with future accuracy outcomes, comparison to simpler ranking baselines, and sensitivity analysis across realistic bounty and duration ranges.

## What Is Missing Relative To The Thesis

Relative to the fuller design described in the thesis, these major components are absent:

- **Relevance curation**: no coherence game, no internal curators, no curator scoring, no weight allocation, and no relevance ranking mechanism
- **Pooled staking**: absent because the relevance/curation layer was never built. The deployed system is article-by-article on the author/challenger side: authors publish individual bonded claims, challengers challenge individual claims, and Kleros jurors handle disputes externally.
- **Author reputation**: no pool-scoped author outcome-history score of the kind specified in the current blueprint. This is separate from curator competence, which the current protocol does not establish through a reputation score.
- **Typed non-falsifiability challenges**: the deployment has no explicit `NonFalsifiable` challenge reason; only `Tied`, `ChallengeFailed`, and `Debunked` exist in [`ITruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/ITruthPost.sol#L13)
- **Claim templates**: the legacy News policy gives jurors general guidance, but there is no structured schema enforcing falsifiability, scope, or required claim fields before posting
- **Versioned evidence policy**: the MVP uses one static News juror-policy document rather than a versioned evidence-policy system pinned per claim or per pool version
- **Protocol-native confidence system**: Trust Score exists, but as app/indexer logic rather than a contract-level protocol primitive
- **Treasury rewards**: treasury tax exists, but there is no reward distribution system for high-quality submissions or for any future curation labor beyond the current author/challenger/arbitration flow
- **Interface redundancy**: a single operational frontend remains a point of failure

## Architectural Constraints And Weaknesses

Several important implementation limits are visible in the current design.

### Off-chain dependence for readability

The `Article` struct stores only:

- `owner`
- `withdrawalPermittedAt`
- `bountyAmount`
- `category`

See [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L45).

The `articleID` is emitted in `NewArticle(...)` but is not stored in article state. See [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L90). That means article retrieval depends on event indexing plus InterPlanetary File System (IPFS) resolution. If indexing or content resolution fails, the claim becomes difficult or impossible to render usefully.

### Publishing lock is ineffective

The interface exposes `isPublishingEnabled`, and `switchPublishingLock()` toggles it in [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L384). But `initializeArticle(...)` never checks that flag. So the publishing lock exists as state but is not enforced.

### Category creation is permissionless

`newCategory(...)` is public in [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L431). There is no governance layer controlling creation of new curation pools or policy surfaces.

### Historical appeal-resolution bug and source repair

The historical `rule()` function contains a bug in the default-win logic:

- it checks `ChallengeFailed` twice
- the `Debunked` default-win branch is therefore unreachable

See [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L267).

This is a material bug in that historical appeal-default path: when only the challenger funds the final appeal round, the function cannot select `Debunked` by default. The source repair was merged on April 20, 2026 in [commit `189a82a`](https://github.com/proveuswrong/contracts-tp/commit/189a82a8653171982dfe30a5c9abf900597982b3). The repaired source checks the two different outcomes. Neither the historical test report nor this source comparison establishes whether any deployed instance encountered the defect or was replaced with repaired bytecode.

### ETH transfer reliability

Several transfers use `send(...)` and deliberately ignore failure:

- refund path in [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L252)
- challenger payout in [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L287)
- contributor reward withdrawal in [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L355)
- treasury transfer in [`TruthPost.sol`](https://github.com/proveuswrong/contracts-tp/blob/9cf886989bad1dfd5df476c5607ef8d9b403a7dd/contracts/TruthPost.sol#L379)

In the contributor and treasury paths, accounting is cleared before the unchecked transfer, so a failed transfer can leave value in the contract without preserving the original claim in that accounting. This is a concrete payment-failure risk; the observation alone does not establish that a deployed transfer failed.

## Operational Status

As checked on March 9, 2026:

- the landing page at `https://truthpost.news/` loaded
- the application route at `https://truthpost.news/0x1/` failed

Observed behavior from browser automation:

- The Graph endpoint returned `200`
- article fetches to `https://ipfs.kleros.io/ipfs/...` failed with `ERR_NAME_NOT_RESOLVED`
- the app crashed with `Unexpected Application Error! Failed to fetch`

This failure is consistent with a known structural vulnerability. The report's own architectural analysis (see "Off-chain dependence for readability" above) documents that article content depends on IPFS resolution through a single gateway (`ipfs.kleros.io`), and the "Missing Relative to the Thesis" section lists interface redundancy as absent. The observed frontend path had no effective fallback for this content-resolution failure; this does not establish that the contract logic was sound. The observed failure matches what the thesis later identified as a design gap, though confirming a single root cause would require more diagnostic data than the browser-automation tests provide.

## Verification Notes

The original analysis recorded cloning the contract repository, installing dependencies, and running:

```bash
yarn install --immutable
yarn test
```

The original analysis recorded 28 passing tests. Its exact checkout, runtime versions and test log were not retained here, so that result is historical evidence rather than a reproducible test result from this cleanup. The October source review above did not install or execute those external dependencies.

## Final Assessment

Truth Post is best understood as a **partial deployment of the accuracy layer**, with a **real but off-chain Trust Score system** used for ranking and reader-facing confidence. The source and interface observations support implementation of the functions listed below. They do not establish economic effectiveness.

Public usage data is sparse but retrievable. On April 9, 2026, the public Ethereum mainnet page for the deployed contract (`0x87AAdE1067Ed0276ec9BEf6db8E17Abe27A6B454`) listed 16 external (non-internal) transactions: five `Initialize Article`, three `Increase Bounty`, three `Initiate Withdraw`, three `Withdraw`, one `Transfer Ownership`, and one `Change Admin`. The public transaction list showed no visible challenge transaction. This records sparse visible activity in that snapshot; it is neither a current total nor sufficient by itself to determine sustained use across deployments or its causes. Sparse activity is consistent with multiple explanations, including distribution failure, user-experience friction, gas and arbitration costs, or the absence of the later relevance layer.

- claims can be bonded
- false claims can be challenged
- disputes can be outsourced to decentralized arbitration
- a confidence metric can be computed from bonded exposure duration

The historical appeal-default defect limits what can be inferred about one-sided appeal funding in the deployment. Its subsequent source repair does not establish that the deployed contract changed.

However, claims that survived without challenge cannot be treated as "validated by absence of challenge." The on-chain record shows which claims survived, not why. Absence of challenge is consistent with multiple explanations: the claim is accurate, no one saw it, no one had resources to challenge, or potential challengers were deterred. Assessing whether the challenge mechanism actually functioned as intended would require off-chain investigation (challenger awareness, resource availability, deterrence effects) that this retrospective does not provide.

What it does **not** demonstrate is the full decentralized curation architecture of the thesis. The missing pieces are precisely the parts that turn an accuracy-only dispute primitive into a broader curation protocol:

- relevance
- pooled participation
- reputation
- typed non-falsifiability challenges
- versioned claim and evidence policy surfaces
- stronger protocol/interface separation

The scope of the evidence is therefore:

- Truth Post was **an accuracy-dispute implementation with an additional off-chain confidence metric** because it had both a live Trust Score and a real juror policy document
- but it was still **far from the full thesis design**
