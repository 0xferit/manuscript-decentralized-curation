/**
 * Thin React state container around the engine controller.
 *
 * The store does three things only:
 *   1. Hold an `AppState` (engine state plus the UI log) in `useState`.
 *   2. Wrap each controller call with `setState` and event-list merge.
 *   3. Bootstrap deterministic seed data on mount and Reset.
 *
 * Domain logic lives in `engine/controller.ts`. Anything more than a
 * pass-through here is a smell; refactor it back into the controller.
 */

import { useCallback, useEffect, useState } from "react";

import {
  makeDefaultPhaseDeps,
  makeInitialEngineState,
  phaseController,
  type AmendInput,
  type ChallengeReason,
  type ControllerResult,
  type DDROutcome,
  type EngineState,
  type LogEvent,
  type PhaseDeps,
} from "@lifecycle";

export type AppState = EngineState & { log: LogEvent[] };

export interface AppActions {
  amend: (id: string, patch: AmendInput) => void;
  retract: (id: string) => void;
  closeSubmission: () => void;
  runEvaluation: () => void;
  enterHoldback: () => void;
  fileChallenge: (input: {
    nominationId: string;
    challengerId: string;
    reason: ChallengeReason;
    newEvidenceNote?: string;
  }) => void;
  resolveDDR: (challengeId: string, outcome: DDROutcome, note?: string) => void;
  expireHoldback: () => void;
  releaseGraced: () => void;
  closeRound: () => void;
  decayReputation: () => void;
  reset: () => void;
}

const DEFAULT_DEPS: PhaseDeps = makeDefaultPhaseDeps();

function initialAppState(): AppState {
  const engine = makeInitialEngineState();
  return {
    ...engine,
    log: [
      {
        tick: 0,
        category: "Phase",
        message: `Pool ${engine.pool.name} created. Phase = Submission. Funding budget ${engine.pool.fundingBudget.toFixed(4)} token, curation budget ${engine.pool.curationBudget.toFixed(4)} token.`,
      },
    ],
  };
}

function applyControllerResult(
  prev: AppState,
  result: ControllerResult,
): AppState {
  return {
    ...result.state,
    log: [...prev.log, ...result.events],
  };
}

export function useAppStore(): { state: AppState; actions: AppActions } {
  const [state, setState] = useState<AppState>(initialAppState);

  useEffect(() => {
    (globalThis as unknown as { __rpgf?: AppState }).__rpgf = state;
  }, [state]);

  const dispatch = useCallback(
    (op: (engine: EngineState) => ControllerResult) => {
      setState((prev) => applyControllerResult(prev, op(prev)));
    },
    [],
  );

  const amend = useCallback(
    (id: string, patch: AmendInput) =>
      dispatch((s) => phaseController.amendNomination(s, id, patch)),
    [dispatch],
  );
  const retract = useCallback(
    (id: string) => dispatch((s) => phaseController.retractNomination(s, id)),
    [dispatch],
  );
  const closeSubmission = useCallback(
    () => dispatch((s) => phaseController.closeSubmission(s)),
    [dispatch],
  );
  const runEvaluation = useCallback(
    () => dispatch((s) => phaseController.runEvaluation(s, DEFAULT_DEPS)),
    [dispatch],
  );
  const enterHoldback = useCallback(
    () => dispatch((s) => phaseController.enterHoldback(s)),
    [dispatch],
  );
  const fileChallenge = useCallback<AppActions["fileChallenge"]>(
    (args) => dispatch((s) => phaseController.fileChallenge(s, args)),
    [dispatch],
  );
  const resolveDDR = useCallback<AppActions["resolveDDR"]>(
    (challengeId, outcome, note) =>
      dispatch((s) =>
        phaseController.resolveDDR(s, challengeId, outcome, DEFAULT_DEPS, note ?? null),
      ),
    [dispatch],
  );
  const expireHoldback = useCallback(
    () => dispatch((s) => phaseController.expireHoldback(s)),
    [dispatch],
  );
  const releaseGraced = useCallback(
    () => dispatch((s) => phaseController.releaseGraced(s)),
    [dispatch],
  );
  const closeRound = useCallback(
    () => dispatch((s) => phaseController.closeRound(s)),
    [dispatch],
  );
  const decayReputation = useCallback(
    () => dispatch((s) => phaseController.decayReputation(s)),
    [dispatch],
  );
  const reset = useCallback(() => setState(initialAppState()), []);

  return {
    state,
    actions: {
      amend,
      retract,
      closeSubmission,
      runEvaluation,
      enterHoldback,
      fileChallenge,
      resolveDDR,
      expireHoldback,
      releaseGraced,
      closeRound,
      decayReputation,
      reset,
    },
  };
}
