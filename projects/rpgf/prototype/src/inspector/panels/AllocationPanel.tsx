import type { AppState } from "../store";
import { fmtNum, fmtPct, fmtToken } from "./shared";

interface Props { readonly state: AppState; }

export function AllocationPanel({ state }: Props) {
  const allocation = state.allocation;
  if (!allocation) {
    return (
      <div className="panel">
        <h2>Provisional allocation</h2>
        <em className="muted">Run evaluation to compute allocation.</em>
      </div>
    );
  }
  const maxShare = Math.max(...allocation.rows.map((r) => r.share), 0.0001);
  return (
    <div className="panel">
      <h2>Allocation vector</h2>
      <div className="kv">
        <dt>Funding budget</dt><dd>{fmtToken(allocation.poolFundingBudget)} token</dd>
        <dt>Denominator (sum of relevance)</dt><dd>{fmtNum(allocation.denominator, 4)}</dd>
        <dt>Rollover</dt><dd>{fmtToken(allocation.rolloverToken)} token</dd>
      </div>
      <table>
        <thead>
          <tr>
            <th>Nomination</th>
            <th>Registry entry</th>
            <th>State</th>
            <th>Score</th>
            <th>Share</th>
            <th>Provisional</th>
            <th>Final</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {allocation.rows.map((row) => {
            const nom = state.nominations.find((n) => n.id === row.nominationId);
            const live = nom?.state ?? row.state;
            return (
              <tr key={row.nominationId}>
                <td>{row.nominationId}</td>
                <td>{row.registryEntryId}</td>
                <td><span className={`tag state-${live}`}>{live}</span></td>
                <td>{fmtNum(row.relevanceScore, 3)}</td>
                <td>{fmtPct(row.share)}</td>
                <td>{fmtToken(row.provisionalToken, 4)}</td>
                <td>{fmtToken(nom?.finalShareToken ?? row.finalToken, 4)}</td>
                <td style={{ width: "20%" }}>
                  <div className="bar">
                    <span style={{ width: `${(row.share / maxShare) * 100}%` }} />
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
