/**
 * DDR resolver boundary.
 *
 * The protocol delegates dispute adjudication to an external decentralized
 * dispute resolution system (Kleros v1). The engine only needs the resolver
 * to expose two things:
 *
 *   1. A way to submit a challenge for adjudication (no-op in the prototype).
 *   2. A way to consume an adjudicated outcome and update the challenge.
 *
 * The prototype ships a `manualMock` resolver that records the user's
 * outcome choice. Production deployments swap this for a chain-call adapter.
 */

import type { Challenge, DDROutcome } from "./types";

export interface DDRResolution {
  challengeId: string;
  ruling: DDROutcome;
  resolvedAtTick: number;
  jurorNote: string | null;
}

export interface DDRResolveInput {
  challenge: Challenge;
  ruling: DDROutcome;
  tick: number;
  jurorNote: string | null;
}

export interface DDRResolveOutput {
  challenge: Challenge;
  resolution: DDRResolution;
}

export interface DDRResolver {
  /** Optional submission hook; no-op for the manual mock. */
  submit?(challenge: Challenge): void;
  resolve(input: DDRResolveInput): DDRResolveOutput;
}

export class DDRResolutionError extends Error {
  constructor(public readonly challengeId: string, message: string) {
    super(message);
    this.name = "DDRResolutionError";
  }
}

export const manualMockDDRResolver: DDRResolver = {
  resolve(input: DDRResolveInput): DDRResolveOutput {
    if (input.challenge.status !== "Pending") {
      throw new DDRResolutionError(
        input.challenge.id,
        `Cannot resolve challenge ${input.challenge.id}: status is ${input.challenge.status}.`,
      );
    }
    return {
      challenge: {
        ...input.challenge,
        status: input.ruling,
        resolvedAtTick: input.tick,
        ruling: input.ruling,
      },
      resolution: {
        challengeId: input.challenge.id,
        ruling: input.ruling,
        resolvedAtTick: input.tick,
        jurorNote: input.jurorNote,
      },
    };
  },
};

/**
 * Backwards-compatible thin wrapper. Prefer `manualMockDDRResolver.resolve`
 * in new code; this signature was the v1 entrypoint and is kept so existing
 * tests do not need to be rewritten.
 */
export function resolveChallenge(
  challenge: Challenge,
  ruling: DDROutcome,
  tick: number,
  jurorNote: string | null,
): DDRResolveOutput {
  return manualMockDDRResolver.resolve({ challenge, ruling, tick, jurorNote });
}
