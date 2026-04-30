import { describe, expect, it } from "vitest";
import {
  ChallengeFilingError,
  challengePayoutFor,
  computeChallengeTax,
  computeCounterStake,
  fileChallenge,
} from "@adjudication";
import { resolveChallenge } from "@adjudication";
import { REFERENCE_POOL_PARAMETERS, makeNominations } from "@bootstrap";
import { markScored } from "@lifecycle";

const params = REFERENCE_POOL_PARAMETERS;

function scoredNom(provisional = 12) {
  const base = makeNominations()[0]!;
  const scored = markScored(base, {
    relevanceScore: 0.8,
    relevanceRoundId: "r",
    tick: 1,
  });
  scored.provisionalShareToken = provisional;
  return scored;
}

describe("challenge math", () => {
  it("uses min when proportional under floor", () => {
    expect(computeCounterStake(0.01, params)).toBeCloseTo(0.01, 12);
  });

  it("uses proportional when above floor", () => {
    expect(computeCounterStake(20, params)).toBeCloseTo(5, 12);
  });

  it("tax is 0.5 percent of share", () => {
    expect(computeChallengeTax(20, params)).toBeCloseTo(0.1, 12);
  });
});

describe("fileChallenge", () => {
  it("rejects challenges against non-Scored nominations", () => {
    const nom = makeNominations()[0]!;
    expect(() =>
      fileChallenge({
        id: "c1",
        nomination: nom,
        challengerId: "cur-anya",
        reason: "Debunking",
        newEvidenceNote: null,
        parameters: params,
        tick: 1,
      }),
    ).toThrow(ChallengeFilingError);
  });

  it("requires new-evidence note after ChallengeFailed", () => {
    const nom = scoredNom();
    nom.adjudicationOutcome = "ChallengeFailed";
    expect(() =>
      fileChallenge({
        id: "c2",
        nomination: nom,
        challengerId: "cur-anya",
        reason: "Debunking",
        newEvidenceNote: null,
        parameters: params,
        tick: 1,
      }),
    ).toThrow();
    const ok = fileChallenge({
      id: "c3",
      nomination: nom,
      challengerId: "cur-anya",
      reason: "Debunking",
      newEvidenceNote: "newly published audit report",
      parameters: params,
      tick: 1,
    });
    expect(ok.status).toBe("Pending");
  });
});

describe("DDR resolve + payout", () => {
  it("Debunked sends counter-stake and bond to challenger", () => {
    const nom = scoredNom(12);
    const c = fileChallenge({
      id: "c-d",
      nomination: nom,
      challengerId: "cur-pia",
      reason: "Debunking",
      newEvidenceNote: null,
      parameters: params,
      tick: 1,
    });
    const { challenge: resolved } = resolveChallenge(c, "Debunked", 5, "ddr-debunk");
    expect(resolved.status).toBe("Debunked");
    const payout = challengePayoutFor("Debunked", resolved);
    expect(payout.authorBondTo).toBe("challenger");
    expect(payout.counterStakeTo).toBe("challenger");
  });

  it("ChallengeFailed sends counter-stake and bond to author", () => {
    const nom = scoredNom(12);
    const c = fileChallenge({
      id: "c-f",
      nomination: nom,
      challengerId: "cur-pia",
      reason: "Debunking",
      newEvidenceNote: null,
      parameters: params,
      tick: 1,
    });
    const { challenge: resolved } = resolveChallenge(c, "ChallengeFailed", 5, null);
    const payout = challengePayoutFor("ChallengeFailed", resolved);
    expect(payout.authorBondTo).toBe("author");
    expect(payout.counterStakeTo).toBe("author");
  });

  it("Timeout treats as challenger loss", () => {
    const nom = scoredNom(12);
    const c = fileChallenge({
      id: "c-t",
      nomination: nom,
      challengerId: "cur-pia",
      reason: "Debunking",
      newEvidenceNote: null,
      parameters: params,
      tick: 1,
    });
    const { challenge: resolved } = resolveChallenge(c, "Timeout", 100, null);
    const payout = challengePayoutFor("Timeout", resolved);
    expect(payout.authorBondTo).toBe("author");
    expect(payout.counterStakeTo).toBe("author");
  });
});
