/**
 * Nomination state machine for the RPGF prototype.
 *
 * Implements the transition table in `projects/rpgf/design.md` "Impact
 * Nomination Lifecycle". Pure functions return the next nomination state and
 * a side-effect description. The store applies side effects against the
 * mutable engine state.
 *
 * Operational states:
 *   Submitted, Retracted, Scored, Disputed, Disbursed, Debunked, Unscored.
 * Adjudication outcomes (orthogonal): Unchallenged, ChallengeFailed, Debunked.
 */

import type {
  AdjudicationOutcome,
  ImpactNomination,
  NominationState,
} from "@shared/types";

export class NominationTransitionError extends Error {
  constructor(
    public readonly nominationId: string,
    public readonly from: NominationState,
    public readonly transition: string,
    message: string,
  ) {
    super(message);
    this.name = "NominationTransitionError";
  }
}

export interface AmendInput {
  evidenceItems?: ImpactNomination["evidenceItems"];
  assertions?: ImpactNomination["assertions"];
  templateOk?: boolean;
  doubleCountTagIds?: string[];
}

export function amendDuringSubmission(
  nomination: ImpactNomination,
  input: AmendInput,
  tick: number,
): ImpactNomination {
  if (nomination.state !== "Submitted") {
    throw new NominationTransitionError(
      nomination.id,
      nomination.state,
      "amend",
      "Amendment only permitted during Submitted state.",
    );
  }
  return {
    ...nomination,
    evidenceItems: input.evidenceItems ?? nomination.evidenceItems,
    assertions: input.assertions ?? nomination.assertions,
    templateOk: input.templateOk ?? nomination.templateOk,
    doubleCountTagIds: input.doubleCountTagIds ?? nomination.doubleCountTagIds,
    lastUpdatedPhaseTick: tick,
  };
}

export function retractNomination(
  nomination: ImpactNomination,
  tick: number,
): ImpactNomination {
  if (nomination.state !== "Submitted") {
    throw new NominationTransitionError(
      nomination.id,
      nomination.state,
      "retract",
      "Retraction only permitted during Submitted state.",
    );
  }
  return {
    ...nomination,
    state: "Retracted",
    lastUpdatedPhaseTick: tick,
  };
}

export function markScored(
  nomination: ImpactNomination,
  args: {
    relevanceScore: number;
    relevanceRoundId: string;
    tick: number;
  },
): ImpactNomination {
  if (nomination.state !== "Submitted") {
    throw new NominationTransitionError(
      nomination.id,
      nomination.state,
      "score",
      "Scoring only permitted from Submitted state.",
    );
  }
  return {
    ...nomination,
    state: "Scored",
    relevanceScore: args.relevanceScore,
    relevanceRoundId: args.relevanceRoundId,
    lastUpdatedPhaseTick: args.tick,
  };
}

export function markUnscored(
  nomination: ImpactNomination,
  tick: number,
): ImpactNomination {
  if (nomination.state !== "Submitted") {
    throw new NominationTransitionError(
      nomination.id,
      nomination.state,
      "unscore",
      "Unscored only reachable from Submitted state.",
    );
  }
  return {
    ...nomination,
    state: "Unscored",
    relevanceScore: null,
    lastUpdatedPhaseTick: tick,
  };
}

export function markDisputed(
  nomination: ImpactNomination,
  tick: number,
): ImpactNomination {
  if (nomination.state !== "Scored") {
    throw new NominationTransitionError(
      nomination.id,
      nomination.state,
      "dispute",
      "Challenge can only be filed against Scored nominations.",
    );
  }
  return {
    ...nomination,
    state: "Disputed",
    lastUpdatedPhaseTick: tick,
  };
}

export function markDebunked(
  nomination: ImpactNomination,
  tick: number,
): ImpactNomination {
  if (nomination.state !== "Disputed") {
    throw new NominationTransitionError(
      nomination.id,
      nomination.state,
      "debunk",
      "Debunked only reachable from Disputed state.",
    );
  }
  return {
    ...nomination,
    state: "Debunked",
    adjudicationOutcome: "Debunked",
    lastUpdatedPhaseTick: tick,
  };
}

export function markChallengeFailed(
  nomination: ImpactNomination,
  tick: number,
  graceTicks: number,
): ImpactNomination {
  if (nomination.state !== "Disputed") {
    throw new NominationTransitionError(
      nomination.id,
      nomination.state,
      "challenge-fail",
      "ChallengeFailed only reachable from Disputed state.",
    );
  }
  return {
    ...nomination,
    state: "Scored",
    adjudicationOutcome: "ChallengeFailed",
    graceEndsAtTick: tick + graceTicks,
    lastUpdatedPhaseTick: tick,
  };
}

export function markDisbursed(
  nomination: ImpactNomination,
  tick: number,
  finalShareToken: number,
): ImpactNomination {
  if (nomination.state !== "Scored") {
    throw new NominationTransitionError(
      nomination.id,
      nomination.state,
      "disburse",
      "Disbursement only permitted from Scored state.",
    );
  }
  return {
    ...nomination,
    state: "Disbursed",
    finalShareToken,
    lastUpdatedPhaseTick: tick,
  };
}

export function topUpFinalShare(
  nomination: ImpactNomination,
  tick: number,
  extraToken: number,
): ImpactNomination {
  if (nomination.state !== "Disbursed") {
    throw new NominationTransitionError(
      nomination.id,
      nomination.state,
      "top-up",
      "Supplementary disbursement only on already-disbursed nominations.",
    );
  }
  return {
    ...nomination,
    finalShareToken: (nomination.finalShareToken ?? 0) + extraToken,
    lastUpdatedPhaseTick: tick,
  };
}

export const nominationOutcomes: AdjudicationOutcome[] = [
  "Unchallenged",
  "ChallengeFailed",
  "Debunked",
];
