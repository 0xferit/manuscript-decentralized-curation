import type { Token } from "./token";

export type CuratorArchetype = "Honest" | "Lazy" | "Adversary";

export type CommitRevealBehavior = "CommitAndReveal" | "CommitOnly" | "NoShow";

/**
 * CuratorIdentity holds the immutable, Bootstrap-owned identity fields of
 * a curator. Once seeded, no module mutates these.
 */
export interface CuratorIdentity {
  id: string;
  displayName: string;
  archetype: CuratorArchetype;
  commitRevealBehavior: CommitRevealBehavior;
  intendedScore: number;
}

/**
 * Backwards-compatible alias used during the incremental refactor. The
 * legacy `Curator` type is the union of identity + financial state. Once
 * call sites are migrated, this alias and the financial fields below will
 * move into `engine/curation/types.ts` as `CuratorFinancialState`.
 */
export interface Curator extends CuratorIdentity {
  depositedToken: Token;
  lockedToken: Token;
  totalRewardsToken: Token;
  totalSlashedToken: Token;
}
