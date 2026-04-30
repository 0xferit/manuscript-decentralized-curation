import type { AppState } from "../store";

interface Props { state: AppState; }

export function ReputationPanel({ state }: Props) {
  const entries = Object.values(state.reputation.byRegistryEntryId);
  return (
    <div className="panel">
      <h2>Reputation ledger</h2>
      <p className="muted" style={{ fontSize: 11 }}>
        Pool-scoped, per-registry-entry. +1 surviving, -5 debunked, decay 1 / epoch toward 0.
        Click "Tick reputation epoch" in the header to apply decay.
      </p>
      <table>
        <thead>
          <tr>
            <th>Registry entry</th>
            <th>Reputation</th>
            <th>Last events</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e) => (
            <tr key={e.registryEntryId}>
              <td>{e.registryEntryId}</td>
              <td>{e.reputation}</td>
              <td className="muted" style={{ fontSize: 11 }}>
                {e.history.slice(-4).map((h, i) => (
                  <div key={i}>
                    tick {h.tick} {h.reason} {h.delta > 0 ? "+" : ""}{h.delta} → {h.newValue}
                  </div>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
