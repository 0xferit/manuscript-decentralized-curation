/**
 * Adjudication module: canonical types + re-exports of shared types used.
 *
 * Owns: Challenge, ChallengeReason, ChallengeStatus, DDROutcome, ChallengePayout,
 * DDRResolver, DDRResolveInput/Output, DDRResolution.
 */

export type {
  PoolParameters,
  ImpactNomination,
} from "@shared/types";

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
  counterStakeToken: number;
  taxToken: number;
  ddrFeeToken: number;
  status: ChallengeStatus;
  filedAtTick: number;
  resolvedAtTick: number | null;
  ruling: DDROutcome | null;
}

export type { ChallengePayout } from "./challenge";
export type {
  DDRResolver,
  DDRResolveInput,
  DDRResolveOutput,
  DDRResolution,
} from "./ddr";
export { ChallengeFilingError } from "./challenge";
export { DDRResolutionError } from "./ddr";
