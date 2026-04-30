/**
 * Pure statistical helpers for the relevance round.
 *
 * Formulas come from `projects/truth-post/blueprint.md` Flow F (steps 12, 13)
 * and `projects/rpgf/design.md` Relevance Scoring section.
 */

export function weightedMean(weights: number[], values: number[]): number {
  if (weights.length !== values.length) {
    throw new Error("weightedMean: arrays must be the same length");
  }
  let totalWeight = 0;
  let weightedSum = 0;
  for (let i = 0; i < weights.length; i++) {
    const w = weights[i];
    const v = values[i];
    totalWeight += w;
    weightedSum += w * v;
  }
  if (totalWeight === 0) return 0;
  return weightedSum / totalWeight;
}

export function weightedStdDev(
  weights: number[],
  values: number[],
  mean?: number,
): number {
  if (weights.length !== values.length) {
    throw new Error("weightedStdDev: arrays must be the same length");
  }
  let totalWeight = 0;
  for (let i = 0; i < weights.length; i++) {
    totalWeight += weights[i];
  }
  if (totalWeight === 0) return 0;
  const mu = mean ?? weightedMean(weights, values);
  let weightedSqSum = 0;
  for (let i = 0; i < weights.length; i++) {
    const w = weights[i];
    const v = values[i];
    weightedSqSum += w * (v - mu) * (v - mu);
  }
  return Math.sqrt(weightedSqSum / totalWeight);
}

export function emaUpdate(
  previous: number,
  latest: number,
  alpha: number,
): number {
  return alpha * latest + (1 - alpha) * previous;
}

export function sigmaRef(epsilonSigma: number, emaSigma: number): number {
  return Math.max(epsilonSigma, emaSigma);
}

export function rewardFactor(
  sigma: number,
  rho: number,
  sigmaRefValue: number,
): number {
  if (sigmaRefValue <= 0) return rho;
  const ratio = Math.min(1, sigma / sigmaRefValue);
  return rho + (1 - rho) * ratio;
}

export function graduatedPenaltyFraction(
  value: number,
  mean: number,
  sigma: number,
  K: number,
): number {
  if (sigma <= 0) return 0;
  const distance = Math.abs(value - mean) / sigma;
  if (distance <= K) return 0;
  const raw = (distance - K) / K;
  if (raw <= 0) return 0;
  if (raw >= 1) return 1;
  return raw;
}
