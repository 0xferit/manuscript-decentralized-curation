import { describe, expect, it } from "vitest";

import {
  applyNonParticipationOnlySlashing,
  applySlashing,
  deterministicCommitRevealSimulator,
  distributeRoundReward,
  reserveRoundReward,
  score,
  settleCurationBudget,
} from "../src/engine/curation/stages";
import { REFERENCE_POOL_PARAMETERS, makeCurators } from "../src/engine/seed";
import { draftSeats } from "../src/engine/curation/drafting";
import type { CuratorRoundState } from "../src/engine/types";

const params = REFERENCE_POOL_PARAMETERS;

function makeStates(): CuratorRoundState[] {
  const curators = makeCurators().map((c) => ({
    ...c,
    commitRevealBehavior: "CommitAndReveal" as const,
  }));
  const draft = draftSeats({
    curators,
    seatSizeL: params.seatSizeL,
    targetSeats: params.draftedSeats,
    seed: "stage-seed",
  });
  return deterministicCommitRevealSimulator.simulate({
    draftedSeats: draft.seats,
    curators,
    parameters: params,
  });
}

describe("reserve stage", () => {
  it("reserves the round reward floor when budget is sufficient", () => {
    const r = reserveRoundReward({
      curationBudgetBefore: 5,
      parameters: params,
    });
    expect(r.kind).toBe("reserved");
    if (r.kind === "reserved") {
      expect(r.reservedRewardToken).toBe(params.roundRewardFloor);
      expect(r.curationBudgetAfter).toBeCloseTo(5 - params.roundRewardFloor, 12);
    }
  });

  it("returns underfunded when budget is short", () => {
    const r = reserveRoundReward({
      curationBudgetBefore: params.roundRewardFloor / 2,
      parameters: params,
    });
    expect(r.kind).toBe("underfunded");
  });

  it("settle returns undistributed share to budget", () => {
    const after = settleCurationBudget({
      reservedRewardToken: 1,
      fReward: 0.6,
      curationBudgetAfterReserve: 4,
    });
    expect(after).toBeCloseTo(4.4, 12);
  });
});

describe("commit-reveal simulator", () => {
  it("produces one state per curator with seats", () => {
    const states = makeStates();
    const seats = states.reduce((a, s) => a + s.seats, 0);
    expect(seats).toBe(params.draftedSeats);
  });

  it("CommitOnly behavior leaves nonParticipation true", () => {
    const curators = makeCurators().map((c) => ({
      ...c,
      commitRevealBehavior: "CommitOnly" as const,
    }));
    const draft = draftSeats({
      curators,
      seatSizeL: params.seatSizeL,
      targetSeats: params.draftedSeats,
      seed: "commit-only-seed",
    });
    const states = deterministicCommitRevealSimulator.simulate({
      draftedSeats: draft.seats,
      curators,
      parameters: params,
    });
    expect(states.every((s) => s.committed && !s.revealed)).toBe(true);
    expect(states.every((s) => s.nonParticipation)).toBe(true);
  });
});

describe("score stage", () => {
  it("returns scored outcome with mu and sigma", () => {
    const states = makeStates();
    const outcome = score({ states, parameters: params, emaSigmaBefore: 0 });
    expect(outcome.kind).toBe("scored");
    if (outcome.kind === "scored") {
      expect(outcome.mu).toBeGreaterThan(0);
      expect(outcome.sigma).toBeGreaterThanOrEqual(0);
    }
  });

  it("returns quorumFailure when reveals are below quorum", () => {
    const curators = makeCurators().map((c) => ({
      ...c,
      commitRevealBehavior: "NoShow" as const,
    }));
    const draft = draftSeats({
      curators,
      seatSizeL: params.seatSizeL,
      targetSeats: params.draftedSeats,
      seed: "quorum-test",
    });
    const states = deterministicCommitRevealSimulator.simulate({
      draftedSeats: draft.seats,
      curators,
      parameters: params,
    });
    const outcome = score({ states, parameters: params, emaSigmaBefore: 0 });
    expect(outcome.kind).toBe("quorumFailure");
  });
});

describe("slash stage", () => {
  it("applies graduated slashing on outliers", () => {
    const states = makeStates();
    states[0]!.revealedScore = 0.0;
    states[1]!.revealedScore = 1.0;
    const out = applySlashing({
      states,
      parameters: params,
      mu: 0.7,
      sigma: 0.05,
      distanceSlashingSkipped: false,
    });
    const slashed = out.states.filter((s) => s.slashedToken > 0);
    expect(slashed.length).toBeGreaterThan(0);
  });

  it("skip distance slashing under low-dispersion", () => {
    const states = makeStates();
    const out = applySlashing({
      states,
      parameters: params,
      mu: 0.7,
      sigma: 0.001,
      distanceSlashingSkipped: true,
    });
    for (const s of out.states.filter((s) => s.revealed)) {
      expect(s.slashedToken).toBe(0);
    }
  });

  it("non-participation only mode preserves valid revealers", () => {
    const states = makeStates();
    states[0]!.nonParticipation = true;
    states[0]!.revealed = false;
    const out = applyNonParticipationOnlySlashing(states);
    const nonPart = out.states.find((s) => s.curatorId === states[0]!.curatorId);
    expect(nonPart?.slashedToken).toBe(states[0]!.weight);
    const valid = out.states.find((s) => s.revealed);
    expect(valid?.slashedToken).toBe(0);
  });
});

describe("reward stage", () => {
  it("distributes reward proportional to coherent weights", () => {
    const states = makeStates().map((s) => ({
      ...s,
      withinBand: true,
      revealed: true,
    }));
    const out = distributeRoundReward({
      states,
      totalSlashedFromValid: 0,
      fReward: 1,
      reservedRewardToken: 1,
    });
    const totalRewards = out.states.reduce((a, s) => a + s.rewardToken, 0);
    expect(totalRewards).toBeCloseTo(1, 9);
    expect(out.distributedRewardToken).toBeCloseTo(1, 9);
  });

  it("distributes nothing when coherent set is empty", () => {
    const states = makeStates().map((s) => ({
      ...s,
      withinBand: false,
    }));
    const out = distributeRoundReward({
      states,
      totalSlashedFromValid: 0.05,
      fReward: 1,
      reservedRewardToken: 1,
    });
    expect(out.distributedRewardToken).toBe(0);
    for (const s of out.states) expect(s.rewardToken).toBe(0);
  });
});
