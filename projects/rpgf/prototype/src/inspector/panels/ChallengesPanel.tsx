import { useMemo, useState } from "react";

import type { AppActions, AppState } from "../store";
import type { ChallengeReason, DDROutcome } from "@adjudication";
import { fmtToken } from "./shared";

interface Props {
  readonly state: AppState;
  readonly actions: AppActions;
}

const REASONS: ChallengeReason[] = [
  "Debunking",
  "NonFalsifiable",
  "TemplateViolation",
];

const OUTCOMES: DDROutcome[] = ["Debunked", "ChallengeFailed", "Timeout"];

function outcomeButtonClass(outcome: DDROutcome): string {
  if (outcome === "Debunked") return "danger";
  if (outcome === "Timeout") return "warning";
  return "";
}

export function ChallengesPanel({ state, actions }: Props) {
  const challengable = state.nominations.filter(
    (n) => n.state === "Scored" && state.pool.phase === "Holdback",
  );
  const [nominationId, setNominationId] = useState<string>(
    challengable[0]?.id ?? "",
  );
  const [challengerId, setChallengerId] = useState<string>(
    state.curators[0]?.id ?? "",
  );
  const [reason, setReason] = useState<ChallengeReason>("Debunking");
  const [evidenceNote, setEvidenceNote] = useState<string>("");

  const filing = useMemo(() => {
    if (!nominationId) return null;
    return state.nominations.find((n) => n.id === nominationId) ?? null;
  }, [state.nominations, nominationId]);

  return (
    <div className="panel">
      <h2>Challenges + DDR mock</h2>
      <p className="muted" style={{ fontSize: 11 }}>
        Challenges may be filed only against `Scored` nominations during `Holdback`.
        The DDR mock is fully deterministic: pick the outcome.
      </p>

      <h3>File a challenge</h3>
      <div className="flex-row">
        <select
          value={nominationId}
          onChange={(e) => setNominationId(e.target.value)}
          disabled={state.pool.phase !== "Holdback" || challengable.length === 0}
        >
          {challengable.length === 0 && <option value="">(no Scored nominations)</option>}
          {challengable.map((n) => (
            <option key={n.id} value={n.id}>{n.id}</option>
          ))}
        </select>
        <select
          value={challengerId}
          onChange={(e) => setChallengerId(e.target.value)}
        >
          {state.curators.map((c) => (
            <option key={c.id} value={c.id}>{c.displayName} ({c.id})</option>
          ))}
        </select>
        <select
          value={reason}
          onChange={(e) => setReason(e.target.value as ChallengeReason)}
        >
          {REASONS.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        <button
          className="warning"
          onClick={() =>
            actions.fileChallenge({
              nominationId,
              challengerId,
              reason,
              newEvidenceNote: evidenceNote || undefined,
            })
          }
          disabled={!nominationId || state.pool.phase !== "Holdback"}
        >
          File challenge
        </button>
      </div>
      {filing?.adjudicationOutcome === "ChallengeFailed" && (
        <input
          placeholder="Required: cite new evidence (anti-relitigation gate)"
          value={evidenceNote}
          onChange={(e) => setEvidenceNote(e.target.value)}
          style={{ marginTop: 8, width: "100%" }}
        />
      )}

      <h3>Open + resolved challenges</h3>
      {state.challenges.length === 0 ? (
        <em className="muted">no challenges filed</em>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Id</th>
              <th>Nomination</th>
              <th>Challenger</th>
              <th>Reason</th>
              <th>Status</th>
              <th>Counter-stake</th>
              <th>Tax</th>
              <th>Resolve</th>
            </tr>
          </thead>
          <tbody>
            {state.challenges.map((c) => (
              <tr key={c.id}>
                <td>{c.id}</td>
                <td>{c.nominationId}</td>
                <td>{c.challengerId}</td>
                <td>{c.reason}</td>
                <td>{c.status}</td>
                <td>{fmtToken(c.counterStakeToken)}</td>
                <td>{fmtToken(c.taxToken)}</td>
                <td>
                  {c.status === "Pending" ? (
                    <div className="flex-row">
                      {OUTCOMES.map((o) => (
                        <button
                          key={o}
                          onClick={() =>
                            actions.resolveDDR(c.id, o, `mock juror chose ${o}`)
                          }
                          className={outcomeButtonClass(o)}
                        >
                          {o}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <span className="muted">tick {c.resolvedAtTick}</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
