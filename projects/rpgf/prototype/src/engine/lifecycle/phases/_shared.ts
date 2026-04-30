/**
 * Shared helpers for phase functions.
 *
 * Each phase action is `(state, args, deps) -> { state, events }`. All
 * helpers below are private to the lifecycle module.
 */

import type { DDRResolver } from "@adjudication";
import type { CommitRevealSimulator } from "@curation";
import type { ImpactNomination } from "@shared/types";
import type { EngineState } from "../types";

export interface PhaseDeps {
  baseSeed: string;
  ddr?: DDRResolver;
  commitRevealSimulator?: CommitRevealSimulator;
}

export function advanceTick(state: EngineState): EngineState {
  return { ...state, tick: state.tick + 1 };
}

export function nomById(
  state: EngineState,
  id: string,
): ImpactNomination | undefined {
  return state.nominations.find((n) => n.id === id);
}

export function replaceNomination(
  state: EngineState,
  next: ImpactNomination,
): EngineState {
  return {
    ...state,
    nominations: state.nominations.map((n) => (n.id === next.id ? next : n)),
  };
}

export function applyCuratorUpdates(
  curators: EngineState["curators"],
  updates: Array<{
    curatorId: string;
    deltaDeposit: number;
    deltaLocked: number;
    deltaReward: number;
    deltaSlashed: number;
  }>,
): EngineState["curators"] {
  if (updates.length === 0) return curators;
  const map = new Map(curators.map((c) => [c.id, { ...c }]));
  for (const u of updates) {
    const c = map.get(u.curatorId);
    if (!c) continue;
    c.depositedToken = Math.max(0, c.depositedToken + u.deltaDeposit);
    c.lockedToken = Math.max(0, c.lockedToken + u.deltaLocked);
    c.totalRewardsToken += u.deltaReward;
    c.totalSlashedToken += u.deltaSlashed;
    map.set(u.curatorId, c);
  }
  return Array.from(map.values());
}
