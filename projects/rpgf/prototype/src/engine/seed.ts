/**
 * Deterministic seed data for the RPGF prototype.
 *
 * Produces:
 *   - 1 pool with reference parameters (`projects/rpgf/design.md` Reference
 *     RPGF Pool Profile, with prototype-specific time scaling).
 *   - 5 registry entries.
 *   - 5 nominations (one clean, one non-falsifiable, one template-violation,
 *     one debunkable, one with overlapping/double-counting credit).
 *   - 16 curators with varied stake and varied commit-reveal behaviors.
 */

import type {
  Curator,
  EvidenceItem,
  ImpactNomination,
  Pool,
  PoolParameters,
  RegistryEntry,
} from "./types";

export const PROTOTYPE_POOL_ID = "pool-eth-infra-2026-q2";
export const PROTOTYPE_FUNDING_ROUND_ID = "fr-eth-infra-2026-q2-r1";
export const PROTOTYPE_BASE_SEED = "rpgf-prototype-deterministic-seed";

export const REFERENCE_POOL_PARAMETERS: PoolParameters = {
  poolFundingBudget: 100,
  curationBudgetReservePct: 0.05,
  submissionBond: 0.01,
  challengeCounterStakeMin: 0.01,
  challengeCounterStakePct: 0.25,
  challengeTaxPct: 0.005,
  ddrFee: 0,
  graceTicks: 1,
  draftedSeats: 15,
  minRevealQuorum: 5,
  seatSizeL: 0.01,
  coherenceK: 1.25,
  epsilonSigma: 0.02,
  rho: 0.3,
  roundRewardFloor: 0.01,
  sigmaRefAlpha: 0.05,
  reputationSurvivingDelta: 1,
  reputationDebunkedDelta: -5,
  reputationDecayPerEpoch: 1,
  minReputationGate: -5,
};

export function makePool(): Pool {
  const params = REFERENCE_POOL_PARAMETERS;
  const fundingBudget = params.poolFundingBudget;
  const curationBudget = fundingBudget * params.curationBudgetReservePct;
  return {
    id: PROTOTYPE_POOL_ID,
    name: "Ethereum Infrastructure (Reference RPGF Pool)",
    registryId: "registry-eth-infra",
    parameters: params,
    curationBudget,
    fundingBudget: fundingBudget - curationBudget,
    emaSigma: 0,
    phase: "Submission",
    currentRoundId: PROTOTYPE_FUNDING_ROUND_ID,
    budgetRolloverToken: 0,
  };
}

export function makeRegistry(): RegistryEntry[] {
  return [
    {
      id: "reg-rollup-bench",
      projectName: "RollupBench",
      beneficiaryAddress: "0xRollupBenchTreasury",
      claimantPolicy: "Maintainer multi-sig (>= 2 of 3) may activate.",
      eligibilityTags: ["ethereum-l2", "open-source", "developer-tooling"],
      reputation: 0,
      lastReputationUpdateEpoch: 0,
    },
    {
      id: "reg-mev-shield",
      projectName: "MEV Shield",
      beneficiaryAddress: "0xMevShieldGnosis",
      claimantPolicy: "Lead author with on-chain attestation.",
      eligibilityTags: ["ethereum-l1", "infrastructure", "security"],
      reputation: 0,
      lastReputationUpdateEpoch: 0,
    },
    {
      id: "reg-light-archive",
      projectName: "LightArchive",
      beneficiaryAddress: "0xLightArchiveSafe",
      claimantPolicy: "Single registered maintainer.",
      eligibilityTags: ["ethereum-l1", "data-availability", "open-source"],
      reputation: 0,
      lastReputationUpdateEpoch: 0,
    },
    {
      id: "reg-modular-vm",
      projectName: "ModularVM",
      beneficiaryAddress: "0xModularVMOps",
      claimantPolicy: "DAO vote required to activate.",
      eligibilityTags: ["ethereum-l2", "vm", "open-source"],
      reputation: 0,
      lastReputationUpdateEpoch: 0,
    },
    {
      id: "reg-graphlens",
      projectName: "GraphLens",
      beneficiaryAddress: "0xGraphLensTreasury",
      claimantPolicy: "Two-of-three maintainer multi-sig.",
      eligibilityTags: ["analytics", "developer-tooling"],
      reputation: 0,
      lastReputationUpdateEpoch: 0,
    },
  ];
}

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

interface CuratorSpec {
  id: string;
  displayName: string;
  archetype: Curator["archetype"];
  depositedToken: number;
  intendedScore: number;
  commitRevealBehavior: Curator["commitRevealBehavior"];
}

const CURATOR_SPECS: CuratorSpec[] = [
  { id: "cur-anya",   displayName: "Anya",   archetype: "Honest",    depositedToken: 0.20, intendedScore: 0.78, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-bram",   displayName: "Bram",   archetype: "Honest",    depositedToken: 0.18, intendedScore: 0.74, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-cleo",   displayName: "Cleo",   archetype: "Honest",    depositedToken: 0.15, intendedScore: 0.82, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-deva",   displayName: "Deva",   archetype: "Honest",    depositedToken: 0.12, intendedScore: 0.76, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-eda",    displayName: "Eda",    archetype: "Honest",    depositedToken: 0.10, intendedScore: 0.80, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-finn",   displayName: "Finn",   archetype: "Honest",    depositedToken: 0.10, intendedScore: 0.72, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-gita",   displayName: "Gita",   archetype: "Honest",    depositedToken: 0.09, intendedScore: 0.68, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-hugo",   displayName: "Hugo",   archetype: "Honest",    depositedToken: 0.08, intendedScore: 0.84, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-iris",   displayName: "Iris",   archetype: "Honest",    depositedToken: 0.08, intendedScore: 0.70, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-jaro",   displayName: "Jaro",   archetype: "Honest",    depositedToken: 0.07, intendedScore: 0.74, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-kira",   displayName: "Kira",   archetype: "Honest",    depositedToken: 0.07, intendedScore: 0.72, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-lior",   displayName: "Lior",   archetype: "Honest",    depositedToken: 0.06, intendedScore: 0.66, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-mona",   displayName: "Mona",   archetype: "Lazy",      depositedToken: 0.05, intendedScore: 0.50, commitRevealBehavior: "CommitOnly" },
  { id: "cur-nox",    displayName: "Nox",    archetype: "Lazy",      depositedToken: 0.04, intendedScore: 0.40, commitRevealBehavior: "NoShow" },
  { id: "cur-orin",   displayName: "Orin",   archetype: "Adversary", depositedToken: 0.06, intendedScore: 0.05, commitRevealBehavior: "CommitAndReveal" },
  { id: "cur-pia",    displayName: "Pia",    archetype: "Adversary", depositedToken: 0.06, intendedScore: 0.99, commitRevealBehavior: "CommitAndReveal" },
];

export function makeCurators(): Curator[] {
  return CURATOR_SPECS.map((s) => ({
    id: s.id,
    displayName: s.displayName,
    archetype: s.archetype,
    depositedToken: s.depositedToken,
    lockedToken: 0,
    commitRevealBehavior: s.commitRevealBehavior,
    intendedScore: s.intendedScore,
    totalRewardsToken: 0,
    totalSlashedToken: 0,
  }));
}
