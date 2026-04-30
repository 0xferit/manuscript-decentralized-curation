import type { EvidenceItem, ImpactNomination } from "@shared/types";
import { REFERENCE_POOL_PARAMETERS } from "./pool";
import {
  PROTOTYPE_FUNDING_ROUND_ID,
  PROTOTYPE_POOL_ID,
} from "./seed-config";

function makeEvidence(
  id: string,
  cls: EvidenceItem["evidenceClass"],
  caption: string,
  uri: string,
): EvidenceItem {
  return { id, evidenceClass: cls, uri, caption };
}

export function makeNominations(): ImpactNomination[] {
  const tick = 0;
  const round = PROTOTYPE_FUNDING_ROUND_ID;
  const pool = PROTOTYPE_POOL_ID;
  const bond = REFERENCE_POOL_PARAMETERS.submissionBond;

  const clean: ImpactNomination = {
    id: "nom-rollup-bench-q1",
    poolId: pool,
    roundId: round,
    registryEntryId: "reg-rollup-bench",
    authorAddress: "0xAuthorRollupBench",
    state: "Submitted",
    adjudicationOutcome: "Unchallenged",
    bondToken: bond,
    assertions: [
      {
        id: "a-rb-1",
        text: "RollupBench v0.7 was integrated into 8 Ethereum L2 mainnets in Q1 2026.",
        timePeriodStart: "2026-01-01",
        timePeriodEnd: "2026-03-31",
        evidenceItemIds: ["e-rb-onchain", "e-rb-thirdparty"],
        falsifiable: true,
      },
      {
        id: "a-rb-2",
        text: "Released six minor versions on the public registry between 2026-01-01 and 2026-03-31.",
        timePeriodStart: "2026-01-01",
        timePeriodEnd: "2026-03-31",
        evidenceItemIds: ["e-rb-repo"],
        falsifiable: true,
      },
    ],
    evidenceItems: [
      makeEvidence("e-rb-repo", "DirectArtifact", "Release tags on github.com/rollup-bench (mock)", "https://example.test/rb-repo"),
      makeEvidence("e-rb-onchain", "DirectArtifact", "Public deployment txns linking RollupBench to L2s (mock)", "https://example.test/rb-onchain"),
      makeEvidence("e-rb-thirdparty", "IndependentThirdParty", "L2Beat integration entry (mock)", "https://example.test/rb-thirdparty"),
    ],
    createdAtPhaseTick: tick,
    lastUpdatedPhaseTick: tick,
    templateOk: true,
    doubleCountTagIds: [],
    relevanceScore: null,
    relevanceRoundId: null,
    provisionalShareToken: null,
    finalShareToken: null,
    graceEndsAtTick: null,
    challengeIds: [],
  };

  const nonFalsifiable: ImpactNomination = {
    id: "nom-mev-shield-narrative",
    poolId: pool,
    roundId: round,
    registryEntryId: "reg-mev-shield",
    authorAddress: "0xAuthorMevShield",
    state: "Submitted",
    adjudicationOutcome: "Unchallenged",
    bondToken: bond,
    assertions: [
      {
        id: "a-mev-1",
        text: "MEV Shield prevented an estimated $4M of value extraction in 2026.",
        timePeriodStart: "2026-01-01",
        timePeriodEnd: "2026-04-30",
        evidenceItemIds: ["e-mev-self"],
        falsifiable: false,
      },
    ],
    evidenceItems: [
      makeEvidence("e-mev-self", "SelfReported", "MEV Shield team blog with counterfactual estimate (mock)", "https://example.test/mev-blog"),
    ],
    createdAtPhaseTick: tick,
    lastUpdatedPhaseTick: tick,
    templateOk: true,
    doubleCountTagIds: [],
    relevanceScore: null,
    relevanceRoundId: null,
    provisionalShareToken: null,
    finalShareToken: null,
    graceEndsAtTick: null,
    challengeIds: [],
  };

  const templateViolation: ImpactNomination = {
    id: "nom-light-archive-incomplete",
    poolId: pool,
    roundId: round,
    registryEntryId: "reg-light-archive",
    authorAddress: "0xAuthorLightArchive",
    state: "Submitted",
    adjudicationOutcome: "Unchallenged",
    bondToken: bond,
    assertions: [
      {
        id: "a-la-1",
        text: "LightArchive shipped 'a lot' of data services this quarter.",
        timePeriodStart: "2026-01-01",
        timePeriodEnd: "2026-04-30",
        evidenceItemIds: [],
        falsifiable: false,
      },
    ],
    evidenceItems: [],
    createdAtPhaseTick: tick,
    lastUpdatedPhaseTick: tick,
    templateOk: false,
    doubleCountTagIds: [],
    relevanceScore: null,
    relevanceRoundId: null,
    provisionalShareToken: null,
    finalShareToken: null,
    graceEndsAtTick: null,
    challengeIds: [],
  };

  const debunkable: ImpactNomination = {
    id: "nom-modular-vm-bogus-deploy",
    poolId: pool,
    roundId: round,
    registryEntryId: "reg-modular-vm",
    authorAddress: "0xAuthorModularVM",
    state: "Submitted",
    adjudicationOutcome: "Unchallenged",
    bondToken: bond,
    assertions: [
      {
        id: "a-mvm-1",
        text: "ModularVM v3.0 was deployed at 0xMODULARVM... on 2026-02-14.",
        timePeriodStart: "2026-02-14",
        timePeriodEnd: "2026-02-14",
        evidenceItemIds: ["e-mvm-onchain"],
        falsifiable: true,
      },
      {
        id: "a-mvm-2",
        text: "Adopted by 11 named L2 sequencers within 30 days of deployment.",
        timePeriodStart: "2026-02-14",
        timePeriodEnd: "2026-03-16",
        evidenceItemIds: ["e-mvm-self"],
        falsifiable: true,
      },
    ],
    evidenceItems: [
      makeEvidence("e-mvm-onchain", "DirectArtifact", "Claimed deploy tx (mock; chain shows 2026-04-14, not 2026-02-14)", "https://example.test/mvm-onchain"),
      makeEvidence("e-mvm-self", "SelfReported", "Internal sequencer adoption tracker (mock)", "https://example.test/mvm-internal"),
    ],
    createdAtPhaseTick: tick,
    lastUpdatedPhaseTick: tick,
    templateOk: true,
    doubleCountTagIds: ["overlap-l2-vm-fork"],
    relevanceScore: null,
    relevanceRoundId: null,
    provisionalShareToken: null,
    finalShareToken: null,
    graceEndsAtTick: null,
    challengeIds: [],
  };

  const overlap: ImpactNomination = {
    id: "nom-graphlens-vm-coverage",
    poolId: pool,
    roundId: round,
    registryEntryId: "reg-graphlens",
    authorAddress: "0xAuthorGraphLens",
    state: "Submitted",
    adjudicationOutcome: "Unchallenged",
    bondToken: bond,
    assertions: [
      {
        id: "a-gl-1",
        text: "GraphLens published 200 dashboards covering ModularVM-fork sequencer adoption in Q1 2026.",
        timePeriodStart: "2026-01-01",
        timePeriodEnd: "2026-03-31",
        evidenceItemIds: ["e-gl-third"],
        falsifiable: true,
      },
    ],
    evidenceItems: [
      makeEvidence("e-gl-third", "IndependentThirdParty", "GraphLens public dashboards index (mock)", "https://example.test/gl-public"),
    ],
    createdAtPhaseTick: tick,
    lastUpdatedPhaseTick: tick,
    templateOk: true,
    doubleCountTagIds: ["overlap-l2-vm-fork"],
    relevanceScore: null,
    relevanceRoundId: null,
    provisionalShareToken: null,
    finalShareToken: null,
    graceEndsAtTick: null,
    challengeIds: [],
  };

  return [clean, nonFalsifiable, templateViolation, debunkable, overlap];
}
