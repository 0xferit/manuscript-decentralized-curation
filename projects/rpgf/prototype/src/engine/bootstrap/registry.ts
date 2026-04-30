import type { RegistryEntry } from "@shared/types";

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
