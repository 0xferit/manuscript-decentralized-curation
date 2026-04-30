/**
 * Registry-entry reputation ledger.
 *
 * Specification (`projects/rpgf/design.md`, "Registry Entry Reputation"):
 *   - +1 per surviving round
 *   - -5 per debunked nomination
 *   - decay: |reputation| -= 1 per epoch, drifts toward 0
 *   - reputation may go negative
 *
 * All mutators are pure: they return a new ledger and never modify the input.
 * This is required because React StrictMode invokes reducers twice; mutating
 * shared state would double-apply effects.
 */

import type {
  ReputationLedger,
  ReputationLedgerEntry,
  ReputationLedgerEvent,
} from "../types";

export function emptyLedger(): ReputationLedger {
  return { byRegistryEntryId: {}, lastDecayEpoch: 0 };
}

export function ensureEntry(
  ledger: ReputationLedger,
  registryEntryId: string,
  poolId: string,
  initialReputation: number,
): ReputationLedger {
  if (ledger.byRegistryEntryId[registryEntryId]) return ledger;
  const created: ReputationLedgerEntry = {
    registryEntryId,
    poolId,
    reputation: initialReputation,
    history: [],
  };
  return {
    ...ledger,
    byRegistryEntryId: {
      ...ledger.byRegistryEntryId,
      [registryEntryId]: created,
    },
  };
}

function applyEvent(
  ledger: ReputationLedger,
  registryEntryId: string,
  poolId: string,
  evt: Omit<ReputationLedgerEvent, "newValue"> & { newValueOverride?: number },
): ReputationLedger {
  const existing =
    ledger.byRegistryEntryId[registryEntryId] ?? {
      registryEntryId,
      poolId,
      reputation: 0,
      history: [] as ReputationLedgerEvent[],
    };
  const newValue =
    evt.newValueOverride !== undefined
      ? evt.newValueOverride
      : existing.reputation + evt.delta;
  const fullEvent: ReputationLedgerEvent = {
    tick: evt.tick,
    delta: evt.delta,
    reason: evt.reason,
    newValue,
    notes: evt.notes,
  };
  const next: ReputationLedgerEntry = {
    ...existing,
    reputation: newValue,
    history: [...existing.history, fullEvent],
  };
  return {
    ...ledger,
    byRegistryEntryId: {
      ...ledger.byRegistryEntryId,
      [registryEntryId]: next,
    },
  };
}

export function awardSurvivingRound(
  ledger: ReputationLedger,
  registryEntryId: string,
  poolId: string,
  delta: number,
  tick: number,
  notes?: string,
): ReputationLedger {
  return applyEvent(ledger, registryEntryId, poolId, {
    tick,
    delta,
    reason: "SurvivingRound",
    notes,
  });
}

export function applyDebunkPenalty(
  ledger: ReputationLedger,
  registryEntryId: string,
  poolId: string,
  delta: number,
  tick: number,
  notes?: string,
): ReputationLedger {
  return applyEvent(ledger, registryEntryId, poolId, {
    tick,
    delta,
    reason: "Debunked",
    notes,
  });
}

export function decayEpoch(
  ledger: ReputationLedger,
  poolId: string,
  decayPerEpoch: number,
  tick: number,
): { ledger: ReputationLedger; updatedIds: string[] } {
  let next = ledger;
  const updatedIds: string[] = [];
  for (const entry of Object.values(ledger.byRegistryEntryId)) {
    if (entry.poolId !== poolId) continue;
    if (entry.reputation === 0) continue;
    const direction = entry.reputation > 0 ? -1 : 1;
    const magnitude = Math.min(decayPerEpoch, Math.abs(entry.reputation));
    const delta = direction * magnitude;
    next = applyEvent(next, entry.registryEntryId, poolId, {
      tick,
      delta,
      reason: "Decay",
      notes: `Drift toward zero (${entry.reputation} -> ${entry.reputation + delta})`,
    });
    updatedIds.push(entry.registryEntryId);
  }
  next = { ...next, lastDecayEpoch: ledger.lastDecayEpoch + 1 };
  return { ledger: next, updatedIds };
}
