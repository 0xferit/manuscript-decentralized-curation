/**
 * Stage: slashing (graduated distance slashing + non-participation slashing).
 *
 * Boundary contract: mutates a copy of the curator state list, returning the
 * updated list. Distance slashing is skipped when `distanceSlashingSkipped`
 * is true (low-dispersion guard); non-participation slashing always applies.
 */

import type { CuratorRoundState, PoolParameters } from "../types";
import { graduatedPenaltyFraction } from "../stats";

const TOKEN_FLOOR_PRECISION = 1e9;

function floorTokens(value: number): number {
  return Math.floor(value * TOKEN_FLOOR_PRECISION) / TOKEN_FLOOR_PRECISION;
}

export interface SlashInput {
  states: CuratorRoundState[];
  parameters: PoolParameters;
  mu: number;
  sigma: number;
  distanceSlashingSkipped: boolean;
}

export interface SlashOutput {
  states: CuratorRoundState[];
  totalSlashedFromValid: number;
}

export function applySlashing(input: SlashInput): SlashOutput {
  const { states, parameters, mu, sigma, distanceSlashingSkipped } = input;
  const next: CuratorRoundState[] = states.map((s) => ({ ...s }));
  let totalSlashedFromValid = 0;

  for (const s of next) {
    if (!s.revealed || s.revealedScore === null) continue;
    if (distanceSlashingSkipped) {
      s.penaltyFraction = 0;
      s.withinBand = true;
      s.slashedToken = 0;
      continue;
    }
    const p = graduatedPenaltyFraction(
      s.revealedScore,
      mu,
      sigma,
      parameters.coherenceK,
    );
    s.penaltyFraction = p;
    s.withinBand = p === 0;
    s.slashedToken = floorTokens(p * s.weight);
    totalSlashedFromValid += s.slashedToken;
  }

  for (const s of next) {
    if (!s.nonParticipation) continue;
    s.penaltyFraction = 1;
    s.withinBand = false;
    s.slashedToken = s.weight;
  }

  return { states: next, totalSlashedFromValid };
}

/**
 * Slashing for a cancelled (quorum-failure) round. Only non-participants
 * lose locked tokens; valid revealers keep their stake.
 */
export function applyNonParticipationOnlySlashing(
  states: CuratorRoundState[],
): SlashOutput {
  const next = states.map((s) => ({ ...s }));
  let totalSlashedFromValid = 0;
  for (const s of next) {
    if (!s.nonParticipation) continue;
    s.penaltyFraction = 1;
    s.withinBand = false;
    s.slashedToken = s.weight;
    totalSlashedFromValid += 0;
  }
  return { states: next, totalSlashedFromValid };
}
