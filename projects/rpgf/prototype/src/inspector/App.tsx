import { useAppStore } from "./store";
import { PoolPanel } from "./panels/PoolPanel";
import { TimelinePanel } from "./panels/TimelinePanel";
import { RegistryPanel } from "./panels/RegistryPanel";
import { CuratorsPanel } from "./panels/CuratorsPanel";
import { NominationsPanel } from "./panels/NominationsPanel";
import { RoundsPanel } from "./panels/RoundsPanel";
import { AllocationPanel } from "./panels/AllocationPanel";
import { ChallengesPanel } from "./panels/ChallengesPanel";
import { ReputationPanel } from "./panels/ReputationPanel";
import { LogPanel } from "./panels/LogPanel";

export function App() {
  const { state, actions } = useAppStore();
  return (
    <div>
      <header className="app-header">
        <h1>RPGF Decentralized Curation Prototype</h1>
        <span className="phase-pill">{state.pool.phase}</span>
        <div className="header-meta">
          <span>tick {state.tick}</span>
          <span>epoch {state.epoch}</span>
          <span>pool {state.pool.id}</span>
          <span>round {state.fundingRound.id} (#{state.fundingRound.index})</span>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <button onClick={actions.decayReputation}>Tick reputation epoch</button>
          <button className="warning" onClick={actions.reset}>
            Reset
          </button>
        </div>
      </header>

      <div className="layout">
        <div className="column">
          <TimelinePanel state={state} actions={actions} />
          <PoolPanel state={state} />
          <RegistryPanel state={state} />
          <CuratorsPanel state={state} />
          <ReputationPanel state={state} />
        </div>
        <div className="column">
          <NominationsPanel state={state} actions={actions} />
          <RoundsPanel state={state} />
          <AllocationPanel state={state} />
          <ChallengesPanel state={state} actions={actions} />
          <LogPanel state={state} />
        </div>
      </div>
    </div>
  );
}
