/**
 * fileChallengeAction: file a typed challenge during the holdback window.
 * Promotes the nomination to Disputed if it was Scored. The pool's funding
 * budget grows by the challenge tax (kept by the pool regardless of outcome).
 */

import { fileChallenge as buildChallenge } from "@adjudication";
import type { ChallengeReason } from "@adjudication";

import { markDisputed } from "../../state-machine";
import type { ControllerResult, EngineState } from "../../types";
import { advanceTick, nomById } from "../_shared";

export interface FileChallengeArgs {
  nominationId: string;
  challengerId: string;
  reason: ChallengeReason;
  newEvidenceNote?: string | null;
}

export function fileChallengeAction(
  state: EngineState,
  args: FileChallengeArgs,
): ControllerResult {
  const nomination = nomById(state, args.nominationId);
  if (!nomination) return { state, events: [] };
  const next = advanceTick(state);
  try {
    const challenge = buildChallenge({
      id: `c-${state.challenges.length + 1}-${args.nominationId}`,
      nomination,
      challengerId: args.challengerId,
      reason: args.reason,
      newEvidenceNote: args.newEvidenceNote ?? null,
      parameters: next.pool.parameters,
      tick: next.tick,
    });
    let nominations = next.nominations;
    if (nomination.state === "Scored") {
      nominations = nominations.map((n) =>
        n.id === nomination.id ? markDisputed(n, next.tick) : n,
      );
    }
    nominations = nominations.map((n) =>
      n.id === nomination.id
        ? { ...n, challengeIds: [...n.challengeIds, challenge.id] }
        : n,
    );
    return {
      state: {
        ...next,
        challenges: [...next.challenges, challenge],
        nominations,
        pool: {
          ...next.pool,
          fundingBudget: next.pool.fundingBudget + challenge.taxToken,
        },
      },
      events: [
        {
          tick: next.tick,
          category: "Challenge",
          message: `Filed ${args.reason} challenge ${challenge.id} on ${args.nominationId} by ${args.challengerId}; counter-stake=${challenge.counterStakeToken.toFixed(4)}, tax=${challenge.taxToken.toFixed(4)}`,
        },
      ],
    };
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    return {
      state: next,
      events: [
        {
          tick: next.tick,
          category: "Challenge",
          message: `Filing rejected for ${args.nominationId}: ${message}`,
        },
      ],
    };
  }
}
