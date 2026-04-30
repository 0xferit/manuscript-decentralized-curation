import { describe, expect, it } from "vitest";
import { buildTicketPool, draftSeats } from "../src/engine/drafting";

const baseCurator = (id: string, deposit: number, locked = 0) => ({
  id,
  depositedToken: deposit,
  lockedToken: locked,
});

describe("buildTicketPool", () => {
  it("uses floor(deposit / L) tickets per curator", () => {
    const tickets = buildTicketPool(
      [baseCurator("a", 0.05), baseCurator("b", 0.025)],
      0.01,
    );
    expect(tickets.filter((t) => t.curatorId === "a")).toHaveLength(5);
    expect(tickets.filter((t) => t.curatorId === "b")).toHaveLength(2);
  });

  it("excludes curators below seat size", () => {
    const tickets = buildTicketPool([baseCurator("a", 0.005)], 0.01);
    expect(tickets).toHaveLength(0);
  });
});

describe("draftSeats", () => {
  it("is deterministic under the same seed", () => {
    const curators = [
      baseCurator("a", 0.10),
      baseCurator("b", 0.10),
      baseCurator("c", 0.10),
    ];
    const result1 = draftSeats({
      curators,
      seatSizeL: 0.01,
      targetSeats: 5,
      seed: "seed-x",
    });
    const result2 = draftSeats({
      curators,
      seatSizeL: 0.01,
      targetSeats: 5,
      seed: "seed-x",
    });
    expect(result1.seats).toEqual(result2.seats);
  });

  it("produces different orderings under different seeds", () => {
    const curators = [
      baseCurator("a", 0.10),
      baseCurator("b", 0.10),
      baseCurator("c", 0.10),
    ];
    const a = draftSeats({
      curators,
      seatSizeL: 0.01,
      targetSeats: 5,
      seed: "seed-a",
    }).seats.map((s) => s.curatorId);
    const b = draftSeats({
      curators,
      seatSizeL: 0.01,
      targetSeats: 5,
      seed: "seed-b",
    }).seats.map((s) => s.curatorId);
    expect(a).not.toEqual(b);
  });

  it("locks at most floor(deposit/L) seats per curator", () => {
    const curators = [baseCurator("a", 0.03), baseCurator("b", 0.10)];
    const out = draftSeats({
      curators,
      seatSizeL: 0.01,
      targetSeats: 8,
      seed: "seed-cap",
    });
    const aSeats = out.seats.filter((s) => s.curatorId === "a").length;
    expect(aSeats).toBeLessThanOrEqual(3);
  });

  it("flags underfunded when not enough fundable tickets", () => {
    const curators = [baseCurator("a", 0.02)];
    const out = draftSeats({
      curators,
      seatSizeL: 0.01,
      targetSeats: 10,
      seed: "seed-under",
    });
    expect(out.underfunded).toBe(true);
    expect(out.totalSeatsLocked).toBeLessThan(10);
  });

  it("respects 3*targetSeats iteration cap", () => {
    const curators = Array.from({ length: 1000 }, (_, i) =>
      baseCurator(`c${i}`, 0.01),
    );
    const out = draftSeats({
      curators,
      seatSizeL: 0.01,
      targetSeats: 5,
      seed: "seed-large",
    });
    expect(out.iterationCap).toBeLessThanOrEqual(3 * 5);
    expect(out.totalSeatsLocked).toBe(5);
  });
});
