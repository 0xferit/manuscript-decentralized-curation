/**
 * Evaluation-phase actions: runEvaluation, enterHoldback.
 *
 * runEvaluation iterates submitted nominations, calls Curation per
 * nomination, applies state-machine transitions, and computes the
 * provisional allocation. enterHoldback advances the pool to the next
 * phase once evaluation has run.
 */

import { computeProvisionalAllocation } from "../../allocation/allocation";
import { evaluateNomination } from "../../curation/round";
import {
  markScored,
  markUnscored,
} from "../state-machine";
import type { ControllerResult, EngineState, LogEvent } from "../types";
import {
  advanceTick,
  applyCuratorUpdates,
  type PhaseDeps,
} from "./_shared";

export function runEvaluation(
  state: EngineState,
  deps: PhaseDeps,
): ControllerResult {
  if (state.pool.phase !== "Evaluation" || state.evaluationRan) {
    return { state, events: [] };
  }
  const next = advanceTick(state);
  let curators = next.curators;
  let emaSigma = next.pool.emaSigma;
  let curationBudget = next.pool.curationBudget;
  let nominations = next.nominations;
  const allRounds = [...next.rounds];
  const events: LogEvent[] = [];

  const submitted = next.nominations.filter((n) => n.state === "Submitted");

  for (const nom of submitted) {
    const result = evaluateNomination({
      poolId: next.pool.id,
      fundingRoundId: next.fundingRound.id,
      nominationId: nom.id,
      curators,
      parameters: next.pool.parameters,
      emaSigmaBefore: emaSigma,
      curationBudgetBefore: curationBudget,
      tick: next.tick,
      baseSeed: deps.baseSeed,
      commitRevealSimulator: deps.commitRevealSimulator,
    });
    curators = applyCuratorUpdates(curators, result.curatorUpdates);
    emaSigma = result.emaSigmaAfter;
    curationBudget = result.curationBudgetAfter;
    allRounds.push(...result.rounds);

    if (result.resolvedAs === "Scored" && result.finalRound) {
      nominations = nominations.map((n) =>
        n.id === nom.id
          ? markScored(n, {
              relevanceScore: result.finalRound!.meanScore ?? 0,
              relevanceRoundId: result.finalRound!.id,
              tick: next.tick,
            })
          : n,
      );
      events.push({
        tick: next.tick,
        category: "Engine",
        message: `Scored ${nom.id}: mu=${(result.finalRound.meanScore ?? 0).toFixed(3)}, sigma=${(result.finalRound.stdDev ?? 0).toFixed(3)}, low-disp=${result.finalRound.distanceSlashingSkipped}`,
      });
    } else if (result.resolvedAs === "Unscored") {
      nominations = nominations.map((n) =>
        n.id === nom.id ? markUnscored(n, next.tick) : n,
      );
      events.push({
        tick: next.tick,
        category: "Engine",
        message: `Unscored ${nom.id}: quorum failure on retry`,
      });
    } else {
      events.push({
        tick: next.tick,
        category: "Engine",
        message: `Underfunded ${nom.id}: round could not reserve full reward floor`,
      });
    }
  }

  const allocation = computeProvisionalAllocation({
    poolId: next.pool.id,
    roundId: next.fundingRound.id,
    poolFundingBudget: next.pool.fundingBudget,
    nominations,
  });
  nominations = nominations.map((n) => {
    const row = allocation.rows.find((r) => r.nominationId === n.id);
    if (!row || n.state !== "Scored") return n;
    return { ...n, provisionalShareToken: row.provisionalToken };
  });

  events.unshift({
    tick: next.tick,
    category: "Phase",
    message: "Evaluation period executed",
  });
  events.push({
    tick: next.tick,
    category: "Engine",
    message: `Provisional allocation: denominator=${allocation.denominator.toFixed(3)}, rollover=${allocation.rolloverToken.toFixed(4)}`,
  });

  return {
    state: {
      ...next,
      curators,
      rounds: allRounds,
      nominations,
      pool: { ...next.pool, emaSigma, curationBudget },
      allocation,
      evaluationRan: true,
    },
    events,
  };
}

export function enterHoldback(state: EngineState): ControllerResult {
  if (state.pool.phase !== "Evaluation" || !state.evaluationRan) {
    return { state, events: [] };
  }
  const next = advanceTick(state);
  return {
    state: {
      ...next,
      pool: { ...next.pool, phase: "Holdback" },
      fundingRound: {
        ...next.fundingRound,
        phase: "Holdback",
        holdbackEndsAtTick: next.tick + 1,
      },
    },
    events: [
      { tick: next.tick, category: "Tick", message: "Holdback opened" },
      {
        tick: next.tick,
        category: "Phase",
        message: "Phase: Evaluation -> Holdback",
      },
    ],
  };
}
