import type { Token } from "./token";

export type NominationState =
  | "Submitted"
  | "Retracted"
  | "Scored"
  | "Disputed"
  | "Disbursed"
  | "Debunked"
  | "Unscored";

export type AdjudicationOutcome =
  | "Unchallenged"
  | "ChallengeFailed"
  | "Debunked";

export type EvidenceClass =
  | "DirectArtifact"
  | "IndependentThirdParty"
  | "SelfReported";

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
