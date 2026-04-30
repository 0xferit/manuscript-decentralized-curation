import type { AppState } from "../store";
import { fmtNum, fmtToken } from "./shared";

interface Props { readonly state: AppState; }

export function CuratorsPanel({ state }: Props) {
  const L = state.pool.parameters.seatSizeL;
  const lastRoundByCurator = new Map<string, number>();
  for (const r of state.rounds) {
    for (const s of r.curatorStates) {
      lastRoundByCurator.set(s.curatorId, (lastRoundByCurator.get(s.curatorId) ?? 0) + s.seats);
    }
  }

  return (
    <div className="panel">
      <h2>Curator pool ({state.curators.length})</h2>
      <table>
        <thead>
          <tr>
            <th>Curator</th>
            <th>Archetype</th>
            <th>Behavior</th>
            <th>Deposit</th>
            <th>Tickets</th>
            <th>Total seats</th>
            <th>Score</th>
            <th>+ rewards</th>
            <th>- slashed</th>
          </tr>
        </thead>
        <tbody>
          {state.curators.map((c) => {
            const tickets = Math.floor(c.depositedToken / L);
            const totalSeats = lastRoundByCurator.get(c.id) ?? 0;
            return (
              <tr key={c.id}>
                <td>
                  <div>{c.displayName}</div>
                  <div className="muted" style={{ fontSize: 10 }}>{c.id}</div>
                </td>
                <td>{c.archetype}</td>
                <td>{c.commitRevealBehavior}</td>
                <td>{fmtToken(c.depositedToken)}</td>
                <td>{tickets}</td>
                <td>{totalSeats}</td>
                <td>{fmtNum(c.intendedScore, 2)}</td>
                <td>{fmtToken(c.totalRewardsToken, 6)}</td>
                <td>{fmtToken(c.totalSlashedToken, 6)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
