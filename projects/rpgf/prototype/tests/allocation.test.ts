import { describe, expect, it } from "vitest";
import {
  computeProvisionalAllocation,
  redistributeDebunkedShare,
} from "../src/engine/allocation";
import type { ImpactNomination } from "../src/engine/types";

function nom(
  id: string,
  state: ImpactNomination["state"],
  score: number | null,
  finalToken: number | null = null,
): ImpactNomination {
  return {
    id,
    poolId: "p",
    roundId: "r",
    registryEntryId: `reg-${id}`,
    authorAddress: "0xA",
    state,
    adjudicationOutcome: "Unchallenged",
    bondToken: 0.01,
    assertions: [],
    evidenceItems: [],
    createdAtPhaseTick: 0,
    lastUpdatedPhaseTick: 0,
    templateOk: true,
    doubleCountTagIds: [],
    relevanceScore: score,
    relevanceRoundId: "r",
    provisionalShareToken: null,
    finalShareToken: finalToken,
    graceEndsAtTick: null,
    challengeIds: [],
  };
}

describe("computeProvisionalAllocation", () => {
  it("computes proportional shares", () => {
    const result = computeProvisionalAllocation({
      poolId: "p",
      roundId: "r",
      poolFundingBudget: 100,
      nominations: [
        nom("a", "Scored", 0.8),
        nom("b", "Scored", 0.4),
        nom("c", "Scored", 0.2),
      ],
    });
    expect(result.denominator).toBeCloseTo(1.4, 12);
    const a = result.rows.find((r) => r.nominationId === "a")!;
    expect(a.share).toBeCloseTo(0.8 / 1.4, 12);
    expect(a.provisionalToken).toBeCloseTo((0.8 / 1.4) * 100, 12);
  });

  it("rolls over when denominator is zero", () => {
    const result = computeProvisionalAllocation({
      poolId: "p",
      roundId: "r",
      poolFundingBudget: 50,
      nominations: [nom("a", "Scored", 0), nom("b", "Scored", 0)],
    });
    expect(result.denominator).toBe(0);
    expect(result.rolloverToken).toBe(50);
    for (const row of result.rows) expect(row.provisionalToken).toBe(0);
  });

  it("excludes Retracted and Unscored from numerator", () => {
    const result = computeProvisionalAllocation({
      poolId: "p",
      roundId: "r",
      poolFundingBudget: 100,
      nominations: [
        nom("a", "Scored", 0.5),
        nom("b", "Retracted", 0.7),
        nom("c", "Unscored", null),
        nom("d", "Scored", 0.5),
      ],
    });
    expect(result.denominator).toBeCloseTo(1.0, 12);
    const a = result.rows.find((r) => r.nominationId === "a")!;
    expect(a.provisionalToken).toBeCloseTo(50, 12);
    const b = result.rows.find((r) => r.nominationId === "b")!;
    expect(b.provisionalToken).toBe(0);
  });
});

describe("redistributeDebunkedShare", () => {
  it("splits freed share pro-rata across surviving disbursed", () => {
    const result = redistributeDebunkedShare({
      freedShareToken: 30,
      survivingDisbursed: [
        nom("a", "Disbursed", 0.6, 30),
        nom("b", "Disbursed", 0.4, 20),
      ],
    });
    expect(result.topUps).toHaveLength(2);
    const topUpA = result.topUps.find((t) => t.nominationId === "a")!;
    expect(topUpA.extraToken).toBeCloseTo(18, 12);
    const topUpB = result.topUps.find((t) => t.nominationId === "b")!;
    expect(topUpB.extraToken).toBeCloseTo(12, 12);
    expect(result.rolloverToken).toBeCloseTo(0, 9);
  });

  it("rolls over freed share when no disbursed survive", () => {
    const result = redistributeDebunkedShare({
      freedShareToken: 25,
      survivingDisbursed: [],
    });
    expect(result.rolloverToken).toBe(25);
  });

  it("rolls over when total disbursed score is zero", () => {
    const result = redistributeDebunkedShare({
      freedShareToken: 25,
      survivingDisbursed: [nom("a", "Disbursed", 0, 0)],
    });
    expect(result.rolloverToken).toBe(25);
  });
});
