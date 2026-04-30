/**
 * Holdback-phase actions: fileChallenge, resolveDDR, expireHoldback.
 *
 * - fileChallenge: file a typed challenge during the holdback window.
 *   Promotes the nomination to Disputed if it was Scored.
 * - resolveDDR: consume an external DDR ruling (via injected resolver),
 *   apply state-machine transition, redistribute on Debunked, update
 *   reputation, log payout.
 * - expireHoldback: at holdback end, disburse Unchallenged Scored
 *   nominations, transition pool to Settlement.
 */

import {
  challengePayoutFor,
  fileChallenge as buildChallenge,
} from "../../adjudication/challenge";
import {
  manualMockDDRResolver,
} from "../../adjudication/ddr";
import { redistributeDebunkedShare } from "../../allocation/allocation";
import {
  applyDebunkPenalty,
  awardSurvivingRound,
} from "../../reputation/reputation";
import {
  markChallengeFailed,
  markDebunked,
  markDisbursed,
  markDisputed,
  topUpFinalShare,
} from "../state-machine";
import type {
  ChallengeReason,
  DDROutcome,
  ImpactNomination,
} from "../../types";
import type { ControllerResult, EngineState, LogEvent } from "../types";
import {
  advanceTick,
  nomById,
  type PhaseDeps,
} from "./_shared";

export interface FileChallengeArgs {
  nominationId: string;
  challengerId: string;
  reason: ChallengeReason;
  newEvidenceNote?: string | null;
}

export function fileChallengeAction(
  state: EngineState,
  args: FileChallengeArgs,
): ControllerResult {
  const nomination = nomById(state, args.nominationId);
  if (!nomination) return { state, events: [] };
  const next = advanceTick(state);
  try {
    const challenge = buildChallenge({
      id: `c-${state.challenges.length + 1}-${args.nominationId}`,
      nomination,
      challengerId: args.challengerId,
      reason: args.reason,
      newEvidenceNote: args.newEvidenceNote ?? null,
      parameters: next.pool.parameters,
      tick: next.tick,
    });
    let nominations = next.nominations;
    if (nomination.state === "Scored") {
      nominations = nominations.map((n) =>
        n.id === nomination.id ? markDisputed(n, next.tick) : n,
      );
    }
    nominations = nominations.map((n) =>
      n.id === nomination.id
        ? { ...n, challengeIds: [...n.challengeIds, challenge.id] }
        : n,
    );
    return {
      state: {
        ...next,
        challenges: [...next.challenges, challenge],
        nominations,
        pool: {
          ...next.pool,
          fundingBudget: next.pool.fundingBudget + challenge.taxToken,
        },
      },
      events: [
        {
          tick: next.tick,
          category: "Challenge",
          message: `Filed ${args.reason} challenge ${challenge.id} on ${args.nominationId} by ${args.challengerId}; counter-stake=${challenge.counterStakeToken.toFixed(4)}, tax=${challenge.taxToken.toFixed(4)}`,
        },
      ],
    };
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    return {
      state: next,
      events: [
        {
          tick: next.tick,
          category: "Challenge",
          message: `Filing rejected for ${args.nominationId}: ${message}`,
        },
      ],
    };
  }
}

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

export function expireHoldback(state: EngineState): ControllerResult {
  if (state.pool.phase !== "Holdback") {
    return { state, events: [] };
  }
  const next = advanceTick(state);
  const events: LogEvent[] = [
    { tick: next.tick, category: "Phase", message: "Phase: Holdback -> Settlement" },
  ];
  let reputation = next.reputation;
  let totalDisbursed = next.fundingRound.totalDisbursedToken;
  const nominations: ImpactNomination[] = [];

  for (const n of next.nominations) {
    if (n.state === "Scored" && n.adjudicationOutcome === "Unchallenged") {
      const provisional = n.provisionalShareToken ?? 0;
      const disbursed = markDisbursed(n, next.tick, provisional);
      nominations.push(disbursed);
      totalDisbursed += provisional;
      events.push({
        tick: next.tick,
        category: "Disbursement",
        message: `Disbursed ${provisional.toFixed(4)} token to ${n.registryEntryId} via ${n.id}`,
      });
      reputation = awardSurvivingRound(
        reputation,
        n.registryEntryId,
        next.pool.id,
        next.pool.parameters.reputationSurvivingDelta,
        next.tick,
        `Survived round ${next.fundingRound.id}`,
      );
      events.push({
        tick: next.tick,
        category: "Reputation",
        message: `Registry ${n.registryEntryId} reputation += ${next.pool.parameters.reputationSurvivingDelta}`,
      });
    } else {
      nominations.push(n);
    }
  }

  return {
    state: {
      ...next,
      nominations,
      reputation,
      disbursementRan: true,
      pool: { ...next.pool, phase: "Settlement" },
      fundingRound: {
        ...next.fundingRound,
        phase: "Settlement",
        totalDisbursedToken: totalDisbursed,
      },
    },
    events,
  };
}
