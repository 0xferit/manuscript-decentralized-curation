import { describe, expect, it } from "vitest";

import {
  DDRResolutionError,
  manualMockDDRResolver,
  type DDRResolver,
} from "../src/engine/adjudication/ddr";
import {
  fileChallenge,
  REFERENCE_POOL_PARAMETERS,
  makeNominations,
  markScored,
} from "../src/engine";

function pendingChallenge() {
  const base = makeNominations()[0]!;
  const scored = markScored(base, {
    relevanceScore: 0.5,
    relevanceRoundId: "r",
    tick: 1,
  });
  scored.provisionalShareToken = 10;
  return fileChallenge({
    id: "c-test",
    nomination: scored,
    challengerId: "cur-anya",
    reason: "Debunking",
    newEvidenceNote: null,
    parameters: REFERENCE_POOL_PARAMETERS,
    tick: 2,
  });
}

describe("DDRResolver interface", () => {
  it("manual mock returns the chosen ruling", () => {
    const c = pendingChallenge();
    const out = manualMockDDRResolver.resolve({
      challenge: c,
      ruling: "Debunked",
      tick: 5,
      jurorNote: "test",
    });
    expect(out.challenge.status).toBe("Debunked");
    expect(out.resolution.ruling).toBe("Debunked");
    expect(out.resolution.resolvedAtTick).toBe(5);
  });

  it("manual mock rejects re-resolution", () => {
    const c = pendingChallenge();
    const once = manualMockDDRResolver.resolve({
      challenge: c,
      ruling: "Debunked",
      tick: 5,
      jurorNote: null,
    });
    expect(() =>
      manualMockDDRResolver.resolve({
        challenge: once.challenge,
        ruling: "Debunked",
        tick: 6,
        jurorNote: null,
      }),
    ).toThrow(DDRResolutionError);
  });

  it("custom resolver implementation can be swapped via interface", () => {
    const fixed: DDRResolver = {
      resolve: ({ challenge, tick }) => ({
        challenge: { ...challenge, status: "Timeout", resolvedAtTick: tick, ruling: "Timeout" },
        resolution: { challengeId: challenge.id, ruling: "Timeout", resolvedAtTick: tick, jurorNote: "force-timeout" },
      }),
    };
    const c = pendingChallenge();
    const out = fixed.resolve({ challenge: c, ruling: "Debunked", tick: 5, jurorNote: null });
    expect(out.challenge.status).toBe("Timeout");
    expect(out.resolution.ruling).toBe("Timeout");
  });
});
