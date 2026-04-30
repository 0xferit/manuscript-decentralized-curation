/**
 * Reputation-tick action: advance one decay epoch across the ledger.
 *
 * Triggered manually by the reviewer (UI) outside any specific phase.
 * Always increments the engine epoch counter.
 */

import { decayEpoch } from "@reputation";
import type { ControllerResult, EngineState } from "../types";
import { advanceTick } from "./_shared";

export function decayReputation(state: EngineState): ControllerResult {
  const next = advanceTick(state);
  const { ledger: reputation, updatedIds } = decayEpoch(
    next.reputation,
    next.pool.id,
    next.pool.parameters.reputationDecayPerEpoch,
    next.tick,
  );
  return {
    state: {
      ...next,
      epoch: next.epoch + 1,
      reputation,
    },
    events: [
      {
        tick: next.tick,
        category: "Reputation",
        message: `Epoch decay applied to ${updatedIds.length} entries (epoch ${next.epoch + 1})`,
      },
    ],
  };
}
