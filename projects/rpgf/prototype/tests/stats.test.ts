import { describe, expect, it } from "vitest";
import {
  emaUpdate,
  graduatedPenaltyFraction,
  rewardFactor,
  sigmaRef,
  weightedMean,
  weightedStdDev,
} from "../src/engine/curation/stats";

describe("weightedMean", () => {
  it("matches arithmetic mean when weights are equal", () => {
    expect(weightedMean([1, 1, 1], [0.2, 0.4, 0.6])).toBeCloseTo(0.4, 12);
  });

  it("biases toward the heavier weight", () => {
    expect(weightedMean([3, 1], [0.2, 1.0])).toBeCloseTo(0.4, 12);
  });

  it("returns 0 when total weight is zero", () => {
    expect(weightedMean([0, 0], [0.5, 0.7])).toBe(0);
  });

  it("rejects mismatched arrays", () => {
    expect(() => weightedMean([1, 2], [0.1])).toThrow();
  });
});

describe("weightedStdDev", () => {
  it("is zero when all values agree", () => {
    expect(weightedStdDev([2, 3, 5], [0.7, 0.7, 0.7])).toBeCloseTo(0, 12);
  });

  it("matches a closed-form weighted dispersion case", () => {
    const weights = [1, 1];
    const values = [0.2, 0.6];
    const mu = 0.4;
    const expected = Math.sqrt(((0.2 - mu) ** 2 + (0.6 - mu) ** 2) / 2);
    expect(weightedStdDev(weights, values, mu)).toBeCloseTo(expected, 12);
  });

  it("uses provided mean when given", () => {
    const weights = [1, 1];
    const values = [0.0, 1.0];
    expect(weightedStdDev(weights, values, 0.5)).toBeCloseTo(0.5, 12);
  });
});

describe("EMA sigma_ref", () => {
  it("bootstraps to epsilon when ema is zero", () => {
    expect(sigmaRef(0.02, 0)).toBe(0.02);
  });

  it("returns ema when above epsilon", () => {
    expect(sigmaRef(0.02, 0.05)).toBe(0.05);
  });

  it("EMA update converges toward latest", () => {
    let s = 0;
    for (let i = 0; i < 200; i++) s = emaUpdate(s, 0.1, 0.05);
    expect(s).toBeCloseTo(0.1, 4);
  });
});

describe("rewardFactor", () => {
  it("equals rho at sigma = 0", () => {
    expect(rewardFactor(0, 0.3, 0.05)).toBeCloseTo(0.3, 12);
  });

  it("equals 1.0 at sigma >= sigma_ref", () => {
    expect(rewardFactor(0.05, 0.3, 0.05)).toBeCloseTo(1.0, 12);
    expect(rewardFactor(0.5, 0.3, 0.05)).toBeCloseTo(1.0, 12);
  });

  it("transitions linearly between rho and 1.0", () => {
    expect(rewardFactor(0.025, 0.3, 0.05)).toBeCloseTo(0.65, 12);
  });
});

describe("graduatedPenaltyFraction", () => {
  it("returns 0 inside the coherence band", () => {
    expect(graduatedPenaltyFraction(0.6, 0.5, 0.1, 1.25)).toBe(0);
    expect(graduatedPenaltyFraction(0.625, 0.5, 0.1, 1.25)).toBe(0);
  });

  it("returns total loss at 2*K boundary", () => {
    const sigma = 0.1;
    const K = 1.25;
    const value = 0.5 + 2 * K * sigma;
    expect(graduatedPenaltyFraction(value, 0.5, sigma, K)).toBeCloseTo(1, 12);
  });

  it("scales linearly between K and 2K boundaries", () => {
    const sigma = 0.1;
    const K = 1.25;
    const value = 0.5 + 1.5 * K * sigma;
    expect(graduatedPenaltyFraction(value, 0.5, sigma, K)).toBeCloseTo(0.5, 12);
  });

  it("clamps to [0,1] beyond 2K", () => {
    expect(graduatedPenaltyFraction(2.0, 0.5, 0.1, 1.25)).toBe(1);
  });
});
