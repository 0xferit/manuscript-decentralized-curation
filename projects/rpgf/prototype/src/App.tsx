import { useAppStore } from "./store";
import { PoolPanel } from "./ui/PoolPanel";
import { TimelinePanel } from "./ui/TimelinePanel";
import { RegistryPanel } from "./ui/RegistryPanel";
import { CuratorsPanel } from "./ui/CuratorsPanel";
import { NominationsPanel } from "./ui/NominationsPanel";
import { RoundsPanel } from "./ui/RoundsPanel";
import { AllocationPanel } from "./ui/AllocationPanel";
import { ChallengesPanel } from "./ui/ChallengesPanel";
import { ReputationPanel } from "./ui/ReputationPanel";
import { LogPanel } from "./ui/LogPanel";

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
