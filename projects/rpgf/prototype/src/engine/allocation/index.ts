/**
 * Allocation module: compute money flows from relevance scores; redistribute
 * the debunked share pro-rata to already-disbursed surviving nominations.
 */

export type { AllocationResult, AllocationRow } from "../types";
export type {
  AllocationInput,
  RedistributionInput,
  RedistributionResult,
} from "./allocation";
export {
  computeProvisionalAllocation,
  redistributeDebunkedShare,
} from "./allocation";
