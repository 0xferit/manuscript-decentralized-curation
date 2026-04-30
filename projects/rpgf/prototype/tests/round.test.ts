import { describe, expect, it } from "vitest";
import { evaluateNomination } from "@curation";
import { makeCurators, REFERENCE_POOL_PARAMETERS } from "@bootstrap";
import type { Curator } from "@shared/types";

describe("evaluateNomination orchestrator", () => {
  it("scores a nomination on first attempt under default seed", () => {
    const out = evaluateNomination({
      poolId: "p",
      fundingRoundId: "fr",
      nominationId: "n1",
      curators: makeCurators(),
      parameters: REFERENCE_POOL_PARAMETERS,
      emaSigmaBefore: 0,
      curationBudgetBefore: 5,
      tick: 0,
      baseSeed: "seed-eval",
    });
    expect(out.resolvedAs).toBe("Scored");
    expect(out.rounds).toHaveLength(1);
    expect(out.finalRound?.phase).toBe("Finalized");
  });

  it("retries on quorum failure and marks Unscored on second failure", () => {
    const noShow: Curator[] = makeCurators().map((c) => ({
      ...c,
      commitRevealBehavior: "NoShow",
    }));
    const out = evaluateNomination({
      poolId: "p",
      fundingRoundId: "fr",
      nominationId: "n1",
      curators: noShow,
      parameters: REFERENCE_POOL_PARAMETERS,
      emaSigmaBefore: 0,
      curationBudgetBefore: 5,
      tick: 0,
      baseSeed: "seed-eval-fail",
    });
    expect(out.rounds).toHaveLength(2);
    expect(out.resolvedAs).toBe("Unscored");
    expect(out.finalRound).toBeNull();
  });

  it("aborts immediately when curation budget cannot reserve a round", () => {
    const out = evaluateNomination({
      poolId: "p",
      fundingRoundId: "fr",
      nominationId: "n1",
      curators: makeCurators(),
      parameters: REFERENCE_POOL_PARAMETERS,
      emaSigmaBefore: 0,
      curationBudgetBefore: 0,
      tick: 0,
      baseSeed: "seed-broke",
    });
    expect(out.rounds).toHaveLength(1);
    expect(out.resolvedAs).toBe("Underfunded");
  });
});
