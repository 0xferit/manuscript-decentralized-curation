/**
 * Lifecycle module: drive nominations through the state machine across
 * pool phases; orchestrate Curation, Adjudication, Allocation, Reputation.
 *
 * Public surface:
 *   - State machine atoms (`markScored`, `markDisputed`, etc.).
 *   - Phase controller object (`phaseController`).
 *   - EngineState envelope and supporting types.
 *
 * Internal helpers (per-phase functions, _shared utilities) stay private.
 */

export type {
  EngineState,
  LogEvent,
  LogCategory,
  ControllerResult,
  ControllerError,
} from "./types";

export type {
  AmendInput,
} from "./state-machine";

export {
  amendDuringSubmission,
  retractNomination,
  markScored,
  markUnscored,
  markDisputed,
  markDebunked,
  markChallengeFailed,
  markDisbursed,
  topUpFinalShare,
  NominationTransitionError,
  nominationOutcomes,
} from "./state-machine";

export type { PhaseDeps, FileChallengeArgs } from "./controller";
export { phaseController } from "./controller";
export type { PhaseController } from "./controller";
