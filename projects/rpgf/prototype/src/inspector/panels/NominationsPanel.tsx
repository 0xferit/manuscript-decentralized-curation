import { useState } from "react";

import type { AppActions, AppState } from "../store";
import type { ImpactNomination } from "@shared/types";
import { fmtNum, fmtToken } from "./shared";

interface Props {
  state: AppState;
  actions: AppActions;
}

export function NominationsPanel({ state, actions }: Props) {
  return (
    <div className="panel">
      <h2>Impact nominations ({state.nominations.length})</h2>
      <p className="muted" style={{ fontSize: 11 }}>
        Click a nomination to inspect assertions, evidence, double-counting tags, and provisional/final allocation.
      </p>
      <div>
        {state.nominations.map((n) => (
          <NominationCard key={n.id} nomination={n} state={state} actions={actions} />
        ))}
      </div>
    </div>
  );
}

function NominationCard({
  nomination,
  state,
  actions,
}: {
  nomination: ImpactNomination;
  state: AppState;
  actions: AppActions;
}) {
  const registry = state.registry.find((r) => r.id === nomination.registryEntryId);
  const round = nomination.relevanceRoundId
    ? state.rounds.find((r) => r.id === nomination.relevanceRoundId)
    : undefined;
  const challenges = state.challenges.filter((c) => c.nominationId === nomination.id);
  const phase = state.pool.phase;
  const canRetract = nomination.state === "Submitted" && phase === "Submission";
  const canFlip = nomination.state === "Submitted" && phase === "Submission";

  const [open, setOpen] = useState(true);

  return (
    <details className="nom-details" open={open} onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}>
      <summary>
        <strong>{nomination.id}</strong>
        <span className={`tag state-${nomination.state}`}>{nomination.state}</span>
        <span className={`tag adj-${nomination.adjudicationOutcome}`}>{nomination.adjudicationOutcome}</span>
        <span className="muted">→ {registry?.projectName ?? nomination.registryEntryId}</span>
        {nomination.relevanceScore !== null && (
          <span className="muted">mu={fmtNum(nomination.relevanceScore, 3)}</span>
        )}
        {nomination.provisionalShareToken !== null && (
          <span className="muted">prov={fmtToken(nomination.provisionalShareToken, 4)}</span>
        )}
        {nomination.finalShareToken !== null && (
          <span className="muted">final={fmtToken(nomination.finalShareToken, 4)}</span>
        )}
      </summary>

      <div className="kv" style={{ marginTop: 8 }}>
        <dt>Author</dt><dd>{nomination.authorAddress}</dd>
        <dt>Registry entry</dt><dd>{nomination.registryEntryId}</dd>
        <dt>Bond</dt><dd>{fmtToken(nomination.bondToken)} token</dd>
        <dt>Template OK</dt><dd>{nomination.templateOk ? "yes" : "no (TemplateViolation grounds)"}</dd>
        <dt>Double-count tags</dt>
        <dd>
          {nomination.doubleCountTagIds.length === 0
            ? "—"
            : nomination.doubleCountTagIds.map((t) => (
                <span key={t} className="tag">{t}</span>
              ))}
        </dd>
        <dt>Created at tick</dt><dd>{nomination.createdAtPhaseTick}</dd>
        <dt>Last update tick</dt><dd>{nomination.lastUpdatedPhaseTick}</dd>
        {nomination.graceEndsAtTick !== null && (
          <>
            <dt>Grace ends at</dt><dd>tick {nomination.graceEndsAtTick}</dd>
          </>
        )}
      </div>

      <h3>Assertions</h3>
      <div>
        {nomination.assertions.length === 0 && <em className="muted">no assertions</em>}
        {nomination.assertions.map((a) => (
          <div
            key={a.id}
            className={`assertion ${
              !a.falsifiable ? "bad-falsifiable" : ""
            } ${!nomination.templateOk ? "bad-template" : ""}`}
          >
            <div>{a.text}</div>
            <div className="muted" style={{ fontSize: 11 }}>
              {a.timePeriodStart} → {a.timePeriodEnd}; falsifiable=
              {a.falsifiable ? "yes" : "no"}; evidence=
              {a.evidenceItemIds.length > 0 ? a.evidenceItemIds.join(", ") : "none"}
            </div>
          </div>
        ))}
      </div>

      <h3>Evidence</h3>
      {nomination.evidenceItems.length === 0 ? (
        <em className="muted">no evidence attached</em>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Class</th>
              <th>Caption</th>
              <th>URI</th>
            </tr>
          </thead>
          <tbody>
            {nomination.evidenceItems.map((e) => (
              <tr key={e.id}>
                <td>{e.evidenceClass}</td>
                <td>{e.caption}</td>
                <td className="muted">{e.uri}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {round && (
        <>
          <h3>Relevance round {round.id}</h3>
          <div className="kv">
            <dt>mu / sigma</dt>
            <dd>
              {fmtNum(round.meanScore, 3)} / {fmtNum(round.stdDev, 3)}
            </dd>
            <dt>sigma_ref / reward factor</dt>
            <dd>
              {fmtNum(round.sigmaRef, 3)} / {fmtNum(round.rewardFactor, 3)}
            </dd>
            <dt>Distance slashing</dt>
            <dd>{round.distanceSlashingSkipped ? "skipped (low dispersion)" : "applied"}</dd>
          </div>
        </>
      )}

      {challenges.length > 0 && (
        <>
          <h3>Challenges</h3>
          <table>
            <thead>
              <tr>
                <th>Id</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Counter-stake</th>
                <th>Tax</th>
              </tr>
            </thead>
            <tbody>
              {challenges.map((c) => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{c.reason}</td>
                  <td>{c.status}</td>
                  <td>{fmtToken(c.counterStakeToken)}</td>
                  <td>{fmtToken(c.taxToken)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      <div className="flex-row" style={{ marginTop: 10 }}>
        <button
          disabled={!canRetract}
          onClick={() => actions.retract(nomination.id)}
        >
          Retract
        </button>
        <button
          disabled={!canFlip}
          onClick={() =>
            actions.amend(nomination.id, { templateOk: !nomination.templateOk })
          }
          title="Toggle template-ok flag (mock author edit)"
        >
          Toggle templateOk
        </button>
      </div>
    </details>
  );
}
