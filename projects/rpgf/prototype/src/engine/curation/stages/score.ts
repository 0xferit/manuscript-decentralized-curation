/**
 * Stage: scoring (mu, sigma, sigma_ref, reward factor).
 *
 * Boundary contract:
 *   input  = curator round states post commit-reveal + pool parameters + emaPrev
 *   output = ScoreOutcome (tagged union: quorumFailure | scored)
 *
 * The score stage owns the quorum check. Lower stages do not see quorum;
 * higher stages branch on the tag.
 */

import type { CuratorRoundState, PoolParameters } from "../types";
import { rewardFactor, sigmaRef as computeSigmaRef, weightedMean, weightedStdDev } from "../stats";

export interface ScoreInput {
  states: CuratorRoundState[];
  parameters: PoolParameters;
  emaSigmaBefore: number;
}

export type ScoreOutcome =
  | { kind: "quorumFailure"; validReveals: number; minQuorum: number }
  | {
      kind: "scored";
      mu: number;
      sigma: number;
      sigmaRef: number;
      fReward: number;
      distanceSlashingSkipped: boolean;
      validIndices: number[];
    };

export function score(input: ScoreInput): ScoreOutcome {
  const { states, parameters, emaSigmaBefore } = input;
  const validIndices: number[] = [];
  for (let i = 0; i < states.length; i++) {
    const s = states[i] as CuratorRoundState;
    if (s.revealed && s.revealedScore !== null) validIndices.push(i);
  }
  if (validIndices.length < parameters.minRevealQuorum) {
    return {
      kind: "quorumFailure",
      validReveals: validIndices.length,
      minQuorum: parameters.minRevealQuorum,
    };
  }
  const weights = validIndices.map((i) => (states[i] as CuratorRoundState).weight);
  const values = validIndices.map(
    (i) => (states[i] as CuratorRoundState).revealedScore as number,
  );
  const mu = weightedMean(weights, values);
  const sigma = weightedStdDev(weights, values, mu);
  const sigmaRefValue = computeSigmaRef(parameters.epsilonSigma, emaSigmaBefore);
  const fReward = rewardFactor(sigma, parameters.rho, sigmaRefValue);
  const distanceSlashingSkipped = sigma < parameters.epsilonSigma;
  return {
    kind: "scored",
    mu,
    sigma,
    sigmaRef: sigmaRefValue,
    fReward,
    distanceSlashingSkipped,
    validIndices,
  };
}
