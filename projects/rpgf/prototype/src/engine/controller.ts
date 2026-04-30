/**
 * Phase controller: pure (state, args, deps) -> { state, events } facades for
 * every reviewer-driven action. The store wraps each function with React's
 * setState; tests can drive the same functions directly with no UI.
 *
 * Invariants:
 *   - The controller never mutates its inputs; every helper returns a new
 *     state object. Reputation updates use the immutable ledger ops.
 *   - The controller is the only place where multi-step transitions live.
 *     Engine atoms (state machine, allocation, ddr, reputation) stay focused.
 *   - The controller never imports React or any UI module.
 *   - DDR and commit-reveal simulation are injected via `PhaseDeps` so
 *     production can swap them.
 */

import {
  computeProvisionalAllocation,
  redistributeDebunkedShare,
} from "./allocation";
import {
  challengePayoutFor,
  fileChallenge as buildChallenge,
} from "./challenge";
import type { ControllerResult, EngineState, LogEvent } from "./controllerTypes";
import { manualMockDDRResolver, type DDRResolver } from "./ddr";
import {
  amendDuringSubmission,
  markChallengeFailed,
  markDebunked,
  markDisbursed,
  markDisputed,
  markScored,
  markUnscored,
  retractNomination as retractNom,
  topUpFinalShare,
  type AmendInput,
} from "./nomination";
import { evaluateNomination } from "./curation/round";
import {
  applyDebunkPenalty,
  awardSurvivingRound,
  decayEpoch,
} from "./reputation";
import type { CommitRevealSimulator } from "./curation/stages";
import type {
  ChallengeReason,
  DDROutcome,
  ImpactNomination,
} from "./types";

export interface PhaseDeps {
  baseSeed: string;
  ddr?: DDRResolver;
  commitRevealSimulator?: CommitRevealSimulator;
}

function tick(state: EngineState): EngineState {
  return { ...state, tick: state.tick + 1 };
}

function nomById(state: EngineState, id: string): ImpactNomination | undefined {
  return state.nominations.find((n) => n.id === id);
}

function replaceNomination(
  state: EngineState,
  next: ImpactNomination,
): EngineState {
  return {
    ...state,
    nominations: state.nominations.map((n) => (n.id === next.id ? next : n)),
  };
}

export function amendNomination(
  state: EngineState,
  id: string,
  patch: AmendInput,
): ControllerResult {
  const nom = nomById(state, id);
  if (!nom) return { state, events: [] };
  const next = tick(state);
  const updated = amendDuringSubmission(nom, patch, next.tick);
  return {
    state: replaceNomination(next, updated),
    events: [
      { tick: next.tick, category: "Author", message: `Amended ${id}` },
    ],
  };
}

export function retractNominationAction(
  state: EngineState,
  id: string,
): ControllerResult {
  const nom = nomById(state, id);
  if (!nom) return { state, events: [] };
  const next = tick(state);
  const updated = retractNom(nom, next.tick);
  return {
    state: replaceNomination(next, updated),
    events: [
      { tick: next.tick, category: "Author", message: `Retracted ${id}` },
    ],
  };
}

export function closeSubmission(state: EngineState): ControllerResult {
  if (state.pool.phase !== "Submission") {
    return {
      state,
      events: [
        {
          tick: state.tick,
          category: "Phase",
          message: `closeSubmission ignored: phase is ${state.pool.phase}.`,
        },
      ],
    };
  }
  const next = tick(state);
  return {
    state: {
      ...next,
      pool: { ...next.pool, phase: "Evaluation" },
      fundingRound: { ...next.fundingRound, phase: "Evaluation" },
    },
    events: [
      { tick: next.tick, category: "Tick", message: "Submission window closed" },
      {
        tick: next.tick,
        category: "Phase",
        message: "Phase: Submission -> Evaluation",
      },
    ],
  };
}

export function runEvaluation(
  state: EngineState,
  deps: PhaseDeps,
): ControllerResult {
  if (state.pool.phase !== "Evaluation" || state.evaluationRan) {
    return { state, events: [] };
  }
  const next = tick(state);
  let curators = next.curators;
  let emaSigma = next.pool.emaSigma;
  let curationBudget = next.pool.curationBudget;
  let nominations = next.nominations;
  const allRounds = [...next.rounds];
  const events: LogEvent[] = [];

  const submitted = next.nominations.filter((n) => n.state === "Submitted");

  for (const nom of submitted) {
    const result = evaluateNomination({
      poolId: next.pool.id,
      fundingRoundId: next.fundingRound.id,
      nominationId: nom.id,
      curators,
      parameters: next.pool.parameters,
      emaSigmaBefore: emaSigma,
      curationBudgetBefore: curationBudget,
      tick: next.tick,
      baseSeed: deps.baseSeed,
      commitRevealSimulator: deps.commitRevealSimulator,
    });
    curators = applyCuratorUpdates(curators, result.curatorUpdates);
    emaSigma = result.emaSigmaAfter;
    curationBudget = result.curationBudgetAfter;
    allRounds.push(...result.rounds);

    if (result.resolvedAs === "Scored" && result.finalRound) {
      nominations = nominations.map((n) =>
        n.id === nom.id
          ? markScored(n, {
              relevanceScore: result.finalRound!.meanScore ?? 0,
              relevanceRoundId: result.finalRound!.id,
              tick: next.tick,
            })
          : n,
      );
      events.push({
        tick: next.tick,
        category: "Engine",
        message: `Scored ${nom.id}: mu=${(result.finalRound.meanScore ?? 0).toFixed(3)}, sigma=${(result.finalRound.stdDev ?? 0).toFixed(3)}, low-disp=${result.finalRound.distanceSlashingSkipped}`,
      });
    } else if (result.resolvedAs === "Unscored") {
      nominations = nominations.map((n) =>
        n.id === nom.id ? markUnscored(n, next.tick) : n,
      );
      events.push({
        tick: next.tick,
        category: "Engine",
        message: `Unscored ${nom.id}: quorum failure on retry`,
      });
    } else {
      events.push({
        tick: next.tick,
        category: "Engine",
        message: `Underfunded ${nom.id}: round could not reserve full reward floor`,
      });
    }
  }

  const allocation = computeProvisionalAllocation({
    poolId: next.pool.id,
    roundId: next.fundingRound.id,
    poolFundingBudget: next.pool.fundingBudget,
    nominations,
  });
  nominations = nominations.map((n) => {
    const row = allocation.rows.find((r) => r.nominationId === n.id);
    if (!row || n.state !== "Scored") return n;
    return { ...n, provisionalShareToken: row.provisionalToken };
  });

  events.unshift({
    tick: next.tick,
    category: "Phase",
    message: "Evaluation period executed",
  });
  events.push({
    tick: next.tick,
    category: "Engine",
    message: `Provisional allocation: denominator=${allocation.denominator.toFixed(3)}, rollover=${allocation.rolloverToken.toFixed(4)}`,
  });

  return {
    state: {
      ...next,
      curators,
      rounds: allRounds,
      nominations,
      pool: { ...next.pool, emaSigma, curationBudget },
      allocation,
      evaluationRan: true,
    },
    events,
  };
}

export function enterHoldback(state: EngineState): ControllerResult {
  if (state.pool.phase !== "Evaluation" || !state.evaluationRan) {
    return { state, events: [] };
  }
  const next = tick(state);
  return {
    state: {
      ...next,
      pool: { ...next.pool, phase: "Holdback" },
      fundingRound: {
        ...next.fundingRound,
        phase: "Holdback",
        holdbackEndsAtTick: next.tick + 1,
      },
    },
    events: [
      { tick: next.tick, category: "Tick", message: "Holdback opened" },
      {
        tick: next.tick,
        category: "Phase",
        message: "Phase: Evaluation -> Holdback",
      },
    ],
  };
}

export interface FileChallengeArgs {
  nominationId: string;
  challengerId: string;
  reason: ChallengeReason;
  newEvidenceNote?: string | null;
}

export function fileChallengeAction(
  state: EngineState,
  args: FileChallengeArgs,
): ControllerResult {
  const nomination = nomById(state, args.nominationId);
  if (!nomination) return { state, events: [] };
  const next = tick(state);
  try {
    const challenge = buildChallenge({
      id: `c-${state.challenges.length + 1}-${args.nominationId}`,
      nomination,
      challengerId: args.challengerId,
      reason: args.reason,
      newEvidenceNote: args.newEvidenceNote ?? null,
      parameters: next.pool.parameters,
      tick: next.tick,
    });
    let nominations = next.nominations;
    if (nomination.state === "Scored") {
      nominations = nominations.map((n) =>
        n.id === nomination.id ? markDisputed(n, next.tick) : n,
      );
    }
    nominations = nominations.map((n) =>
      n.id === nomination.id
        ? { ...n, challengeIds: [...n.challengeIds, challenge.id] }
        : n,
    );
    return {
      state: {
        ...next,
        challenges: [...next.challenges, challenge],
        nominations,
        pool: {
          ...next.pool,
          fundingBudget: next.pool.fundingBudget + challenge.taxToken,
        },
      },
      events: [
        {
          tick: next.tick,
          category: "Challenge",
          message: `Filed ${args.reason} challenge ${challenge.id} on ${args.nominationId} by ${args.challengerId}; counter-stake=${challenge.counterStakeToken.toFixed(4)}, tax=${challenge.taxToken.toFixed(4)}`,
        },
      ],
    };
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    return {
      state: next,
      events: [
        {
          tick: next.tick,
          category: "Challenge",
          message: `Filing rejected for ${args.nominationId}: ${message}`,
        },
      ],
    };
  }
}

export function resolveDDR(
  state: EngineState,
  challengeId: string,
  outcome: DDROutcome,
  deps: PhaseDeps,
  jurorNote: string | null = null,
): ControllerResult {
  const challenge = state.challenges.find((c) => c.id === challengeId);
  if (!challenge || challenge.status !== "Pending") {
    return { state, events: [] };
  }
  const ddr = deps.ddr ?? manualMockDDRResolver;
  const next = tick(state);
  const { challenge: resolved } = ddr.resolve({
    challenge,
    ruling: outcome,
    tick: next.tick,
    jurorNote,
  });
  const challenges = next.challenges.map((c) => (c.id === challengeId ? resolved : c));
  const nomination = next.nominations.find((n) => n.id === resolved.nominationId);
  if (!nomination) return { state: next, events: [] };

  const events: LogEvent[] = [];
  let nominations = next.nominations;
  let reputation = next.reputation;
  let allocation = next.allocation;

  if (outcome === "Debunked") {
    nominations = nominations.map((n) =>
      n.id === nomination.id ? markDebunked(n, next.tick) : n,
    );
    reputation = applyDebunkPenalty(
      reputation,
      nomination.registryEntryId,
      next.pool.id,
      next.pool.parameters.reputationDebunkedDelta,
      next.tick,
      `DDR debunked nomination ${nomination.id}`,
    );
    const freed = nomination.provisionalShareToken ?? 0;
    const survivingDisbursed = nominations.filter(
      (n) =>
        n.state === "Disbursed" &&
        n.id !== nomination.id &&
        n.relevanceScore !== null,
    );
    const redistribution = redistributeDebunkedShare({
      freedShareToken: freed,
      survivingDisbursed,
    });
    nominations = nominations.map((n) => {
      const tu = redistribution.topUps.find((t) => t.nominationId === n.id);
      if (!tu) return n;
      return topUpFinalShare(n, next.tick, tu.extraToken);
    });
    if (allocation) {
      allocation = {
        ...allocation,
        rolloverToken: allocation.rolloverToken + redistribution.rolloverToken,
      };
    }
    events.push({
      tick: next.tick,
      category: "DDR",
      message: `Debunked ${nomination.id}: redistributed ${(freed - redistribution.rolloverToken).toFixed(4)} token across ${redistribution.topUps.length} disbursed nominations; rollover ${redistribution.rolloverToken.toFixed(4)} token`,
    });
    events.push({
      tick: next.tick,
      category: "Reputation",
      message: `Registry ${nomination.registryEntryId} reputation -= ${Math.abs(next.pool.parameters.reputationDebunkedDelta)}`,
    });
  } else {
    nominations = nominations.map((n) =>
      n.id === nomination.id
        ? markChallengeFailed(n, next.tick, next.pool.parameters.graceTicks)
        : n,
    );
    events.push({
      tick: next.tick,
      category: "DDR",
      message: `${outcome} on ${nomination.id}: nomination returns to Scored with grace until tick ${next.tick + next.pool.parameters.graceTicks}`,
    });
  }

  const payout = challengePayoutFor(outcome, resolved);
  events.push({
    tick: next.tick,
    category: "DDR",
    message: `Payout: bond -> ${payout.authorBondTo}, counter-stake -> ${payout.counterStakeTo}, tax retained ${payout.taxToPool.toFixed(4)} in pool`,
  });

  return {
    state: { ...next, challenges, nominations, reputation, allocation },
    events,
  };
}

export function expireHoldback(state: EngineState): ControllerResult {
  if (state.pool.phase !== "Holdback") {
    return { state, events: [] };
  }
  const next = tick(state);
  const events: LogEvent[] = [
    { tick: next.tick, category: "Phase", message: "Phase: Holdback -> Settlement" },
  ];
  let reputation = next.reputation;
  let totalDisbursed = next.fundingRound.totalDisbursedToken;
  const nominations: ImpactNomination[] = [];

  for (const n of next.nominations) {
    if (n.state === "Scored" && n.adjudicationOutcome === "Unchallenged") {
      const provisional = n.provisionalShareToken ?? 0;
      const disbursed = markDisbursed(n, next.tick, provisional);
      nominations.push(disbursed);
      totalDisbursed += provisional;
      events.push({
        tick: next.tick,
        category: "Disbursement",
        message: `Disbursed ${provisional.toFixed(4)} token to ${n.registryEntryId} via ${n.id}`,
      });
      reputation = awardSurvivingRound(
        reputation,
        n.registryEntryId,
        next.pool.id,
        next.pool.parameters.reputationSurvivingDelta,
        next.tick,
        `Survived round ${next.fundingRound.id}`,
      );
      events.push({
        tick: next.tick,
        category: "Reputation",
        message: `Registry ${n.registryEntryId} reputation += ${next.pool.parameters.reputationSurvivingDelta}`,
      });
    } else {
      nominations.push(n);
    }
  }

  return {
    state: {
      ...next,
      nominations,
      reputation,
      disbursementRan: true,
      pool: { ...next.pool, phase: "Settlement" },
      fundingRound: {
        ...next.fundingRound,
        phase: "Settlement",
        totalDisbursedToken: totalDisbursed,
      },
    },
    events,
  };
}

export function releaseGraced(state: EngineState): ControllerResult {
  if (state.pool.phase !== "Settlement") {
    return { state, events: [] };
  }
  const next = tick(state);
  const events: LogEvent[] = [
    {
      tick: next.tick,
      category: "Phase",
      message: `Grace tick advanced (now tick ${next.tick})`,
    },
  ];
  let reputation = next.reputation;
  let totalDisbursed = next.fundingRound.totalDisbursedToken;

  const nominations = next.nominations.map((n) => {
    const noOpenChallenge = !next.challenges.some(
      (c) => c.nominationId === n.id && c.status === "Pending",
    );
    if (
      n.state === "Scored" &&
      n.adjudicationOutcome === "ChallengeFailed" &&
      n.graceEndsAtTick !== null &&
      next.tick >= n.graceEndsAtTick &&
      noOpenChallenge
    ) {
      const provisional = n.provisionalShareToken ?? 0;
      totalDisbursed += provisional;
      events.push({
        tick: next.tick,
        category: "Disbursement",
        message: `Grace expired for ${n.id}: disbursed ${provisional.toFixed(4)} token`,
      });
      reputation = awardSurvivingRound(
        reputation,
        n.registryEntryId,
        next.pool.id,
        next.pool.parameters.reputationSurvivingDelta,
        next.tick,
        `Survived round (grace) ${next.fundingRound.id}`,
      );
      return markDisbursed(n, next.tick, provisional);
    }
    return n;
  });

  return {
    state: {
      ...next,
      nominations,
      reputation,
      fundingRound: {
        ...next.fundingRound,
        totalDisbursedToken: totalDisbursed,
      },
    },
    events,
  };
}

export function closeRound(state: EngineState): ControllerResult {
  const stillOpen = state.challenges.some((c) => c.status === "Pending");
  if (stillOpen) {
    return {
      state,
      events: [
        {
          tick: state.tick,
          category: "Phase",
          message: "Cannot close round: pending DDR challenges remain.",
        },
      ],
    };
  }
  const next = tick(state);
  return {
    state: {
      ...next,
      pool: { ...next.pool, phase: "Closed" },
      fundingRound: {
        ...next.fundingRound,
        phase: "Closed",
        finalizedAtTick: next.tick,
      },
    },
    events: [{ tick: next.tick, category: "Phase", message: "Round closed" }],
  };
}

export function decayReputation(state: EngineState): ControllerResult {
  const next = tick(state);
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

function applyCuratorUpdates(
  curators: EngineState["curators"],
  updates: Array<{
    curatorId: string;
    deltaDeposit: number;
    deltaLocked: number;
    deltaReward: number;
    deltaSlashed: number;
  }>,
): EngineState["curators"] {
  if (updates.length === 0) return curators;
  const map = new Map(curators.map((c) => [c.id, { ...c }]));
  for (const u of updates) {
    const c = map.get(u.curatorId);
    if (!c) continue;
    c.depositedToken = Math.max(0, c.depositedToken + u.deltaDeposit);
    c.lockedToken = Math.max(0, c.lockedToken + u.deltaLocked);
    c.totalRewardsToken += u.deltaReward;
    c.totalSlashedToken += u.deltaSlashed;
    map.set(u.curatorId, c);
  }
  return Array.from(map.values());
}

export const phaseController = {
  amendNomination,
  retractNomination: retractNominationAction,
  closeSubmission,
  runEvaluation,
  enterHoldback,
  fileChallenge: fileChallengeAction,
  resolveDDR,
  expireHoldback,
  releaseGraced,
  closeRound,
  decayReputation,
};

export type PhaseController = typeof phaseController;

