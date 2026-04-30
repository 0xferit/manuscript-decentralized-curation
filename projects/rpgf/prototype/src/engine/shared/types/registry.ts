export interface RegistryEntry {
  id: string;
  projectName: string;
  beneficiaryAddress: string;
  claimantPolicy: string;
  eligibilityTags: string[];
  reputation: number;
  lastReputationUpdateEpoch: number;
}
