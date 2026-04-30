import type { Token } from "./token";

export type CuratorArchetype = "Honest" | "Lazy" | "Adversary";

export type CommitRevealBehavior = "CommitAndReveal" | "CommitOnly" | "NoShow";

/**
 * Single Curator type kept whole for backwards compatibility during the
 * incremental refactor. Step 4 splits this into CuratorIdentity (this file,
 * shared kernel) and CuratorFinancialState (curation/types.ts).
 */
export interface Curator {
  id: string;
  displayName: string;
  archetype: CuratorArchetype;
  depositedToken: Token;
  lockedToken: Token;
  commitRevealBehavior: CommitRevealBehavior;
  intendedScore: number;
  totalRewardsToken: Token;
  totalSlashedToken: Token;
}
