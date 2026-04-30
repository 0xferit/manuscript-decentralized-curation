# RPGF Decentralized Curation Prototype

A controlled, deterministic prototype of the RPGF Decentralized Curation
mechanism specified in `projects/rpgf/design.md`. It runs the full mechanism
flow end to end:

```
registry -> pool -> nomination -> relevance scoring -> provisional allocation
        -> challenge / DDR mock -> holdback / disbursement -> redistribution
        -> reputation update
```

It is a TypeScript app with:

- a pure, framework-independent **domain engine** under `src/engine/` and
  matching tests under `tests/`;
- a Vite + React **inspector UI** under `src/ui/` and `src/App.tsx` that
  exercises every engine path with reviewer-driven controls and a deterministic
  event log.

Treat this as a working blueprint, not production code. There are no smart
contracts, no fees, no real funds.

## What this prototype demonstrates

- A static project-beneficiary registry with five entries, each carrying
  pool-scoped reputation, claimant policy, and eligibility tags.
- A reference RPGF pool whose parameters mirror the table in
  `projects/rpgf/design.md` (15 drafted seats, K=1.25, epsilon_sigma=0.02,
  rho=0.3, EMA `sigma_ref` with alpha=0.05, etc.).
- Five seeded impact nominations covering the canonical edge cases:
  - one **clean** falsifiable nomination,
  - one **non-falsifiable** narrative nomination,
  - one **template-violating** nomination (no evidence, no measurable claim),
  - one **debunkable** nomination (mock on-chain date conflicts with claim),
  - one **overlapping/double-counting** nomination sharing a tag with the
    debunkable nomination.
- A curator pool of 16 curators with varied stake, three archetypes
  (`Honest`, `Lazy`, `Adversary`), and three commit-reveal behaviors
  (`CommitAndReveal`, `CommitOnly`, `NoShow`) that drive non-participation
  slashing.
- A coherence-game relevance round per nomination with seat-based draw-and-
  lock drafting, weighted mean and standard deviation, the low-dispersion
  guard at `sigma < epsilon_sigma`, graduated slashing
  (`p_i = clamp((|v_i - mu|/sigma - K)/K, 0, 1)`), non-participation slashing
  at `p_i = 1`, and smooth reward scaling
  `f_reward = rho + (1 - rho) * min(1, sigma / sigma_ref)` with
  `sigma_ref = max(epsilon_sigma, ema_sigma)`.
- Quorum-failure retry and `Unscored` terminal state on second failure.
- Provisional allocation
  `allocation_i = (relevanceScore_i / sum(relevanceScore_j)) * poolFundingBudget`
  with rollover when the denominator is zero.
- Holdback, three challenge types (`Debunking`, `NonFalsifiable`,
  `TemplateViolation`), counter-stake and tax computed from the spec
  (`counter-stake = max(0.01, 0.25 * b)`, `tax = 0.005 * b`), and
  anti-relitigation gate after `ChallengeFailed`.
- A deterministic DDR mock with three outcomes (`Debunked`,
  `ChallengeFailed`, `Timeout`).
- Per-spec disbursement at holdback expiry, debunked-share pro-rata
  redistribution to already-disbursed survivors, grace window after
  `ChallengeFailed` or `Timeout`, and registry-entry reputation updates
  (`+1` per surviving round, `-5` per debunked, decay 1 per epoch toward
  zero).

## How to install / run / test

Requires Node 20 or newer. The repo root package manager is irrelevant to
this prototype.

```bash
cd projects/rpgf/prototype
npm install
npm run typecheck    # TypeScript strict-mode check
npm run lint         # ESLint
npm test             # Vitest (currently 64 tests, all pure engine)
npm run build        # Type-check + vite build into dist/
npm run dev          # Vite dev server on http://localhost:5173
```

The dev server boots in under a second on a typical laptop.

The UI is a single page with two columns:

- **Left**: round timeline, pool profile, registry, curator pool, reputation
  ledger.
- **Right**: nominations (with assertions + evidence + state tags),
  relevance round details (mu, sigma, sigma_ref, slash and reward per
  curator), allocation vector with proportional bars, challenge filing form
  + DDR resolution buttons, full event log.

To exercise the full flow:

1. Click **1. Close submission** to advance from `Submission` to
   `Evaluation`.
2. Click **2. Run evaluation** to draft seats and run all relevance rounds.
   Provisional allocation will populate.
3. Click **3. Open holdback** to enter `Holdback`.
4. In the **Challenges + DDR mock** panel, pick a `Scored` nomination and
   click **File challenge**. The nomination becomes `Disputed`.
5. Click **4. Expire holdback**. Unchallenged nominations disburse; disputed
   nominations stay in escrow.
6. Click **Debunked** (or `ChallengeFailed`/`Timeout`) on the open challenge.
   On `Debunked`, the nomination's provisional share is redistributed
   pro-rata to disbursed nominations and registry-entry reputation drops by
   five.
7. Click **5. Advance grace tick** if any nomination is in the post-
   `ChallengeFailed` grace window, then **6. Close round**.
8. Use **Tick reputation epoch** in the header to apply the per-epoch decay.

The window object exposes the live engine state on `window.__rpgf` for
programmatic inspection from the browser console.

## What is mocked

This is a controlled lab, not an on-chain implementation. The following
deviate from a production deployment:

- **Registry governance**: the registry is hard-coded; there is no claimant-
  policy enforcement. Authors are matched to entries by id.
- **Pool creation**: a single pool is seeded with reference parameters; no
  permissionless creation, no template versioning.
- **Time**: there are no real waits. Every transition advances a phase tick
  triggered by an explicit button.
- **Randomness**: drafting uses a deterministic seeded mulberry32 PRNG keyed
  by `(poolId, nominationId, roundId, attempt, baseSeed)` rather than VRF.
- **DDR**: a manual deterministic resolver lets the reviewer pick one of
  three outcomes (`Debunked`, `ChallengeFailed`, `Timeout`).
- **Money**: every bond, stake, tax, reward, and disbursement is bookkeeping
  on in-memory ledgers. No transfers, no gas.
- **Appeals**: the relevance-round escalation layer described in the
  blueprint is intentionally not implemented in v1.
- **Pre-reveal leak reporting**: not modeled.
- **Curator exit cooldown**: not modeled. Deposits are static through a
  round.
- **Anti-relitigation**: enforced only as a UI gate that requires a "new
  evidence" string after `ChallengeFailed`; the prototype does not adjudicate
  legitimacy.

`PROTOTYPE_PROFILE.md` lists every deviation explicitly.

## How it maps to `projects/rpgf/design.md`

| Design section | Prototype location |
|---|---|
| Reference pool profile (parameters table) | `src/engine/seed.ts:REFERENCE_POOL_PARAMETERS` |
| Impact nomination structure | `src/engine/types.ts:ImpactNomination` and `src/engine/seed.ts` |
| Nomination state machine | `src/engine/nomination.ts` |
| Coherence-game relevance round | `src/engine/relevance.ts`, `src/engine/drafting.ts`, `src/engine/stats.ts` |
| Quorum failure retry, Unscored terminal | `src/engine/round.ts:evaluateNomination` |
| Provisional allocation | `src/engine/allocation.ts:computeProvisionalAllocation` |
| Holdback + disbursement + grace | `src/store.ts:expireHoldback`, `releaseGraced` |
| Challenge filing + payout matrix | `src/engine/challenge.ts` |
| DDR mock | `src/engine/ddr.ts` |
| Debunked redistribution pro-rata | `src/engine/allocation.ts:redistributeDebunkedShare` and `src/store.ts:resolveDDR` |
| Registry-entry reputation | `src/engine/reputation.ts` |

The core formulas come from `projects/truth-post/blueprint.md` Flow F (the
relevance-round computation steps 12-16) and the Reference RPGF Pool Profile
table in `projects/rpgf/design.md`. Specifically:

- `mu = sum(w_i * v_i) / sum(w_i)` over valid reveals (weighted mean).
- `sigma = sqrt(sum(w_i * (v_i - mu)^2) / sum(w_i))` (weighted standard
  deviation).
- `sigma_ref = max(epsilon_sigma, ema_sigma)` with EMA update
  `ema_sigma = alpha * sigma_round + (1 - alpha) * ema_sigma_prev`.
- `f_reward = rho + (1 - rho) * min(1, sigma / sigma_ref)`.
- `p_i = clamp((|v_i - mu| / sigma - K) / K, 0, 1)`.
- `delta_i = floor(p_i * w_i)`.

## Known limitations

- **Single-round runtime.** The prototype runs one funding round end-to-end.
  Multi-round behavior is exercised manually by clicking **Reset** or
  **Tick reputation epoch** between rounds.
- **No appeals.** A v2 should add the relevance-round escalation flow before
  any claim about formal correctness against the blueprint.
- **No private commitment.** Commit-reveal is modeled as a phase boundary,
  not via cryptographic commit hashes. The phase semantics are tracked but
  the privacy property is not provided.
- **Static curator behavior.** Curators have a fixed `intendedScore` and a
  fixed commit-reveal behavior per seed; they do not adapt to the current
  round's results, so the prototype cannot study adaptive collusion or
  learning dynamics.
- **No registry governance, no Sybil resistance.** The registry is a static
  list; the prototype assumes the upstream registry is honest. Sybil-aware
  drafting is out of scope.
- **No external evidence fetching.** Evidence URIs are display strings.
  Falsifiability flags are seeded directly on assertions.
- **No on-chain persistence.** State lives in React state and is reset on
  page reload or **Reset** click.

## Next steps toward production readiness

1. **Implement appeals.** Port the relevance-round escalation layer
   (Flow F-bis) from the blueprint, including escalation depth, appeal
   committee size multiplier, and appeal exposure tracking.
2. **Replace the seeded PRNG with a verifiable randomness source** (VRF or
   chain randomness) and add the iteration cap and snapshot block semantics
   from the blueprint.
3. **Move the engine behind a typed actor boundary.** Today the store
   imports engine functions directly. A production deployment would run the
   engine inside an EVM contract or rollup; the engine is already framework-
   independent so the boundary lives at `src/store.ts`.
4. **Wire up an actual DDR provider** (Kleros v1 or equivalent). The DDR
   mock in `src/engine/ddr.ts` is intentionally a one-function adapter; swap
   the resolver for a chain-call shim.
5. **Add multi-round tests** that exercise the reputation decay path,
   cross-round nomination eligibility gating, and registry rotation.
6. **Add cryptographic commit-reveal.** The current commit-reveal semantics
   live in phase tags only. A real deployment must store hash commitments
   and verify openings.
7. **Handle pre-reveal leak reporting.** Implement the leak commit and slash
   bounty path defined in the blueprint.
8. **Stress test with adversarial seeds.** The deterministic PRNG makes
   adversarial regression tests cheap; add fuzz tests for graduated slashing
   and redistribution edge cases.

## Files

```
projects/rpgf/prototype/
├── PROTOTYPE_PROFILE.md   <- frozen scope decisions, deviations from spec
├── README.md              <- this file
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── eslint.config.js
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── styles.css
│   ├── store.ts
│   ├── engine/
│   │   ├── index.ts
│   │   ├── types.ts
│   │   ├── prng.ts
│   │   ├── stats.ts
│   │   ├── drafting.ts
│   │   ├── relevance.ts
│   │   ├── nomination.ts
│   │   ├── allocation.ts
│   │   ├── reputation.ts
│   │   ├── challenge.ts
│   │   ├── ddr.ts
│   │   ├── round.ts
│   │   └── seed.ts
│   └── ui/
│       ├── shared.ts
│       ├── TimelinePanel.tsx
│       ├── PoolPanel.tsx
│       ├── RegistryPanel.tsx
│       ├── CuratorsPanel.tsx
│       ├── NominationsPanel.tsx
│       ├── RoundsPanel.tsx
│       ├── AllocationPanel.tsx
│       ├── ChallengesPanel.tsx
│       ├── ReputationPanel.tsx
│       └── LogPanel.tsx
└── tests/
    ├── stats.test.ts
    ├── drafting.test.ts
    ├── relevance.test.ts
    ├── nomination.test.ts
    ├── allocation.test.ts
    ├── reputation.test.ts
    ├── challenge.test.ts
    └── round.test.ts
```
