import type { Pool, PoolParameters } from "@shared/types";
import {
  PROTOTYPE_FUNDING_ROUND_ID,
  PROTOTYPE_POOL_ID,
} from "./seed-config";

export const REFERENCE_POOL_PARAMETERS: PoolParameters = {
  poolFundingBudget: 100,
  curationBudgetReservePct: 0.05,
  submissionBond: 0.01,
  challengeCounterStakeMin: 0.01,
  challengeCounterStakePct: 0.25,
  challengeTaxPct: 0.005,
  ddrFee: 0,
  graceTicks: 1,
  draftedSeats: 15,
  minRevealQuorum: 5,
  seatSizeL: 0.01,
  coherenceK: 1.25,
  epsilonSigma: 0.02,
  rho: 0.3,
  roundRewardFloor: 0.01,
  sigmaRefAlpha: 0.05,
  reputationSurvivingDelta: 1,
  reputationDebunkedDelta: -5,
  reputationDecayPerEpoch: 1,
  minReputationGate: -5,
};

export function makePool(): Pool {
  const params = REFERENCE_POOL_PARAMETERS;
  const fundingBudget = params.poolFundingBudget;
  const curationBudget = fundingBudget * params.curationBudgetReservePct;
  return {
    id: PROTOTYPE_POOL_ID,
    name: "Ethereum Infrastructure (Reference RPGF Pool)",
    registryId: "registry-eth-infra",
    parameters: params,
    curationBudget,
    fundingBudget: fundingBudget - curationBudget,
    emaSigma: 0,
    phase: "Submission",
    currentRoundId: PROTOTYPE_FUNDING_ROUND_ID,
    budgetRolloverToken: 0,
  };
}
