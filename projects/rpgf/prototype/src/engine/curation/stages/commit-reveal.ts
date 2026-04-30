/**
 * Stage: commit-reveal simulation.
 *
 * Boundary contract: turns a per-seat draft + curator metadata into a list of
 * `CuratorRoundState`s populated with `committed`, `revealed`, `revealedScore`,
 * and `nonParticipation`. No slashing, scoring, or reward logic here.
 *
 * In production, this stage is an adapter to the real commit-reveal protocol
 * (cryptographic commits + reveal opens). The prototype substitutes a
 * deterministic simulator that consults `Curator.commitRevealBehavior` and
 * `Curator.intendedScore` to derive each seat's reveal outcome.
 *
 * Implementations MUST satisfy: one `CuratorRoundState` per drafted seat
 * group, weights add to `seats * L`, and `nonParticipation = !revealed`.
 */

import type {
  CommitRevealBehavior,
  Curator,
  CuratorRoundState,
  PoolParameters,
} from "../types";
import { summarizeSeatsByCurator, type DraftedSeat } from "../drafting";

export interface CommitRevealInput {
  draftedSeats: DraftedSeat[];
  curators: ReadonlyArray<Curator>;
  parameters: PoolParameters;
}

export interface CommitRevealSimulator {
  simulate(input: CommitRevealInput): CuratorRoundState[];
}

function applyBehavior(
  behavior: CommitRevealBehavior,
  intended: number,
): { committed: boolean; revealed: boolean; revealedScore: number | null } {
  switch (behavior) {
    case "CommitAndReveal":
      return { committed: true, revealed: true, revealedScore: intended };
    case "CommitOnly":
      return { committed: true, revealed: false, revealedScore: null };
    case "NoShow":
      return { committed: false, revealed: false, revealedScore: null };
    default:
      return { committed: false, revealed: false, revealedScore: null };
  }
}

export const deterministicCommitRevealSimulator: CommitRevealSimulator = {
  simulate({ draftedSeats, curators, parameters }: CommitRevealInput): CuratorRoundState[] {
    const seatsByCurator = summarizeSeatsByCurator(draftedSeats);
    const states: CuratorRoundState[] = [];
    for (const [curatorId, seats] of seatsByCurator.entries()) {
      const curator = curators.find((c) => c.id === curatorId);
      if (!curator) continue;
      const reveal = applyBehavior(curator.commitRevealBehavior, curator.intendedScore);
      const weight = seats * parameters.seatSizeL;
      states.push({
        curatorId,
        seats,
        weight,
        intendedScore: curator.intendedScore,
        behavior: curator.commitRevealBehavior,
        committed: reveal.committed,
        revealed: reveal.revealed,
        revealedScore: reveal.revealedScore,
        penaltyFraction: 0,
        slashedToken: 0,
        rewardToken: 0,
        withinBand: false,
        nonParticipation: !reveal.revealed,
      });
    }
    return states;
  },
};
