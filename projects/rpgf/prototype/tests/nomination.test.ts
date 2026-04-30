import { describe, expect, it } from "vitest";
import {
  amendDuringSubmission,
  markChallengeFailed,
  markDebunked,
  markDisbursed,
  markDisputed,
  markScored,
  markUnscored,
  NominationTransitionError,
  retractNomination,
  topUpFinalShare,
} from "../src/engine/lifecycle/state-machine";
import { makeNominations } from "../src/engine/seed";

function clean() {
  return makeNominations()[0]!;
}

describe("nomination state machine", () => {
  it("amend allowed only in Submitted", () => {
    const nom = clean();
    const amended = amendDuringSubmission(nom, { templateOk: true }, 1);
    expect(amended.lastUpdatedPhaseTick).toBe(1);
    const scored = markScored(nom, { relevanceScore: 0.8, relevanceRoundId: "r", tick: 2 });
    expect(() => amendDuringSubmission(scored, { templateOk: true }, 3)).toThrow(
      NominationTransitionError,
    );
  });

  it("retract from Submitted only", () => {
    const nom = clean();
    expect(retractNomination(nom, 1).state).toBe("Retracted");
    const scored = markScored(nom, { relevanceScore: 0.8, relevanceRoundId: "r", tick: 2 });
    expect(() => retractNomination(scored, 3)).toThrow(NominationTransitionError);
  });

  it("Scored transitions only from Submitted", () => {
    const scored = markScored(clean(), {
      relevanceScore: 0.8,
      relevanceRoundId: "r",
      tick: 1,
    });
    expect(scored.state).toBe("Scored");
    expect(() => markScored(scored, { relevanceScore: 0.9, relevanceRoundId: "r2", tick: 2 })).toThrow();
  });

  it("Unscored only reachable from Submitted", () => {
    const u = markUnscored(clean(), 1);
    expect(u.state).toBe("Unscored");
    expect(u.relevanceScore).toBeNull();
  });

  it("Disputed only from Scored", () => {
    expect(() => markDisputed(clean(), 1)).toThrow(NominationTransitionError);
    const scored = markScored(clean(), {
      relevanceScore: 0.8,
      relevanceRoundId: "r",
      tick: 1,
    });
    expect(markDisputed(scored, 2).state).toBe("Disputed");
  });

  it("Debunked only from Disputed", () => {
    const scored = markScored(clean(), {
      relevanceScore: 0.8,
      relevanceRoundId: "r",
      tick: 1,
    });
    const disputed = markDisputed(scored, 2);
    const debunked = markDebunked(disputed, 3);
    expect(debunked.state).toBe("Debunked");
    expect(debunked.adjudicationOutcome).toBe("Debunked");
  });

  it("ChallengeFailed restores Scored with grace window", () => {
    const scored = markScored(clean(), {
      relevanceScore: 0.8,
      relevanceRoundId: "r",
      tick: 1,
    });
    const disputed = markDisputed(scored, 2);
    const restored = markChallengeFailed(disputed, 5, 1);
    expect(restored.state).toBe("Scored");
    expect(restored.adjudicationOutcome).toBe("ChallengeFailed");
    expect(restored.graceEndsAtTick).toBe(6);
  });

  it("Disbursed only from Scored; top-up only after disbursed", () => {
    const scored = markScored(clean(), {
      relevanceScore: 0.8,
      relevanceRoundId: "r",
      tick: 1,
    });
    const disbursed = markDisbursed(scored, 2, 12.5);
    expect(disbursed.state).toBe("Disbursed");
    expect(disbursed.finalShareToken).toBe(12.5);
    const topped = topUpFinalShare(disbursed, 3, 4.0);
    expect(topped.finalShareToken).toBe(16.5);
    expect(() => topUpFinalShare(scored, 4, 1.0)).toThrow();
  });
});
