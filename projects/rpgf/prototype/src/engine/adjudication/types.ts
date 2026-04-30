/**
 * Adjudication module: internal types + re-exports of shared types used.
 */

export type {
  Challenge,
  ChallengeReason,
  ChallengeStatus,
  DDROutcome,
  Token,
  PoolParameters,
  ImpactNomination,
} from "../types";

export type { ChallengePayout } from "./challenge";
export type {
  DDRResolver,
  DDRResolveInput,
  DDRResolveOutput,
  DDRResolution,
} from "./ddr";
export { ChallengeFilingError } from "./challenge";
export { DDRResolutionError } from "./ddr";
