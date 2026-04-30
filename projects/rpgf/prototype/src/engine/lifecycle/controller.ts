/**
 * Phase controller barrel.
 *
 * Each phase action lives in its own file under `./phases/`. This file
 * re-exports each via `export ... from` and assembles them into the
 * `phaseController` object that the store and tests dispatch against.
 *
 * Invariants (enforced by per-phase modules):
 *   - Pure (state, args, deps) -> { state, events }; no input mutation.
 *   - The controller is the only place where multi-step transitions live.
 *     Each phase function may compose engine atoms (curation, adjudication,
 *     allocation, reputation) but never imports React or any UI module.
 *   - DDR + commit-reveal simulators are injected via `PhaseDeps` so
 *     production swaps are a one-line change.
 */

export type { PhaseDeps } from "./phases/_shared";

export { amendNomination, retractNominationAction, closeSubmission } from "./phases/submission";
export { runEvaluation, enterHoldback } from "./phases/evaluation";
export {
  fileChallengeAction,
  resolveDDR,
  expireHoldback,
} from "./phases/holdback";
export type { FileChallengeArgs } from "./phases/holdback";
export { releaseGraced, closeRound } from "./phases/settlement";
export { decayReputation } from "./phases/reputation-tick";

import { amendNomination, retractNominationAction, closeSubmission } from "./phases/submission";
import { runEvaluation, enterHoldback } from "./phases/evaluation";
import { fileChallengeAction, resolveDDR, expireHoldback } from "./phases/holdback";
import { releaseGraced, closeRound } from "./phases/settlement";
import { decayReputation } from "./phases/reputation-tick";

export const phaseController = {
  amendNomination,
  retractNomination: retractNominationAction,
  closeSubmission,
  runEvaluation,
  enterHoldback,
  fileChallenge: fileChallengeAction,
  resolveDDR,
  expireHoldback,
  releaseGraced,
  closeRound,
  decayReputation,
};

export type PhaseController = typeof phaseController;
