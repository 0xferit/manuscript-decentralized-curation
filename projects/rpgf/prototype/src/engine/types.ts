/**
 * Aggregated domain types for the RPGF prototype engine.
 *
 * Cross-module data shapes (Token, PoolMeta, RegistryEntry, CuratorIdentity,
 * ImpactNomination, etc.) live in `./shared/types/` and are re-exported here
 * for backwards compatibility during the incremental refactor.
 *
 * Module-internal types (RelevanceRound, Challenge, ReputationLedger, etc.)
 * still live below until each module is promoted (steps 3a-3f of the
 * refactor plan).
 */

import type { Token } from "./shared/types/token";
import type { CommitRevealBehavior } from "./shared/types/curator";

export type {
  Token,
  PoolPhase,
  PoolParameters,
  Pool,
  RegistryEntry,
  CuratorArchetype,
  CommitRevealBehavior,
  Curator,
  NominationState,
  AdjudicationOutcome,
  EvidenceClass,
  EvidenceItem,
  Assertion,
  ImpactNomination,
  FundingRound,
} from "./shared/types";

// ---------------------------------------------------------------------------
// Adjudication-internal types (will move to engine/adjudication/types.ts)
// ---------------------------------------------------------------------------

export type ChallengeReason =
  | "Debunking"
  | "NonFalsifiable"
  | "TemplateViolation";

export type DDROutcome = "Debunked" | "ChallengeFailed" | "Timeout";

export type ChallengeStatus = "Pending" | DDROutcome;

export interface Challenge {
  id: string;
  nominationId: string;
  challengerId: string;
  reason: ChallengeReason;
  newEvidenceNote: string | null;
  counterStakeToken: Token;
  taxToken: Token;
  ddrFeeToken: Token;
  status: ChallengeStatus;
  filedAtTick: number;
  resolvedAtTick: number | null;
  ruling: DDROutcome | null;
}

// ---------------------------------------------------------------------------
// Curation-internal types (will move to engine/curation/types.ts)
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Reputation-internal types (will move to engine/reputation/types.ts)
// ---------------------------------------------------------------------------

export interface ReputationLedgerEntry {
  registryEntryId: string;
  poolId: string;
  reputation: number;
  history: ReputationLedgerEvent[];
}

export interface ReputationLedgerEvent {
  tick: number;
  delta: number;
  reason: "SurvivingRound" | "Debunked" | "Decay";
  newValue: number;
  notes?: string;
}

export interface ReputationLedger {
  byRegistryEntryId: Record<string, ReputationLedgerEntry>;
  lastDecayEpoch: number;
}

// ---------------------------------------------------------------------------
// Allocation-internal types (will move to engine/allocation/types.ts)
// ---------------------------------------------------------------------------

export interface AllocationRow {
  nominationId: string;
  registryEntryId: string;
  relevanceScore: number;
  share: number;
  provisionalToken: Token;
  finalToken: Token | null;
  state: import("./shared/types").NominationState;
}

export interface AllocationResult {
  poolId: string;
  roundId: string;
  poolFundingBudget: Token;
  denominator: number;
  rolloverToken: Token;
  rows: AllocationRow[];
}
