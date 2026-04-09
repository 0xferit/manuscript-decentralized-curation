# Truth Post Implementation Report

Date of analysis: March 9, 2026

## Summary

Truth Post is a partial implementation of the thesis design for decentralized news curation. It implements an **accuracy-layer bonded dispute mechanism** on-chain and a **Trust Score** confidence metric in the webapp/subgraph layer. It does **not** implement the full protocol described in the thesis. In particular, it omits the relevance layer, and therefore also has no internal curator role, no pooled staking layer, no reputation layer, no ambiguity handling through an `Under-specified` verdict, and no interface redundancy.

The key correction to my earlier assessment is this: **Trust Score was implemented**. It exists in the webapp and indexing layer, not in the Solidity contract itself.

## Sources Reviewed

- Thesis section on Truth Post in [`paper.qmd`](/Users/ferit/Documents/Projects/0xferit/manuscript-decentralized-curation/paper.qmd#L505)
- Smart contract repo: `https://github.com/proveuswrong/contracts-tp`
- Webapp repo: `https://github.com/proveuswrong/webapp-tp`
- Live site: `https://truthpost.news/` and `https://truthpost.news/0x1/`
- Legacy deployed News dispute policy: `https://bafybeihfbyagmbt5ilixqtoj2ga3pxv77gnpwquyr5usq6yhdzxvi3w354.ipfs.dweb.link/`

## Mechanism Design

Truth Post implements a narrow but real mechanism:

1. An author publishes a claim and locks ETH as a bounty.
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

The Solidity contract in [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L16) implements:

- Author submission with a bonded bounty via `initializeArticle(...)` in [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L71)
- Bounty increases via `increaseBounty(...)` in [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L103)
- Withdrawal timelock and withdrawal via [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L117) and [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L127)
- Open challenges routed to Kleros via [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L147)
- Appeal crowdfunding via [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L177)
- Distribution of bounty to the challenger on successful debunking via [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L282)
- Basic admin controls for challenge tax, treasury, and dispute parameters

The deploy script configures a single `News` category and asks a binary policy question:

- "Is this article accurate according to the policy of this curation pool?"

This is defined in [`1_deploy_truthpost.js`](/tmp/contracts-tp.mgfmL9/deploy/1_deploy_truthpost.js#L24).

The deployed system also references one fixed `News` dispute policy document through the Kleros metaevidence URI. That document is the actual juror policy surface used by the MVP. It is thin, but real. In substance it says:

- submissions must be understandable in English
- submissions must actually pertain to news
- challengers should provide a reason and supporting evidence
- if any part of the article is inaccurate, the article is inaccurate
- time-sensitive claims should be judged within the article's stated timeframe
- evidence should be submitted in open file formats

So the MVP did not use a naked true/false question with no surrounding policy. It used one static pool-level dispute policy. What it lacked was the richer, versioned policy stack described in the complete blueprint: structured claim templates, explicit evidence-policy versions, and an `UnderSpecified` outcome.

## What Is Implemented In The Webapp

The Trust Score confidence mechanism exists in the webapp and subgraph layer.

The app fetches the following article fields from the subgraph in [`fragments.js`](/tmp/webapp-tp.vULtMf/src/data/graphql/fragments.js#L1):

- `bounty`
- `lastCalculatedScore`
- `lastBalanceUpdate`

The Trust Score is computed in [`getTrustScore.js`](/tmp/webapp-tp.vULtMf/src/businessLogic/getTrustScore.js#L1) as:

```text
TrustScore = lastCalculatedScore + (currentBlockNumber - lastBalanceUpdate) * bounty
```

The block delta is computed in [`getTimePastSinceLastBountyUpdate.js`](/tmp/webapp-tp.vULtMf/src/businessLogic/getTimePastSinceLastBountyUpdate.js#L1).

The app then uses this score to:

- sort articles in browse view in [`listArticles/index.jsx`](/tmp/webapp-tp.vULtMf/src/components/others/listArticles/index.jsx#L1)
- display Trust Score on article pages in [`keyMetrics/index.jsx`](/tmp/webapp-tp.vULtMf/src/components/others/route_article/keyMetrics/index.jsx#L1)
- explain the intended semantics in the FAQ in [`faq/index.jsx`](/tmp/webapp-tp.vULtMf/src/routes/faq/index.jsx#L10)

The article UI explicitly labels the unit as `Etherblocks`, which is accurate to the implementation.

**Validation caveat.** Trust Score was implemented and displayed, but never empirically validated. No correlation analysis was performed between Trust Score rankings and actual article accuracy, and no comparison was made against a baseline (e.g., unweighted chronological ordering). The formula also differs from the blueprint's `confidenceIntegral` design, which specifies pause/resume semantics during challenges and withdrawals; the MVP formula lacks these pause/freeze semantics.

Validating Trust Score as a meaningful confidence metric would require at minimum: correlation with future accuracy outcomes, comparison to simpler ranking baselines, and sensitivity analysis across realistic bounty and duration ranges.

## What Is Missing Relative To The Thesis

Relative to the fuller design described in the thesis, these major components are absent:

- **Relevance curation**: no coherence game, no internal curators, no curator scoring, no weight allocation, and no relevance ranking mechanism
- **Pooled staking**: absent because the relevance/curation layer was never built. The deployed system is article-by-article on the author/challenger side: authors publish individual bonded claims, challengers challenge individual claims, and Kleros jurors handle disputes externally.
- **Reputation**: no topic-scoped non-transferable competence score, again because the protocol never introduced an internal curator/validator layer
- **Under-specified verdict**: only `Tied`, `ChallengeFailed`, and `Debunked` exist in [`ITruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/ITruthPost.sol#L13)
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

See [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L45).

The `articleID` is emitted in `NewArticle(...)` but is not stored in article state. See [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L90). That means article retrieval depends on event indexing plus IPFS resolution. If indexing or content resolution fails, the claim becomes difficult or impossible to render usefully.

### Publishing lock is ineffective

The interface exposes `isPublishingEnabled`, and `switchPublishingLock()` toggles it in [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L384). But `initializeArticle(...)` never checks that flag. So the publishing lock exists as state but is not enforced.

### Category creation is permissionless

`newCategory(...)` is public in [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L431). There is no governance layer controlling creation of new curation pools or policy surfaces.

### Appeal-resolution bug

The `rule()` function appears to contain a real bug in the default-win logic:

- it checks `ChallengeFailed` twice
- the `Debunked` default-win branch is therefore unreachable

See [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L267).

This is a material bug in the appeal-default path. When one appeal side is fully funded and the other is not, the intended "single funded side wins by default" logic is described in the FAQ, but the implementation cannot realize the `Debunked` outcome on that path. I did not verify whether any on-chain appeal actually hit this branch.

### ETH transfer reliability

Several transfers use `send(...)` and deliberately ignore failure:

- refund path in [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L252)
- challenger payout in [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L287)
- contributor reward withdrawal in [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L355)
- treasury transfer in [`TruthPost.sol`](/tmp/contracts-tp.mgfmL9/contracts/TruthPost.sol#L379)

This does not prove the system is unusable, but it is weaker than a more robust payout design.

## Operational Status

As checked on March 9, 2026:

- the landing page at `https://truthpost.news/` loaded
- the application route at `https://truthpost.news/0x1/` failed

Observed behavior from browser automation:

- The Graph endpoint returned `200`
- article fetches to `https://ipfs.kleros.io/ipfs/...` failed with `ERR_NAME_NOT_RESOLVED`
- the app crashed with `Unexpected Application Error! Failed to fetch`

This failure is consistent with a known structural vulnerability. The report's own architectural analysis (see "Off-chain dependence for readability" above) documents that article content depends on IPFS resolution through a single gateway (`ipfs.kleros.io`), and the "Missing Relative to the Thesis" section lists interface redundancy as absent. The contract logic may be sound in isolation, but the system as deployed had no redundancy for this off-chain dependency. The observed failure matches what the thesis later identified as a design gap, though confirming a single root cause would require more diagnostic data than the browser-automation tests provide.

## Verification Notes

I cloned `contracts-tp` into a temporary directory, installed dependencies, and ran:

```bash
yarn install --immutable
yarn test
```

The test suite passed with 28 passing tests. That indicates the basic accuracy/dispute flow was implemented and locally test-covered.

## Final Assessment

Truth Post is best understood as a **partial deployment of the accuracy layer**, with a **real but off-chain Trust Score system** used for ranking and reader-facing confidence. The deployment demonstrated that the following were implemented:

Public usage data is sparse but retrievable. On April 9, 2026, the public Ethereum mainnet page for the deployed contract (`0x87AAdE1067Ed0276ec9BEf6db8E17Abe27A6B454`) listed 16 total transactions: five `Initialize Article`, three `Increase Bounty`, three `Initiate Withdraw`, three `Withdraw`, one `Transfer Ownership`, and one `Change Admin`. The public transaction list showed no visible challenge transaction. That is enough to say the deployment did not bootstrap sustained on-chain usage. It is not enough to identify a unique cause. Sparse activity is consistent with multiple explanations, including distribution failure, UX friction, gas and arbitration costs, or the absence of the later relevance layer.

- claims can be bonded
- false claims can be challenged
- disputes can be outsourced to decentralized arbitration
- a confidence metric can be computed from bonded exposure duration

That said, the appeal-default path for `Debunked` appears broken, so this report does not establish that the intended one-sided-funding appeal flow finalized correctly.

However, claims that survived without challenge cannot be treated as "validated by absence of challenge." The on-chain record shows which claims survived, not why. Absence of challenge is consistent with multiple explanations: the claim is accurate, no one saw it, no one had resources to challenge, or potential challengers were deterred. Assessing whether the challenge mechanism actually functioned as intended would require off-chain investigation (challenger awareness, resource availability, deterrence effects) that this retrospective does not provide.

What it does **not** demonstrate is the full decentralized curation architecture of the thesis. The missing pieces are precisely the parts that turn an accuracy-only dispute primitive into a broader curation protocol:

- relevance
- pooled participation
- reputation
- structured ambiguity handling
- versioned claim and evidence policy surfaces
- stronger protocol/interface separation

So the corrected conclusion is:

- Truth Post was **more complete than "just Kleros disputes"** because it had both a live Trust Score and a real juror policy document
- but it was still **far from the full thesis design**
