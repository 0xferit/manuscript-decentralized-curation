import type { AppState } from "../store";

interface Props { state: AppState; }

export function RegistryPanel({ state }: Props) {
  return (
    <div className="panel">
      <h2>Project-beneficiary registry</h2>
      <table>
        <thead>
          <tr>
            <th>Project</th>
            <th>Beneficiary</th>
            <th>Tags</th>
            <th>Reputation</th>
          </tr>
        </thead>
        <tbody>
          {state.registry.map((r) => {
            const ledger = state.reputation.byRegistryEntryId[r.id];
            return (
              <tr key={r.id}>
                <td>
                  <div>{r.projectName}</div>
                  <div className="muted" style={{ fontSize: 10 }}>{r.id}</div>
                </td>
                <td>{r.beneficiaryAddress}</td>
                <td>
                  {r.eligibilityTags.map((t) => (
                    <span key={t} className="tag">{t}</span>
                  ))}
                </td>
                <td>{ledger?.reputation ?? r.reputation}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
