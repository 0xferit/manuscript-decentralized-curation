/**
 * Settlement-phase actions: releaseGraced, closeRound.
 *
 * - releaseGraced: advance grace tick; disburse nominations whose
 *   ChallengeFailed grace window has expired with no new pending challenge.
 * - closeRound: terminal transition to Closed; blocked while any DDR
 *   challenge is still Pending.
 */

import { awardSurvivingRound } from "@reputation";
import { markDisbursed } from "../state-machine";
import type { ControllerResult, EngineState, LogEvent } from "../types";
import { advanceTick } from "./_shared";

export function releaseGraced(state: EngineState): ControllerResult {
  if (state.pool.phase !== "Settlement") {
    return { state, events: [] };
  }
  const next = advanceTick(state);
  const events: LogEvent[] = [
    {
      tick: next.tick,
      category: "Phase",
      message: `Grace tick advanced (now tick ${next.tick})`,
    },
  ];
  let reputation = next.reputation;
  let totalDisbursed = next.fundingRound.totalDisbursedToken;

  const nominations = next.nominations.map((n) => {
    const noOpenChallenge = !next.challenges.some(
      (c) => c.nominationId === n.id && c.status === "Pending",
    );
    if (
      n.state === "Scored" &&
      n.adjudicationOutcome === "ChallengeFailed" &&
      n.graceEndsAtTick !== null &&
      next.tick >= n.graceEndsAtTick &&
      noOpenChallenge
    ) {
      const provisional = n.provisionalShareToken ?? 0;
      totalDisbursed += provisional;
      events.push({
        tick: next.tick,
        category: "Disbursement",
        message: `Grace expired for ${n.id}: disbursed ${provisional.toFixed(4)} token`,
      });
      reputation = awardSurvivingRound(
        reputation,
        n.registryEntryId,
        next.pool.id,
        next.pool.parameters.reputationSurvivingDelta,
        next.tick,
        `Survived round (grace) ${next.fundingRound.id}`,
      );
      return markDisbursed(n, next.tick, provisional);
    }
    return n;
  });

  return {
    state: {
      ...next,
      nominations,
      reputation,
      fundingRound: {
        ...next.fundingRound,
        totalDisbursedToken: totalDisbursed,
      },
    },
    events,
  };
}

export function closeRound(state: EngineState): ControllerResult {
  const stillOpen = state.challenges.some((c) => c.status === "Pending");
  if (stillOpen) {
    return {
      state,
      events: [
        {
          tick: state.tick,
          category: "Phase",
          message: "Cannot close round: pending DDR challenges remain.",
        },
      ],
    };
  }
  const next = advanceTick(state);
  return {
    state: {
      ...next,
      pool: { ...next.pool, phase: "Closed" },
      fundingRound: {
        ...next.fundingRound,
        phase: "Closed",
        finalizedAtTick: next.tick,
      },
    },
    events: [{ tick: next.tick, category: "Phase", message: "Round closed" }],
  };
}
