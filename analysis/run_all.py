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
        prob += (
            math.comb(n_jurors, k)
            * (p_juror_correct**k)
            * ((1 - p_juror_correct) ** (n_jurors - k))
        )
    return prob


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def save_metadata() -> None:
    payload = {
        "generated_at_utc": utc_now_iso(),
        "git_sha": os.getenv("GITHUB_SHA")
        or os.getenv("CF_PAGES_COMMIT_SHA")
        or "unknown",
        "python": {
            "version": platform.python_version(),
        },
        "dependencies": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "matplotlib": plt.matplotlib.__version__,
        },
    }
    (OUT_DIR / "metadata.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def _truncate_0_1(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 0.0, 1.0)


def _ci95(values: np.ndarray) -> float:
    """95% confidence interval half-width for the mean."""
    return float(1.96 * values.std() / np.sqrt(len(values)))


# ---------------------------------------------------------------------------
# E1: Accuracy dispute simulation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class E1Params:
    n_jurors: int = 5
    bounty: float = 100.0
    stake_ratios: tuple[float, ...] = (0.05, 0.1, 0.25, 0.5)
    p_detect: float = (
        0.35  # probability a false claim is noticed & challenged in window
    )


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
        plt.plot(
            sub["p_juror_correct"],
            sub["ev_false"] / params.bounty,
            label=f"S/B={s_over_b:g}",
        )
    plt.axhline(0.0, color="black", linewidth=0.8)
    plt.xlabel("Per-juror correctness p")
    plt.ylabel("Challenger EV on false claim (normalized by bounty)")
    plt.title(
        f"E1: Challenger EV vs juror accuracy (N={params.n_jurors}, p_detect={params.p_detect:g})"
    )
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


# ---------------------------------------------------------------------------
# E1-Adv: Repeated attack by a well-funded adversary (multi-seed)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class E1AdvParams:
    n_jurors: int = 5
    bounty: float = 100.0
    stake_ratio: float = 0.25
    p_detect: float = 0.35
    n_attacks: int = 50  # adversary submits this many false claims
    p_juror_range: tuple[float, ...] = (0.60, 0.70, 0.80, 0.90)
    n_seeds: int = 100


def _e1_adv_single_run(
    params: E1AdvParams, p: float, rng: np.random.Generator
) -> dict:
    """Single Monte Carlo run of adversarial attacks at a given jury accuracy."""
    p_majority = majority_correct_probability(params.n_jurors, p)
    b = params.bounty
    s = b * params.stake_ratio
    adv_balance = 0.0
    survived = 0
    challenged_count = 0

    for _ in range(params.n_attacks):
        detected = rng.random() < params.p_detect
        if detected:
            challenged_count += 1
            jury_correct = rng.random() < p_majority
            if jury_correct:
                adv_balance -= b
            else:
                adv_balance += s
                survived += 1
        else:
            survived += 1

    return {
        "survival_rate": survived / params.n_attacks,
        "adversary_balance": adv_balance,
        "adversary_balance_per_attack": adv_balance / params.n_attacks,
    }


def run_e1_adversarial(params: E1AdvParams) -> None:
    """
    Simulate a well-funded adversary who submits many false claims.
    Runs N independent seeds per jury accuracy level and reports
    mean, std, and 95% CI for all metrics.
    """
    rows: list[dict] = []

    for p in params.p_juror_range:
        seed_results = []
        for seed_idx in range(params.n_seeds):
            rng = np.random.default_rng(seed_idx)
            result = _e1_adv_single_run(params, p, rng)
            seed_results.append(result)

        sr = np.array([r["survival_rate"] for r in seed_results])
        bal = np.array([r["adversary_balance"] for r in seed_results])
        bpa = np.array([r["adversary_balance_per_attack"] for r in seed_results])

        rows.append(
            {
                "p_juror_correct": p,
                "n_attacks": params.n_attacks,
                "n_seeds": params.n_seeds,
                "survival_rate_mean": float(sr.mean()),
                "survival_rate_std": float(sr.std()),
                "survival_rate_ci95": _ci95(sr),
                "adversary_balance_mean": float(bal.mean()),
                "adversary_balance_std": float(bal.std()),
                "adversary_balance_ci95": _ci95(bal),
                "adversary_balance_per_attack_mean": float(bpa.mean()),
                "adversary_balance_per_attack_std": float(bpa.std()),
                "adversary_balance_per_attack_ci95": _ci95(bpa),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e1_adversarial_results.csv", index=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.5))
    labels = [f"p={p:.2f}" for p in params.p_juror_range]

    ax1.bar(
        labels,
        df["survival_rate_mean"],
        yerr=df["survival_rate_ci95"],
        color="#4C72B0",
        capsize=4,
    )
    ax1.set_ylabel("False claim survival rate")
    ax1.set_title(
        f"E1-Adv: Survival rate ({params.n_attacks} attacks, "
        f"N={params.n_seeds} seeds, 95% CI)"
    )
    ax1.set_ylim(0.0, 1.0)
    ax1.axhline(
        1.0 - params.p_detect,
        color="gray",
        linestyle="--",
        linewidth=0.8,
        label="Unchallenged rate",
    )
    ax1.legend(frameon=False, fontsize=9)

    colors = ["#C44E52" if v < 0 else "#55A868" for v in df["adversary_balance_mean"]]
    ax2.bar(
        labels,
        df["adversary_balance_mean"],
        yerr=df["adversary_balance_ci95"],
        color=colors,
        capsize=4,
    )
    ax2.set_ylabel("Adversary cumulative balance")
    ax2.set_title(
        f"E1-Adv: Adversary profit/loss ({params.n_attacks} attacks, "
        f"N={params.n_seeds} seeds, 95% CI)"
    )
    ax2.axhline(0.0, color="black", linewidth=0.8)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "e1_adversarial.png", dpi=200)
    plt.close()


# ---------------------------------------------------------------------------
# E2: Relevance coherence game (scale: [0, 1])
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class E2Params:
    n_curators: int = 200
    rounds: int = 200
    slash_rate: float = 0.03
    noise_sigma: float = 0.08  # noise on [0,1] scale (was 0.8 on [0,10])
    ks: tuple[float, ...] = (0.8, 1.0, 1.25, 1.5)
    competent_fracs: tuple[float, ...] = (0.1, 0.3, 0.5, 0.7, 0.9)


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
                r_true = float(rng.uniform(0.0, 1.0))

                v = np.empty(params.n_curators, dtype=float)
                v[is_comp] = _truncate_0_1(
                    rng.normal(loc=r_true, scale=params.noise_sigma, size=is_comp.sum())
                )
                v[~is_comp] = rng.uniform(0.0, 1.0, size=(~is_comp).sum())

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
                    w[coherent] += total_slashed * (
                        coherent_w / float(coherent_w.sum())
                    )

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
        plt.plot(
            sub["competent_frac"], sub["mean_abs_error"], marker="o", label=f"K={k:g}"
        )
    plt.xlabel("Fraction competent curators")
    plt.ylabel("Mean |μ − r|")
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


# ---------------------------------------------------------------------------
# E2-Adv: Coherence game under adversarial collusion (multi-seed)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class E2AdvParams:
    n_curators: int = 200
    rounds: int = 200
    slash_rate: float = 0.03
    noise_sigma: float = 0.08
    K: float = 1.25
    competent_frac: float = 0.6
    colluding_fracs: tuple[float, ...] = (0.0, 0.05, 0.10, 0.15, 0.20, 0.30)
    collusion_bias: float = 0.3  # colluders add this bias toward 1.0
    n_seeds: int = 100


def _e2_adv_single_run(
    params: E2AdvParams, col_frac: float, rng: np.random.Generator
) -> dict:
    """Single run of the adversarial coherence game at a given collusion fraction."""
    n_comp = int(round(params.n_curators * params.competent_frac))
    n_collude = int(round(params.n_curators * col_frac))
    n_comp_actual = max(0, n_comp - n_collude)
    n_incomp = params.n_curators - n_comp_actual - n_collude

    types = np.array(
        [0] * n_comp_actual + [1] * n_incomp + [2] * n_collude,
        dtype=int,
    )
    rng.shuffle(types)

    w = np.ones(params.n_curators, dtype=float)
    abs_errors: list[float] = []

    for t in range(params.rounds):
        r_true = float(rng.uniform(0.0, 1.0))

        v = np.empty(params.n_curators, dtype=float)
        comp_mask = types == 0
        incomp_mask = types == 1
        col_mask = types == 2

        v[comp_mask] = _truncate_0_1(
            rng.normal(loc=r_true, scale=params.noise_sigma, size=comp_mask.sum())
        )
        v[incomp_mask] = rng.uniform(0.0, 1.0, size=incomp_mask.sum())
        if col_mask.any():
            biased_target = min(1.0, r_true + params.collusion_bias)
            v[col_mask] = _truncate_0_1(
                rng.normal(
                    loc=biased_target,
                    scale=params.noise_sigma * 0.5,
                    size=col_mask.sum(),
                )
            )

        w_sum = float(w.sum())
        mu = float((w * v).sum() / w_sum)
        sigma = float(np.sqrt(((w * (v - mu) ** 2).sum() / w_sum)))

        if sigma == 0.0:
            coherent = np.ones(params.n_curators, dtype=bool)
        else:
            coherent = np.abs(v - mu) <= (params.K * sigma)

        incoherent = ~coherent
        slashed = params.slash_rate * w[incoherent]
        total_slashed = float(slashed.sum())
        w[incoherent] -= slashed

        if total_slashed > 0 and coherent.any():
            coherent_w = w[coherent]
            w[coherent] += total_slashed * (coherent_w / float(coherent_w.sum()))

        abs_errors.append(abs(mu - r_true))

    col_share_final = (
        float(w[types == 2].sum() / float(w.sum())) if n_collude > 0 else 0.0
    )
    return {
        "mean_abs_error": float(np.mean(abs_errors)),
        "final_colluder_stake_share": col_share_final,
        "mean_abs_error_last_50": float(np.mean(abs_errors[-50:])),
    }


def run_e2_adversarial(params: E2AdvParams) -> None:
    """
    A colluding bloc of curators coordinates on biased ratings.
    Runs N independent seeds per collusion level and reports
    mean, std, and 95% CI for all metrics.
    """
    rows: list[dict] = []

    for col_frac in params.colluding_fracs:
        seed_results = []
        for seed_idx in range(params.n_seeds):
            seed = int(10_000 * col_frac + seed_idx)
            rng = np.random.default_rng(seed)
            result = _e2_adv_single_run(params, col_frac, rng)
            seed_results.append(result)

        errors = np.array([r["mean_abs_error"] for r in seed_results])
        errors_l50 = np.array([r["mean_abs_error_last_50"] for r in seed_results])
        col_shares = np.array(
            [r["final_colluder_stake_share"] for r in seed_results]
        )

        rows.append(
            {
                "colluding_frac": col_frac,
                "mean_abs_error_mean": float(errors.mean()),
                "mean_abs_error_std": float(errors.std()),
                "mean_abs_error_ci95": _ci95(errors),
                "mean_abs_error_last_50_mean": float(errors_l50.mean()),
                "mean_abs_error_last_50_std": float(errors_l50.std()),
                "mean_abs_error_last_50_ci95": _ci95(errors_l50),
                "final_colluder_stake_share_mean": float(col_shares.mean()),
                "final_colluder_stake_share_std": float(col_shares.std()),
                "final_colluder_stake_share_ci95": _ci95(col_shares),
                "initial_colluder_stake_share": col_frac,
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e2_adversarial_results.csv", index=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.5))
    x = df["colluding_frac"]

    ax1.plot(
        x, df["mean_abs_error_mean"], marker="o", color="#4C72B0", label="Full run"
    )
    ax1.fill_between(
        x,
        df["mean_abs_error_mean"] - df["mean_abs_error_ci95"],
        df["mean_abs_error_mean"] + df["mean_abs_error_ci95"],
        alpha=0.2,
        color="#4C72B0",
    )
    ax1.plot(
        x,
        df["mean_abs_error_last_50_mean"],
        marker="s",
        color="#55A868",
        label="Last 50 rounds",
    )
    ax1.fill_between(
        x,
        df["mean_abs_error_last_50_mean"] - df["mean_abs_error_last_50_ci95"],
        df["mean_abs_error_last_50_mean"] + df["mean_abs_error_last_50_ci95"],
        alpha=0.2,
        color="#55A868",
    )
    ax1.set_xlabel("Fraction of colluding curators")
    ax1.set_ylabel("Mean |μ − r|")
    ax1.set_title(
        f"E2-Adv: Signal error under collusion "
        f"(K={params.K}, N={params.n_seeds} seeds, 95% CI)"
    )
    ax1.legend(frameon=False, fontsize=9)

    ax2.plot(
        x,
        df["initial_colluder_stake_share"],
        marker="o",
        linestyle="--",
        color="gray",
        label="Initial share",
    )
    ax2.plot(
        x,
        df["final_colluder_stake_share_mean"],
        marker="o",
        color="#C44E52",
        label="Final share",
    )
    ax2.fill_between(
        x,
        df["final_colluder_stake_share_mean"] - df["final_colluder_stake_share_ci95"],
        df["final_colluder_stake_share_mean"] + df["final_colluder_stake_share_ci95"],
        alpha=0.2,
        color="#C44E52",
    )
    ax2.set_xlabel("Fraction of colluding curators")
    ax2.set_ylabel("Colluder stake share")
    ax2.set_title(
        f"E2-Adv: Colluder stake decay "
        f"(K={params.K}, N={params.n_seeds} seeds, 95% CI)"
    )
    ax2.set_ylim(0.0, max(0.4, df["initial_colluder_stake_share"].max() * 1.2))
    ax2.legend(frameon=False, fontsize=9)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "e2_adversarial.png", dpi=200)
    plt.close()


# ---------------------------------------------------------------------------
# E3: Ambiguity stress test
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class E3Params:
    n_claims: int = 20_000
    n_jurors: int = 5
    p_wellposed_juror_correct: float = 0.85
    p_ambig_juror_correct: float = 0.55
    under_spec_prob: float = (
        0.85  # defended system: chance juror chooses Under-specified on ambiguous claim
    )
    ambig_fracs: tuple[float, ...] = (0.0, 0.1, 0.25, 0.5)


def run_e3(params: E3Params) -> None:
    def majority_vote_prob(n: int, p: float) -> float:
        return majority_correct_probability(n, p)

    rows: list[dict] = []
    for frac in params.ambig_fracs:
        rng = np.random.default_rng(int(1_000 * frac + 7))
        is_ambig = rng.random(params.n_claims) < frac

        # Baseline: no Under-specified verdict; ambiguous claims are adjudicated with lower correctness.
        p_major_well = majority_vote_prob(
            params.n_jurors, params.p_wellposed_juror_correct
        )
        p_major_amb = majority_vote_prob(params.n_jurors, params.p_ambig_juror_correct)

        baseline_wrong = float(
            (~is_ambig).mean() * (1 - p_major_well)
            + is_ambig.mean() * (1 - p_major_amb)
        )

        # Defended: ambiguous claims are mostly classified as Under-specified (correct outcome for ambiguity).
        # Model: each juror chooses Under-specified with prob under_spec_prob; otherwise votes with ambig correctness.
        # We approximate correct handling of ambiguity as: majority chooses Under-specified.
        p_major_under = majority_vote_prob(params.n_jurors, params.under_spec_prob)
        defended_wrong_on_well = float(1 - p_major_well)
        # On ambiguous: wrong if not Under-specified majority AND also wrong truth label.
        defended_wrong_on_amb = float((1 - p_major_under) * (1 - p_major_amb))
        defended_wrong = float(
            (~is_ambig).mean() * defended_wrong_on_well
            + is_ambig.mean() * defended_wrong_on_amb
        )

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
    plt.plot(
        df["ambig_frac"],
        df["baseline_wrong_rate"],
        marker="o",
        label="baseline (no Under-specified)",
    )
    plt.plot(
        df["ambig_frac"],
        df["defended_wrong_rate"],
        marker="o",
        label="defended (Under-specified)",
    )
    plt.xlabel("Fraction of ambiguous claims")
    plt.ylabel("Overall wrong-resolution rate")
    plt.title("E3: Ambiguity increases error without Under-specified")
    plt.legend(frameon=False)
    plt.ylim(0.0, 1.0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e3_ambiguity.png", dpi=200)
    plt.close()


# ---------------------------------------------------------------------------
# E4: Reputation mechanism validation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class E4aParams:
    n_curators: int = 200
    rounds: int = 500
    slash_rate: float = 0.03
    noise_sigma: float = 0.08
    K: float = 1.25
    competent_frac: float = 0.5
    alphas: tuple[float, ...] = (0.0, 0.1, 0.25, 0.5, 1.0)
    decay_rates: tuple[float, ...] = (0.0, 0.01, 0.05)
    n_seeds: int = 100
    # Cash-poor experts: 10% of competent curators start with s_i=0.1
    cash_poor_frac: float = 0.1


def _e4a_single_run(
    params: E4aParams,
    alpha: float,
    decay_rate: float,
    rng: np.random.Generator,
) -> dict:
    """Single run of the alpha/decay sweep."""
    n_comp = int(round(params.n_curators * params.competent_frac))
    is_comp = np.zeros(params.n_curators, dtype=bool)
    is_comp[:n_comp] = True
    rng.shuffle(is_comp)

    # Identify cash-poor experts among competent curators
    comp_indices = np.where(is_comp)[0]
    n_cash_poor = max(1, int(round(len(comp_indices) * params.cash_poor_frac)))
    cash_poor_mask = np.zeros(params.n_curators, dtype=bool)
    cash_poor_mask[comp_indices[:n_cash_poor]] = True

    # Financial stake: cash-poor start at 0.1, others at 1.0
    s = np.ones(params.n_curators, dtype=float)
    s[cash_poor_mask] = 0.1

    # Reputation: all start at 0
    rep = np.zeros(params.n_curators, dtype=float)

    abs_errors: list[float] = []
    time_to_entry = params.rounds  # default: never reached median

    for t in range(params.rounds):
        # Compute weights
        w = s + alpha * rep

        r_true = float(rng.uniform(0.0, 1.0))

        v = np.empty(params.n_curators, dtype=float)
        v[is_comp] = _truncate_0_1(
            rng.normal(loc=r_true, scale=params.noise_sigma, size=is_comp.sum())
        )
        v[~is_comp] = rng.uniform(0.0, 1.0, size=(~is_comp).sum())

        w_sum = float(w.sum())
        mu = float((w * v).sum() / w_sum)
        sigma = float(np.sqrt(((w * (v - mu) ** 2).sum() / w_sum)))

        if sigma == 0.0:
            coherent = np.ones(params.n_curators, dtype=bool)
        else:
            coherent = np.abs(v - mu) <= (params.K * sigma)

        incoherent = ~coherent

        # Slash incoherent financial stake
        slashed = params.slash_rate * s[incoherent]
        total_slashed = float(slashed.sum())
        s[incoherent] -= slashed

        if total_slashed > 0 and coherent.any():
            coherent_s = s[coherent]
            s[coherent] += total_slashed * (coherent_s / float(coherent_s.sum()))

        # Update reputation: coherent gain 1.0, then all decay
        rep[coherent] += 1.0
        rep *= 1.0 - decay_rate

        abs_errors.append(abs(mu - r_true))

        # Check if any cash-poor expert reached median weight
        if time_to_entry == params.rounds:
            w_updated = s + alpha * rep
            median_w = float(np.median(w_updated))
            if median_w > 0 and float(w_updated[cash_poor_mask].max()) >= median_w:
                time_to_entry = t + 1

    # Gini coefficient of final weights
    w_final = s + alpha * rep
    w_sorted = np.sort(w_final)
    n = len(w_sorted)
    cumw = np.cumsum(w_sorted)
    gini = float((2.0 * np.sum((np.arange(1, n + 1) * w_sorted)) / (n * cumw[-1])) - (n + 1) / n)

    return {
        "mean_abs_error": float(np.mean(abs_errors)),
        "time_to_entry": time_to_entry,
        "gini": gini,
    }


def run_e4a(params: E4aParams) -> None:
    """E4a: Alpha and decay rate sweep measuring competence filter with reputation."""
    rows: list[dict] = []

    for alpha in params.alphas:
        for decay_rate in params.decay_rates:
            seed_results = []
            for seed_idx in range(params.n_seeds):
                seed = int(100_000 * alpha + 10_000 * decay_rate + seed_idx)
                rng = np.random.default_rng(seed)
                result = _e4a_single_run(params, alpha, decay_rate, rng)
                seed_results.append(result)

            errors = np.array([r["mean_abs_error"] for r in seed_results])
            entries = np.array([r["time_to_entry"] for r in seed_results])
            ginis = np.array([r["gini"] for r in seed_results])

            rows.append(
                {
                    "alpha": alpha,
                    "decay_rate": decay_rate,
                    "mean_abs_error_mean": float(errors.mean()),
                    "mean_abs_error_ci95": _ci95(errors),
                    "time_to_entry_mean": float(entries.mean()),
                    "time_to_entry_ci95": _ci95(entries),
                    "gini_mean": float(ginis.mean()),
                    "gini_ci95": _ci95(ginis),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e4a_alpha_sweep.csv", index=False)

    # Heatmap: time to non-whale entry
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    pivot = df.pivot(index="decay_rate", columns="alpha", values="time_to_entry_mean")
    im = ax.imshow(pivot.values, aspect="auto", cmap="viridis_r", origin="lower")
    ax.set_xticks(range(len(params.alphas)))
    ax.set_xticklabels([f"{a:g}" for a in params.alphas])
    ax.set_yticks(range(len(params.decay_rates)))
    ax.set_yticklabels([f"{d:g}" for d in params.decay_rates])
    ax.set_xlabel("α (reputation weight)")
    ax.set_ylabel("Decay rate δ")
    ax.set_title(
        f"E4a: Rounds until cash-poor expert reaches median weight "
        f"(N={params.n_seeds} seeds)"
    )
    for i in range(len(params.decay_rates)):
        for j in range(len(params.alphas)):
            val = pivot.values[i, j]
            ax.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=9,
                    color="white" if val > pivot.values.mean() else "black")
    fig.colorbar(im, ax=ax, label="Rounds")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e4a_alpha_heatmap.png", dpi=200)
    plt.close()

    # Line plot: Gini coefficient vs alpha for each decay rate
    plt.figure(figsize=(7.0, 4.0))
    for d in params.decay_rates:
        sub = df[df["decay_rate"] == d].sort_values("alpha")
        plt.errorbar(
            sub["alpha"],
            sub["gini_mean"],
            yerr=sub["gini_ci95"],
            marker="o",
            capsize=3,
            label=f"δ={d:g}",
        )
    plt.xlabel("α (reputation weight)")
    plt.ylabel("Gini coefficient of final weights")
    plt.title(f"E4a: Weight inequality vs α (N={params.n_seeds} seeds, 95% CI)")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e4a_gini.png", dpi=200)
    plt.close()


@dataclass(frozen=True)
class E4bParams:
    n_curators: int = 200
    rounds: int = 300
    slash_rate: float = 0.03
    noise_sigma: float = 0.08
    K: float = 1.25
    competent_frac: float = 0.5
    alphas: tuple[float, ...] = (0.25, 0.5, 1.0)
    decay_rates: tuple[float, ...] = (0.0, 0.01, 0.05, 0.10)
    attacker_initial_rep: float = 200.0
    n_seeds: int = 100


def _e4b_single_run(
    params: E4bParams,
    alpha: float,
    decay_rate: float,
    rng: np.random.Generator,
) -> dict:
    """Single run: measure how long a reputation-rich attacker retains influence."""
    n_comp = int(round(params.n_curators * params.competent_frac))
    is_comp = np.zeros(params.n_curators, dtype=bool)
    is_comp[:n_comp] = True
    # Last curator is the attacker (incompetent but reputation-rich)
    attacker_idx = params.n_curators - 1
    is_comp[attacker_idx] = False
    rng.shuffle(is_comp[:attacker_idx])  # shuffle everyone except attacker

    s = np.ones(params.n_curators, dtype=float)
    rep = np.zeros(params.n_curators, dtype=float)
    rep[attacker_idx] = params.attacker_initial_rep

    rounds_above_median = 0

    for t in range(params.rounds):
        w = s + alpha * rep

        r_true = float(rng.uniform(0.0, 1.0))

        v = np.empty(params.n_curators, dtype=float)
        # Competent curators vote honestly
        v[is_comp] = _truncate_0_1(
            rng.normal(loc=r_true, scale=params.noise_sigma, size=is_comp.sum())
        )
        # Incompetent (including attacker) vote randomly
        v[~is_comp] = rng.uniform(0.0, 1.0, size=(~is_comp).sum())

        w_sum = float(w.sum())
        mu = float((w * v).sum() / w_sum)
        sigma = float(np.sqrt(((w * (v - mu) ** 2).sum() / w_sum)))

        if sigma == 0.0:
            coherent = np.ones(params.n_curators, dtype=bool)
        else:
            coherent = np.abs(v - mu) <= (params.K * sigma)

        incoherent = ~coherent
        slashed = params.slash_rate * s[incoherent]
        total_slashed = float(slashed.sum())
        s[incoherent] -= slashed

        if total_slashed > 0 and coherent.any():
            coherent_s = s[coherent]
            s[coherent] += total_slashed * (coherent_s / float(coherent_s.sum()))

        rep[coherent] += 1.0
        rep *= 1.0 - decay_rate

        w_updated = s + alpha * rep
        if w_updated[attacker_idx] >= float(np.median(w_updated)):
            rounds_above_median += 1

    return {"rounds_above_median": rounds_above_median}


def run_e4b(params: E4bParams) -> None:
    """E4b: Reputation gaming attack. How long does a reputation-rich attacker retain influence?"""
    rows: list[dict] = []

    for alpha in params.alphas:
        for decay_rate in params.decay_rates:
            seed_results = []
            for seed_idx in range(params.n_seeds):
                seed = int(100_000 * alpha + 10_000 * decay_rate + seed_idx + 50_000)
                rng = np.random.default_rng(seed)
                result = _e4b_single_run(params, alpha, decay_rate, rng)
                seed_results.append(result)

            above = np.array([r["rounds_above_median"] for r in seed_results])
            rows.append(
                {
                    "alpha": alpha,
                    "decay_rate": decay_rate,
                    "rounds_above_median_mean": float(above.mean()),
                    "rounds_above_median_std": float(above.std()),
                    "rounds_above_median_ci95": _ci95(above),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e4b_reputation_gaming.csv", index=False)

    plt.figure(figsize=(7.0, 4.0))
    for alpha in params.alphas:
        sub = df[df["alpha"] == alpha].sort_values("decay_rate")
        plt.errorbar(
            sub["decay_rate"],
            sub["rounds_above_median_mean"],
            yerr=sub["rounds_above_median_ci95"],
            marker="o",
            capsize=3,
            label=f"α={alpha:g}",
        )
    plt.xlabel("Decay rate δ")
    plt.ylabel(f"Rounds attacker weight ≥ median (of {params.rounds})")
    plt.title(
        f"E4b: Reputation gaming persistence "
        f"(rep₀={params.attacker_initial_rep:.0f}, N={params.n_seeds} seeds, 95% CI)"
    )
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e4b_gaming_decay.png", dpi=200)
    plt.close()


@dataclass(frozen=True)
class E4cParams:
    n_curators: int = 200
    rounds_buildup: int = 100  # rounds of honest voting to build reputation
    rounds_attack: int = 100  # rounds of coordinated biased voting
    slash_rate: float = 0.03
    noise_sigma: float = 0.08
    K: float = 1.25
    competent_frac: float = 0.5
    n_sybils: int = 20  # number of Sybil identities
    collusion_bias: float = 0.3
    alphas: tuple[float, ...] = (0.0, 0.5, 1.0)
    decay_rate: float = 0.01
    n_seeds: int = 100


def _e4c_single_run(
    params: E4cParams,
    alpha: float,
    rng: np.random.Generator,
) -> dict:
    """Single run: Sybils build reputation honestly, then attack."""
    n_comp = int(round(params.n_curators * params.competent_frac))
    n_sybils = params.n_sybils

    # Sybils replace some incompetent curators
    n_incomp = params.n_curators - n_comp - n_sybils
    if n_incomp < 0:
        n_incomp = 0
        n_comp = params.n_curators - n_sybils

    # types: 0=competent, 1=incompetent, 2=sybil
    types = np.array([0] * n_comp + [1] * n_incomp + [2] * n_sybils, dtype=int)
    rng.shuffle(types)

    s = np.ones(params.n_curators, dtype=float)
    rep = np.zeros(params.n_curators, dtype=float)
    sybil_mask = types == 2

    total_rounds = params.rounds_buildup + params.rounds_attack
    errors_attack: list[float] = []

    for t in range(total_rounds):
        w = s + alpha * rep
        r_true = float(rng.uniform(0.0, 1.0))
        v = np.empty(params.n_curators, dtype=float)

        comp_mask = types == 0
        incomp_mask = types == 1

        v[comp_mask] = _truncate_0_1(
            rng.normal(loc=r_true, scale=params.noise_sigma, size=comp_mask.sum())
        )
        v[incomp_mask] = rng.uniform(0.0, 1.0, size=incomp_mask.sum())

        # Sybils: honest during buildup, biased during attack
        if t < params.rounds_buildup:
            v[sybil_mask] = _truncate_0_1(
                rng.normal(loc=r_true, scale=params.noise_sigma, size=sybil_mask.sum())
            )
        else:
            biased_target = min(1.0, r_true + params.collusion_bias)
            v[sybil_mask] = _truncate_0_1(
                rng.normal(
                    loc=biased_target,
                    scale=params.noise_sigma * 0.5,
                    size=sybil_mask.sum(),
                )
            )

        w_sum = float(w.sum())
        mu = float((w * v).sum() / w_sum)
        sigma = float(np.sqrt(((w * (v - mu) ** 2).sum() / w_sum)))

        if sigma == 0.0:
            coherent = np.ones(params.n_curators, dtype=bool)
        else:
            coherent = np.abs(v - mu) <= (params.K * sigma)

        incoherent = ~coherent
        slashed = params.slash_rate * s[incoherent]
        total_slashed = float(slashed.sum())
        s[incoherent] -= slashed

        if total_slashed > 0 and coherent.any():
            coherent_s = s[coherent]
            s[coherent] += total_slashed * (coherent_s / float(coherent_s.sum()))

        rep[coherent] += 1.0
        rep *= 1.0 - params.decay_rate

        if t >= params.rounds_buildup:
            errors_attack.append(abs(mu - r_true))

    sybil_share = float(
        (s[sybil_mask].sum() + alpha * rep[sybil_mask].sum())
        / float((s + alpha * rep).sum())
    )
    return {
        "mean_abs_error_attack": float(np.mean(errors_attack)),
        "final_sybil_weight_share": sybil_share,
    }


def run_e4c(params: E4cParams) -> None:
    """E4c: Reputation laundering via Sybil buildup then coordinated attack."""
    rows: list[dict] = []

    for alpha in params.alphas:
        seed_results = []
        for seed_idx in range(params.n_seeds):
            seed = int(100_000 * alpha + seed_idx + 90_000)
            rng = np.random.default_rng(seed)
            result = _e4c_single_run(params, alpha, rng)
            seed_results.append(result)

        errors = np.array([r["mean_abs_error_attack"] for r in seed_results])
        shares = np.array([r["final_sybil_weight_share"] for r in seed_results])

        rows.append(
            {
                "alpha": alpha,
                "decay_rate": params.decay_rate,
                "n_sybils": params.n_sybils,
                "mean_abs_error_attack_mean": float(errors.mean()),
                "mean_abs_error_attack_ci95": _ci95(errors),
                "final_sybil_weight_share_mean": float(shares.mean()),
                "final_sybil_weight_share_ci95": _ci95(shares),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e4c_reputation_laundering.csv", index=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.5))

    ax1.bar(
        [f"α={a:g}" for a in params.alphas],
        df["mean_abs_error_attack_mean"],
        yerr=df["mean_abs_error_attack_ci95"],
        color="#4C72B0",
        capsize=4,
    )
    ax1.set_ylabel("Mean |μ − r| during attack phase")
    ax1.set_title(
        f"E4c: Signal error during Sybil attack "
        f"({params.n_sybils} Sybils, N={params.n_seeds} seeds, 95% CI)"
    )

    ax2.bar(
        [f"α={a:g}" for a in params.alphas],
        df["final_sybil_weight_share_mean"],
        yerr=df["final_sybil_weight_share_ci95"],
        color="#C44E52",
        capsize=4,
    )
    ax2.set_ylabel("Sybil weight share after attack")
    ax2.set_title(
        f"E4c: Sybil influence after laundering "
        f"(δ={params.decay_rate}, N={params.n_seeds} seeds, 95% CI)"
    )
    ax2.axhline(
        params.n_sybils / params.n_curators,
        color="gray",
        linestyle="--",
        linewidth=0.8,
        label="Initial Sybil share",
    )
    ax2.legend(frameon=False, fontsize=9)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "e4c_sybil_comparison.png", dpi=200)
    plt.close()


# ---------------------------------------------------------------------------
# Evaluation summary
# ---------------------------------------------------------------------------


def write_eval_summary() -> None:
    params_e1 = E1Params()
    e1 = pd.read_csv(OUT_DIR / "e1_results.csv")
    e2 = pd.read_csv(OUT_DIR / "e2_results.csv")
    e3 = pd.read_csv(OUT_DIR / "e3_results.csv")
    e1_adv = pd.read_csv(OUT_DIR / "e1_adversarial_results.csv")
    e2_adv = pd.read_csv(OUT_DIR / "e2_adversarial_results.csv")
    e4a = pd.read_csv(OUT_DIR / "e4a_alpha_sweep.csv")
    e4b = pd.read_csv(OUT_DIR / "e4b_reputation_gaming.csv")
    e4c = pd.read_csv(OUT_DIR / "e4c_reputation_laundering.csv")

    # Pick representative summary points (deterministic).
    e1_sub = e1[e1["stake_over_bounty"] == 0.25].copy()
    e1_sub["p_delta"] = (e1_sub["p_juror_correct"] - 0.8).abs()
    e1_point = e1_sub.sort_values("p_delta").iloc[0]
    e2_point = e2[(e2["K"] == 1.25) & (e2["competent_frac"] == 0.7)].iloc[0]
    e3_point = e3[e3["ambig_frac"] == 0.25].iloc[0]
    e1_adv_point = e1_adv[e1_adv["p_juror_correct"] == 0.80].iloc[0]
    e2_adv_point = e2_adv[e2_adv["colluding_frac"] == 0.15].iloc[0]
    e2_adv_base = e2_adv[e2_adv["colluding_frac"] == 0.0].iloc[0]
    e4a_point = e4a[(e4a["alpha"] == 0.5) & (e4a["decay_rate"] == 0.01)].iloc[0]
    e4b_point = e4b[(e4b["alpha"] == 0.5) & (e4b["decay_rate"] == 0.05)].iloc[0]
    e4c_point_a0 = e4c[e4c["alpha"] == 0.0].iloc[0]
    e4c_point_a05 = e4c[e4c["alpha"] == 0.5].iloc[0]

    summary = f"""\
### Evaluation snapshot (representative points)

- **E1:** At $p=0.80$ (per-juror), $N={params_e1.n_jurors}$, $S/B=0.25$, challenger EV on false claims is **{e1_point["ev_false"] / params_e1.bounty:.2f}\\times bounty** and false-claim survival (one window, $p_\\mathrm{{detect}}={params_e1.p_detect:.2f}$) is **{e1_point["false_survival"]:.2f}**.
- **E2:** At initial competence 0.70 and $K=1.25$, mean relevance error is **{e2_point["mean_abs_error"]:.3f}** and final competent stake share is **{e2_point["final_competent_stake_share"]:.2f}**.
- **E3:** At ambiguity rate 0.25, baseline wrong-rate is **{e3_point["baseline_wrong_rate"]:.2f}** vs defended **{e3_point["defended_wrong_rate"]:.2f}** (Under-specified enabled).
- **E1-Adv:** A well-funded adversary submitting {int(e1_adv_point["n_attacks"])} false claims at $p=0.80$ achieves survival rate **{e1_adv_point["survival_rate_mean"]:.2f} $\\pm$ {e1_adv_point["survival_rate_ci95"]:.2f}** (95% CI, $N={int(e1_adv_point["n_seeds"])}$ seeds) with cumulative balance **{e1_adv_point["adversary_balance_mean"]:.0f} $\\pm$ {e1_adv_point["adversary_balance_ci95"]:.0f}** (negative = system wins).
- **E2-Adv:** A 15% colluding bloc (bias $= +0.30$) shifts mean error from {e2_adv_base["mean_abs_error_mean"]:.3f} to **{e2_adv_point["mean_abs_error_mean"]:.3f} $\\pm$ {e2_adv_point["mean_abs_error_ci95"]:.3f}** (95% CI, $N={int(e1_adv_point["n_seeds"])}$ seeds) over 200 rounds, and their stake share decays from {e2_adv_point["initial_colluder_stake_share"]:.2f} to **{e2_adv_point["final_colluder_stake_share_mean"]:.3f} $\\pm$ {e2_adv_point["final_colluder_stake_share_ci95"]:.3f}**.
- **E4a:** At $\\alpha=0.5$, $\\delta=0.01$, cash-poor experts reach median weight in **{e4a_point["time_to_entry_mean"]:.0f} $\\pm$ {e4a_point["time_to_entry_ci95"]:.0f}** rounds (95% CI); Gini coefficient is **{e4a_point["gini_mean"]:.3f}**.
- **E4b:** At $\\alpha=0.5$, $\\delta=0.05$, a reputation-rich attacker (rep$_0=200$) retains above-median influence for **{e4b_point["rounds_above_median_mean"]:.0f} $\\pm$ {e4b_point["rounds_above_median_ci95"]:.0f}** of {E4bParams().rounds} rounds.
- **E4c:** Sybil laundering at $\\alpha=0.0$: attack-phase error = **{e4c_point_a0["mean_abs_error_attack_mean"]:.3f}**; at $\\alpha=0.5$: **{e4c_point_a05["mean_abs_error_attack_mean"]:.3f} $\\pm$ {e4c_point_a05["mean_abs_error_attack_ci95"]:.3f}**.
"""
    (OUT_DIR / "eval_summary.md").write_text(summary, encoding="utf-8")


def write_reading_time() -> None:
    """Count content elements in paper.qmd and emit per-persona comprehension times."""
    import re

    paper = ROOT / "paper.qmd"
    raw = paper.read_text(encoding="utf-8")

    # Strip YAML front matter
    body = raw
    if body.startswith("---"):
        end = body.index("---", 3)
        body = body[end + 3 :]

    # Count structural elements before stripping
    n_figures = len(re.findall(r"\{#fig-", raw))
    n_tables = len(re.findall(r"\{#tbl-", raw))
    n_display_math = len(re.findall(r"\$\$", body)) // 2
    # Inline math: single-$ pairs that are not display math
    body_no_display = re.sub(r"\$\$[^$]*?\$\$", "", body, flags=re.DOTALL)
    n_inline_math = len(re.findall(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", body_no_display))

    # Word count: strip shortcodes, display math, inline math, image refs
    prose = body
    prose = re.sub(r"\{\{<.*?>\}\}", "", prose)
    prose = re.sub(r"\$\$[^$]*?\$\$", "", prose, flags=re.DOTALL)
    prose = re.sub(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", "", prose)
    prose = re.sub(r"!\[.*?\]\(.*?\)", "", prose)
    words = len(prose.split())

    # Persona rates: (prose_wpm, inline_math_sec, display_math_sec, fig_min, tbl_min)
    personas = {
        "Domain expert": (180, 2, 10, 1, 1),
        "Technical reader": (120, 6, 30, 2, 2),
        "General reader": (80, 12, 60, 3, 3),
    }

    estimates: dict[str, int] = {}
    for name, (wpm, im_s, dm_s, fig_m, tbl_m) in personas.items():
        minutes = (
            words / wpm
            + n_inline_math * im_s / 60
            + n_display_math * dm_s / 60
            + n_figures * fig_m
            + n_tables * tbl_m
        )
        estimates[name] = round(minutes)

    header = (
        f"**Estimated comprehension time** "
        f"({words:,} words, {n_inline_math} equations, "
        f"{n_figures} figures, {n_tables} tables)"
    )
    row = " | ".join(f"~{estimates[p]} min" for p in personas)
    col_headers = " | ".join(personas.keys())

    snippet = f"""\
{header}

| | {col_headers} |
|---|---|---|---|
| | {row} |
"""
    (OUT_DIR / "reading_time.md").write_text(snippet, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    save_metadata()

    run_e1(E1Params())
    run_e1_adversarial(E1AdvParams())
    run_e2(E2Params())
    run_e2_adversarial(E2AdvParams())
    run_e3(E3Params())
    run_e4a(E4aParams())
    run_e4b(E4bParams())
    run_e4c(E4cParams())
    write_eval_summary()
    write_reading_time()


if __name__ == "__main__":
    main()
