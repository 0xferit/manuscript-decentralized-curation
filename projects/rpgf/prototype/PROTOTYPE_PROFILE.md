# RPGF Decentralized Curation Prototype: Profile

This profile freezes the scope of the RPGF prototype under
`projects/rpgf/prototype/`. The prototype is a controlled, deterministic
single-pool simulation. It is not production code, not on-chain, and not
audited. Its purpose is to demonstrate the full mechanism flow described in
`projects/rpgf/design.md`: registry to pool to nomination to relevance scoring
to provisional allocation to challenge/DDR mock to holdback/disbursement to
redistribution to reputation update.

When this profile and `projects/rpgf/design.md` disagree, the design document
wins for normative claims. The profile records implementation choices; it does
not amend the spec.

## Scope summary

| Concern | Prototype choice |
|---|---|
| Surface | TypeScript domain engine plus Vite + React inspector UI |
| Pool count | One static pool |
| Registry governance | Static registry; not implemented |
| Time | Phase advances by explicit user action; no real waits |
| Randomness | Deterministic seeded PRNG (mulberry32) instead of VRF |
| DDR | Manual deterministic mock with `Debunked`, `ChallengeFailed`, `Timeout` |
| Funds | Tracked as numeric units (`token` unit, 1.0 = 1 ETH-equivalent); no transfers |
| Appeals | Disabled in v1 |
| Pre-reveal leak | Not modeled |
| Curator exit cooldown | Not modeled |
| Pool versioning by content hash | Not modeled |

## Registry model

The pool references one in-memory project-beneficiary registry. Each
`RegistryEntry` carries:

- `id` (stable, used as the nomination join key)
- `projectName`
- `beneficiaryAddress` (mock string; not a real chain address)
- `claimantPolicy` (string; informational only)
- `eligibilityTags` (e.g. `["ethereum-l2", "open-source"]`)
- `reputation` (integer; pool-scoped)
- `lastReputationUpdateEpoch`

The prototype does not implement registry governance, registry-entry creation
flow, or claimant-policy enforcement. Authors are matched to registry entries
by id.

## Nomination JSON shape

```ts
type ImpactNomination = {
  id: string;
  poolId: string;
  registryEntryId: string;
  authorAddress: string;
  state:
    | "Submitted"
    | "Retracted"
    | "Scored"
    | "Disputed"
    | "Disbursed"
    | "Debunked"
    | "Unscored";
  adjudicationOutcome: "Unchallenged" | "ChallengeFailed" | "Debunked";
  bondToken: number;             // pool.submissionBond
  assertions: Array<{
    id: string;
    text: string;
    timePeriodStart: string;     // ISO date
    timePeriodEnd: string;
    evidenceItemIds: string[];
    falsifiable: boolean;        // mock flag for the prototype
  }>;
  evidenceItems: EvidenceItem[];
  createdAtPhaseTick: number;
  lastUpdatedPhaseTick: number;
  templateOk: boolean;           // mock flag for the prototype
  doubleCountTagIds: string[];   // surface overlap visually
  relevanceScore?: number;       // mu of the round, in [0,1]
  relevanceRoundId?: string;
  provisionalShareToken?: number;
  finalShareToken?: number;
  graceEndsAtTick?: number;
};
```

Evidence items carry a class (`DirectArtifact`, `IndependentThirdParty`,
`SelfReported`), a URI string, and a free-text caption. The engine never
fetches URIs; they are display strings only.

## Pool parameters (frozen)

The reference profile in `projects/rpgf/design.md` is honored where it can be.
Time-based parameters are reinterpreted as discrete phase ticks for the
prototype.

| Parameter | Spec default | Prototype value |
|---|---|---|
| Pool funding budget | configurable | `100` token |
| Curation budget reserve | 5% of pool funding budget | `5` token (5% of 100) |
| Author bond | 0.01 ETH | `0.01` token |
| Challenger counter-stake | `max(0.01, 0.25 * b * P)` | implemented as formula |
| Challenge tax | 0.5% of challenged share | implemented as formula |
| DDR fee | external | `0` (mock; recorded but not charged) |
| Submission window | 30 days | one phase, advanced by button |
| Holdback period | 30 days | one phase, advanced by button |
| Grace after `ChallengeFailed` | 7 days | `1` tick |
| DDR timeout | 90 days | manual `Timeout` outcome |
| Drafted seats per round | 15 | 15 |
| Min reveal quorum | 5 | 5 |
| Seat size `L` | ~0.01 ETH | `0.01` token |
| Coherence `K` | 1.25 | 1.25 |
| Dispersion floor `epsilon_sigma` | 0.02 | 0.02 |
| Min reward fraction `rho` | 0.3 | 0.3 |
| Round reward floor | 0.01 ETH equiv | `0.01` token |
| `sigma_ref` mode | EMA | EMA, alpha = 0.05, bootstrap `emaSigma = 0` |
| Reputation: surviving round | +1 | +1 |
| Reputation: debunking | -5 | -5 |
| Reputation: decay | abs(reputation) -= 1 per epoch | same; epoch = one phase tick |
| Max nominations per round | `curationBudget / roundRewardFloor` | derived (5 / 0.01 = 500); prototype seeds 5 |

## Curator and stake model

`Curator` carries:

- `id`
- `displayName`
- `depositedToken` (initial deposit, varied across seeds)
- `lockedToken` (active locks across rounds)
- `archetype`: one of `Honest`, `Lazy`, `Adversary`. This is metadata only;
  scoring behavior is driven by an `intendedScore` and a `participation`
  field per round seed, not by archetype magic.
- `commitRevealBehavior`: `CommitAndReveal`, `CommitOnly`, or `NoShow`. Drives
  non-participation slashing.

Tickets per curator are computed exactly as in the blueprint:
`d_i = floor(deposited / L)`. The prototype does not model deposits, top-ups,
or exits during a round; the deposit set is fixed once the round is drafted.

## Relevance round rules

Per nomination, the engine runs one relevance round. It:

1. Snapshots the curator deposit set.
2. Builds the seat-ticket pool: each curator contributes `floor(deposited/L)`
   tickets.
3. Drafts seats by deterministic weighted draw-and-lock:
   - shuffles the ticket array under the round seed using mulberry32 +
     Fisher-Yates;
   - iterates up to `min(totalTickets, 3 * targetSeats)` tickets;
   - locks one seat of size `L` per ticket if the curator has spare available
     deposit covering all seats locked so far in this round;
   - stops once `targetSeats` seats are locked (success) or the iteration cap
     is exhausted (round cancelled as underfunded).
4. Models commit-reveal phase explicitly. The UI lets the user advance from
   commit to reveal phase, but each curator's intended behavior is encoded in
   their seed `commitRevealBehavior`.
5. Computes weighted mean (`mu`) and weighted standard deviation (`sigma`)
   over valid reveals.
6. Applies the low-dispersion guard: if `sigma < epsilon_sigma`, distance
   slashing is skipped for valid revealers but non-participation slashing
   still applies.
7. Otherwise applies graduated slashing
   `p_i = clamp((|v_i - mu| / sigma - K) / K, 0, 1)`,
   `delta_i = floor(p_i * w_i)` per blueprint.
8. Applies non-participation slashing at `p_i = 1` for drafted seats whose
   curator did not commit-and-reveal a valid score.
9. Computes round reward factor
   `f_reward = rho + (1 - rho) * min(1, sigma / sigma_ref)`
   where `sigma_ref = max(epsilon_sigma, emaSigma)`.
10. Reserves one `roundRewardFloor` from the pool curation budget per
    scheduled round. Released back if the round is cancelled or undistributed
    portions remain after a low-dispersion / no-coherent-set outcome.
11. Updates the pool's `emaSigma` after a finalized round:
    `emaSigma = alpha * sigma_round + (1 - alpha) * emaSigma_prev`. Cancelled
    rounds do not update `emaSigma`.
12. On quorum failure, the round is retried once with a fresh seed. If retry
    also fails, the nomination transitions to `Unscored`.

The relevance round produces `relevanceScore = mu` for the nomination on
success and leaves the nomination unscored otherwise.

## Appeals

Disabled in v1. `RelevanceRound` carries no appeal fields. The design
document's appeal mechanism is intentionally not implemented to keep the
prototype scope manageable; this is a documented deviation.

## DDR mock behavior

`DDRMock.resolve(challengeId, outcome)` accepts one of three outcomes:

- `Debunked`: nomination becomes `Debunked`; provisional share redistributed.
- `ChallengeFailed`: nomination returns to `Scored`; remaining holdback set
  to `max(remaining, graceTicks)` where `graceTicks = 1` in the prototype.
- `Timeout`: same effect as `ChallengeFailed` (per design.md DDR timeout
  defaults to author victory).

The mock does not consume any fee. It records who ruled it and at which tick.
It is fully deterministic: outcomes are chosen by the user from the UI.

## Challenge rules

A challenge is created against a `Scored` nomination during holdback. It
carries:

- `id`, `nominationId`, `challengerId`
- `reason`: one of `Debunking`, `NonFalsifiable`, `TemplateViolation`
- `counterStakeToken = max(submissionBond, 0.25 * provisionalShare)`
- `taxToken = 0.005 * provisionalShare` (paid to pool budget at filing)
- `ddrFeeToken = 0` (mock)
- `outcome`: `Pending` until DDR resolves
- `filedAtTick`, `resolvedAtTick`

Anti-relitigation is partially modeled: a follow-on challenge against a
nomination whose latest resolved outcome was `ChallengeFailed` requires the
user to type "new evidence" in the form. The prototype does not adjudicate
relitigation legitimacy beyond that gate.

## Distribution and redistribution rules

Provisional allocation is computed once per pool round, after evaluation:

```text
allocation_i = (relevanceScore_i / sum(relevanceScore_j over surviving j)) * poolFundingBudget
```

If the denominator is zero (no surviving nominations or all zero scores), no
allocation is made and the budget rolls over for the next round.

At holdback expiry:

- `Scored` and `Unchallenged` nominations move to `Disbursed`.
- `Disputed` nominations stay in escrow until DDR resolves.

On DDR resolution:

- `Debunked`: nomination's `provisionalShare` is redistributed pro rata by
  relevance score to nominations that have already disbursed in this round.
  If no disbursed nominations exist, the share rolls over to the next round.
- `ChallengeFailed` or `Timeout`: nomination returns to `Scored` with a
  one-tick grace window. After the grace tick with no new challenge, it
  disburses.

## Reputation rules

Reputation is integer-valued, pool-scoped, attached to registry entries:

- `+1` per surviving round (i.e., when nomination disburses without being
  debunked in that round).
- `-5` per `Debunked` outcome.
- Decay per epoch: if `reputation > 0`, `reputation -= 1`; if
  `reputation < 0`, `reputation += 1`. Stops at zero.
- Decay is applied by an explicit `tickEpoch()` call from the UI, so the
  reviewer can trigger it deterministically.

## Known deviations from `projects/rpgf/design.md`

1. **15 curators reinterpreted as 15 drafted seats.** The inherited draw-and-
   lock mechanism is seat-based and a single curator can hold multiple seats.
   The prototype keeps this seat-based draw and counts seats, not unique
   curators.
2. **Time replaced with phase ticks.** No 30/90-day waits. Phases advance
   when the reviewer clicks a button. Reputation decay also runs per tick.
3. **Manual DDR mock.** No external DDR. The reviewer chooses outcomes.
4. **Static registry, static pool.** No registry governance, no permissionless
   pool creation, no template authoring. The pool template flags
   (`templateOk`, `falsifiable`) are seeded directly on nominations.
5. **No appeals.** The design's relevance-round escalation is not
   implemented. A future v2 can add it without changing the round-level API.
6. **No pre-reveal leak reporting.** Curators have no way to leak; reporters
   have no way to report.
7. **No curator exit cooldown.** Deposits are static through a round.
8. **Anti-relitigation reduced to a UI gate.** A "new evidence" string is
   required to file a follow-on challenge after a `ChallengeFailed` outcome.
9. **Fees are tracked but not transferred.** All bonds, stakes, taxes, and
   rewards are bookkeeping entries on in-memory ledgers; the prototype does
   not model gas or external payment rails.
10. **One pool, one round at a time.** Multi-round histories are visible in
    the UI but only one round can be active; cross-round registry-reputation
    decay is supported.

These deviations are intentional and scoped. The mechanism shape of the
design document is preserved: nomination state machine, seat-based drafting,
graduated slashing, smooth reward scaling, EMA `sigma_ref`, holdback,
debunked redistribution, and pool-scoped registry-entry reputation are all
implemented as pure functions and exercised by the UI.
