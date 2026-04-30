import type { AppActions, AppState } from "../store";

interface Props {
  readonly state: AppState;
  readonly actions: AppActions;
}

const STAGES = [
  { id: "Submission", label: "Submission" },
  { id: "Evaluation", label: "Evaluation" },
  { id: "Holdback", label: "Holdback" },
  { id: "Settlement", label: "Settlement" },
  { id: "Closed", label: "Closed" },
] as const;

export function TimelinePanel({ state, actions }: Props) {
  const phase = state.pool.phase;
  const evaluationDone = state.evaluationRan;
  const disbursementDone = state.disbursementRan;
  const pendingChallenges = state.challenges.filter((c) => c.status === "Pending").length;
  const submittedNominations = state.nominations.filter(
    (n) => n.state === "Submitted",
  ).length;
  const disputedNominations = state.nominations.filter(
    (n) => n.state === "Disputed",
  ).length;

  return (
    <div className="panel">
      <h2>Round timeline</h2>
      <div className="timeline">
        {STAGES.map((s) => (
          <div key={s.id} className={`stage${s.id === phase ? " active" : ""}`}>
            {s.label}
          </div>
        ))}
      </div>
      <h3>Drive the round</h3>
      <div className="flex-row">
        <button
          onClick={actions.closeSubmission}
          disabled={phase !== "Submission"}
        >
          1. Close submission ({submittedNominations} active)
        </button>
        <button
          className="primary"
          onClick={actions.runEvaluation}
          disabled={phase !== "Evaluation" || evaluationDone}
        >
          2. Run evaluation
        </button>
        <button
          onClick={actions.enterHoldback}
          disabled={phase !== "Evaluation" || !evaluationDone}
        >
          3. Open holdback
        </button>
        <button
          onClick={actions.expireHoldback}
          disabled={phase !== "Holdback"}
        >
          4. Expire holdback ({disputedNominations} disputed)
        </button>
        <button
          onClick={actions.releaseGraced}
          disabled={phase !== "Settlement" || !disbursementDone}
        >
          5. Advance grace tick
        </button>
        <button
          onClick={actions.closeRound}
          disabled={phase === "Closed" || pendingChallenges > 0}
        >
          6. Close round
        </button>
      </div>
    </div>
  );
}
