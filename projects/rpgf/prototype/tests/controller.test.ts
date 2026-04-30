/**
 * Boundary tests for the phase controller. The controller is pure, so these
 * tests run with no React, no DOM, no async.
 */

import { describe, expect, it } from "vitest";

import {
  makeCurators,
  makeNominations,
  makePool,
  makeRegistry,
  PROTOTYPE_BASE_SEED,
  PROTOTYPE_FUNDING_ROUND_ID,
} from "@bootstrap";
import { manualMockDDRResolver } from "@adjudication";
import { emptyLedger, ensureEntry } from "@reputation";
import {
  phaseController,
  type ControllerResult,
  type EngineState,
  type PhaseDeps,
} from "@lifecycle";

const DEFAULT_DEPS: PhaseDeps = {
  baseSeed: PROTOTYPE_BASE_SEED,
  ddr: manualMockDDRResolver,
};

function freshState(): EngineState {
  const pool = makePool();
  const registry = makeRegistry();
  const curators = makeCurators();
  const nominations = makeNominations();
  let reputation = emptyLedger();
  for (const e of registry) {
    reputation = ensureEntry(reputation, e.id, pool.id, e.reputation);
  }
  return {
    pool,
    registry,
    curators,
    nominations,
    challenges: [],
    rounds: [],
    fundingRound: {
      id: PROTOTYPE_FUNDING_ROUND_ID,
      poolId: pool.id,
      index: 1,
      phase: pool.phase,
      nominationIds: nominations.map((n) => n.id),
      holdbackEndsAtTick: null,
      finalizedAtTick: null,
      totalDisbursedToken: 0,
      rolloverToken: 0,
    },
    reputation,
    allocation: null,
    tick: 0,
    epoch: 0,
    evaluationRan: false,
    disbursementRan: false,
  };
}

function chain(
  state: EngineState,
  ...ops: Array<(s: EngineState) => ControllerResult>
): EngineState {
  let s = state;
  for (const op of ops) s = op(s).state;
  return s;
}

describe("phase controller", () => {
  it("close + run + holdback advances pool through phases", () => {
    const final = chain(
      freshState(),
      (s) => phaseController.closeSubmission(s),
      (s) => phaseController.runEvaluation(s, DEFAULT_DEPS),
      (s) => phaseController.enterHoldback(s),
    );
    expect(final.pool.phase).toBe("Holdback");
    expect(final.evaluationRan).toBe(true);
    expect(final.allocation).not.toBeNull();
  });

  it("evaluation produces deterministic mu under default seed", () => {
    const finalA = chain(
      freshState(),
      (s) => phaseController.closeSubmission(s),
      (s) => phaseController.runEvaluation(s, DEFAULT_DEPS),
    );
    const finalB = chain(
      freshState(),
      (s) => phaseController.closeSubmission(s),
      (s) => phaseController.runEvaluation(s, DEFAULT_DEPS),
    );
    const muA = finalA.nominations.map((n) => n.relevanceScore);
    const muB = finalB.nominations.map((n) => n.relevanceScore);
    expect(muA).toEqual(muB);
  });

  it("file challenge -> debunked redistributes to surviving disbursed", () => {
    const start = chain(
      freshState(),
      (s) => phaseController.closeSubmission(s),
      (s) => phaseController.runEvaluation(s, DEFAULT_DEPS),
      (s) => phaseController.enterHoldback(s),
    );
    const challengeTarget = "nom-modular-vm-bogus-deploy";
    const filed = phaseController
      .fileChallenge(start, {
        nominationId: challengeTarget,
        challengerId: "cur-cleo",
        reason: "Debunking",
      })
      .state;
    expect(filed.challenges).toHaveLength(1);
    const expired = phaseController.expireHoldback(filed).state;
    const challengeId = filed.challenges[0]!.id;
    const resolved = phaseController.resolveDDR(
      expired,
      challengeId,
      "Debunked",
      DEFAULT_DEPS,
    ).state;

    const debunked = resolved.nominations.find((n) => n.id === challengeTarget)!;
    expect(debunked.state).toBe("Debunked");
    const sumFinals = resolved.nominations.reduce(
      (a, n) => a + (n.finalShareToken ?? 0),
      0,
    );
    expect(sumFinals).toBeCloseTo(start.pool.fundingBudget, 6);
  });

  it("ChallengeFailed returns Scored with grace and disburses on grace tick", () => {
    const start = chain(
      freshState(),
      (s) => phaseController.closeSubmission(s),
      (s) => phaseController.runEvaluation(s, DEFAULT_DEPS),
      (s) => phaseController.enterHoldback(s),
    );
    const target = "nom-modular-vm-bogus-deploy";
    const filed = phaseController
      .fileChallenge(start, {
        nominationId: target,
        challengerId: "cur-cleo",
        reason: "Debunking",
      })
      .state;
    const expired = phaseController.expireHoldback(filed).state;
    const challengeId = filed.challenges[0]!.id;
    const resolved = phaseController.resolveDDR(
      expired,
      challengeId,
      "ChallengeFailed",
      DEFAULT_DEPS,
    ).state;
    const targetNom = resolved.nominations.find((n) => n.id === target)!;
    expect(targetNom.state).toBe("Scored");
    expect(targetNom.adjudicationOutcome).toBe("ChallengeFailed");
    expect(targetNom.graceEndsAtTick).not.toBeNull();
    const after = phaseController.releaseGraced(resolved).state;
    const final = after.nominations.find((n) => n.id === target)!;
    expect(final.state).toBe("Disbursed");
  });

  it("closeRound is blocked while challenges are pending", () => {
    const start = chain(
      freshState(),
      (s) => phaseController.closeSubmission(s),
      (s) => phaseController.runEvaluation(s, DEFAULT_DEPS),
      (s) => phaseController.enterHoldback(s),
    );
    const filed = phaseController
      .fileChallenge(start, {
        nominationId: "nom-modular-vm-bogus-deploy",
        challengerId: "cur-cleo",
        reason: "Debunking",
      })
      .state;
    const result = phaseController.closeRound(filed);
    expect(result.state.pool.phase).toBe("Holdback");
    expect(result.events.some((e) => e.message.includes("Cannot close"))).toBe(true);
  });

  it("decayReputation drives values toward zero", () => {
    const start = chain(
      freshState(),
      (s) => phaseController.closeSubmission(s),
      (s) => phaseController.runEvaluation(s, DEFAULT_DEPS),
      (s) => phaseController.enterHoldback(s),
      (s) => phaseController.expireHoldback(s),
    );
    const decayed = phaseController.decayReputation(start).state;
    for (const e of Object.values(decayed.reputation.byRegistryEntryId)) {
      expect(Math.abs(e.reputation)).toBeLessThanOrEqual(1);
    }
  });

  it("controller calls do not mutate input state", () => {
    const before = freshState();
    const beforeJson = JSON.stringify(before);
    phaseController.closeSubmission(before);
    expect(JSON.stringify(before)).toBe(beforeJson);
  });
});
