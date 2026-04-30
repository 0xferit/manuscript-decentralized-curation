/**
 * Deterministic PRNG utilities. The protocol design relies on a verifiable
 * randomness source (VRF). The prototype substitutes a seeded mulberry32 PRNG
 * so that reviewers can reproduce drafting and resolution outcomes exactly.
 */

const FNV_OFFSET = 2166136261;
const FNV_PRIME = 16777619;
const UINT32_MASK = 0xffffffff;

export function hashStringToUint32(input: string): number {
  let h = FNV_OFFSET;
  for (let i = 0; i < input.length; i++) {
    h ^= input.codePointAt(i) ?? 0;
    h = Math.imul(h, FNV_PRIME);
  }
  return h >>> 0;
}

export interface PRNG {
  next(): number;
  nextInt(maxExclusive: number): number;
  shuffle<T>(items: readonly T[]): T[];
}

export function createPRNG(seed: string): PRNG {
  let state = hashStringToUint32(seed);
  if (state === 0) state = 1;

  function next(): number {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / (UINT32_MASK + 1);
  }

  function nextInt(maxExclusive: number): number {
    if (maxExclusive <= 0) return 0;
    return Math.floor(next() * maxExclusive);
  }

  function shuffle<T>(items: readonly T[]): T[] {
    const copy = items.slice();
    for (let i = copy.length - 1; i > 0; i--) {
      const j = nextInt(i + 1);
      const tmp = copy[i];
      copy[i] = copy[j];
      copy[j] = tmp;
    }
    return copy;
  }

  return { next, nextInt, shuffle };
}

export function deriveRoundSeed(args: {
  poolId: string;
  nominationId: string;
  roundId: string;
  attempt: number;
  baseSeed: string;
}): string {
  return [
    args.baseSeed,
    args.poolId,
    args.nominationId,
    args.roundId,
    `attempt:${args.attempt}`,
  ].join("|");
}
