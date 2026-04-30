/**
 * Allocation module: canonical types.
 *
 * Owns: AllocationRow, AllocationResult.
 */

import type { NominationState } from "@shared/types";

export interface AllocationRow {
  nominationId: string;
  registryEntryId: string;
  relevanceScore: number;
  share: number;
  provisionalToken: number;
  finalToken: number | null;
  state: NominationState;
}

export interface AllocationResult {
  poolId: string;
  roundId: string;
  poolFundingBudget: number;
  denominator: number;
  rolloverToken: number;
  rows: AllocationRow[];
}
