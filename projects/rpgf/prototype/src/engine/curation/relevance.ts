/**
 * Relevance round orchestrator.
 *
 * Composes the pipeline: reserve -> draft -> commit-reveal -> score -> slash
 * -> reward -> EMA update. Each stage has its own module under `./stages/`
 * with its own io contract. This file does no math: it sequences stages.
 *
 * The commit-reveal simulator is injected so that production deployments can
 * swap in a real on-chain commit-reveal adapter without touching the round
 * logic.
 */

import { draftSeats } from "./drafting";
import { emaUpdate } from "./stats";
import {
  applyNonParticipationOnlySlashing,
  applySlashing,
  deterministicCommitRevealSimulator,
  distributeRoundReward,
  reserveRoundReward,
  score,
  settleCurationBudget,
  type CommitRevealSimulator,
} from "./stages";
import type {
  Curator,
  CuratorRoundState,
  PoolParameters,
  RelevanceRound,
} from "./types";

export interface RunRelevanceRoundInput {
  roundId: string;
  poolId: string;
  nominationId: string;
  fundingRoundId: string;
  attemptIndex: number;
  seed: string;
  curators: Curator[];
  parameters: PoolParameters;
  emaSigmaBefore: number;
  curationBudgetBefore: number;
  tick: number;
  commitRevealSimulator?: CommitRevealSimulator;
}

export interface CuratorRoundDelta {
  curatorId: string;
  deltaDeposit: number;
  deltaLocked: number;
  deltaReward: number;
  deltaSlashed: number;
}

export interface RelevanceRoundOutcome {
  round: RelevanceRound;
  curatorUpdates: CuratorRoundDelta[];
  emaSigmaAfter: number;
  curationBudgetAfter: number;
  cancelled: boolean;
  cancellationReason: RelevanceRound["cancellationReason"];
}

function buildBaseRound(args: {
  input: RunRelevanceRoundInput;
  reservedRewardToken: number;
  sigmaRef: number;
}): RelevanceRound {
  const { input, reservedRewardToken, sigmaRef } = args;
  return {
    id: input.roundId,
    poolId: input.poolId,
    nominationId: input.nominationId,
    fundingRoundId: input.fundingRoundId,
    attemptIndex: input.attemptIndex,
    seed: input.seed,
    phase: "PreDraft",
    targetSeats: input.parameters.draftedSeats,
    totalSeatsLocked: 0,
    curatorStates: [],
    meanScore: null,
    stdDev: null,
    sigmaRef,
    rewardFactor: 0,
    reservedRewardToken,
    distributedRewardToken: 0,
    distanceSlashingSkipped: false,
    cancellationReason: null,
    finalizedAtTick: null,
  };
}

function statesToUpdates(states: CuratorRoundState[]): CuratorRoundDelta[] {
  return states.map((s) => ({
    curatorId: s.curatorId,
    deltaDeposit: -s.slashedToken + s.rewardToken,
    deltaLocked: 0,
    deltaReward: s.rewardToken,
    deltaSlashed: s.slashedToken,
  }));
}

export function runRelevanceRound(
  input: RunRelevanceRoundInput,
): RelevanceRoundOutcome {
  const simulator = input.commitRevealSimulator ?? deterministicCommitRevealSimulator;

  // Stage 1: reserve round reward from curation budget.
  const reservation = reserveRoundReward({
    curationBudgetBefore: input.curationBudgetBefore,
    parameters: input.parameters,
  });
  if (reservation.kind === "underfunded") {
    return {
      round: {
        ...buildBaseRound({
          input,
          reservedRewardToken: 0,
          sigmaRef: Math.max(input.parameters.epsilonSigma, input.emaSigmaBefore),
        }),
        phase: "Cancelled",
        cancellationReason: "Underfunded",
      },
      curatorUpdates: [],
      emaSigmaAfter: input.emaSigmaBefore,
      curationBudgetAfter: input.curationBudgetBefore,
      cancelled: true,
      cancellationReason: "Underfunded",
    };
  }

  const baseRound = buildBaseRound({
    input,
    reservedRewardToken: reservation.reservedRewardToken,
    sigmaRef: Math.max(input.parameters.epsilonSigma, input.emaSigmaBefore),
  });

  // Stage 2: draft seats.
  const draft = draftSeats({
    curators: input.curators.map((c) => ({
      id: c.id,
      depositedToken: c.depositedToken,
      lockedToken: c.lockedToken,
    })),
    seatSizeL: input.parameters.seatSizeL,
    targetSeats: input.parameters.draftedSeats,
    seed: input.seed,
  });

  if (draft.totalSeatsLocked < input.parameters.draftedSeats) {
    return {
      round: {
        ...baseRound,
        phase: "Cancelled",
        cancellationReason: "Underfunded",
      },
      curatorUpdates: [],
      emaSigmaAfter: input.emaSigmaBefore,
      curationBudgetAfter: input.curationBudgetBefore,
      cancelled: true,
      cancellationReason: "Underfunded",
    };
  }

  // Stage 3: simulate commit-reveal.
  const draftedStates = simulator.simulate({
    draftedSeats: draft.seats,
    curators: input.curators,
    parameters: input.parameters,
  });

  // Stage 4: score (with quorum check).
  const scoreOutcome = score({
    states: draftedStates,
    parameters: input.parameters,
    emaSigmaBefore: input.emaSigmaBefore,
  });

  if (scoreOutcome.kind === "quorumFailure") {
    const onlyNonParticipation = applyNonParticipationOnlySlashing(draftedStates);
    return {
      round: {
        ...baseRound,
        phase: "Cancelled",
        cancellationReason: "QuorumFailure",
        curatorStates: onlyNonParticipation.states,
        totalSeatsLocked: draft.totalSeatsLocked,
      },
      curatorUpdates: statesToUpdates(onlyNonParticipation.states),
      emaSigmaAfter: input.emaSigmaBefore,
      curationBudgetAfter: input.curationBudgetBefore,
      cancelled: true,
      cancellationReason: "QuorumFailure",
    };
  }

  // Stage 5: slash (graduated + non-participation).
  const slashed = applySlashing({
    states: draftedStates,
    parameters: input.parameters,
    mu: scoreOutcome.mu,
    sigma: scoreOutcome.sigma,
    distanceSlashingSkipped: scoreOutcome.distanceSlashingSkipped,
  });

  // Stage 6: distribute reward.
  const rewarded = distributeRoundReward({
    states: slashed.states,
    totalSlashedFromValid: slashed.totalSlashedFromValid,
    fReward: scoreOutcome.fReward,
    reservedRewardToken: reservation.reservedRewardToken,
  });

  // Stage 7: settle curation budget; update EMA.
  const curationBudgetAfter = settleCurationBudget({
    reservedRewardToken: reservation.reservedRewardToken,
    fReward: scoreOutcome.fReward,
    curationBudgetAfterReserve: reservation.curationBudgetAfter,
  });
  const emaSigmaAfter = emaUpdate(
    input.emaSigmaBefore,
    scoreOutcome.sigma,
    input.parameters.sigmaRefAlpha,
  );

  return {
    round: {
      ...baseRound,
      phase: "Finalized",
      totalSeatsLocked: draft.totalSeatsLocked,
      curatorStates: rewarded.states,
      meanScore: scoreOutcome.mu,
      stdDev: scoreOutcome.sigma,
      sigmaRef: scoreOutcome.sigmaRef,
      rewardFactor: scoreOutcome.fReward,
      distributedRewardToken: rewarded.distributedRewardToken,
      distanceSlashingSkipped: scoreOutcome.distanceSlashingSkipped,
      finalizedAtTick: input.tick,
    },
    curatorUpdates: statesToUpdates(rewarded.states),
    emaSigmaAfter,
    curationBudgetAfter,
    cancelled: false,
    cancellationReason: null,
  };
}
