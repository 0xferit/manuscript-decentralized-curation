/**
 * Boundary types between the engine controller and any caller (UI, CLI,
 * test harness). The controller never touches React or the DOM. The caller
 * never touches engine internals: it only handles `EngineState` envelopes
 * and `LogEvent` lists returned from controller calls.
 */

import type {
  AllocationResult,
  Challenge,
  Curator,
  FundingRound,
  ImpactNomination,
  Pool,
  RegistryEntry,
  RelevanceRound,
  ReputationLedger,
} from "../types";

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
