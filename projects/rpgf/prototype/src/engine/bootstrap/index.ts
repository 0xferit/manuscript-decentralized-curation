/**
 * Bootstrap module: deterministic mock data for the prototype.
 *
 * Job: produce one pool config + one registry + one curator pool + one
 * batch of seeded nominations from a fixed `PROTOTYPE_BASE_SEED`. This
 * module is read-only after init; it never mutates engine state.
 */

export {
  PROTOTYPE_POOL_ID,
  PROTOTYPE_FUNDING_ROUND_ID,
  PROTOTYPE_BASE_SEED,
} from "./seed-config";
export { REFERENCE_POOL_PARAMETERS, makePool } from "./pool";
export { makeRegistry } from "./registry";
export { makeNominations } from "./nominations";
export { makeCurators } from "./curators";
