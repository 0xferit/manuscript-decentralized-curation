/**
 * Curation module: internal types + re-export of shared types used inside.
 *
 * RelevanceRound, CuratorRoundState, RoundPhase live here because they are
 * Curation-internal data shapes. Other modules read them indirectly through
 * EngineState (composed in lifecycle).
 */

import type {
  CommitRevealBehavior,
  Token,
} from "@shared/types";

export type {
  Token,
  PoolParameters,
  Curator,
  CommitRevealBehavior,
} from "@shared/types";

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
  weight: Token;
  intendedScore: number;
  behavior: CommitRevealBehavior;
  committed: boolean;
  revealed: boolean;
  revealedScore: number | null;
  penaltyFraction: number;
  slashedToken: Token;
  rewardToken: Token;
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
  reservedRewardToken: Token;
  distributedRewardToken: Token;
  distanceSlashingSkipped: boolean;
  cancellationReason: "QuorumFailure" | "Underfunded" | null;
  finalizedAtTick: number | null;
}
