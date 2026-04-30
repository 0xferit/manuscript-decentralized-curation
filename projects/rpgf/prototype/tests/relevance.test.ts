import { describe, expect, it } from "vitest";
import { runRelevanceRound } from "@curation";
import { makeCurators, REFERENCE_POOL_PARAMETERS } from "@bootstrap";
import type { Curator } from "@shared/types";

function curators(overrides?: Partial<Curator>[]): Curator[] {
  const base = makeCurators();
  if (!overrides) return base;
  return base.map((c, i) => ({ ...c, ...(overrides[i] ?? {}) }));
}

describe("runRelevanceRound", () => {
  it("produces a finalized round under default seed", () => {
    const out = runRelevanceRound({
      roundId: "r1",
      poolId: "p",
      nominationId: "n1",
      fundingRoundId: "fr",
      attemptIndex: 0,
      seed: "seed-default",
      curators: curators(),
      parameters: REFERENCE_POOL_PARAMETERS,
      emaSigmaBefore: 0,
      curationBudgetBefore: 1,
      tick: 0,
    });
    expect(out.cancelled).toBe(false);
    expect(out.round.phase).toBe("Finalized");
    expect(out.round.meanScore).not.toBeNull();
    expect(out.round.totalSeatsLocked).toBe(REFERENCE_POOL_PARAMETERS.draftedSeats);
  });

  it("low-dispersion guard skips distance slashing but pays at rho * R", () => {
    const flat = curators().map((c) => ({
      ...c,
      intendedScore: 0.7,
      commitRevealBehavior: "CommitAndReveal" as const,
    }));
    const out = runRelevanceRound({
      roundId: "r-flat",
      poolId: "p",
      nominationId: "n",
      fundingRoundId: "fr",
      attemptIndex: 0,
      seed: "seed-flat",
      curators: flat,
      parameters: REFERENCE_POOL_PARAMETERS,
      emaSigmaBefore: 0,
      curationBudgetBefore: 1,
      tick: 0,
    });
    expect(out.round.distanceSlashingSkipped).toBe(true);
    for (const s of out.round.curatorStates) {
      if (s.revealed) expect(s.slashedToken).toBe(0);
    }
    expect(out.round.rewardFactor).toBeCloseTo(REFERENCE_POOL_PARAMETERS.rho, 12);
  });

  it("graduated slashing punishes outliers when sigma >= epsilon_sigma", () => {
    const c = curators().map((c) => ({
      ...c,
      commitRevealBehavior: "CommitAndReveal" as const,
    }));
    c[0]!.intendedScore = 0.0;
    c[1]!.intendedScore = 1.0;
    for (let i = 2; i < c.length; i++) c[i]!.intendedScore = 0.7;
    const out = runRelevanceRound({
      roundId: "r-out",
      poolId: "p",
      nominationId: "n",
      fundingRoundId: "fr",
      attemptIndex: 0,
      seed: "seed-out",
      curators: c,
      parameters: REFERENCE_POOL_PARAMETERS,
      emaSigmaBefore: 0,
      curationBudgetBefore: 1,
      tick: 0,
    });
    expect(out.round.distanceSlashingSkipped).toBe(false);
    const slashedTotal = out.round.curatorStates.reduce(
      (a, s) => a + s.slashedToken,
      0,
    );
    expect(slashedTotal).toBeGreaterThan(0);
  });

  it("returns QuorumFailure when too few reveals", () => {
    const c = curators().map((c) => ({
      ...c,
      commitRevealBehavior: "NoShow" as const,
    }));
    const out = runRelevanceRound({
      roundId: "r-quorum",
      poolId: "p",
      nominationId: "n",
      fundingRoundId: "fr",
      attemptIndex: 0,
      seed: "seed-quorum",
      curators: c,
      parameters: REFERENCE_POOL_PARAMETERS,
      emaSigmaBefore: 0,
      curationBudgetBefore: 1,
      tick: 0,
    });
    expect(out.cancelled).toBe(true);
    expect(out.cancellationReason).toBe("QuorumFailure");
  });

  it("non-participants are slashed at p_i = 1", () => {
    const c: Curator[] = curators().map((c) => ({
      ...c,
      commitRevealBehavior: "CommitAndReveal" as const,
    }));
    c[0]!.commitRevealBehavior = "NoShow";
    const out = runRelevanceRound({
      roundId: "r-np",
      poolId: "p",
      nominationId: "n",
      fundingRoundId: "fr",
      attemptIndex: 0,
      seed: "seed-np",
      curators: c,
      parameters: REFERENCE_POOL_PARAMETERS,
      emaSigmaBefore: 0,
      curationBudgetBefore: 1,
      tick: 0,
    });
    const c0 = out.round.curatorStates.find((s) => s.curatorId === "cur-anya");
    if (c0 && c0.seats > 0) {
      expect(c0.nonParticipation).toBe(true);
      expect(c0.penaltyFraction).toBe(1);
      expect(c0.slashedToken).toBeCloseTo(c0.weight, 12);
    }
  });

  it("drafting is reproducible across runs", () => {
    const a = runRelevanceRound({
      roundId: "r-rep",
      poolId: "p",
      nominationId: "n",
      fundingRoundId: "fr",
      attemptIndex: 0,
      seed: "seed-rep",
      curators: curators(),
      parameters: REFERENCE_POOL_PARAMETERS,
      emaSigmaBefore: 0,
      curationBudgetBefore: 1,
      tick: 0,
    });
    const b = runRelevanceRound({
      roundId: "r-rep",
      poolId: "p",
      nominationId: "n",
      fundingRoundId: "fr",
      attemptIndex: 0,
      seed: "seed-rep",
      curators: curators(),
      parameters: REFERENCE_POOL_PARAMETERS,
      emaSigmaBefore: 0,
      curationBudgetBefore: 1,
      tick: 0,
    });
    const seatsA = a.round.curatorStates
      .map((s) => `${s.curatorId}:${s.seats}`)
      .sort();
    const seatsB = b.round.curatorStates
      .map((s) => `${s.curatorId}:${s.seats}`)
      .sort();
    expect(seatsA).toEqual(seatsB);
  });
});
