/**
 * Curation module: internal types + re-export of shared types used inside.
 *
 * RelevanceRound, CuratorRoundState, RoundPhase live here because they are
 * Curation-internal data shapes. Other modules read them indirectly through
 * EngineState (composed in lifecycle).
 */

import type {
  CommitRevealBehavior,
} from "@shared/types";

export type {
  PoolParameters,
  Curator,
  CuratorIdentity,
  CommitRevealBehavior,
} from "@shared/types";

/**
 * Financial state of a curator. Owned by Curation: deposit at init from
 * Bootstrap, then mutated by Curation rounds via slashes and rewards.
 * Joined to `CuratorIdentity` by `id` at the UI boundary.
 */
export interface CuratorFinancialState {
  id: string;
  depositedToken: number;
  lockedToken: number;
  totalRewardsToken: number;
  totalSlashedToken: number;
}

export type RoundPhase =
  | "PreDraft"
  | "Drafted"
  | "Commit"
  | "Reveal"
  | "Finalized"
  | "Cancelled";

export interface CuratorRoundState {
  curatorId: string;
  seats: number;
  weight: number;
  intendedScore: number;
  behavior: CommitRevealBehavior;
  committed: boolean;
  revealed: boolean;
  revealedScore: number | null;
  penaltyFraction: number;
  slashedToken: number;
  rewardToken: number;
  withinBand: boolean;
  nonParticipation: boolean;
}

export interface RelevanceRound {
  id: string;
  poolId: string;
  nominationId: string;
  fundingRoundId: string;
  attemptIndex: number;
  seed: string;
  phase: RoundPhase;
  targetSeats: number;
  totalSeatsLocked: number;
  curatorStates: CuratorRoundState[];
  meanScore: number | null;
  stdDev: number | null;
  sigmaRef: number;
  rewardFactor: number;
  reservedRewardToken: number;
  distributedRewardToken: number;
  distanceSlashingSkipped: boolean;
  cancellationReason: "QuorumFailure" | "Underfunded" | null;
  finalizedAtTick: number | null;
}
