/**
 * Stage: reward reservation.
 *
 * Boundary contract: reserve one `roundRewardFloor` from the pool's curation
 * budget. Returns either a successful reservation with the new budget, or a
 * failure when the budget is short. No state mutation; pure transformation.
 */

import type { PoolParameters } from "../types";

export type ReserveOutcome =
  | {
      kind: "reserved";
      reservedRewardToken: number;
      curationBudgetAfter: number;
    }
  | {
      kind: "underfunded";
      requiredToken: number;
      curationBudgetBefore: number;
    };

export function reserveRoundReward(input: {
  curationBudgetBefore: number;
  parameters: PoolParameters;
}): ReserveOutcome {
  const { curationBudgetBefore, parameters } = input;
  const required = parameters.roundRewardFloor;
  if (curationBudgetBefore < required) {
    return {
      kind: "underfunded",
      requiredToken: required,
      curationBudgetBefore,
    };
  }
  return {
    kind: "reserved",
    reservedRewardToken: required,
    curationBudgetAfter: curationBudgetBefore - required,
  };
}

/**
 * Compute the curation-budget restitution after a finalized round. The
 * undistributed portion (`(1 - fReward) * R`) returns to the pool budget.
 */
export function settleCurationBudget(input: {
  reservedRewardToken: number;
  fReward: number;
  curationBudgetAfterReserve: number;
}): number {
  const undistributed = input.reservedRewardToken * (1 - input.fReward);
  return input.curationBudgetAfterReserve + undistributed;
}
