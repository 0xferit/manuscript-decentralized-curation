/**
 * Initial-engine-state factory for the prototype.
 *
 * The lifecycle module is the natural home for this composition because it
 * is the only module allowed to import from bootstrap, reputation, and the
 * adapter ports. Callers (UI, tests) build a starting `EngineState` and the
 * default `PhaseDeps` from here without reaching past the `@lifecycle`
 * barrel.
 */

import {
  PROTOTYPE_BASE_SEED,
  PROTOTYPE_FUNDING_ROUND_ID,
  makeCurators,
  makeNominations,
  makePool,
  makeRegistry,
} from "@bootstrap";
import { manualMockDDRResolver } from "@adjudication";
import { emptyLedger, ensureEntry } from "@reputation";

import type { PhaseDeps } from "./phases/_shared";
import type { EngineState } from "./types";

export function makeInitialEngineState(): EngineState {
  const pool = makePool();
  const registry = makeRegistry();
  const curators = makeCurators();
  const nominations = makeNominations();
  let reputation = emptyLedger();
  for (const entry of registry) {
    reputation = ensureEntry(reputation, entry.id, pool.id, entry.reputation);
  }
  return {
    pool,
    registry,
    curators,
    nominations,
    challenges: [],
    rounds: [],
    fundingRound: {
      id: PROTOTYPE_FUNDING_ROUND_ID,
      poolId: pool.id,
      index: 1,
      phase: pool.phase,
      nominationIds: nominations.map((n) => n.id),
      holdbackEndsAtTick: null,
      finalizedAtTick: null,
      totalDisbursedToken: 0,
      rolloverToken: 0,
    },
    reputation,
    allocation: null,
    tick: 0,
    epoch: 0,
    evaluationRan: false,
    disbursementRan: false,
  };
}

export function makeDefaultPhaseDeps(): PhaseDeps {
  return {
    baseSeed: PROTOTYPE_BASE_SEED,
    ddr: manualMockDDRResolver,
  };
}
