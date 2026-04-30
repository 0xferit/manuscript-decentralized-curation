/**
 * Reputation module: canonical ledger types.
 *
 * Owns: ReputationLedger, ReputationLedgerEntry, ReputationLedgerEvent.
 */

export interface ReputationLedgerEntry {
  registryEntryId: string;
  poolId: string;
  reputation: number;
  history: ReputationLedgerEvent[];
}

export interface ReputationLedgerEvent {
  tick: number;
  delta: number;
  reason: "SurvivingRound" | "Debunked" | "Decay";
  newValue: number;
  notes?: string;
}

export interface ReputationLedger {
  byRegistryEntryId: Record<string, ReputationLedgerEntry>;
  lastDecayEpoch: number;
}
