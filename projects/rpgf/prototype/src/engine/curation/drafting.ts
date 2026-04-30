/**
 * Deterministic seat-based draw-and-lock drafting.
 *
 * Each curator contributes `floor(deposited / L)` tickets to the seat-ticket
 * pool. The protocol shuffles the ticket pool under the round seed and walks
 * up to `min(totalTickets, maxIterMultiplier * targetSeats)` tickets. For
 * each ticket it tries to lock one seat of size L for the corresponding
 * curator, accepting only as many seats per curator as the curator can fund
 * out of their unlocked deposit.
 *
 * Inputs are read-only; the draft never mutates curator state. Locking the
 * actual deposits is performed by the relevance round runner.
 */

import type { Curator } from "./types";
import { createPRNG } from "./prng";

export interface DraftedSeat {
  curatorId: string;
  ticketIndex: number;
  seatIndexForCurator: number;
}

export interface DraftResult {
  seats: DraftedSeat[];
  totalSeatsLocked: number;
  totalTickets: number;
  iterationCap: number;
  underfunded: boolean;
}

export interface DraftInput {
  curators: ReadonlyArray<Pick<Curator, "id" | "depositedToken" | "lockedToken">>;
  seatSizeL: number;
  targetSeats: number;
  seed: string;
  maxIterMultiplier?: number;
}

export function buildTicketPool(
  curators: DraftInput["curators"],
  seatSizeL: number,
): Array<{ curatorId: string; ticketIndex: number }> {
  const tickets: Array<{ curatorId: string; ticketIndex: number }> = [];
  for (const c of curators) {
    if (c.depositedToken < seatSizeL) continue;
    const tickets_i = Math.floor(c.depositedToken / seatSizeL);
    for (let k = 0; k < tickets_i; k++) {
      tickets.push({ curatorId: c.id, ticketIndex: tickets.length });
    }
  }
  return tickets;
}

export function draftSeats(input: DraftInput): DraftResult {
  const { curators, seatSizeL, targetSeats, seed } = input;
  const maxIterMultiplier = input.maxIterMultiplier ?? 3;

  const tickets = buildTicketPool(curators, seatSizeL);
  const prng = createPRNG(seed);
  const shuffled = prng.shuffle(tickets);

  const iterationCap = Math.min(
    shuffled.length,
    Math.max(targetSeats, maxIterMultiplier * targetSeats),
  );

  const availableByCurator = new Map<string, number>();
  for (const c of curators) {
    availableByCurator.set(c.id, c.depositedToken - c.lockedToken);
  }
  const seatsByCurator = new Map<string, number>();

  const seats: DraftedSeat[] = [];

  for (let i = 0; i < iterationCap && seats.length < targetSeats; i++) {
    const ticket = shuffled[i];
    if (!ticket) break;
    const seatsSoFar = seatsByCurator.get(ticket.curatorId) ?? 0;
    const available = availableByCurator.get(ticket.curatorId) ?? 0;
    if (available >= (seatsSoFar + 1) * seatSizeL) {
      seats.push({
        curatorId: ticket.curatorId,
        ticketIndex: ticket.ticketIndex,
        seatIndexForCurator: seatsSoFar,
      });
      seatsByCurator.set(ticket.curatorId, seatsSoFar + 1);
    }
  }

  return {
    seats,
    totalSeatsLocked: seats.length,
    totalTickets: tickets.length,
    iterationCap,
    underfunded: seats.length < targetSeats,
  };
}

export function summarizeSeatsByCurator(
  seats: DraftedSeat[],
): Map<string, number> {
  const byCurator = new Map<string, number>();
  for (const s of seats) {
    byCurator.set(s.curatorId, (byCurator.get(s.curatorId) ?? 0) + 1);
  }
  return byCurator;
}
