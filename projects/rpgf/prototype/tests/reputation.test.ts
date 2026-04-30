import { describe, expect, it } from "vitest";
import {
  applyDebunkPenalty,
  awardSurvivingRound,
  decayEpoch,
  emptyLedger,
  ensureEntry,
} from "../src/engine/reputation";

describe("reputation ledger (immutable)", () => {
  it("does not mutate input ledger", () => {
    const before = emptyLedger();
    const after = awardSurvivingRound(before, "reg-a", "p", 1, 1);
    expect(before.byRegistryEntryId["reg-a"]).toBeUndefined();
    expect(after.byRegistryEntryId["reg-a"]?.reputation).toBe(1);
  });

  it("awards +1 per surviving round", () => {
    let ledger = emptyLedger();
    ledger = awardSurvivingRound(ledger, "reg-a", "p", 1, 1);
    ledger = awardSurvivingRound(ledger, "reg-a", "p", 1, 2);
    expect(ledger.byRegistryEntryId["reg-a"]?.reputation).toBe(2);
  });

  it("applies -5 on debunk", () => {
    let ledger = emptyLedger();
    ledger = awardSurvivingRound(ledger, "reg-a", "p", 1, 1);
    ledger = applyDebunkPenalty(ledger, "reg-a", "p", -5, 2);
    expect(ledger.byRegistryEntryId["reg-a"]?.reputation).toBe(-4);
  });

  it("decays toward zero from positive", () => {
    let ledger = emptyLedger();
    ledger = ensureEntry(ledger, "reg-a", "p", 0);
    ledger = awardSurvivingRound(ledger, "reg-a", "p", 3, 1);
    ledger = decayEpoch(ledger, "p", 1, 2).ledger;
    expect(ledger.byRegistryEntryId["reg-a"]?.reputation).toBe(2);
    ledger = decayEpoch(ledger, "p", 1, 3).ledger;
    ledger = decayEpoch(ledger, "p", 1, 4).ledger;
    expect(ledger.byRegistryEntryId["reg-a"]?.reputation).toBe(0);
  });

  it("decays toward zero from negative", () => {
    let ledger = emptyLedger();
    ledger = applyDebunkPenalty(ledger, "reg-a", "p", -3, 1);
    ledger = decayEpoch(ledger, "p", 1, 2).ledger;
    expect(ledger.byRegistryEntryId["reg-a"]?.reputation).toBe(-2);
  });

  it("decay never overshoots zero", () => {
    let ledger = emptyLedger();
    ledger = awardSurvivingRound(ledger, "reg-a", "p", 1, 1);
    ledger = decayEpoch(ledger, "p", 5, 2).ledger;
    expect(ledger.byRegistryEntryId["reg-a"]?.reputation).toBe(0);
  });

  it("skips entries with zero reputation on decay", () => {
    let ledger = emptyLedger();
    ledger = ensureEntry(ledger, "reg-a", "p", 0);
    const result = decayEpoch(ledger, "p", 1, 2);
    expect(result.updatedIds).toHaveLength(0);
  });

  it("history records each event", () => {
    let ledger = emptyLedger();
    ledger = awardSurvivingRound(ledger, "reg-a", "p", 1, 1);
    ledger = applyDebunkPenalty(ledger, "reg-a", "p", -5, 2, "DDR ruled debunked");
    ledger = decayEpoch(ledger, "p", 1, 3).ledger;
    expect(ledger.byRegistryEntryId["reg-a"]?.history).toHaveLength(3);
  });

  it("ensureEntry is idempotent", () => {
    let ledger = emptyLedger();
    ledger = ensureEntry(ledger, "reg-a", "p", 7);
    ledger = ensureEntry(ledger, "reg-a", "p", 9);
    expect(ledger.byRegistryEntryId["reg-a"]?.reputation).toBe(7);
  });
});
