/**
 * Reputation module: per-registry-entry honesty ledger.
 *
 * +1 per surviving round, -5 per debunked nomination, decay 1 per epoch
 * toward zero. All mutators are pure: they return a new ledger.
 */

export type {
  ReputationLedger,
  ReputationLedgerEntry,
  ReputationLedgerEvent,
} from "../types";

export {
  emptyLedger,
  ensureEntry,
  awardSurvivingRound,
  applyDebunkPenalty,
  decayEpoch,
} from "./reputation";
