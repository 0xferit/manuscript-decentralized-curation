import type { CommitRevealBehavior, Curator, CuratorArchetype } from "@shared/types";

interface CuratorSpec {
  id: string;
  displayName: string;
  archetype: CuratorArchetype;
  depositedToken: number;
  intendedScore: number;
  commitRevealBehavior: CommitRevealBehavior;
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
