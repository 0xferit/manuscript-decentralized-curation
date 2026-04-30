/**
 * Adjudication module: resolve disputes.
 *
 * Public surface: file challenges, run external DDR (via injected resolver),
 * apply payouts. The DDR port is part of this module's contract; the
 * default mock and any production adapter implement DDRResolver.
 */

export type {
  Challenge,
  ChallengeReason,
  ChallengeStatus,
  DDROutcome,
  ChallengePayout,
  DDRResolver,
  DDRResolveInput,
  DDRResolveOutput,
  DDRResolution,
} from "./types";

export {
  ChallengeFilingError,
  DDRResolutionError,
} from "./types";

export {
  fileChallenge,
  computeCounterStake,
  computeChallengeTax,
  challengePayoutFor,
} from "./challenge";

export type { FileChallengeInput } from "./challenge";

export { manualMockDDRResolver, resolveChallenge } from "./ddr";
