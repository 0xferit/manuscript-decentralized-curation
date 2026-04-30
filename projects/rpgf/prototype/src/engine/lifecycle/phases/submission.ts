/**
 * Submission-phase actions: amendNomination, retractNominationAction,
 * closeSubmission. Edit window operations + transition to Evaluation.
 */

import {
  amendDuringSubmission,
  retractNomination as retractNom,
  type AmendInput,
} from "../state-machine";
import type { ControllerResult, EngineState } from "../types";
import {
  advanceTick,
  nomById,
  replaceNomination,
} from "./_shared";

export function amendNomination(
  state: EngineState,
  id: string,
  patch: AmendInput,
): ControllerResult {
  const nom = nomById(state, id);
  if (!nom) return { state, events: [] };
  const next = advanceTick(state);
  const updated = amendDuringSubmission(nom, patch, next.tick);
  return {
    state: replaceNomination(next, updated),
    events: [
      { tick: next.tick, category: "Author", message: `Amended ${id}` },
    ],
  };
}

export function retractNominationAction(
  state: EngineState,
  id: string,
): ControllerResult {
  const nom = nomById(state, id);
  if (!nom) return { state, events: [] };
  const next = advanceTick(state);
  const updated = retractNom(nom, next.tick);
  return {
    state: replaceNomination(next, updated),
    events: [
      { tick: next.tick, category: "Author", message: `Retracted ${id}` },
    ],
  };
}

export function closeSubmission(state: EngineState): ControllerResult {
  if (state.pool.phase !== "Submission") {
    return {
      state,
      events: [
        {
          tick: state.tick,
          category: "Phase",
          message: `closeSubmission ignored: phase is ${state.pool.phase}.`,
        },
      ],
    };
  }
  const next = advanceTick(state);
  return {
    state: {
      ...next,
      pool: { ...next.pool, phase: "Evaluation" },
      fundingRound: { ...next.fundingRound, phase: "Evaluation" },
    },
    events: [
      { tick: next.tick, category: "Tick", message: "Submission window closed" },
      {
        tick: next.tick,
        category: "Phase",
        message: "Phase: Submission -> Evaluation",
      },
    ],
  };
}
