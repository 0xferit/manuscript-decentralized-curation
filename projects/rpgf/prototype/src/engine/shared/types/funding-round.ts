import type { PoolPhase } from "./pool";

export interface FundingRound {
  id: string;
  poolId: string;
  index: number;
  phase: PoolPhase;
  nominationIds: string[];
  holdbackEndsAtTick: number | null;
  finalizedAtTick: number | null;
  totalDisbursedToken: number;
  rolloverToken: number;
}
