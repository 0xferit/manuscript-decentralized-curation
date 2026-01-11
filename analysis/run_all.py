from __future__ import annotations

import json
import math
import os
import platform
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis" / "out"
FIG_DIR = ROOT / "analysis" / "fig"

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def majority_correct_probability(n_jurors: int, p_juror_correct: float) -> float:
    """
    Probability that a majority vote matches ground truth,
    assuming independent jurors with correctness probability p.
    """
    if n_jurors <= 0 or n_jurors % 2 == 0:
        raise ValueError("n_jurors must be a positive odd integer")
    if not (0.0 <= p_juror_correct <= 1.0):
        raise ValueError("p_juror_correct must be in [0, 1]")

    k_min = (n_jurors // 2) + 1
    prob = 0.0
    for k in range(k_min, n_jurors + 1):
        prob += math.comb(n_jurors, k) * (p_juror_correct**k) * ((1 - p_juror_correct) ** (n_jurors - k))
    return prob


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def save_metadata() -> None:
    payload = {
        "generated_at_utc": utc_now_iso(),
        "git_sha": os.getenv("GITHUB_SHA") or os.getenv("CF_PAGES_COMMIT_SHA") or "unknown",
        "python": {
            "version": platform.python_version(),
        },
        "dependencies": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "matplotlib": plt.matplotlib.__version__,
        },
    }
    (OUT_DIR / "metadata.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class E1Params:
    n_jurors: int = 5
    bounty: float = 100.0
    stake_ratios: tuple[float, ...] = (0.05, 0.1, 0.25, 0.5)
    p_detect: float = 0.35  # probability a false claim is noticed & challenged in window


def run_e1(params: E1Params) -> None:
    ps = np.linspace(0.50, 0.99, 50)

    rows: list[dict] = []
    for p in ps:
        p_majority = majority_correct_probability(params.n_jurors, float(p))
        for s_over_b in params.stake_ratios:
            b = params.bounty
            s = b * s_over_b
            ev_false = p_majority * b - (1 - p_majority) * s
            ev_true = (1 - p_majority) * b - p_majority * s

            # Simple survival model for a false claim with one challenge window:
            # - challenged with probability p_detect (if challenger finds it)
            # - if challenged, false survives iff jury is wrong
            false_survival = (1 - params.p_detect) + params.p_detect * (1 - p_majority)

            rows.append(
                {
                    "p_juror_correct": float(p),
                    "p_majority_correct": float(p_majority),
                    "stake_over_bounty": float(s_over_b),
                    "ev_false": float(ev_false),
                    "ev_true": float(ev_true),
                    "false_survival": float(false_survival),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e1_results.csv", index=False)

    # Plot: EV for challenging a false claim vs juror accuracy.
    plt.figure(figsize=(7.0, 4.0))
    for s_over_b in params.stake_ratios:
        sub = df[df["stake_over_bounty"] == s_over_b]
        plt.plot(sub["p_juror_correct"], sub["ev_false"] / params.bounty, label=f"S/B={s_over_b:g}")
    plt.axhline(0.0, color="black", linewidth=0.8)
    plt.xlabel("Per-juror correctness p")
    plt.ylabel("Challenger EV on false claim (normalized by bounty)")
    plt.title(f"E1: Challenger EV vs juror accuracy (N={params.n_jurors}, p_detect={params.p_detect:g})")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e1_challenger_ev.png", dpi=200)
    plt.close()

    # Plot: false claim survival vs juror accuracy for one representative stake ratio.
    plt.figure(figsize=(7.0, 4.0))
    s_over_b = 0.25
    sub = df[df["stake_over_bounty"] == s_over_b]
    plt.plot(sub["p_juror_correct"], sub["false_survival"])
    plt.xlabel("Per-juror correctness p")
    plt.ylabel("False claim survival probability")
    plt.title(f"E1: False claim survival (S/B={s_over_b:g}, N={params.n_jurors})")
    plt.ylim(0.0, 1.0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e1_false_survival.png", dpi=200)
    plt.close()


@dataclass(frozen=True)
class E2Params:
    n_curators: int = 200
    rounds: int = 200
    slash_rate: float = 0.03
    noise_sigma: float = 0.8
    ks: tuple[float, ...] = (0.8, 1.0, 1.25, 1.5)
    competent_fracs: tuple[float, ...] = (0.1, 0.3, 0.5, 0.7, 0.9)


def _truncate_0_10(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 0.0, 10.0)


def run_e2(params: E2Params) -> None:
    rows: list[dict] = []

    for frac in params.competent_fracs:
        for k in params.ks:
            # Deterministic seed per (frac, k) combo
            seed = int(10_000 * frac + 100 * k)
            rng = np.random.default_rng(seed)

            n_comp = int(round(params.n_curators * frac))
            is_comp = np.zeros(params.n_curators, dtype=bool)
            is_comp[:n_comp] = True
            rng.shuffle(is_comp)

            w = np.ones(params.n_curators, dtype=float)
            abs_errors: list[float] = []

            for t in range(params.rounds):
                r_true = float(rng.uniform(0.0, 10.0))

                v = np.empty(params.n_curators, dtype=float)
                v[is_comp] = _truncate_0_10(rng.normal(loc=r_true, scale=params.noise_sigma, size=is_comp.sum()))
                v[~is_comp] = rng.uniform(0.0, 10.0, size=(~is_comp).sum())

                w_sum = float(w.sum())
                mu = float((w * v).sum() / w_sum)
                sigma = float(np.sqrt(((w * (v - mu) ** 2).sum() / w_sum)))

                # Avoid degenerate sigma=0 (all votes identical); treat everyone coherent.
                if sigma == 0.0:
                    coherent = np.ones(params.n_curators, dtype=bool)
                else:
                    coherent = np.abs(v - mu) <= (k * sigma)

                incoherent = ~coherent
                slashed = params.slash_rate * w[incoherent]
                total_slashed = float(slashed.sum())
                w[incoherent] -= slashed

                if total_slashed > 0 and coherent.any():
                    # Redistribute proportionally to coherent stake.
                    coherent_w = w[coherent]
                    w[coherent] += total_slashed * (coherent_w / float(coherent_w.sum()))

                abs_errors.append(abs(mu - r_true))

            comp_share = float(w[is_comp].sum() / float(w.sum()))
            rows.append(
                {
                    "competent_frac": float(frac),
                    "K": float(k),
                    "mean_abs_error": float(np.mean(abs_errors)),
                    "final_competent_stake_share": comp_share,
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e2_results.csv", index=False)

    # Plot: mean abs error vs competent fraction for each K.
    plt.figure(figsize=(7.0, 4.0))
    for k in params.ks:
        sub = df[df["K"] == k].sort_values("competent_frac")
        plt.plot(sub["competent_frac"], sub["mean_abs_error"], marker="o", label=f"K={k:g}")
    plt.xlabel("Fraction competent curators")
    plt.ylabel("Mean |mu - r|")
    plt.title("E2: Relevance signal error vs competence and K")
    plt.legend(frameon=False, ncol=2)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e2_relevance_error.png", dpi=200)
    plt.close()

    # Plot: final competent stake share vs competent fraction (for one K).
    k = 1.25
    plt.figure(figsize=(7.0, 4.0))
    sub = df[df["K"] == k].sort_values("competent_frac")
    plt.plot(sub["competent_frac"], sub["final_competent_stake_share"], marker="o")
    plt.xlabel("Initial fraction competent curators")
    plt.ylabel("Final competent stake share")
    plt.title(f"E2: Competence filter outcome (K={k:g})")
    plt.ylim(0.0, 1.0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e2_competence_filter.png", dpi=200)
    plt.close()


@dataclass(frozen=True)
class E3Params:
    n_claims: int = 20_000
    n_jurors: int = 5
    p_wellposed_juror_correct: float = 0.85
    p_ambig_juror_correct: float = 0.55
    under_spec_prob: float = 0.85  # defended system: chance juror chooses Under-specified on ambiguous claim
    ambig_fracs: tuple[float, ...] = (0.0, 0.1, 0.25, 0.5)


def run_e3(params: E3Params) -> None:
    def majority_vote_prob(n: int, p: float) -> float:
        return majority_correct_probability(n, p)

    rows: list[dict] = []
    for frac in params.ambig_fracs:
        rng = np.random.default_rng(int(1_000 * frac + 7))
        is_ambig = rng.random(params.n_claims) < frac

        # Baseline: no Under-specified verdict; ambiguous claims are adjudicated with lower correctness.
        p_major_well = majority_vote_prob(params.n_jurors, params.p_wellposed_juror_correct)
        p_major_amb = majority_vote_prob(params.n_jurors, params.p_ambig_juror_correct)

        baseline_wrong = float((~is_ambig).mean() * (1 - p_major_well) + is_ambig.mean() * (1 - p_major_amb))

        # Defended: ambiguous claims are mostly classified as Under-specified (correct outcome for ambiguity).
        # Model: each juror chooses Under-specified with prob under_spec_prob; otherwise votes with ambig correctness.
        # We approximate correct handling of ambiguity as: majority chooses Under-specified.
        p_major_under = majority_vote_prob(params.n_jurors, params.under_spec_prob)
        defended_wrong_on_well = float(1 - p_major_well)
        # On ambiguous: wrong if not Under-specified majority AND also wrong truth label.
        defended_wrong_on_amb = float((1 - p_major_under) * (1 - p_major_amb))
        defended_wrong = float((~is_ambig).mean() * defended_wrong_on_well + is_ambig.mean() * defended_wrong_on_amb)

        rows.append(
            {
                "ambig_frac": float(frac),
                "baseline_wrong_rate": baseline_wrong,
                "defended_wrong_rate": defended_wrong,
                "p_major_under_spec": float(p_major_under),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e3_results.csv", index=False)

    plt.figure(figsize=(7.0, 4.0))
    plt.plot(df["ambig_frac"], df["baseline_wrong_rate"], marker="o", label="baseline (no Under-specified)")
    plt.plot(df["ambig_frac"], df["defended_wrong_rate"], marker="o", label="defended (Under-specified)")
    plt.xlabel("Fraction of ambiguous claims")
    plt.ylabel("Overall wrong-resolution rate")
    plt.title("E3: Ambiguity increases error without Under-specified")
    plt.legend(frameon=False)
    plt.ylim(0.0, 1.0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e3_ambiguity.png", dpi=200)
    plt.close()


def write_eval_summary() -> None:
    params_e1 = E1Params()
    e1 = pd.read_csv(OUT_DIR / "e1_results.csv")
    e2 = pd.read_csv(OUT_DIR / "e2_results.csv")
    e3 = pd.read_csv(OUT_DIR / "e3_results.csv")

    # Pick representative summary points (deterministic).
    e1_sub = e1[e1["stake_over_bounty"] == 0.25].copy()
    e1_sub["p_delta"] = (e1_sub["p_juror_correct"] - 0.8).abs()
    e1_point = e1_sub.sort_values("p_delta").iloc[0]
    e2_point = e2[(e2["K"] == 1.25) & (e2["competent_frac"] == 0.7)].iloc[0]
    e3_point = e3[e3["ambig_frac"] == 0.25].iloc[0]

    summary = f"""\
### Evaluation snapshot (representative points)

- **E1:** At $p=0.80$ (per-juror), $N={params_e1.n_jurors}$, $S/B=0.25$, challenger EV on false claims is **{e1_point['ev_false'] / params_e1.bounty:.2f}× bounty** and false-claim survival (one window, $p_\\mathrm{{detect}}={params_e1.p_detect:.2f}$) is **{e1_point['false_survival']:.2f}**.
- **E2:** At initial competence 0.70 and $K=1.25$, mean relevance error is **{e2_point['mean_abs_error']:.2f}** and final competent stake share is **{e2_point['final_competent_stake_share']:.2f}**.
- **E3:** At ambiguity rate 0.25, baseline wrong-rate is **{e3_point['baseline_wrong_rate']:.2f}** vs defended **{e3_point['defended_wrong_rate']:.2f}** (Under-specified enabled).
"""
    (OUT_DIR / "eval_summary.md").write_text(summary, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    save_metadata()

    run_e1(E1Params())
    run_e2(E2Params())
    run_e3(E3Params())
    write_eval_summary()


if __name__ == "__main__":
    main()

