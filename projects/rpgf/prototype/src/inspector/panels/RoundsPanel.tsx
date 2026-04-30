import type { AppState } from "../store";
import { fmtNum, fmtToken } from "./shared";

interface Props { readonly state: AppState; }

function curatorBandLabel(s: { nonParticipation: boolean; withinBand: boolean }): string {
  if (s.nonParticipation) return "no-show";
  if (s.withinBand) return "in";
  return "out";
}

export function RoundsPanel({ state }: Props) {
  if (state.rounds.length === 0) {
    return (
      <div className="panel">
        <h2>Relevance rounds</h2>
        <em className="muted">No rounds yet. Close submission and run evaluation.</em>
      </div>
    );
  }
  return (
    <div className="panel">
      <h2>Relevance rounds ({state.rounds.length})</h2>
      {state.rounds.map((r) => {
        const nom = state.nominations.find((n) => n.id === r.nominationId);
        return (
          <details key={r.id} className="nom-details">
            <summary>
              <strong>{r.id}</strong>
              <span className={`tag state-${r.phase === "Finalized" ? "Disbursed" : "Disputed"}`}>{r.phase}</span>
              <span className="muted">→ {nom?.id ?? r.nominationId}</span>
              {r.cancellationReason && (
                <span className="tag adj-Debunked">{r.cancellationReason}</span>
              )}
            </summary>
            <div className="kv" style={{ marginTop: 8 }}>
              <dt>Attempt</dt><dd>{r.attemptIndex}</dd>
              <dt>Seats locked</dt><dd>{r.totalSeatsLocked}</dd>
              <dt>mu / sigma</dt>
              <dd>{fmtNum(r.meanScore, 4)} / {fmtNum(r.stdDev, 4)}</dd>
              <dt>sigma_ref</dt><dd>{fmtNum(r.sigmaRef, 4)}</dd>
              <dt>Reward factor</dt><dd>{fmtNum(r.rewardFactor, 3)}</dd>
              <dt>Reserved reward</dt><dd>{fmtToken(r.reservedRewardToken, 6)}</dd>
              <dt>Distributed reward</dt><dd>{fmtToken(r.distributedRewardToken, 6)}</dd>
              <dt>Distance slashing skipped</dt><dd>{r.distanceSlashingSkipped ? "yes" : "no"}</dd>
            </div>
            <h3>Curator round states</h3>
            <table>
              <thead>
                <tr>
                  <th>Curator</th>
                  <th>Seats</th>
                  <th>Weight</th>
                  <th>Behavior</th>
                  <th>Score</th>
                  <th>p_i</th>
                  <th>Slashed</th>
                  <th>Reward</th>
                  <th>Band</th>
                </tr>
              </thead>
              <tbody>
                {r.curatorStates.map((s) => (
                  <tr key={s.curatorId}>
                    <td>{s.curatorId}</td>
                    <td>{s.seats}</td>
                    <td>{fmtToken(s.weight, 4)}</td>
                    <td>{s.behavior}</td>
                    <td>{fmtNum(s.revealedScore, 3)}</td>
                    <td>{fmtNum(s.penaltyFraction, 3)}</td>
                    <td>{fmtToken(s.slashedToken, 6)}</td>
                    <td>{fmtToken(s.rewardToken, 6)}</td>
                    <td>{curatorBandLabel(s)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </details>
        );
      })}
    </div>
  );
}
