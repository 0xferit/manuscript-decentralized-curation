# Architecture

This document maps the prototype's structure using standard software-modeling
diagrams: a C4-style **container diagram** for the high-level shape, a
**component diagram** for the engine internals, a **package diagram** for
folder grouping, a **sequence diagram** for runtime flow, and **class
diagrams** for the swap-point interfaces. Every diagram is Mermaid; renders
in IntelliJ (with the Mermaid plugin), GitHub, and Quarto without extra
tooling.

---

## 1. Container diagram (system shape)

Shows the deployable units of the prototype and the external systems they
adapt. Production swaps the two adapters; everything else stays.

```mermaid
flowchart TB
  user(["Reviewer<br/>(browser)"])

  subgraph proto["RPGF Prototype (single-page Vite app)"]
    direction TB
    ui["UI Layer<br/><i>React panels</i>"]
    store["State Container<br/><i>store.ts</i>"]
    engine["Domain Engine<br/><i>pure TypeScript</i>"]
  end

  subgraph external["External systems (adapters in v2)"]
    direction TB
    ddr["DDR Provider<br/><i>e.g. Kleros v1</i>"]
    cr["On-chain Commit-Reveal<br/><i>EVM contract</i>"]
  end

  user -->|clicks, reads| ui
  ui -->|actions| store
  store -->|dispatch| engine
  engine -.->|DDRResolver iface| ddr
  engine -.->|CommitRevealSimulator iface| cr

  classDef ext stroke-dasharray: 5 5,fill:#1f2630,color:#d6dde8
  class ddr,cr ext
```

Solid arrows are direct calls inside the prototype. Dashed arrows are
interface boundaries that today resolve to mock implementations and in
production resolve to chain adapters.

---

## 2. Component diagram (engine internals)

Each component is one or more `.ts` modules with a single responsibility.
Provided interfaces are shown as dashed boxes; the rest are concrete modules.

```mermaid
flowchart TB
  subgraph store_layer["store.ts (React glue)"]
    store["useAppStore"]
  end

  subgraph facade["Phase facade"]
    controller["controller.ts<br/>phaseController"]
  end

  subgraph atoms["Engine atoms (pure)"]
    nom["nomination.ts<br/>state machine"]
    alloc["allocation.ts<br/>alloc + redistribute"]
    rep["reputation.ts<br/>immutable ledger"]
    chal["challenge.ts<br/>filing + payout"]
  end

  subgraph round_layer["Round orchestration"]
    round["round.ts<br/>retry loop"]
    relevance["relevance.ts<br/>pipeline composer"]
  end

  subgraph stages_layer["Stages (per-phase atoms)"]
    s_reserve["reserve"]
    s_draft["drafting.ts"]
    s_cr["commitReveal"]
    s_score["score"]
    s_slash["slash"]
    s_reward["reward"]
  end

  subgraph prim["Primitives"]
    stats["stats.ts"]
    prng["prng.ts"]
  end

  ddr_iface[/"&laquo;interface&raquo;<br/>DDRResolver"/]
  cr_iface[/"&laquo;interface&raquo;<br/>CommitRevealSimulator"/]
  ddr_mock["manualMockDDRResolver"]
  cr_mock["deterministicCommitRevealSimulator"]

  store --> controller
  controller --> nom
  controller --> alloc
  controller --> rep
  controller --> chal
  controller --> round
  controller -. requires .-> ddr_iface
  ddr_mock -. provides .-> ddr_iface

  round --> relevance
  relevance --> s_reserve
  relevance --> s_draft
  relevance -. requires .-> cr_iface
  cr_mock -. provides .-> cr_iface
  relevance --> s_score
  relevance --> s_slash
  relevance --> s_reward

  s_score --> stats
  s_slash --> stats
  s_reward --> stats
  s_draft --> prng

  classDef iface stroke-dasharray: 5 5,fill:#1f2630
  classDef mock fill:#0e1116,stroke:#56d364
  class ddr_iface,cr_iface iface
  class ddr_mock,cr_mock mock
```

The controller is the only multi-step coordinator. Atoms each own one
concern. Stages are sequenced by `relevance.ts`; primitives are leaf
modules with no engine knowledge.

---

## 3. Package diagram (folder grouping)

Maps directly to the on-disk layout. Arrows show allowed cross-package
imports; anything not drawn is forbidden by the dependency layering.

```mermaid
flowchart LR
  subgraph src["src/"]
    direction TB
    ui_pkg["ui/<br/>10 panels + shared.ts"]
    store_pkg["store.ts"]
    subgraph engine_pkg["engine/"]
      direction TB
      atoms_pkg["atoms<br/>nomination · allocation · reputation · challenge"]
      facade_pkg["controller<br/>controller.ts · controllerTypes.ts"]
      round_pkg["round / relevance"]
      stages_pkg["stages/<br/>reserve · commitReveal · score · slash · reward"]
      prim_pkg["primitives<br/>stats · prng · drafting · types · seed · ddr"]
    end
  end

  tests_pkg["tests/<br/>11 spec files"]

  ui_pkg --> store_pkg
  store_pkg --> facade_pkg
  facade_pkg --> atoms_pkg
  facade_pkg --> round_pkg
  facade_pkg --> prim_pkg
  round_pkg --> stages_pkg
  round_pkg --> prim_pkg
  stages_pkg --> prim_pkg
  atoms_pkg --> prim_pkg

  tests_pkg -. tests .-> engine_pkg
```

Constraints encoded by the layout:

- `ui/` may import from `store.ts` only. No direct engine import.
- `store.ts` may import from `engine/` (controller + types only) and
  `engine/seed.ts` for bootstrap. Never engine internals.
- `engine/controller.ts` is the engine's only multi-step coordinator.
- Stages, atoms, and primitives are leaf modules: each may only import
  from its own package and `primitives`.
- `tests/` may import from anywhere in `engine/`; not from `ui/`.

---

## 4. Sequence diagram (runtime: "Run evaluation")

Shows what happens when the reviewer clicks the "Run evaluation" button on
the timeline panel. Other actions follow the same shape: UI dispatches to
store, store calls one controller method, controller composes engine atoms,
result returns up the stack.

```mermaid
sequenceDiagram
  autonumber
  actor U as Reviewer
  participant TL as TimelinePanel
  participant ST as store.ts
  participant CT as phaseController
  participant RD as round.ts
  participant RV as relevance.ts
  participant SG as stages/*
  participant NM as nomination.ts
  participant AL as allocation.ts

  U->>TL: click "Run evaluation"
  TL->>ST: actions.runEvaluation()
  ST->>CT: runEvaluation(state, deps)
  loop for each Submitted nomination
    CT->>RD: evaluateNomination(...)
    loop attempt = 0..1
      RD->>RV: runRelevanceRound(...)
      RV->>SG: reserveRoundReward
      RV->>SG: draftSeats (uses prng)
      RV->>SG: simulator.simulate
      RV->>SG: score (uses stats)
      alt scored
        RV->>SG: applySlashing
        RV->>SG: distributeRoundReward
      else quorumFailure
        RV->>SG: applyNonParticipationOnlySlashing
      end
      RV-->>RD: RelevanceRoundOutcome
    end
    RD-->>CT: EvaluateNominationOutput
    CT->>NM: markScored | markUnscored
  end
  CT->>AL: computeProvisionalAllocation
  CT-->>ST: ControllerResult { state, events }
  ST->>ST: setState(prev → merged)
  ST-->>TL: re-render with new state
```

Key invariants visible in the diagram:

- Every controller call is a single dispatch. The store never coordinates
  multi-step engine flows directly.
- The retry loop lives entirely in `round.ts`; the controller never sees
  individual attempts.
- Stages run in fixed order inside `relevance.ts`. Adding a stage means
  editing one orchestrator, not the controller.

---

## 5. Class diagrams (swap-point interfaces)

The two contracts that production must implement to replace the
prototype's mocks.

```mermaid
classDiagram
  class DDRResolver {
    <<interface>>
    +submit(challenge: Challenge)$ void
    +resolve(input: DDRResolveInput) DDRResolveOutput
  }
  class manualMockDDRResolver {
    +resolve(input) DDRResolveOutput
  }
  class KlerosAdapter {
    <<production>>
    +submit(challenge) void
    +resolve(input) DDRResolveOutput
  }
  DDRResolver <|.. manualMockDDRResolver
  DDRResolver <|.. KlerosAdapter

  class DDRResolveInput {
    +challenge: Challenge
    +ruling: DDROutcome
    +tick: number
    +jurorNote: string|null
  }
  class DDRResolveOutput {
    +challenge: Challenge
    +resolution: DDRResolution
  }
  DDRResolver ..> DDRResolveInput
  DDRResolver ..> DDRResolveOutput
```

```mermaid
classDiagram
  class CommitRevealSimulator {
    <<interface>>
    +simulate(input: CommitRevealInput) CuratorRoundState[]
  }
  class deterministicCommitRevealSimulator {
    +simulate(input) CuratorRoundState[]
  }
  class OnChainCommitRevealAdapter {
    <<production>>
    +simulate(input) CuratorRoundState[]
  }
  CommitRevealSimulator <|.. deterministicCommitRevealSimulator
  CommitRevealSimulator <|.. OnChainCommitRevealAdapter
```

```mermaid
classDiagram
  class PhaseController {
    +amendNomination(state, id, patch) ControllerResult
    +retractNomination(state, id) ControllerResult
    +closeSubmission(state) ControllerResult
    +runEvaluation(state, deps) ControllerResult
    +enterHoldback(state) ControllerResult
    +fileChallenge(state, args) ControllerResult
    +resolveDDR(state, id, outcome, deps) ControllerResult
    +expireHoldback(state) ControllerResult
    +releaseGraced(state) ControllerResult
    +closeRound(state) ControllerResult
    +decayReputation(state) ControllerResult
  }
  class EngineState {
    +pool: Pool
    +registry: RegistryEntry[]
    +curators: Curator[]
    +nominations: ImpactNomination[]
    +challenges: Challenge[]
    +rounds: RelevanceRound[]
    +fundingRound: FundingRound
    +reputation: ReputationLedger
    +allocation: AllocationResult|null
    +tick: number
    +epoch: number
    +evaluationRan: boolean
    +disbursementRan: boolean
  }
  class ControllerResult {
    +state: EngineState
    +events: LogEvent[]
  }
  class PhaseDeps {
    +baseSeed: string
    +ddr?: DDRResolver
    +commitRevealSimulator?: CommitRevealSimulator
  }
  PhaseController ..> EngineState
  PhaseController ..> ControllerResult
  PhaseController ..> PhaseDeps
```

Every public type listed here corresponds to one exported declaration in
`src/engine/`. Tests pin each contract: `tests/ddr.test.ts` covers the
DDR boundary, `tests/stages.test.ts` covers the simulator boundary, and
`tests/controller.test.ts` covers the controller surface plus its
immutability invariant.

---

## Diagram choice rationale

| Diagram | Purpose here | Standard intent |
|---|---|---|
| Container | Show the prototype as one deployable unit and its external adapters | C4 level 2: deployable runtime units |
| Component | Show the modules inside the engine and which interfaces they require/provide | C4 level 3 / UML 2 component diagram |
| Package | Show folder/namespace grouping and the layering rules | UML 2 package diagram |
| Sequence | Show one user action's call path through the system | UML 2 interaction diagram |
| Class | Pin the swap-point interface contracts | UML 2 class diagram |

This set covers structure (packages, components, classes), runtime
behavior (sequence), and deployment/integration boundaries (container).
Sufficient for any future work to be planned against a fixed surface.
