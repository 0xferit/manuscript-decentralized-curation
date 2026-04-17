from __future__ import annotations

import functools
import json
import math
import os
import platform
import re
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

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


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def save_metadata() -> None:
    payload = {
        "generated_at_utc": utc_now_iso(),
        "git_sha": os.getenv("GITHUB_SHA")
        or os.getenv("CF_PAGES_COMMIT_SHA")
        or "unknown",
        "python": {"version": platform.python_version()},
        "dependencies": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "matplotlib": plt.matplotlib.__version__,
        },
    }
    (OUT_DIR / "metadata.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def majority_correct_probability(n_jurors: int, p_juror_correct: float) -> float:
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


def false_claim_survival_probability(p_detect: float, p_majority: float) -> float:
    return (1 - p_detect) + p_detect * (1 - p_majority)


def bond_threshold_multiplier(p_detect: float, p_majority: float) -> float:
    detection_success = p_detect * p_majority
    if detection_success <= 0:
        raise ValueError("p_detect * p_majority must be positive")
    return (1 - detection_success) / detection_success


def _truncate_0_1(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 0.0, 1.0)


def _ci95(values: np.ndarray) -> float:
    return float(1.96 * values.std() / np.sqrt(len(values)))


def _weighted_sample_without_replacement(
    rng: np.random.Generator, weights: np.ndarray, k: int
) -> np.ndarray:
    k = min(k, len(weights))
    if k <= 0:
        return np.array([], dtype=int)
    total = float(weights.sum())
    if total <= 0:
        probs = np.full(len(weights), 1.0 / len(weights))
    else:
        probs = weights / total
    return rng.choice(len(weights), size=k, replace=False, p=probs)


def _committee_weights(stakes: np.ndarray, cap_share: float) -> np.ndarray:
    if len(stakes) == 0:
        return stakes
    total = float(stakes.sum())
    if total <= 0:
        return np.zeros_like(stakes)
    cap = cap_share * total
    return np.minimum(stakes, cap)


def _gini(values: np.ndarray) -> float:
    if len(values) == 0:
        return 0.0
    arr = np.sort(np.asarray(values, dtype=float))
    if float(arr.sum()) <= 0:
        return 0.0
    n = len(arr)
    cum = np.cumsum(arr)
    return float((2.0 * np.sum((np.arange(1, n + 1) * arr)) / (n * cum[-1])) - (n + 1) / n)


# ---------------------------------------------------------------------------
# E1: Accuracy challenge economics
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class E1Params:
    n_jurors: int = 5
    bounty: float = 100.0
    stake_ratios: tuple[float, ...] = (0.05, 0.10, 0.25, 0.50)
    p_detect: float = 0.35
    challenge_tax_bps: float = 50.0
    ddr_fee: float = 5.0
    n_seeds: int = 100
    trials_per_seed: int = 2_000


def _e1_single_run(params: E1Params, p: float, s_over_b: float, seed_idx: int) -> dict:
    rng = np.random.default_rng(
        seed_idx * 10_000 + int(round(1_000 * p)) + int(round(100 * s_over_b))
    )
    p_majority = majority_correct_probability(params.n_jurors, p)
    b = params.bounty
    s = b * s_over_b
    sunk = b * params.challenge_tax_bps / 10_000.0 + params.ddr_fee

    jury_correct = rng.random(params.trials_per_seed) < p_majority
    detected = rng.random(params.trials_per_seed) < params.p_detect
    challenged_correctly = rng.random(params.trials_per_seed) < p_majority

    ev_false = np.where(jury_correct, b - sunk, -s - sunk)
    ev_true = np.where(jury_correct, -s - sunk, b - sunk)
    false_survival = np.where(detected, (~challenged_correctly).astype(float), 1.0)

    return {
        "ev_false": float(ev_false.mean()),
        "ev_true": float(ev_true.mean()),
        "false_survival": float(false_survival.mean()),
    }


@dataclass(frozen=True)
class E1SensitivityParams:
    n_jurors: int = 5
    p_juror_correct: float = 0.80
    representative_p_detect: float = 0.35
    p_detect_min: float = 0.05
    p_detect_max: float = 0.80
    n_points: int = 76


def run_e1(params: E1Params) -> None:
    ps = np.linspace(0.50, 0.99, 50)
    rows: list[dict] = []
    tax = params.bounty * params.challenge_tax_bps / 10_000.0

    for p in ps:
        p_majority = majority_correct_probability(params.n_jurors, float(p))
        for s_over_b in params.stake_ratios:
            seed_results = [
                _e1_single_run(params, float(p), float(s_over_b), seed_idx)
                for seed_idx in range(params.n_seeds)
            ]
            ev_false = np.array([r["ev_false"] for r in seed_results])
            ev_true = np.array([r["ev_true"] for r in seed_results])
            false_survival = np.array([r["false_survival"] for r in seed_results])
            rows.append(
                {
                    "p_juror_correct": float(p),
                    "p_majority_correct": float(p_majority),
                    "stake_over_bounty": float(s_over_b),
                    "n_seeds": params.n_seeds,
                    "trials_per_seed": params.trials_per_seed,
                    "ev_false_mean": float(ev_false.mean()),
                    "ev_false_std": float(ev_false.std()),
                    "ev_false_ci95": _ci95(ev_false),
                    "ev_true_mean": float(ev_true.mean()),
                    "ev_true_std": float(ev_true.std()),
                    "ev_true_ci95": _ci95(ev_true),
                    "false_survival_mean": float(false_survival.mean()),
                    "false_survival_std": float(false_survival.std()),
                    "false_survival_ci95": _ci95(false_survival),
                    "challenge_tax": float(tax),
                    "ddr_fee": float(params.ddr_fee),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e1_results.csv", index=False)

    plt.figure(figsize=(7.0, 4.0))
    for s_over_b in params.stake_ratios:
        sub = df[df["stake_over_bounty"] == s_over_b]
        plt.plot(
            sub["p_juror_correct"],
            sub["ev_false_mean"] / params.bounty,
            label=f"S/B={s_over_b:g}",
        )
        plt.fill_between(
            sub["p_juror_correct"],
            (sub["ev_false_mean"] - sub["ev_false_ci95"]) / params.bounty,
            (sub["ev_false_mean"] + sub["ev_false_ci95"]) / params.bounty,
            alpha=0.15,
        )
    plt.axhline(0.0, color="black", linewidth=0.8)
    plt.xlabel("Per-juror correctness p")
    plt.ylabel("Challenger EV on debunking challenge (normalized by bounty)")
    plt.title(
        f"E1: Debunking-challenge EV vs juror accuracy ({params.n_seeds} seeds, 95% CI)"
    )
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e1_challenger_ev.png", dpi=200)
    plt.close()

    plt.figure(figsize=(7.0, 4.0))
    s_over_b = 0.25
    sub = df[df["stake_over_bounty"] == s_over_b]
    plt.plot(sub["p_juror_correct"], sub["false_survival_mean"])
    plt.fill_between(
        sub["p_juror_correct"],
        sub["false_survival_mean"] - sub["false_survival_ci95"],
        sub["false_survival_mean"] + sub["false_survival_ci95"],
        alpha=0.2,
    )
    plt.xlabel("Per-juror correctness p")
    plt.ylabel("False-claim survival probability")
    plt.title(
        f"E1: False-claim survival (S/B={s_over_b:g}, {params.n_seeds} seeds, 95% CI)"
    )
    plt.ylim(0.0, 1.0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e1_false_survival.png", dpi=200)
    plt.close()


def run_e1_detection_sensitivity(params: E1SensitivityParams) -> None:
    p_majority = majority_correct_probability(params.n_jurors, params.p_juror_correct)
    p_detect_values = np.linspace(params.p_detect_min, params.p_detect_max, params.n_points)
    rows = []
    for p_detect in p_detect_values:
        rows.append(
            {
                "p_detect": float(p_detect),
                "p_juror_correct": float(params.p_juror_correct),
                "p_majority_correct": float(p_majority),
                "false_survival": float(
                    false_claim_survival_probability(float(p_detect), p_majority)
                ),
                "bond_threshold_multiplier": float(
                    bond_threshold_multiplier(float(p_detect), p_majority)
                ),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e1_detection_sensitivity.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.0), sharex=True)

    axes[0].plot(df["p_detect"], df["false_survival"], color="#1f77b4")
    axes[0].axvline(
        params.representative_p_detect,
        color="black",
        linestyle="--",
        linewidth=0.8,
    )
    axes[0].set_xlabel("Detection probability p_detect")
    axes[0].set_ylabel("False-claim survival probability")
    axes[0].set_ylim(0.0, 1.0)
    axes[0].set_title("Single-window survival")

    axes[1].plot(df["p_detect"], df["bond_threshold_multiplier"], color="#d62728")
    axes[1].axvline(
        params.representative_p_detect,
        color="black",
        linestyle="--",
        linewidth=0.8,
    )
    axes[1].set_xlabel("Detection probability p_detect")
    axes[1].set_ylabel("Required bond multiple B*/V")
    axes[1].set_ylim(0.0, df["bond_threshold_multiplier"].max() * 1.05)
    axes[1].set_title("Deterrence threshold")

    fig.suptitle(
        f"E1: Sensitivity to detection coverage at p={params.p_juror_correct:.2f}, N={params.n_jurors}"
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))
    fig.savefig(FIG_DIR / "e1_detection_sensitivity.png", dpi=200)
    plt.close(fig)


@dataclass(frozen=True)
class E1AdvParams:
    n_jurors: int = 5
    bounty: float = 100.0
    stake_ratio: float = 0.25
    p_detect: float = 0.35
    challenge_tax_bps: float = 50.0
    ddr_fee: float = 5.0
    n_attacks: int = 50
    p_juror_range: tuple[float, ...] = (0.60, 0.70, 0.80, 0.90)
    n_seeds: int = 100


def _e1_adv_single_run(params: E1AdvParams, p: float, seed_idx: int) -> dict:
    rng = np.random.default_rng(seed_idx)
    p_majority = majority_correct_probability(params.n_jurors, p)
    b = params.bounty
    s = b * params.stake_ratio
    sunk = b * params.challenge_tax_bps / 10_000.0 + params.ddr_fee
    adv_balance = 0.0
    survived = 0

    for _ in range(params.n_attacks):
        detected = rng.random() < params.p_detect
        if not detected:
            survived += 1
            continue
        jury_correct = rng.random() < p_majority
        if jury_correct:
            adv_balance -= b
        else:
            adv_balance += s
            survived += 1
        adv_balance -= sunk

    return {
        "survival_rate": survived / params.n_attacks,
        "adversary_balance": adv_balance,
        "adversary_balance_per_attack": adv_balance / params.n_attacks,
    }


def run_e1_adversarial(params: E1AdvParams) -> None:
    rows: list[dict] = []
    for p in params.p_juror_range:
        with ProcessPoolExecutor() as executor:
            seed_results = list(
                executor.map(
                    functools.partial(_e1_adv_single_run, params, p),
                    range(params.n_seeds),
                )
            )

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
    ax1.set_ylabel("False-claim survival rate")
    ax1.set_title(
        f"E1-Adv: Survival rate ({params.n_attacks} attacks, N={params.n_seeds} seeds, 95% CI)"
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
        f"E1-Adv: Adversary profit/loss ({params.n_attacks} attacks, N={params.n_seeds} seeds, 95% CI)"
    )
    ax2.axhline(0.0, color="black", linewidth=0.8)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "e1_adversarial.png", dpi=200)
    plt.close()


# ---------------------------------------------------------------------------
# E2: Relevance coherence game with drafted curators
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class E2Params:
    n_curators: int = 200
    committee_size: int = 15
    rounds: int = 200
    slash_rate: float = 0.03
    noise_sigma: float = 0.08
    coherence_cap_share: float = 1.0  # cap disabled for this run
    flat_round_stddev_min: float = 0.02
    ks: tuple[float, ...] = (0.8, 1.0, 1.25, 1.5)
    competent_fracs: tuple[float, ...] = (0.1, 0.3, 0.5, 0.7, 0.9)
    n_seeds: int = 100


def _run_relevance_process(
    *,
    n_curators: int,
    committee_size: int,
    rounds: int,
    slash_rate: float,
    noise_sigma: float,
    coherence_cap_share: float,
    flat_round_stddev_min: float,
    k: float,
    rng: np.random.Generator,
    types: np.ndarray,
    initial_stakes: np.ndarray | None = None,
) -> dict:
    if initial_stakes is None:
        stakes = np.ones(n_curators, dtype=float)
    else:
        stakes = initial_stakes.astype(float).copy()
    abs_errors: list[float] = []
    cancelled_rounds = 0
    selection_counts = np.zeros(n_curators, dtype=int)

    for _ in range(rounds):
        draft_scores = stakes.copy()
        drafted = _weighted_sample_without_replacement(rng, draft_scores, committee_size)
        selection_counts[drafted] += 1

        r_true = float(rng.uniform(0.0, 1.0))
        votes = np.empty(len(drafted), dtype=float)

        drafted_types = types[drafted]
        comp_mask = drafted_types == 0
        noisy_mask = drafted_types == 1
        colluder_mask = drafted_types == 2

        if comp_mask.any():
            votes[comp_mask] = _truncate_0_1(
                rng.normal(loc=r_true, scale=noise_sigma, size=comp_mask.sum())
            )
        if noisy_mask.any():
            votes[noisy_mask] = rng.uniform(0.0, 1.0, size=noisy_mask.sum())
        if colluder_mask.any():
            biased_target = min(1.0, r_true + 0.30)
            votes[colluder_mask] = _truncate_0_1(
                rng.normal(
                    loc=biased_target,
                    scale=noise_sigma * 0.5,
                    size=colluder_mask.sum(),
                )
            )

        weights = _committee_weights(stakes[drafted], coherence_cap_share)
        weight_sum = float(weights.sum())
        if weight_sum <= 0:
            cancelled_rounds += 1
            continue

        mu = float((weights * votes).sum() / weight_sum)
        sigma = float(np.sqrt(((weights * (votes - mu) ** 2).sum() / weight_sum)))

        if sigma < flat_round_stddev_min:
            cancelled_rounds += 1
            continue

        coherent = np.abs(votes - mu) <= (k * sigma)
        incoherent = ~coherent
        incoherent_idx = drafted[incoherent]
        coherent_idx = drafted[coherent]

        slashed = slash_rate * stakes[incoherent_idx]
        total_slashed = float(slashed.sum())
        stakes[incoherent_idx] -= slashed

        if total_slashed > 0 and len(coherent_idx) > 0:
            coherent_stakes = stakes[coherent_idx]
            coherent_total = float(coherent_stakes.sum())
            if coherent_total > 0:
                stakes[coherent_idx] += total_slashed * (coherent_stakes / coherent_total)

        abs_errors.append(abs(mu - r_true))

    return {
        "mean_abs_error": float(np.mean(abs_errors)) if abs_errors else 0.0,
        "cancelled_round_share": cancelled_rounds / rounds,
        "selection_counts": selection_counts,
        "stakes": stakes,
    }


def _e2_single_run(params: E2Params, frac: float, k: float, seed_idx: int) -> dict:
    rng = np.random.default_rng(seed_idx * 10_000 + int(1_000 * frac) + int(100 * k))
    n_comp = int(round(params.n_curators * frac))
    types = np.array([0] * n_comp + [1] * (params.n_curators - n_comp), dtype=int)
    rng.shuffle(types)

    result = _run_relevance_process(
        n_curators=params.n_curators,
        committee_size=params.committee_size,
        rounds=params.rounds,
        slash_rate=params.slash_rate,
        noise_sigma=params.noise_sigma,
        coherence_cap_share=params.coherence_cap_share,
        flat_round_stddev_min=params.flat_round_stddev_min,
        k=k,
        rng=rng,
        types=types,
    )

    competent_mask = types == 0
    return {
        "mean_abs_error": result["mean_abs_error"],
        "cancelled_round_share": result["cancelled_round_share"],
        "final_competent_stake_share": float(
            result["stakes"][competent_mask].sum() / result["stakes"].sum()
        ),
        "competent_draft_share": float(
            result["selection_counts"][competent_mask].sum()
            / result["selection_counts"].sum()
        ),
    }


def run_e2(params: E2Params) -> None:
    rows: list[dict] = []

    for frac in params.competent_fracs:
        for k in params.ks:
            with ProcessPoolExecutor() as executor:
                seed_results = list(
                    executor.map(
                        functools.partial(_e2_single_run, params, frac, k),
                        range(params.n_seeds),
                    )
                )

            errors = np.array([r["mean_abs_error"] for r in seed_results])
            cancelled = np.array([r["cancelled_round_share"] for r in seed_results])
            stakes = np.array([r["final_competent_stake_share"] for r in seed_results])
            draft = np.array([r["competent_draft_share"] for r in seed_results])

            rows.append(
                {
                    "competent_frac": float(frac),
                    "K": float(k),
                    "n_seeds": params.n_seeds,
                    "mean_abs_error_mean": float(errors.mean()),
                    "mean_abs_error_std": float(errors.std()),
                    "mean_abs_error_ci95": _ci95(errors),
                    "cancelled_round_share_mean": float(cancelled.mean()),
                    "cancelled_round_share_std": float(cancelled.std()),
                    "cancelled_round_share_ci95": _ci95(cancelled),
                    "final_competent_stake_share_mean": float(stakes.mean()),
                    "final_competent_stake_share_std": float(stakes.std()),
                    "final_competent_stake_share_ci95": _ci95(stakes),
                    "competent_draft_share_mean": float(draft.mean()),
                    "competent_draft_share_std": float(draft.std()),
                    "competent_draft_share_ci95": _ci95(draft),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e2_results.csv", index=False)

    plt.figure(figsize=(7.0, 4.0))
    for k in params.ks:
        sub = df[df["K"] == k].sort_values("competent_frac")
        plt.plot(
            sub["competent_frac"],
            sub["mean_abs_error_mean"],
            marker="o",
            label=f"K={k:g}",
        )
        plt.fill_between(
            sub["competent_frac"],
            sub["mean_abs_error_mean"] - sub["mean_abs_error_ci95"],
            sub["mean_abs_error_mean"] + sub["mean_abs_error_ci95"],
            alpha=0.15,
        )
    plt.xlabel("Fraction competent curators")
    plt.ylabel("Mean |mu - r|")
    plt.title(
        f"E2: Drafted-curator relevance error vs competence and K (N={params.n_seeds} seeds)"
    )
    plt.legend(frameon=False, ncol=2)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e2_relevance_error.png", dpi=200)
    plt.close()

    plt.figure(figsize=(7.0, 4.0))
    sub = df[df["K"] == 1.25].sort_values("competent_frac")
    plt.plot(
        sub["competent_frac"], sub["final_competent_stake_share_mean"], marker="o"
    )
    plt.fill_between(
        sub["competent_frac"],
        sub["final_competent_stake_share_mean"]
        - sub["final_competent_stake_share_ci95"],
        sub["final_competent_stake_share_mean"]
        + sub["final_competent_stake_share_ci95"],
        alpha=0.2,
    )
    plt.xlabel("Initial fraction competent curators")
    plt.ylabel("Final competent stake share")
    plt.title(
        f"E2: Competence filter with drafted curators (K=1.25, N={params.n_seeds} seeds)"
    )
    plt.ylim(0.0, 1.0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e2_competence_filter.png", dpi=200)
    plt.close()


@dataclass(frozen=True)
class E2AdvParams:
    n_curators: int = 200
    committee_size: int = 15
    rounds: int = 200
    slash_rate: float = 0.03
    noise_sigma: float = 0.08
    coherence_cap_share: float = 1.0  # cap disabled for this run
    flat_round_stddev_min: float = 0.02
    K: float = 1.25
    competent_frac: float = 0.6
    colluding_fracs: tuple[float, ...] = (0.0, 0.05, 0.10, 0.15, 0.20, 0.30)
    n_seeds: int = 100


def _e2_adv_single_run(params: E2AdvParams, col_frac: float, seed_idx: int) -> dict:
    rng = np.random.default_rng(int(10_000 * col_frac + seed_idx))
    n_comp = int(round(params.n_curators * params.competent_frac))
    n_collude = int(round(params.n_curators * col_frac))
    n_honest_comp = max(0, n_comp - n_collude)
    n_noisy = params.n_curators - n_honest_comp - n_collude
    types = np.array(
        [0] * n_honest_comp + [1] * n_noisy + [2] * n_collude,
        dtype=int,
    )
    rng.shuffle(types)

    result = _run_relevance_process(
        n_curators=params.n_curators,
        committee_size=params.committee_size,
        rounds=params.rounds,
        slash_rate=params.slash_rate,
        noise_sigma=params.noise_sigma,
        coherence_cap_share=params.coherence_cap_share,
        flat_round_stddev_min=params.flat_round_stddev_min,
        k=params.K,
        rng=rng,
        types=types,
    )

    colluder_mask = types == 2
    draft_total = int(result["selection_counts"].sum())
    return {
        "mean_abs_error": result["mean_abs_error"],
        "final_colluder_stake_share": float(
            result["stakes"][colluder_mask].sum() / result["stakes"].sum()
        )
        if colluder_mask.any()
        else 0.0,
        "colluder_draft_share": float(
            result["selection_counts"][colluder_mask].sum() / draft_total
        )
        if colluder_mask.any() and draft_total > 0
        else 0.0,
        "cancelled_round_share": result["cancelled_round_share"],
    }


def run_e2_adversarial(params: E2AdvParams) -> None:
    rows: list[dict] = []
    for col_frac in params.colluding_fracs:
        with ProcessPoolExecutor() as executor:
            seed_results = list(
                executor.map(
                    functools.partial(_e2_adv_single_run, params, col_frac),
                    range(params.n_seeds),
                )
            )

        errors = np.array([r["mean_abs_error"] for r in seed_results])
        stake_shares = np.array([r["final_colluder_stake_share"] for r in seed_results])
        draft_shares = np.array([r["colluder_draft_share"] for r in seed_results])
        cancelled = np.array([r["cancelled_round_share"] for r in seed_results])

        rows.append(
            {
                "colluding_frac": col_frac,
                "n_seeds": params.n_seeds,
                "mean_abs_error_mean": float(errors.mean()),
                "mean_abs_error_ci95": _ci95(errors),
                "final_colluder_stake_share_mean": float(stake_shares.mean()),
                "final_colluder_stake_share_ci95": _ci95(stake_shares),
                "colluder_draft_share_mean": float(draft_shares.mean()),
                "colluder_draft_share_ci95": _ci95(draft_shares),
                "cancelled_round_share_mean": float(cancelled.mean()),
                "initial_colluder_stake_share": col_frac,
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e2_adversarial_results.csv", index=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.5))
    x = df["colluding_frac"]

    ax1.plot(x, df["mean_abs_error_mean"], marker="o", color="#4C72B0")
    ax1.fill_between(
        x,
        df["mean_abs_error_mean"] - df["mean_abs_error_ci95"],
        df["mean_abs_error_mean"] + df["mean_abs_error_ci95"],
        alpha=0.2,
        color="#4C72B0",
    )
    ax1.set_xlabel("Fraction of colluding curators")
    ax1.set_ylabel("Mean |mu - r|")
    ax1.set_title(
        f"E2-Adv: Drafted-curator signal error under collusion (K={params.K}, N={params.n_seeds} seeds)"
    )

    ax2.plot(
        x,
        df["initial_colluder_stake_share"],
        marker="o",
        linestyle="--",
        color="gray",
        label="Initial stake share",
    )
    ax2.plot(
        x,
        df["final_colluder_stake_share_mean"],
        marker="o",
        color="#C44E52",
        label="Final stake share",
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
        f"E2-Adv: Colluder stake share after repeated rounds (N={params.n_seeds} seeds)"
    )
    ax2.set_ylim(0.0, max(0.4, df["initial_colluder_stake_share"].max() * 1.2))
    ax2.legend(frameon=False, fontsize=9)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "e2_adversarial.png", dpi=200)
    plt.close()


# ---------------------------------------------------------------------------
# E3: Non-falsifiable challenge defense
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class E3Params:
    n_jurors: int = 5
    p_false_claim_juror_correct: float = 0.85
    p_nonfalsifiable_reason_juror_correct: float = 0.85
    forced_binary_juror_correct_scenarios: tuple[float, ...] = (0.55, 0.65, 0.75, 0.85)
    nonfalsifiable_fracs: tuple[float, ...] = (
        0.0,
        0.05,
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
    )


def _e3_bad_item_retention(
    nonfalsifiable_frac: float,
    p_major_false: float,
    p_major_nonfalsifiable: float,
) -> float:
    return (1 - nonfalsifiable_frac) * (1 - p_major_false) + nonfalsifiable_frac * (
        1 - p_major_nonfalsifiable
    )


def run_e3(params: E3Params) -> None:
    p_major_false = majority_correct_probability(
        params.n_jurors, params.p_false_claim_juror_correct
    )
    p_major_nf_defended = majority_correct_probability(
        params.n_jurors, params.p_nonfalsifiable_reason_juror_correct
    )

    rows: list[dict] = []
    for forced_binary_p in params.forced_binary_juror_correct_scenarios:
        p_major_nf_baseline = majority_correct_probability(
            params.n_jurors, forced_binary_p
        )
        for frac in params.nonfalsifiable_fracs:
            baseline_retention = _e3_bad_item_retention(
                frac, p_major_false, p_major_nf_baseline
            )
            defended_retention = _e3_bad_item_retention(
                frac, p_major_false, p_major_nf_defended
            )
            rows.append(
                {
                    "nonfalsifiable_frac": float(frac),
                    "forced_binary_juror_correct": float(forced_binary_p),
                    "baseline_bad_item_retention": float(baseline_retention),
                    "defended_bad_item_retention": float(defended_retention),
                    "retention_reduction": float(
                        baseline_retention - defended_retention
                    ),
                    "p_major_false": float(p_major_false),
                    "p_major_nf_baseline": float(p_major_nf_baseline),
                    "p_major_nf_defended": float(p_major_nf_defended),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e3_results.csv", index=False)

    plt.figure(figsize=(7.0, 4.0))
    defended = (
        df[df["forced_binary_juror_correct"] == params.forced_binary_juror_correct_scenarios[0]]
        .sort_values("nonfalsifiable_frac")
        .copy()
    )
    for forced_binary_p in params.forced_binary_juror_correct_scenarios:
        sub = (
            df[df["forced_binary_juror_correct"] == forced_binary_p]
            .sort_values("nonfalsifiable_frac")
            .copy()
        )
        plt.plot(
            sub["nonfalsifiable_frac"],
            sub["baseline_bad_item_retention"],
            marker="o",
            label=f"forced binary baseline (p={forced_binary_p:.2f})",
        )
    plt.plot(
        defended["nonfalsifiable_frac"],
        defended["defended_bad_item_retention"],
        marker="o",
        linewidth=2.2,
        color="black",
        label=f"dedicated reason (p={params.p_nonfalsifiable_reason_juror_correct:.2f})",
    )
    plt.xlabel("Fraction of non-falsifiable bad items")
    plt.ylabel("Bad-item retention after challenge")
    plt.title("E3: Closed-form scenario analysis for non-falsifiable challenges")
    plt.legend(frameon=False, fontsize=8)
    plt.ylim(0.0, 1.0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e3_nonfalsifiable.png", dpi=200)
    plt.close()


# ---------------------------------------------------------------------------
# E4: Reputation redesign
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class E4aParams:
    n_authors: int = 200
    rounds: int = 120
    n_seeds: int = 100
    honest_frac: float = 0.6
    honest_challenge_failed_prob: float = 0.85
    dishonest_challenge_failed_prob: float = 0.20
    dishonest_challenge_failed_grid: tuple[float, ...] = (0.20, 0.30, 0.40, 0.50, 0.60)
    rep_reward: float = 1.0
    bust_slash_rate: float = 0.50
    rep_decay: float = 0.01


def _e4a_single_run(
    params: E4aParams, dishonest_challenge_failed_prob: float, seed_idx: int
) -> dict[str, np.ndarray]:
    n_honest = int(round(params.n_authors * params.honest_frac))
    author_type = np.array([0] * n_honest + [1] * (params.n_authors - n_honest), dtype=int)
    honest_mask = author_type == 0
    dishonest_mask = author_type == 1
    probs = np.where(
        honest_mask,
        params.honest_challenge_failed_prob,
        dishonest_challenge_failed_prob,
    ).astype(float)

    rng = np.random.default_rng(seed_idx)
    rep = np.zeros(params.n_authors, dtype=float)
    honest_median = np.zeros(params.rounds, dtype=float)
    dishonest_median = np.zeros(params.rounds, dtype=float)
    honest_mean = np.zeros(params.rounds, dtype=float)
    dishonest_mean = np.zeros(params.rounds, dtype=float)

    for round_idx in range(params.rounds):
        outcomes = rng.random(params.n_authors) < probs
        rep[outcomes] += params.rep_reward
        rep[~outcomes] *= 1.0 - params.bust_slash_rate
        rep *= 1.0 - params.rep_decay

        honest_median[round_idx] = float(np.median(rep[honest_mask]))
        dishonest_median[round_idx] = float(np.median(rep[dishonest_mask]))
        honest_mean[round_idx] = float(rep[honest_mask].mean())
        dishonest_mean[round_idx] = float(rep[dishonest_mask].mean())

    return {
        "honest_median_rep": honest_median,
        "dishonest_median_rep": dishonest_median,
        "honest_mean_rep": honest_mean,
        "dishonest_mean_rep": dishonest_mean,
    }


def run_e4a(params: E4aParams) -> None:
    baseline_runs = [
        _e4a_single_run(params, params.dishonest_challenge_failed_prob, seed_idx)
        for seed_idx in range(params.n_seeds)
    ]
    honest_median = np.vstack([run["honest_median_rep"] for run in baseline_runs])
    dishonest_median = np.vstack([run["dishonest_median_rep"] for run in baseline_runs])
    honest_mean = np.vstack([run["honest_mean_rep"] for run in baseline_runs])
    dishonest_mean = np.vstack([run["dishonest_mean_rep"] for run in baseline_runs])

    df = pd.DataFrame(
        {
            "round": np.arange(1, params.rounds + 1),
            "n_seeds": params.n_seeds,
            "dishonest_challenge_failed_prob": params.dishonest_challenge_failed_prob,
            "honest_median_rep_mean": honest_median.mean(axis=0),
            "honest_median_rep_ci95": [_ci95(honest_median[:, i]) for i in range(params.rounds)],
            "dishonest_median_rep_mean": dishonest_median.mean(axis=0),
            "dishonest_median_rep_ci95": [
                _ci95(dishonest_median[:, i]) for i in range(params.rounds)
            ],
            "honest_mean_rep_mean": honest_mean.mean(axis=0),
            "honest_mean_rep_ci95": [_ci95(honest_mean[:, i]) for i in range(params.rounds)],
            "dishonest_mean_rep_mean": dishonest_mean.mean(axis=0),
            "dishonest_mean_rep_ci95": [
                _ci95(dishonest_mean[:, i]) for i in range(params.rounds)
            ],
        }
    )
    df.to_csv(OUT_DIR / "e4a_author_reputation.csv", index=False)

    sensitivity_rows: list[dict] = []
    for dishonest_prob in params.dishonest_challenge_failed_grid:
        runs = [
            _e4a_single_run(params, dishonest_prob, seed_idx)
            for seed_idx in range(params.n_seeds)
        ]
        honest_final = np.array([run["honest_median_rep"][-1] for run in runs], dtype=float)
        dishonest_final = np.array(
            [run["dishonest_median_rep"][-1] for run in runs], dtype=float
        )
        gap = honest_final - dishonest_final
        sensitivity_rows.append(
            {
                "dishonest_challenge_failed_prob": dishonest_prob,
                "n_seeds": params.n_seeds,
                "honest_final_median_rep_mean": float(honest_final.mean()),
                "honest_final_median_rep_ci95": _ci95(honest_final),
                "dishonest_final_median_rep_mean": float(dishonest_final.mean()),
                "dishonest_final_median_rep_ci95": _ci95(dishonest_final),
                "median_gap_mean": float(gap.mean()),
                "median_gap_ci95": _ci95(gap),
            }
        )

    sensitivity = pd.DataFrame(sensitivity_rows)
    sensitivity.to_csv(OUT_DIR / "e4a_author_reputation_sensitivity.csv", index=False)

    plt.figure(figsize=(11.0, 4.0))
    ax1 = plt.subplot(1, 2, 1)
    ax1.plot(df["round"], df["honest_median_rep_mean"], label="honest authors")
    ax1.fill_between(
        df["round"],
        df["honest_median_rep_mean"] - df["honest_median_rep_ci95"],
        df["honest_median_rep_mean"] + df["honest_median_rep_ci95"],
        alpha=0.2,
    )
    ax1.plot(df["round"], df["dishonest_median_rep_mean"], label="dishonest authors")
    ax1.fill_between(
        df["round"],
        df["dishonest_median_rep_mean"] - df["dishonest_median_rep_ci95"],
        df["dishonest_median_rep_mean"] + df["dishonest_median_rep_ci95"],
        alpha=0.2,
    )
    ax1.set_xlabel("Publication rounds")
    ax1.set_ylabel("Median author reputation")
    ax1.set_title("Baseline trajectories")
    ax1.legend(frameon=False)

    ax2 = plt.subplot(1, 2, 2)
    ax2.plot(
        sensitivity["dishonest_challenge_failed_prob"],
        sensitivity["honest_final_median_rep_mean"],
        label="honest authors",
    )
    ax2.fill_between(
        sensitivity["dishonest_challenge_failed_prob"],
        sensitivity["honest_final_median_rep_mean"]
        - sensitivity["honest_final_median_rep_ci95"],
        sensitivity["honest_final_median_rep_mean"]
        + sensitivity["honest_final_median_rep_ci95"],
        alpha=0.2,
    )
    ax2.plot(
        sensitivity["dishonest_challenge_failed_prob"],
        sensitivity["dishonest_final_median_rep_mean"],
        label="dishonest authors",
    )
    ax2.fill_between(
        sensitivity["dishonest_challenge_failed_prob"],
        sensitivity["dishonest_final_median_rep_mean"]
        - sensitivity["dishonest_final_median_rep_ci95"],
        sensitivity["dishonest_final_median_rep_mean"]
        + sensitivity["dishonest_final_median_rep_ci95"],
        alpha=0.2,
    )
    ax2.axvline(
        params.dishonest_challenge_failed_prob,
        color="0.4",
        linestyle="--",
        linewidth=1.0,
    )
    ax2.set_xlabel("Dishonest challenge-survival probability")
    ax2.set_ylabel("Final-round median reputation")
    ax2.set_title("Sensitivity to harder-to-challenge false claims")

    plt.suptitle("E4a: Author reputation as a standing bond", y=1.02)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e4a_author_reputation.png", dpi=200)
    plt.close()


@dataclass(frozen=True)
class E4dParams:
    build_rounds: int = 80
    attack_rounds: int = 40
    n_local_honest_authors: int = 50
    low_stakes_honest_success_prob: float = 0.95
    high_stakes_honest_success_prob: float = 0.85
    high_stakes_attacker_success_prob: float = 0.20
    rep_reward: float = 1.0
    bust_slash_rate: float = 0.50
    rep_decay: float = 0.01
    n_seeds: int = 200
    exhaustion_epsilon: float = 0.10


def _update_scalar_reputation(
    rep: float, success: bool, reward: float, slash_rate: float, decay: float
) -> float:
    if success:
        rep += reward
    else:
        rep *= 1.0 - slash_rate
    rep *= 1.0 - decay
    return float(rep)


def _update_vector_reputation(
    rep: np.ndarray, success: np.ndarray, reward: float, slash_rate: float, decay: float
) -> np.ndarray:
    rep = rep.copy()
    rep[success] += reward
    rep[~success] *= 1.0 - slash_rate
    rep *= 1.0 - decay
    return rep


def run_e4d(params: E4dParams) -> None:
    round_rows: list[dict] = []
    imported_reps: list[float] = []
    exhaustion_rounds: list[float] = []

    for seed in range(params.n_seeds):
        rng = np.random.default_rng(seed)

        pool_l_rep = 0.0
        for _ in range(params.build_rounds):
            pool_l_rep = _update_scalar_reputation(
                pool_l_rep,
                bool(rng.random() < params.low_stakes_honest_success_prob),
                params.rep_reward,
                params.bust_slash_rate,
                params.rep_decay,
            )

        local_honest_rep = np.zeros(params.n_local_honest_authors, dtype=float)
        for _ in range(params.build_rounds):
            local_honest_rep = _update_vector_reputation(
                local_honest_rep,
                rng.random(params.n_local_honest_authors)
                < params.high_stakes_honest_success_prob,
                params.rep_reward,
                params.bust_slash_rate,
                params.rep_decay,
            )

        imported_reps.append(pool_l_rep)
        attacker_rep_scoped = 0.0
        attacker_rep_unscoped = pool_l_rep
        exhaustion_round = float(params.attack_rounds)

        for attack_round in range(1, params.attack_rounds + 1):
            local_honest_rep = _update_vector_reputation(
                local_honest_rep,
                rng.random(params.n_local_honest_authors)
                < params.high_stakes_honest_success_prob,
                params.rep_reward,
                params.bust_slash_rate,
                params.rep_decay,
            )
            attacker_success = bool(
                rng.random() < params.high_stakes_attacker_success_prob
            )
            attacker_rep_scoped = _update_scalar_reputation(
                attacker_rep_scoped,
                attacker_success,
                params.rep_reward,
                params.bust_slash_rate,
                params.rep_decay,
            )
            attacker_rep_unscoped = _update_scalar_reputation(
                attacker_rep_unscoped,
                attacker_success,
                params.rep_reward,
                params.bust_slash_rate,
                params.rep_decay,
            )

            total_rep_scoped = float(local_honest_rep.sum() + attacker_rep_scoped)
            total_rep_unscoped = float(local_honest_rep.sum() + attacker_rep_unscoped)

            round_rows.append(
                {
                    "seed": seed,
                    "attack_round": attack_round,
                    "condition": "scoped",
                    "attacker_rep": attacker_rep_scoped,
                    "attacker_rep_share": (
                        attacker_rep_scoped / total_rep_scoped if total_rep_scoped > 0 else 0.0
                    ),
                }
            )
            round_rows.append(
                {
                    "seed": seed,
                    "attack_round": attack_round,
                    "condition": "unscoped",
                    "attacker_rep": attacker_rep_unscoped,
                    "attacker_rep_share": (
                        attacker_rep_unscoped / total_rep_unscoped
                        if total_rep_unscoped > 0
                        else 0.0
                    ),
                }
            )

            if (
                exhaustion_round == float(params.attack_rounds)
                and attacker_rep_unscoped <= attacker_rep_scoped + params.exhaustion_epsilon
            ):
                exhaustion_round = float(attack_round)

        exhaustion_rounds.append(exhaustion_round)

    round_df = pd.DataFrame(round_rows)
    agg = (
        round_df.groupby(["condition", "attack_round"], as_index=False)
        .agg(
            attacker_rep_mean=("attacker_rep", "mean"),
            attacker_rep_ci95=("attacker_rep", lambda x: _ci95(x.to_numpy())),
            attacker_rep_share_mean=("attacker_rep_share", "mean"),
            attacker_rep_share_ci95=("attacker_rep_share", lambda x: _ci95(x.to_numpy())),
        )
        .sort_values(["condition", "attack_round"])
    )
    agg.to_csv(OUT_DIR / "e4d_cross_domain_scoping.csv", index=False)

    early_window = round_df[round_df["attack_round"] <= 10]
    early_share = (
        early_window.groupby(["seed", "condition"], as_index=False)["attacker_rep_share"].mean()
    )
    early_share_wide = early_share.pivot(
        index="seed", columns="condition", values="attacker_rep_share"
    )

    summary = pd.DataFrame(
        [
            {
                "n_seeds": params.n_seeds,
                "imported_rep_at_entry_mean": float(np.mean(imported_reps)),
                "imported_rep_at_entry_ci95": _ci95(np.asarray(imported_reps)),
                "mean_attacker_rep_share_scoped_first10": float(
                    early_share_wide["scoped"].mean()
                ),
                "mean_attacker_rep_share_scoped_first10_ci95": _ci95(
                    early_share_wide["scoped"].to_numpy()
                ),
                "mean_attacker_rep_share_unscoped_first10": float(
                    early_share_wide["unscoped"].mean()
                ),
                "mean_attacker_rep_share_unscoped_first10_ci95": _ci95(
                    early_share_wide["unscoped"].to_numpy()
                ),
                "advantage_exhaustion_round_mean": float(np.mean(exhaustion_rounds)),
                "advantage_exhaustion_round_ci95": _ci95(np.asarray(exhaustion_rounds)),
            }
        ]
    )
    summary.to_csv(OUT_DIR / "e4d_cross_domain_scoping_summary.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0))
    labels = {"scoped": "scoped (Pool H starts at 0)", "unscoped": "unscoped (imports Pool L rep)"}
    colors = {"scoped": "#1f77b4", "unscoped": "#d62728"}

    for condition in ("scoped", "unscoped"):
        sub = agg[agg["condition"] == condition]
        axes[0].plot(
            sub["attack_round"],
            sub["attacker_rep_mean"],
            label=labels[condition],
            color=colors[condition],
        )
        axes[0].fill_between(
            sub["attack_round"],
            sub["attacker_rep_mean"] - sub["attacker_rep_ci95"],
            sub["attacker_rep_mean"] + sub["attacker_rep_ci95"],
            color=colors[condition],
            alpha=0.15,
        )
        axes[1].plot(
            sub["attack_round"],
            sub["attacker_rep_share_mean"],
            label=labels[condition],
            color=colors[condition],
        )
        axes[1].fill_between(
            sub["attack_round"],
            sub["attacker_rep_share_mean"] - sub["attacker_rep_share_ci95"],
            sub["attacker_rep_share_mean"] + sub["attacker_rep_share_ci95"],
            color=colors[condition],
            alpha=0.15,
        )

    axes[0].set_xlabel("Attack rounds in Pool H")
    axes[0].set_ylabel("Mean attacker reputation in Pool H")
    axes[0].set_title("Imported reputation persists without scoping")
    axes[0].legend(frameon=False, fontsize=8)

    axes[1].set_xlabel("Attack rounds in Pool H")
    axes[1].set_ylabel("Mean attacker share of Pool H author reputation")
    axes[1].set_ylim(0.0, 0.35)
    axes[1].set_title("Carryover appears as interface-level credibility context")

    fig.suptitle("E4d: Cross-domain author reputation scoping", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "e4d_cross_domain_scoping.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
@dataclass(frozen=True)
class E4bParams:
    n_honest_curators: int = 14
    rounds: int = 300
    honest_rep_0: float = 100.0
    attacker_rep_0: float = 200.0
    honest_noise_sigma: float = 0.08
    attacker_noise_sigma: float = 0.04
    K: float = 1.25
    rep_decays: tuple[float, ...] = (0.005, 0.01, 0.02)
    attacker_biases: tuple[float, ...] = (0.15, 0.30)
    n_seeds: int = 100


def _e4b_attacker_vote(
    rng: np.random.Generator,
    r_true: float,
    attacker_model: str,
    attacker_noise_sigma: float,
) -> float:
    if attacker_model == "random":
        return float(rng.uniform(0.0, 1.0))
    if attacker_model.startswith("bias_"):
        bias = float(attacker_model.split("_", maxsplit=1)[1])
        return float(
            _truncate_0_1(rng.normal(r_true + bias, attacker_noise_sigma, size=1))[0]
        )
    raise ValueError(f"unknown attacker model: {attacker_model}")


def _e4b_single_run(params: E4bParams, rep_decay: float, attacker_model: str, seed_idx: int) -> dict:
    seed = int(100_000 * rep_decay) + 1_000 * seed_idx + sum(
        ord(ch) for ch in attacker_model
    )
    rng = np.random.default_rng(seed)

    rep = np.full(params.n_honest_curators + 1, params.honest_rep_0, dtype=float)
    rep[-1] = params.attacker_rep_0

    above_median_rounds = 0
    mean_abs_errors: list[float] = []
    mean_excess_abs_errors: list[float] = []
    mean_signal_shifts: list[float] = []

    for _ in range(params.rounds):
        r_true = float(rng.uniform(0.0, 1.0))
        honest_votes = _truncate_0_1(
            rng.normal(
                loc=r_true,
                scale=params.honest_noise_sigma,
                size=params.n_honest_curators,
            )
        )
        attacker_vote = _e4b_attacker_vote(
            rng, r_true, attacker_model, params.attacker_noise_sigma
        )
        votes = np.concatenate([honest_votes, [attacker_vote]])

        total_rep = float(rep.sum())
        if total_rep <= 0:
            weights = np.full_like(rep, 1.0 / len(rep))
        else:
            weights = rep / total_rep

        mu = float((weights * votes).sum())
        sigma = float(np.sqrt((weights * (votes - mu) ** 2).sum()))
        honest_mu = float(honest_votes.mean())

        mean_abs_errors.append(abs(mu - r_true))
        mean_excess_abs_errors.append(abs(mu - r_true) - abs(honest_mu - r_true))
        mean_signal_shifts.append(mu - honest_mu)

        coherent = np.abs(votes - mu) <= (params.K * sigma)
        rep = rep * (1.0 - rep_decay) + coherent.astype(float)
        if rep[-1] > float(np.median(rep[:-1])):
            above_median_rounds += 1

    return {
        "above_median_rounds": float(above_median_rounds),
        "above_median_round_share": above_median_rounds / params.rounds,
        "mean_abs_error": float(np.mean(mean_abs_errors)),
        "mean_excess_abs_error": float(np.mean(mean_excess_abs_errors)),
        "mean_signal_shift": float(np.mean(mean_signal_shifts)),
    }


def run_e4b(params: E4bParams) -> None:
    rows: list[dict] = []
    attacker_models = ["random", *[f"bias_{bias:.2f}" for bias in params.attacker_biases]]

    for rep_decay in params.rep_decays:
        for attacker_model in attacker_models:
            with ProcessPoolExecutor() as executor:
                seed_results = list(
                    executor.map(
                        functools.partial(_e4b_single_run, params, rep_decay, attacker_model),
                        range(params.n_seeds),
                    )
                )

            above = np.array([r["above_median_rounds"] for r in seed_results])
            above_share = np.array([r["above_median_round_share"] for r in seed_results])
            abs_error = np.array([r["mean_abs_error"] for r in seed_results])
            excess_error = np.array([r["mean_excess_abs_error"] for r in seed_results])
            shift = np.array([r["mean_signal_shift"] for r in seed_results])

            rows.append(
                {
                    "rep_decay": float(rep_decay),
                    "attacker_model": attacker_model,
                    "n_seeds": params.n_seeds,
                    "rounds": params.rounds,
                    "above_median_rounds_mean": float(above.mean()),
                    "above_median_rounds_ci95": _ci95(above),
                    "above_median_round_share_mean": float(above_share.mean()),
                    "above_median_round_share_ci95": _ci95(above_share),
                    "mean_abs_error_mean": float(abs_error.mean()),
                    "mean_abs_error_ci95": _ci95(abs_error),
                    "mean_excess_abs_error_mean": float(excess_error.mean()),
                    "mean_excess_abs_error_ci95": _ci95(excess_error),
                    "mean_signal_shift_mean": float(shift.mean()),
                    "mean_signal_shift_ci95": _ci95(shift),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e4b_reputation_attack.csv", index=False)

    labels = ["random", *[f"+{bias:.2f} bias" for bias in params.attacker_biases]]
    attacker_models = ["random", *[f"bias_{bias:.2f}" for bias in params.attacker_biases]]
    colors = ["#4C72B0", "#DD8452", "#C44E52"]
    x = np.arange(len(params.rep_decays))
    width = 0.24

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.5))
    if not (len(attacker_models) == len(labels) == len(colors)):
        raise ValueError("E4b plotting metadata must have matching lengths")
    for idx, (attacker_model, label, color) in enumerate(
        zip(attacker_models, labels, colors)
    ):
        sub = df[df["attacker_model"] == attacker_model].sort_values("rep_decay")
        offset = (idx - 1) * width

        ax1.bar(
            x + offset,
            sub["above_median_rounds_mean"],
            width=width,
            yerr=sub["above_median_rounds_ci95"],
            color=color,
            capsize=3,
            label=label,
        )
        ax2.bar(
            x + offset,
            sub["mean_signal_shift_mean"],
            width=width,
            yerr=sub["mean_signal_shift_ci95"],
            color=color,
            capsize=3,
            label=label,
        )

    tick_labels = [f"{rep_decay:.3f}" for rep_decay in params.rep_decays]
    ax1.set_xticks(x)
    ax1.set_xticklabels(tick_labels)
    ax1.set_xlabel("Reputation decay rate δ")
    ax1.set_ylabel("Rounds above median committee weight")
    ax1.set_title(
        f"E4b: Single high-reputation attacker retention ({params.rounds} rounds, N={params.n_seeds} seeds)"
    )
    ax1.legend(frameon=False, fontsize=9)

    ax2.axhline(0.0, color="black", linewidth=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(tick_labels)
    ax2.set_xlabel("Reputation decay rate δ")
    ax2.set_ylabel("Mean signal shift vs honest-only committee")
    ax2.set_title("E4b: Directional distortion under biased strategic voting")

    plt.tight_layout()
    plt.savefig(FIG_DIR / "e4b_reputation_attack.png", dpi=200)
    plt.close()




# ---------------------------------------------------------------------------
# Evaluation summary
# ---------------------------------------------------------------------------


def write_eval_summary() -> None:
    params_e1 = E1Params()
    params_e1_sensitivity = E1SensitivityParams()
    e1 = pd.read_csv(OUT_DIR / "e1_results.csv")
    e1_sensitivity = pd.read_csv(OUT_DIR / "e1_detection_sensitivity.csv")
    e2 = pd.read_csv(OUT_DIR / "e2_results.csv")
    e3 = pd.read_csv(OUT_DIR / "e3_results.csv")
    e1_adv = pd.read_csv(OUT_DIR / "e1_adversarial_results.csv")
    e2_adv = pd.read_csv(OUT_DIR / "e2_adversarial_results.csv")
    e4a = pd.read_csv(OUT_DIR / "e4a_author_reputation.csv")
    e4b = pd.read_csv(OUT_DIR / "e4b_reputation_attack.csv")
    e4d = pd.read_csv(OUT_DIR / "e4d_cross_domain_scoping_summary.csv")
    e1_sub = e1[e1["stake_over_bounty"] == 0.25].copy()
    e1_sub["p_delta"] = (e1_sub["p_juror_correct"] - 0.8).abs()
    e1_point = e1_sub.sort_values("p_delta").iloc[0]
    e1_sensitivity_010 = e1_sensitivity.iloc[
        (e1_sensitivity["p_detect"] - 0.10).abs().argmin()
    ]
    e1_sensitivity_050 = e1_sensitivity.iloc[
        (e1_sensitivity["p_detect"] - 0.50).abs().argmin()
    ]
    e2_point = e2[(e2["K"] == 1.25) & (e2["competent_frac"] == 0.70)].iloc[0]
    e3_point = e3[
        (e3["nonfalsifiable_frac"] == 0.25)
        & (e3["forced_binary_juror_correct"] == 0.55)
    ].iloc[0]
    e1_adv_point = e1_adv[e1_adv["p_juror_correct"] == 0.80].iloc[0]
    e2_adv_point = e2_adv[e2_adv["colluding_frac"] == 0.15].iloc[0]
    e2_adv_base = e2_adv[e2_adv["colluding_frac"] == 0.0].iloc[0]
    e4a_point = e4a.iloc[-1]
    e4b_random = e4b[(e4b["rep_decay"] == 0.01) & (e4b["attacker_model"] == "random")].iloc[0]
    e4b_biased = e4b[(e4b["rep_decay"] == 0.01) & (e4b["attacker_model"] == "bias_0.15")].iloc[0]
    e4d_point = e4d.iloc[0]
    summary = f"""\
### Evaluation snapshot (representative points)

- **E1:** At $p=0.80$ (per-juror), $N={params_e1.n_jurors}$, $S/B=0.25$, challenger EV on a debunking challenge is **{e1_point["ev_false_mean"] / params_e1.bounty:.3f} $\\pm$ {e1_point["ev_false_ci95"] / params_e1.bounty:.3f}\\times bounty** (95% CI, $N={int(e1_point["n_seeds"])}$ seeds) after tax and DDR fees, and false-claim survival (one window, $p_\\mathrm{{detect}}={params_e1.p_detect:.2f}$) is **{e1_point["false_survival_mean"]:.3f} $\\pm$ {e1_point["false_survival_ci95"]:.3f}**.
- **E1 sensitivity:** Holding $p=0.80$ and $N={params_e1_sensitivity.n_jurors}$ fixed, increasing $p_\\mathrm{{detect}}$ from **{e1_sensitivity_010["p_detect"]:.2f}** to **{e1_sensitivity_050["p_detect"]:.2f}** lowers single-window false-claim survival from **{e1_sensitivity_010["false_survival"]:.2f}** to **{e1_sensitivity_050["false_survival"]:.2f}** and lowers the deterrence threshold from **{e1_sensitivity_010["bond_threshold_multiplier"]:.2f}\\times V** to **{e1_sensitivity_050["bond_threshold_multiplier"]:.2f}\\times V**.
- **E2:** At initial competence 0.70 and $K=1.25$, mean relevance error is **{e2_point["mean_abs_error_mean"]:.3f} $\\pm$ {e2_point["mean_abs_error_ci95"]:.3f}** (95% CI, $N={int(e2_point["n_seeds"])}$ seeds), cancelled-round share is **{e2_point["cancelled_round_share_mean"]:.3f} $\\pm$ {e2_point["cancelled_round_share_ci95"]:.3f}**, and final competent stake share is **{e2_point["final_competent_stake_share_mean"]:.2f} $\\pm$ {e2_point["final_competent_stake_share_ci95"]:.2f}**.
- **E3:** Closed-form scenario analysis only. At non-falsifiable share 0.25, bad-item retention is **{e3_point["baseline_bad_item_retention"]:.2f}** under an illustrative forced-binary assumption of $p=0.55$ versus **{e3_point["defended_bad_item_retention"]:.2f}** when a dedicated `NonFalsifiable` challenge reason raises the assumed per-juror accuracy to $p=0.85$.
- **E1-Adv:** A well-funded adversary submitting {int(e1_adv_point["n_attacks"])} false claims at $p=0.80$ and representative $p_\\mathrm{{detect}}={params_e1.p_detect:.2f}$ achieves survival rate **{e1_adv_point["survival_rate_mean"]:.2f} $\\pm$ {e1_adv_point["survival_rate_ci95"]:.2f}** (95% CI, $N={int(e1_adv_point["n_seeds"])}$ seeds) with cumulative balance **{e1_adv_point["adversary_balance_mean"]:.0f} $\\pm$ {e1_adv_point["adversary_balance_ci95"]:.0f}**.
- **E2-Adv:** A 15% colluding bloc shifts mean relevance error from **{e2_adv_base["mean_abs_error_mean"]:.3f}** to **{e2_adv_point["mean_abs_error_mean"]:.3f} $\\pm$ {e2_adv_point["mean_abs_error_ci95"]:.3f}** and ends with **{e2_adv_point["final_colluder_stake_share_mean"]:.3f} $\\pm$ {e2_adv_point["final_colluder_stake_share_ci95"]:.3f}** stake share.
- **E4a:** By round {int(e4a_point["round"])}, median honest-author reputation reaches **{e4a_point["honest_median_rep_mean"]:.2f} $\\pm$ {e4a_point["honest_median_rep_ci95"]:.2f}** (95% CI, $N={int(e4a_point["n_seeds"])}$ seeds) while median dishonest-author reputation remains at **{e4a_point["dishonest_median_rep_mean"]:.2f} $\\pm$ {e4a_point["dishonest_median_rep_ci95"]:.2f}**.
- **E4b:** In a counterfactual reputation-weighted committee with decay $\\delta=0.01$, a random high-reputation attacker stays above median weight for **{e4b_random["above_median_rounds_mean"]:.0f} $\\pm$ {e4b_random["above_median_rounds_ci95"]:.0f}** rounds, while a $+0.15$ strategic-bias attacker lasts **{e4b_biased["above_median_rounds_mean"]:.0f} $\\pm$ {e4b_biased["above_median_rounds_ci95"]:.0f}** rounds and shifts the final signal upward by **{e4b_biased["mean_signal_shift_mean"]:.3f} $\\pm$ {e4b_biased["mean_signal_shift_ci95"]:.3f}**.
- **E4d:** After building reputation in Pool L, an unscoped attacker enters Pool H with **{e4d_point["imported_rep_at_entry_mean"]:.2f} $\\pm$ {e4d_point["imported_rep_at_entry_ci95"]:.2f}** imported reputation units (95% CI, $N={int(e4d_point["n_seeds"])}$ seeds); over the first 10 attack rounds, mean attacker share of Pool H author reputation is **{e4d_point["mean_attacker_rep_share_unscoped_first10"]:.3f} $\\pm$ {e4d_point["mean_attacker_rep_share_unscoped_first10_ci95"]:.3f}** unscoped versus **{e4d_point["mean_attacker_rep_share_scoped_first10"]:.3f} $\\pm$ {e4d_point["mean_attacker_rep_share_scoped_first10_ci95"]:.3f}** when reputation is pool-scoped, and the imported advantage decays to within {E4dParams().exhaustion_epsilon:.2f} reputation units after **{e4d_point["advantage_exhaustion_round_mean"]:.1f} $\\pm$ {e4d_point["advantage_exhaustion_round_ci95"]:.1f}** attack rounds.
"""
    (OUT_DIR / "eval_summary.md").write_text(summary, encoding="utf-8")


def _compute_reading_time(source_path: Path, has_yaml_front_matter: bool) -> str:
    raw = source_path.read_text(encoding="utf-8")

    body = raw
    if has_yaml_front_matter and body.startswith("---"):
        end = body.index("---", 3)
        body = body[end + 3 :]

    n_figures = len(re.findall(r"\{#fig-", raw))
    n_tables = len(re.findall(r"\{#tbl-", raw))
    n_display_math = len(re.findall(r"\$\$", body)) // 2
    body_no_display = re.sub(r"\$\$[^$]*?\$\$", "", body, flags=re.DOTALL)
    n_inline_math = len(
        re.findall(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", body_no_display)
    )

    prose = body
    prose = re.sub(r"\{\{<.*?>\}\}", "", prose)
    prose = re.sub(r"\$\$[^$]*?\$\$", "", prose, flags=re.DOTALL)
    prose = re.sub(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", "", prose)
    prose = re.sub(r"!\[.*?\]\(.*?\)", "", prose)
    words = len(prose.split())

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
        f"({words:,} words, {n_inline_math} equations, {n_figures} figures, {n_tables} tables)"
    )
    row = " | ".join(f"~{estimates[p]} min" for p in personas)
    col_headers = " | ".join(personas.keys())

    return f"""\
{header}

| | {col_headers} |
|---|---|---|---|
| | {row} |
"""


def write_reading_time() -> None:
    documents = [
        (ROOT / "paper.qmd", OUT_DIR / "reading_time.md", True),
        (ROOT / "projects" / "rpgf" / "design.md", OUT_DIR / "reading_time_rpgf.md", False),
        (ROOT / "projects" / "truth-post" / "blueprint.md", OUT_DIR / "reading_time_blueprint.md", False),
    ]
    for source, output, has_yaml in documents:
        snippet = _compute_reading_time(source, has_yaml)
        output.write_text(snippet, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    save_metadata()
    run_e1(E1Params())
    run_e1_detection_sensitivity(E1SensitivityParams())
    run_e1_adversarial(E1AdvParams())
    run_e2(E2Params())
    run_e2_adversarial(E2AdvParams())
    run_e3(E3Params())
    run_e4a(E4aParams())
    run_e4b(E4bParams())
    run_e4d(E4dParams())
    write_eval_summary()
    write_reading_time()


if __name__ == "__main__":
    main()
