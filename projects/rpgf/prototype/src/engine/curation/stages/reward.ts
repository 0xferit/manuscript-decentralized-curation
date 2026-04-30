/**
 * Stage: reward distribution.
 *
 * Boundary contract: takes post-slashing curator states + reward-related
 * inputs, mutates a copy with per-curator rewards, and returns the
 * distributed total. Coherent set is `revealed && withinBand` (i.e.
 * p_i = 0 valid revealers). If the coherent set is empty, no reward is
 * distributed and the slashed pool stays in the pool budget.
 */

import type { CuratorRoundState } from "../types";

export interface RewardInput {
  states: CuratorRoundState[];
  totalSlashedFromValid: number;
  fReward: number;
  reservedRewardToken: number;
}

export interface RewardOutput {
  states: CuratorRoundState[];
  distributedRewardToken: number;
}

export function distributeRoundReward(input: RewardInput): RewardOutput {
  const { states, totalSlashedFromValid, fReward, reservedRewardToken } = input;
  const next = states.map((s) => ({ ...s }));
  const coherent = next.filter((s) => s.revealed && s.withinBand);
  const budget = totalSlashedFromValid + fReward * reservedRewardToken;
  let distributed = 0;
  if (coherent.length > 0) {
    const totalCoherentWeight = coherent.reduce((a, s) => a + s.weight, 0);
    if (totalCoherentWeight > 0) {
      for (const s of coherent) {
        const reward = (s.weight / totalCoherentWeight) * budget;
        s.rewardToken = reward;
        distributed += reward;
      }
    }
  }
  return { states: next, distributedRewardToken: distributed };
}
