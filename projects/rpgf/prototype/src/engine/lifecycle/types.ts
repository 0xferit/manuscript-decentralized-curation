/**
 * Boundary types between the engine controller and any caller (UI, CLI,
 * test harness). The controller never touches React or the DOM. The caller
 * never touches engine internals: it only handles `EngineState` envelopes
 * and `LogEvent` lists returned from controller calls.
 */

import type {
  Curator,
  FundingRound,
  ImpactNomination,
  Pool,
  RegistryEntry,
} from "@shared/types";
import type { Challenge } from "@adjudication";
import type { AllocationResult } from "@allocation";
import type { ReputationLedger } from "@reputation";
import type { RelevanceRound } from "@curation";

/**
 * Engine state envelope.
 *
 * Slice ownership (enforced by code review + module-import lint rules,
 * not yet by structural type splits):
 *
 * - `bootstrap` (Identity): seeds `pool` (config + ids), `registry`, and
 *   the identity portion of `curators`. Read-only after init.
 * - `curation`: writes `pool.emaSigma`, `pool.curationBudget`, `rounds`,
 *   and the financial portion of `curators` (deposit/locked/rewards/slashed).
 * - `adjudication`: writes `challenges`. Reads nominations by id.
 * - `allocation`: writes `pool.fundingBudget` (tax accumulation),
 *   `pool.budgetRolloverToken`, and `allocation`.
 * - `reputation`: writes `reputation`.
 * - `lifecycle`: writes `pool.phase`, `pool.currentRoundId`, `nominations`,
 *   `fundingRound`, `tick`, `epoch`, `evaluationRan`, `disbursementRan`.
 *   Composes slice updates from the modules above into a new envelope.
 *
 * The flat shape is preserved during the incremental refactor to avoid a
 * mass UI rewrite. A future step may group slices structurally
 * (`identity`, `curation`, `adjudication`, `allocation`, `reputation`,
 * `lifecycle`) once boundary discipline is verified at runtime.
 */
export interface EngineState {
  pool: Pool;
  registry: RegistryEntry[];
  curators: Curator[];
  nominations: ImpactNomination[];
  challenges: Challenge[];
  rounds: RelevanceRound[];
  fundingRound: FundingRound;
  reputation: ReputationLedger;
  allocation: AllocationResult | null;
  tick: number;
  epoch: number;
  evaluationRan: boolean;
  disbursementRan: boolean;
}

export type LogCategory =
  | "Phase"
  | "Engine"
  | "Author"
  | "Challenge"
  | "DDR"
  | "Disbursement"
  | "Reputation"
  | "Tick";

export interface LogEvent {
  tick: number;
  category: LogCategory;
  message: string;
}

export interface ControllerResult {
  state: EngineState;
  events: LogEvent[];
}

export type ControllerError =
  | { kind: "PhaseMismatch"; expected: string; actual: string }
  | { kind: "EngineError"; message: string };
