/**
 * resolveDDR: consume an external DDR ruling (via injected resolver), apply
 * the state-machine transition, redistribute on Debunked, update reputation,
 * and log payout.
 */

import {
  challengePayoutFor,
  manualMockDDRResolver,
} from "@adjudication";
import type { DDROutcome } from "@adjudication";
import { redistributeDebunkedShare } from "@allocation";
import { applyDebunkPenalty } from "@reputation";

import {
  markChallengeFailed,
  markDebunked,
  topUpFinalShare,
} from "../../state-machine";
import type { ControllerResult, EngineState, LogEvent } from "../../types";
import { advanceTick, type PhaseDeps } from "../_shared";

export function resolveDDR(
  state: EngineState,
  challengeId: string,
  outcome: DDROutcome,
  deps: PhaseDeps,
  jurorNote: string | null = null,
): ControllerResult {
  const challenge = state.challenges.find((c) => c.id === challengeId);
  if (challenge?.status !== "Pending") {
    return { state, events: [] };
  }
  const ddr = deps.ddr ?? manualMockDDRResolver;
  const next = advanceTick(state);
  const { challenge: resolved } = ddr.resolve({
    challenge,
    ruling: outcome,
    tick: next.tick,
    jurorNote,
  });
  const challenges = next.challenges.map((c) =>
    c.id === challengeId ? resolved : c,
  );
  const nomination = next.nominations.find(
    (n) => n.id === resolved.nominationId,
  );
  if (!nomination) return { state: next, events: [] };

  const events: LogEvent[] = [];
  let nominations = next.nominations;
  let reputation = next.reputation;
  let allocation = next.allocation;

  if (outcome === "Debunked") {
    nominations = nominations.map((n) =>
      n.id === nomination.id ? markDebunked(n, next.tick) : n,
    );
    reputation = applyDebunkPenalty(
      reputation,
      nomination.registryEntryId,
      next.pool.id,
      next.pool.parameters.reputationDebunkedDelta,
      next.tick,
      `DDR debunked nomination ${nomination.id}`,
    );
    const freed = nomination.provisionalShareToken ?? 0;
    const survivingDisbursed = nominations.filter(
      (n) =>
        n.state === "Disbursed" &&
        n.id !== nomination.id &&
        n.relevanceScore !== null,
    );
    const redistribution = redistributeDebunkedShare({
      freedShareToken: freed,
      survivingDisbursed,
    });
    nominations = nominations.map((n) => {
      const tu = redistribution.topUps.find((t) => t.nominationId === n.id);
      if (!tu) return n;
      return topUpFinalShare(n, next.tick, tu.extraToken);
    });
    if (allocation) {
      allocation = {
        ...allocation,
        rolloverToken: allocation.rolloverToken + redistribution.rolloverToken,
      };
    }
    events.push({
      tick: next.tick,
      category: "DDR",
      message: `Debunked ${nomination.id}: redistributed ${(freed - redistribution.rolloverToken).toFixed(4)} token across ${redistribution.topUps.length} disbursed nominations; rollover ${redistribution.rolloverToken.toFixed(4)} token`,
    });
    events.push({
      tick: next.tick,
      category: "Reputation",
      message: `Registry ${nomination.registryEntryId} reputation -= ${Math.abs(next.pool.parameters.reputationDebunkedDelta)}`,
    });
  } else {
    nominations = nominations.map((n) =>
      n.id === nomination.id
        ? markChallengeFailed(n, next.tick, next.pool.parameters.graceTicks)
        : n,
    );
    events.push({
      tick: next.tick,
      category: "DDR",
      message: `${outcome} on ${nomination.id}: nomination returns to Scored with grace until tick ${next.tick + next.pool.parameters.graceTicks}`,
    });
  }

  const payout = challengePayoutFor(outcome, resolved);
  events.push({
    tick: next.tick,
    category: "DDR",
    message: `Payout: bond -> ${payout.authorBondTo}, counter-stake -> ${payout.counterStakeTo}, tax retained ${payout.taxToPool.toFixed(4)} in pool`,
  });

  return {
    state: { ...next, challenges, nominations, reputation, allocation },
    events,
  };
}
