/**
 * Round orchestrator.
 *
 * Wires the relevance engine to a per-nomination evaluation loop. Handles
 * quorum-failure retry semantics: one initial round, one retry on quorum
 * failure, mark Unscored on second failure. Underfunded drafts are not
 * retried; the round is recorded and the nomination is left Submitted (the
 * orchestrator returns control to the caller, who can decide whether to
 * cancel).
 */

import { runRelevanceRound } from "./relevance";
import { deriveRoundSeed } from "./prng";
import type { CommitRevealSimulator } from "./stages";
import type {
  Curator,
  PoolParameters,
  RelevanceRound,
  Token,
} from "./types";

export interface EvaluateNominationInput {
  poolId: string;
  fundingRoundId: string;
  nominationId: string;
  curators: Curator[];
  parameters: PoolParameters;
  emaSigmaBefore: number;
  curationBudgetBefore: Token;
  tick: number;
  baseSeed: string;
  commitRevealSimulator?: CommitRevealSimulator;
}

export interface EvaluateNominationOutput {
  rounds: RelevanceRound[];
  curatorUpdates: Array<{
    curatorId: string;
    deltaDeposit: number;
    deltaLocked: number;
    deltaReward: number;
    deltaSlashed: number;
  }>;
  emaSigmaAfter: number;
  curationBudgetAfter: Token;
  finalRound: RelevanceRound | null;
  resolvedAs: "Scored" | "Unscored" | "Underfunded";
}

export function evaluateNomination(
  input: EvaluateNominationInput,
): EvaluateNominationOutput {
  const rounds: RelevanceRound[] = [];
  const allCuratorUpdates: EvaluateNominationOutput["curatorUpdates"] = [];
  let emaSigma = input.emaSigmaBefore;
  let curationBudget = input.curationBudgetBefore;
  let finalRound: RelevanceRound | null = null;
  let resolvedAs: EvaluateNominationOutput["resolvedAs"] = "Underfunded";

  for (let attempt = 0; attempt < 2; attempt++) {
    const roundId = `r-${input.nominationId}-a${attempt}`;
    const seed = deriveRoundSeed({
      poolId: input.poolId,
      nominationId: input.nominationId,
      roundId,
      attempt,
      baseSeed: input.baseSeed,
    });
    const outcome = runRelevanceRound({
      roundId,
      poolId: input.poolId,
      nominationId: input.nominationId,
      fundingRoundId: input.fundingRoundId,
      attemptIndex: attempt,
      seed,
      curators: input.curators,
      parameters: input.parameters,
      emaSigmaBefore: emaSigma,
      curationBudgetBefore: curationBudget,
      tick: input.tick,
      commitRevealSimulator: input.commitRevealSimulator,
    });
    rounds.push(outcome.round);
    allCuratorUpdates.push(...outcome.curatorUpdates);
    emaSigma = outcome.emaSigmaAfter;
    curationBudget = outcome.curationBudgetAfter;

    if (!outcome.cancelled) {
      finalRound = outcome.round;
      resolvedAs = "Scored";
      break;
    }
    if (outcome.cancellationReason === "Underfunded") {
      resolvedAs = "Underfunded";
      break;
    }
    if (outcome.cancellationReason === "QuorumFailure" && attempt === 1) {
      resolvedAs = "Unscored";
    }
  }

  return {
    rounds,
    curatorUpdates: allCuratorUpdates,
    emaSigmaAfter: emaSigma,
    curationBudgetAfter: curationBudget,
    finalRound,
    resolvedAs,
  };
}
