/**
 * Domain types for the RPGF decentralized curation prototype.
 *
 * All numeric amounts use the `Token` brand: 1 Token represents 1 ETH-
 * equivalent unit in the prototype. The engine never transfers value; ledgers
 * are bookkeeping only.
 */

export type Token = number;

export type NominationState =
  | "Submitted"
  | "Retracted"
  | "Scored"
  | "Disputed"
  | "Disbursed"
  | "Debunked"
  | "Unscored";

export type AdjudicationOutcome = "Unchallenged" | "ChallengeFailed" | "Debunked";

export type ChallengeReason = "Debunking" | "NonFalsifiable" | "TemplateViolation";

export type DDROutcome = "Debunked" | "ChallengeFailed" | "Timeout";

export type ChallengeStatus = "Pending" | DDROutcome;

export type EvidenceClass =
  | "DirectArtifact"
  | "IndependentThirdParty"
  | "SelfReported";

export type CuratorArchetype = "Honest" | "Lazy" | "Adversary";

export type CommitRevealBehavior = "CommitAndReveal" | "CommitOnly" | "NoShow";

export type RoundPhase =
  | "PreDraft"
  | "Drafted"
  | "Commit"
  | "Reveal"
  | "Finalized"
  | "Cancelled";

export type PoolPhase =
  | "Submission"
  | "Evaluation"
  | "Holdback"
  | "Settlement"
  | "Closed";

export interface RegistryEntry {
  id: string;
  projectName: string;
  beneficiaryAddress: string;
  claimantPolicy: string;
  eligibilityTags: string[];
  reputation: number;
  lastReputationUpdateEpoch: number;
}

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

export interface FundingRound {
  id: string;
  poolId: string;
  index: number;
  phase: PoolPhase;
  nominationIds: string[];
  holdbackEndsAtTick: number | null;
  finalizedAtTick: number | null;
  totalDisbursedToken: Token;
  rolloverToken: Token;
}

export interface EvidenceItem {
  id: string;
  evidenceClass: EvidenceClass;
  uri: string;
  caption: string;
}

export interface Assertion {
  id: string;
  text: string;
  timePeriodStart: string;
  timePeriodEnd: string;
  evidenceItemIds: string[];
  falsifiable: boolean;
}

export interface ImpactNomination {
  id: string;
  poolId: string;
  roundId: string;
  registryEntryId: string;
  authorAddress: string;
  state: NominationState;
  adjudicationOutcome: AdjudicationOutcome;
  bondToken: Token;
  assertions: Assertion[];
  evidenceItems: EvidenceItem[];
  createdAtPhaseTick: number;
  lastUpdatedPhaseTick: number;
  templateOk: boolean;
  doubleCountTagIds: string[];
  relevanceScore: number | null;
  relevanceRoundId: string | null;
  provisionalShareToken: Token | null;
  finalShareToken: Token | null;
  graceEndsAtTick: number | null;
  challengeIds: string[];
}

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

export interface Curator {
  id: string;
  displayName: string;
  archetype: CuratorArchetype;
  depositedToken: Token;
  lockedToken: Token;
  commitRevealBehavior: CommitRevealBehavior;
  intendedScore: number;
  totalRewardsToken: Token;
  totalSlashedToken: Token;
}

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

export interface AllocationRow {
  nominationId: string;
  registryEntryId: string;
  relevanceScore: number;
  share: number;
  provisionalToken: Token;
  finalToken: Token | null;
  state: NominationState;
}

export interface AllocationResult {
  poolId: string;
  roundId: string;
  poolFundingBudget: Token;
  denominator: number;
  rolloverToken: Token;
  rows: AllocationRow[];
}

export interface PhaseClock {
  tick: number;
  epoch: number;
  history: Array<{
    tick: number;
    label: string;
    note?: string;
  }>;
}
