/**
 * Provisional allocation and debunked-share redistribution.
 *
 * Specification:
 *   nominationFunding = (relevanceScore_i / sum(relevanceScore_j over surviving j)) * poolFundingBudget
 *
 * If the denominator is zero, no allocation is made and the budget rolls
 * over to the next funding round.
 *
 * Redistribution of debunked shares is pro-rata over relevance score across
 * already-disbursed surviving nominations. If no disbursed nominations exist
 * at debunk time, the freed share rolls over.
 */

import type {
  AllocationResult,
  AllocationRow,
  ImpactNomination,
  Token,
} from "./types";

export interface AllocationInput {
  poolId: string;
  roundId: string;
  poolFundingBudget: Token;
  nominations: ImpactNomination[];
}

export function computeProvisionalAllocation(
  input: AllocationInput,
): AllocationResult {
  const { poolId, roundId, poolFundingBudget, nominations } = input;
  const eligible = nominations.filter(
    (n) =>
      n.state !== "Retracted" &&
      n.state !== "Unscored" &&
      n.relevanceScore !== null,
  );
  const denominator = eligible.reduce(
    (sum, n) => sum + (n.relevanceScore ?? 0),
    0,
  );

  if (denominator <= 0) {
    return {
      poolId,
      roundId,
      poolFundingBudget,
      denominator: 0,
      rolloverToken: poolFundingBudget,
      rows: nominations.map((n) => ({
        nominationId: n.id,
        registryEntryId: n.registryEntryId,
        relevanceScore: n.relevanceScore ?? 0,
        share: 0,
        provisionalToken: 0,
        finalToken: null,
        state: n.state,
      })),
    };
  }

  const rows: AllocationRow[] = nominations.map((n) => {
    if (
      n.state === "Retracted" ||
      n.state === "Unscored" ||
      n.relevanceScore === null
    ) {
      return {
        nominationId: n.id,
        registryEntryId: n.registryEntryId,
        relevanceScore: n.relevanceScore ?? 0,
        share: 0,
        provisionalToken: 0,
        finalToken: n.finalShareToken,
        state: n.state,
      };
    }
    const share = n.relevanceScore / denominator;
    const provisional = share * poolFundingBudget;
    return {
      nominationId: n.id,
      registryEntryId: n.registryEntryId,
      relevanceScore: n.relevanceScore,
      share,
      provisionalToken: provisional,
      finalToken: n.finalShareToken,
      state: n.state,
    };
  });

  return {
    poolId,
    roundId,
    poolFundingBudget,
    denominator,
    rolloverToken: 0,
    rows,
  };
}

export interface RedistributionInput {
  freedShareToken: Token;
  survivingDisbursed: ImpactNomination[];
}

export interface RedistributionResult {
  topUps: Array<{
    nominationId: string;
    registryEntryId: string;
    extraToken: Token;
  }>;
  rolloverToken: Token;
  denominator: number;
}

export function redistributeDebunkedShare(
  input: RedistributionInput,
): RedistributionResult {
  const { freedShareToken, survivingDisbursed } = input;
  const denominator = survivingDisbursed.reduce(
    (sum, n) => sum + (n.relevanceScore ?? 0),
    0,
  );
  if (denominator <= 0 || survivingDisbursed.length === 0) {
    return { topUps: [], rolloverToken: freedShareToken, denominator };
  }
  let allocated = 0;
  const topUps = survivingDisbursed.map((n) => {
    const share = (n.relevanceScore ?? 0) / denominator;
    const extra = share * freedShareToken;
    allocated += extra;
    return {
      nominationId: n.id,
      registryEntryId: n.registryEntryId,
      extraToken: extra,
    };
  });
  const rolloverToken = Math.max(0, freedShareToken - allocated);
  return { topUps, rolloverToken, denominator };
}
