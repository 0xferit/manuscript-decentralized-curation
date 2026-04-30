import type { Token } from "./token";

export type PoolPhase =
  | "Submission"
  | "Evaluation"
  | "Holdback"
  | "Settlement"
  | "Closed";

export interface PoolParameters {
  poolFundingBudget: Token;
  curationBudgetReservePct: number;
  submissionBond: Token;
  challengeCounterStakeMin: Token;
  challengeCounterStakePct: number;
  challengeTaxPct: number;
  ddrFee: Token;
  graceTicks: number;
  draftedSeats: number;
  minRevealQuorum: number;
  seatSizeL: Token;
  coherenceK: number;
  epsilonSigma: number;
  rho: number;
  roundRewardFloor: Token;
  sigmaRefAlpha: number;
  reputationSurvivingDelta: number;
  reputationDebunkedDelta: number;
  reputationDecayPerEpoch: number;
  minReputationGate: number;
}

/**
 * Pool envelope kept whole for backwards compatibility during the
 * incremental refactor. Future steps split it into PoolMeta (immutable
 * Bootstrap-owned) plus per-module slice fields (curationBudget + emaSigma
 * to Curation; fundingBudget + budgetRolloverToken to Allocation; phase
 * to Lifecycle).
 */
export interface Pool {
  id: string;
  name: string;
  registryId: string;
  parameters: PoolParameters;
  curationBudget: Token;
  fundingBudget: Token;
  emaSigma: number;
  phase: PoolPhase;
  currentRoundId: string | null;
  budgetRolloverToken: Token;
}
