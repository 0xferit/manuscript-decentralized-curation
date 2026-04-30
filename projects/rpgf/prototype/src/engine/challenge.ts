/**
 * Challenge filing and payout helpers.
 *
 * Cashflows are defined in `projects/rpgf/design.md` (Challenge payout
 * rules). At filing the challenger escrows the counter-stake, pays the
 * challenge tax to the pool budget, and pays the external DDR fee. The DDR
 * fee is sunk regardless of outcome.
 */

import type {
  Challenge,
  ChallengeReason,
  DDROutcome,
  ImpactNomination,
  PoolParameters,
  Token,
} from "./types";

export interface FileChallengeInput {
  id: string;
  nomination: ImpactNomination;
  challengerId: string;
  reason: ChallengeReason;
  newEvidenceNote: string | null;
  parameters: PoolParameters;
  tick: number;
}

export class ChallengeFilingError extends Error {
  constructor(public readonly nominationId: string, message: string) {
    super(message);
    this.name = "ChallengeFilingError";
  }
}

export function computeCounterStake(
  provisionalShareToken: Token,
  parameters: PoolParameters,
): Token {
  const proportional =
    parameters.challengeCounterStakePct * provisionalShareToken;
  return Math.max(parameters.challengeCounterStakeMin, proportional);
}

export function computeChallengeTax(
  provisionalShareToken: Token,
  parameters: PoolParameters,
): Token {
  return parameters.challengeTaxPct * provisionalShareToken;
}

export function fileChallenge(input: FileChallengeInput): Challenge {
  const { id, nomination, challengerId, reason, newEvidenceNote, parameters, tick } = input;
  if (nomination.state !== "Scored") {
    throw new ChallengeFilingError(
      nomination.id,
      `Cannot file challenge: nomination state is ${nomination.state}.`,
    );
  }
  if (
    nomination.adjudicationOutcome === "ChallengeFailed" &&
    !newEvidenceNote?.trim()
  ) {
    throw new ChallengeFilingError(
      nomination.id,
      "Anti-relitigation: follow-on challenges after ChallengeFailed must cite new evidence.",
    );
  }
  const provisional = nomination.provisionalShareToken ?? 0;
  return {
    id,
    nominationId: nomination.id,
    challengerId,
    reason,
    newEvidenceNote: newEvidenceNote ?? null,
    counterStakeToken: computeCounterStake(provisional, parameters),
    taxToken: computeChallengeTax(provisional, parameters),
    ddrFeeToken: parameters.ddrFee,
    status: "Pending",
    filedAtTick: tick,
    resolvedAtTick: null,
    ruling: null,
  };
}

export interface ChallengePayout {
  authorBondTo: "author" | "challenger";
  counterStakeTo: "author" | "challenger";
  taxToPool: Token;
  ddrFeeSunk: Token;
}

export function challengePayoutFor(
  outcome: DDROutcome,
  challenge: Challenge,
): ChallengePayout {
  const taxToPool = challenge.taxToken;
  const ddrFeeSunk = challenge.ddrFeeToken;
  if (outcome === "Debunked") {
    return {
      authorBondTo: "challenger",
      counterStakeTo: "challenger",
      taxToPool,
      ddrFeeSunk,
    };
  }
  return {
    authorBondTo: "author",
    counterStakeTo: "author",
    taxToPool,
    ddrFeeSunk,
  };
}
