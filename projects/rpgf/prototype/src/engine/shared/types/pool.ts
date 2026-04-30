
export type PoolPhase =
  | "Submission"
  | "Evaluation"
  | "Holdback"
  | "Settlement"
  | "Closed";

export interface PoolParameters {
  poolFundingBudget: number;
  curationBudgetReservePct: number;
  submissionBond: number;
  challengeCounterStakeMin: number;
  challengeCounterStakePct: number;
  challengeTaxPct: number;
  ddrFee: number;
  graceTicks: number;
  draftedSeats: number;
  minRevealQuorum: number;
  seatSizeL: number;
  coherenceK: number;
  epsilonSigma: number;
  rho: number;
  roundRewardFloor: number;
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
  curationBudget: number;
  fundingBudget: number;
  emaSigma: number;
  phase: PoolPhase;
  currentRoundId: string | null;
  budgetRolloverToken: number;
}
