/**
 * expireHoldback: at holdback end, disburse Unchallenged Scored nominations,
 * award reputation, transition pool + funding round to Settlement.
 */

import { awardSurvivingRound } from "@reputation";
import type { ImpactNomination } from "@shared/types";

import { markDisbursed } from "../../state-machine";
import type { ControllerResult, EngineState, LogEvent } from "../../types";
import { advanceTick } from "../_shared";

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
