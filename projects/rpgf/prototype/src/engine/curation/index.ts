/**
 * Curation module: score relevance via the coherence game.
 *
 * Public surface only. Internal helpers (stats, prng, drafting, individual
 * stages) stay private; consumers use `evaluateNomination` and the types
 * exported below.
 */

export type {
  RelevanceRound,
  RoundPhase,
  CuratorRoundState,
  CuratorFinancialState,
} from "./types";

export type {
  CommitRevealSimulator,
  CommitRevealInput,
} from "./stages/commit-reveal";

export { deterministicCommitRevealSimulator } from "./stages/commit-reveal";

export type {
  EvaluateNominationInput,
  EvaluateNominationOutput,
} from "./round";
export { evaluateNomination } from "./round";

export type {
  RunRelevanceRoundInput,
  RelevanceRoundOutcome,
  CuratorRoundDelta,
} from "./relevance";
export { runRelevanceRound } from "./relevance";
