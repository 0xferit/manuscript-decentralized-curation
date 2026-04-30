import type { AppState } from "../store";
import { fmtNum, fmtPct, fmtToken } from "./shared";

interface Props { readonly state: AppState; }

export function PoolPanel({ state }: Props) {
  const p = state.pool;
  const par = p.parameters;
  const totalDisbursed = state.fundingRound.totalDisbursedToken;
  const provisionalSum = state.nominations.reduce(
    (s, n) => s + (n.provisionalShareToken ?? 0),
    0,
  );

  return (
    <div className="panel">
      <h2>Pool profile</h2>
      <div className="kv">
        <dt>Name</dt><dd>{p.name}</dd>
        <dt>Pool id</dt><dd>{p.id}</dd>
        <dt>Registry id</dt><dd>{p.registryId}</dd>
        <dt>Funding budget</dt><dd>{fmtToken(p.fundingBudget)} token</dd>
        <dt>Curation budget</dt><dd>{fmtToken(p.curationBudget)} token</dd>
        <dt>Provisional sum</dt><dd>{fmtToken(provisionalSum)} token</dd>
        <dt>Disbursed (so far)</dt><dd>{fmtToken(totalDisbursed)} token</dd>
        <dt>EMA sigma</dt><dd>{fmtNum(p.emaSigma)}</dd>
      </div>
      <h3>Parameters</h3>
      <div className="kv">
        <dt>Drafted seats</dt><dd>{par.draftedSeats}</dd>
        <dt>Min reveal quorum</dt><dd>{par.minRevealQuorum}</dd>
        <dt>Seat size L</dt><dd>{fmtToken(par.seatSizeL)}</dd>
        <dt>Coherence K</dt><dd>{par.coherenceK}</dd>
        <dt>epsilon_sigma</dt><dd>{par.epsilonSigma}</dd>
        <dt>rho</dt><dd>{par.rho}</dd>
        <dt>Round reward floor</dt><dd>{fmtToken(par.roundRewardFloor)}</dd>
        <dt>sigmaRefAlpha</dt><dd>{par.sigmaRefAlpha}</dd>
        <dt>Submission bond</dt><dd>{fmtToken(par.submissionBond)}</dd>
        <dt>Counter-stake floor</dt><dd>{fmtToken(par.challengeCounterStakeMin)}</dd>
        <dt>Counter-stake ratio</dt><dd>{fmtPct(par.challengeCounterStakePct)}</dd>
        <dt>Challenge tax</dt><dd>{fmtPct(par.challengeTaxPct)}</dd>
        <dt>Grace ticks</dt><dd>{par.graceTicks}</dd>
        <dt>Reputation +/-/decay</dt>
        <dd>
          +{par.reputationSurvivingDelta}, {par.reputationDebunkedDelta}, decay {par.reputationDecayPerEpoch}/epoch
        </dd>
      </div>
    </div>
  );
}
