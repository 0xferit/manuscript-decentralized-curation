from __future__ import annotations

import functools
import json
import math
import os
import platform
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


def run_e1(params: E1Params) -> None:
    ps = np.linspace(0.50, 0.99, 50)
    rows: list[dict] = []
    tax = params.bounty * params.challenge_tax_bps / 10_000.0

    for p in ps:
        p_majority = majority_correct_probability(params.n_jurors, float(p))
        for s_over_b in params.stake_ratios:
            b = params.bounty
            s = b * s_over_b
            sunk = tax + params.ddr_fee
            ev_false = p_majority * (b - sunk) + (1 - p_majority) * (-s - sunk)
            ev_true = p_majority * (-s - sunk) + (1 - p_majority) * (b - sunk)
            false_survival = (1 - params.p_detect) + params.p_detect * (1 - p_majority)
            rows.append(
                {
                    "p_juror_correct": float(p),
                    "p_majority_correct": float(p_majority),
                    "stake_over_bounty": float(s_over_b),
                    "ev_false": float(ev_false),
                    "ev_true": float(ev_true),
                    "false_survival": float(false_survival),
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
            sub["ev_false"] / params.bounty,
            label=f"S/B={s_over_b:g}",
        )
    plt.axhline(0.0, color="black", linewidth=0.8)
    plt.xlabel("Per-juror correctness p")
    plt.ylabel("Challenger EV on debunking challenge (normalized by bounty)")
    plt.title(
        f"E1: Debunking-challenge EV vs juror accuracy (N={params.n_jurors}, p_detect={params.p_detect:g})"
    )
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e1_challenger_ev.png", dpi=200)
    plt.close()

    plt.figure(figsize=(7.0, 4.0))
    s_over_b = 0.25
    sub = df[df["stake_over_bounty"] == s_over_b]
    plt.plot(sub["p_juror_correct"], sub["false_survival"])
    plt.xlabel("Per-juror correctness p")
    plt.ylabel("False-claim survival probability")
    plt.title(f"E1: False-claim survival (S/B={s_over_b:g}, N={params.n_jurors})")
    plt.ylim(0.0, 1.0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e1_false_survival.png", dpi=200)
    plt.close()


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
    draft_alpha: float = 0.25
    rep_decay: float = 0.01
    noise_sigma: float = 0.08
    coherence_cap_share: float = 0.10
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
    draft_alpha: float,
    rep_decay: float,
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
    rep = np.zeros(n_curators, dtype=float)
    abs_errors: list[float] = []
    cancelled_rounds = 0
    selection_counts = np.zeros(n_curators, dtype=int)

    for _ in range(rounds):
        draft_scores = stakes + draft_alpha * rep
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
            rep *= 1.0 - rep_decay
            continue

        mu = float((weights * votes).sum() / weight_sum)
        sigma = float(np.sqrt(((weights * (votes - mu) ** 2).sum() / weight_sum)))

        if sigma < flat_round_stddev_min:
            cancelled_rounds += 1
            rep *= 1.0 - rep_decay
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

        rep[coherent_idx] += 1.0
        rep *= 1.0 - rep_decay
        abs_errors.append(abs(mu - r_true))

    return {
        "mean_abs_error": float(np.mean(abs_errors)) if abs_errors else 0.0,
        "cancelled_round_share": cancelled_rounds / rounds,
        "selection_counts": selection_counts,
        "stakes": stakes,
        "rep": rep,
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
        draft_alpha=params.draft_alpha,
        rep_decay=params.rep_decay,
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
                    "mean_abs_error_ci95": _ci95(errors),
                    "cancelled_round_share_mean": float(cancelled.mean()),
                    "cancelled_round_share_ci95": _ci95(cancelled),
                    "final_competent_stake_share_mean": float(stakes.mean()),
                    "final_competent_stake_share_ci95": _ci95(stakes),
                    "competent_draft_share_mean": float(draft.mean()),
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
    draft_alpha: float = 0.25
    rep_decay: float = 0.01
    noise_sigma: float = 0.08
    coherence_cap_share: float = 0.10
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
        draft_alpha=params.draft_alpha,
        rep_decay=params.rep_decay,
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
    p_nonfalsifiable_binary_juror_correct: float = 0.55
    p_nonfalsifiable_reason_juror_correct: float = 0.85
    nonfalsifiable_fracs: tuple[float, ...] = (0.0, 0.10, 0.25, 0.50)


def run_e3(params: E3Params) -> None:
    p_major_false = majority_correct_probability(
        params.n_jurors, params.p_false_claim_juror_correct
    )
    p_major_nf_baseline = majority_correct_probability(
        params.n_jurors, params.p_nonfalsifiable_binary_juror_correct
    )
    p_major_nf_defended = majority_correct_probability(
        params.n_jurors, params.p_nonfalsifiable_reason_juror_correct
    )

    rows: list[dict] = []
    for frac in params.nonfalsifiable_fracs:
        baseline_retention = (1 - frac) * (1 - p_major_false) + frac * (
            1 - p_major_nf_baseline
        )
        defended_retention = (1 - frac) * (1 - p_major_false) + frac * (
            1 - p_major_nf_defended
        )
        rows.append(
            {
                "nonfalsifiable_frac": float(frac),
                "baseline_bad_item_retention": float(baseline_retention),
                "defended_bad_item_retention": float(defended_retention),
                "p_major_nf_baseline": float(p_major_nf_baseline),
                "p_major_nf_defended": float(p_major_nf_defended),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e3_results.csv", index=False)

    plt.figure(figsize=(7.0, 4.0))
    plt.plot(
        df["nonfalsifiable_frac"],
        df["baseline_bad_item_retention"],
        marker="o",
        label="baseline (forced binary adjudication)",
    )
    plt.plot(
        df["nonfalsifiable_frac"],
        df["defended_bad_item_retention"],
        marker="o",
        label="defended (NonFalsifiable challenge reason)",
    )
    plt.xlabel("Fraction of non-falsifiable bad items")
    plt.ylabel("Bad-item retention after challenge")
    plt.title("E3: Non-falsifiable challenges reduce bad-item retention")
    plt.legend(frameon=False)
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
    honest_frac: float = 0.6
    honest_challenge_failed_prob: float = 0.85
    dishonest_challenge_failed_prob: float = 0.20
    rep_reward: float = 1.0
    bust_slash_rate: float = 0.50
    rep_decay: float = 0.01


def run_e4a(params: E4aParams) -> None:
    n_honest = int(round(params.n_authors * params.honest_frac))
    author_type = np.array([0] * n_honest + [1] * (params.n_authors - n_honest), dtype=int)
    honest_mask = author_type == 0
    dishonest_mask = author_type == 1

    rep = np.zeros(params.n_authors, dtype=float)
    rows: list[dict] = []

    for round_idx in range(1, params.rounds + 1):
        honest_success = np.full(honest_mask.sum(), params.honest_challenge_failed_prob)
        dishonest_success = np.full(
            dishonest_mask.sum(), params.dishonest_challenge_failed_prob
        )
        probs = np.concatenate([honest_success, dishonest_success])
        outcomes = np.random.default_rng(round_idx).random(params.n_authors) < probs

        rep[outcomes] += params.rep_reward
        rep[~outcomes] *= 1.0 - params.bust_slash_rate
        rep *= 1.0 - params.rep_decay

        rows.append(
            {
                "round": round_idx,
                "honest_median_rep": float(np.median(rep[honest_mask])),
                "dishonest_median_rep": float(np.median(rep[dishonest_mask])),
                "honest_mean_rep": float(rep[honest_mask].mean()),
                "dishonest_mean_rep": float(rep[dishonest_mask].mean()),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e4a_author_reputation.csv", index=False)

    plt.figure(figsize=(7.0, 4.0))
    plt.plot(df["round"], df["honest_median_rep"], label="honest authors")
    plt.plot(df["round"], df["dishonest_median_rep"], label="dishonest authors")
    plt.xlabel("Publication rounds")
    plt.ylabel("Median author reputation")
    plt.title("E4a: Author reputation separates honest and dishonest publishers")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e4a_author_reputation.png", dpi=200)
    plt.close()


@dataclass(frozen=True)
class E4bParams:
    n_curators: int = 200
    committee_size: int = 15
    rounds: int = 300
    slash_rate: float = 0.03
    noise_sigma: float = 0.08
    K: float = 1.25
    competent_frac: float = 0.5
    cash_poor_frac: float = 0.10
    coherence_cap_share: float = 0.10
    flat_round_stddev_min: float = 0.02
    alphas: tuple[float, ...] = (0.0, 0.10, 0.25, 0.50, 1.0)
    decay_rates: tuple[float, ...] = (0.0, 0.01, 0.05)
    n_seeds: int = 100


def _e4b_single_run(params: E4bParams, alpha: float, decay_rate: float, seed_idx: int) -> dict:
    rng = np.random.default_rng(int(100_000 * alpha + 10_000 * decay_rate + seed_idx))
    n_comp = int(round(params.n_curators * params.competent_frac))
    types = np.array([0] * n_comp + [1] * (params.n_curators - n_comp), dtype=int)
    rng.shuffle(types)

    competent_indices = np.where(types == 0)[0]
    n_cash_poor = max(1, int(round(len(competent_indices) * params.cash_poor_frac)))
    cash_poor_mask = np.zeros(params.n_curators, dtype=bool)
    cash_poor_mask[competent_indices[:n_cash_poor]] = True

    stakes = np.ones(params.n_curators, dtype=float)
    stakes[cash_poor_mask] = 0.1

    rep = np.zeros(params.n_curators, dtype=float)
    abs_errors: list[float] = []
    time_to_entry = params.rounds

    for round_idx in range(params.rounds):
        draft_scores = stakes + alpha * rep
        drafted = _weighted_sample_without_replacement(
            rng, draft_scores, params.committee_size
        )

        r_true = float(rng.uniform(0.0, 1.0))
        votes = np.empty(len(drafted), dtype=float)
        drafted_types = types[drafted]
        comp_mask = drafted_types == 0
        noisy_mask = drafted_types == 1

        if comp_mask.any():
            votes[comp_mask] = _truncate_0_1(
                rng.normal(loc=r_true, scale=params.noise_sigma, size=comp_mask.sum())
            )
        if noisy_mask.any():
            votes[noisy_mask] = rng.uniform(0.0, 1.0, size=noisy_mask.sum())

        weights = _committee_weights(stakes[drafted], params.coherence_cap_share)
        weight_sum = float(weights.sum())
        if weight_sum > 0:
            mu = float((weights * votes).sum() / weight_sum)
            sigma = float(np.sqrt(((weights * (votes - mu) ** 2).sum() / weight_sum)))
            if sigma >= params.flat_round_stddev_min:
                coherent = np.abs(votes - mu) <= (params.K * sigma)
                incoherent = ~coherent
                incoherent_idx = drafted[incoherent]
                coherent_idx = drafted[coherent]

                slashed = params.slash_rate * stakes[incoherent_idx]
                total_slashed = float(slashed.sum())
                stakes[incoherent_idx] -= slashed
                if total_slashed > 0 and len(coherent_idx) > 0:
                    coherent_stakes = stakes[coherent_idx]
                    coherent_total = float(coherent_stakes.sum())
                    if coherent_total > 0:
                        stakes[coherent_idx] += total_slashed * (
                            coherent_stakes / coherent_total
                        )
                rep[coherent_idx] += 1.0
                abs_errors.append(abs(mu - r_true))

        rep *= 1.0 - decay_rate

        if time_to_entry == params.rounds:
            current_scores = stakes + alpha * rep
            if float(current_scores[cash_poor_mask].max()) >= float(np.median(current_scores)):
                time_to_entry = round_idx + 1

    return {
        "time_to_entry": time_to_entry,
        "mean_abs_error": float(np.mean(abs_errors)) if abs_errors else 0.0,
    }


def run_e4b(params: E4bParams) -> None:
    rows: list[dict] = []
    for alpha in params.alphas:
        for decay_rate in params.decay_rates:
            with ProcessPoolExecutor() as executor:
                seed_results = list(
                    executor.map(
                        functools.partial(_e4b_single_run, params, alpha, decay_rate),
                        range(params.n_seeds),
                    )
                )

            entries = np.array([r["time_to_entry"] for r in seed_results])
            errors = np.array([r["mean_abs_error"] for r in seed_results])
            rows.append(
                {
                    "alpha": alpha,
                    "decay_rate": decay_rate,
                    "time_to_entry_mean": float(entries.mean()),
                    "time_to_entry_ci95": _ci95(entries),
                    "mean_abs_error_mean": float(errors.mean()),
                    "mean_abs_error_ci95": _ci95(errors),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e4b_curator_entry.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    pivot = df.pivot(index="decay_rate", columns="alpha", values="time_to_entry_mean")
    im = ax.imshow(pivot.values, aspect="auto", cmap="viridis_r", origin="lower")
    ax.set_xticks(range(len(params.alphas)))
    ax.set_xticklabels([f"{a:g}" for a in params.alphas])
    ax.set_yticks(range(len(params.decay_rates)))
    ax.set_yticklabels([f"{d:g}" for d in params.decay_rates])
    ax.set_xlabel("Curator reputation draft boost alpha")
    ax.set_ylabel("Curator reputation decay")
    ax.set_title(
        f"E4b: Rounds until cash-poor expert reaches median draft score (N={params.n_seeds} seeds)"
    )
    for i in range(len(params.decay_rates)):
        for j in range(len(params.alphas)):
            val = pivot.values[i, j]
            ax.text(
                j,
                i,
                f"{val:.0f}",
                ha="center",
                va="center",
                fontsize=9,
                color="white" if val > pivot.values.mean() else "black",
            )
    fig.colorbar(im, ax=ax, label="Rounds")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e4b_curator_entry_heatmap.png", dpi=200)
    plt.close()

    plt.figure(figsize=(7.0, 4.0))
    for decay_rate in params.decay_rates:
        sub = df[df["decay_rate"] == decay_rate].sort_values("alpha")
        plt.errorbar(
            sub["alpha"],
            sub["mean_abs_error_mean"],
            yerr=sub["mean_abs_error_ci95"],
            marker="o",
            capsize=3,
            label=f"delta={decay_rate:g}",
        )
    plt.xlabel("Curator reputation draft boost alpha")
    plt.ylabel("Mean |mu - r|")
    plt.title(f"E4b: Relevance error under draft-only curator reputation (N={params.n_seeds} seeds)")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "e4b_curator_error.png", dpi=200)
    plt.close()


@dataclass(frozen=True)
class E4cParams:
    n_curators: int = 200
    committee_size: int = 15
    rounds_buildup: int = 100
    rounds_attack: int = 100
    slash_rate: float = 0.03
    noise_sigma: float = 0.08
    K: float = 1.25
    competent_frac: float = 0.5
    n_sybils: int = 20
    coherence_cap_share: float = 0.10
    flat_round_stddev_min: float = 0.02
    alphas: tuple[float, ...] = (0.0, 0.25, 0.5, 1.0)
    decay_rate: float = 0.01
    n_seeds: int = 100


def _e4c_single_run(params: E4cParams, alpha: float, seed_idx: int) -> dict:
    rng = np.random.default_rng(int(100_000 * alpha + seed_idx + 90_000))
    n_comp = int(round(params.n_curators * params.competent_frac))
    n_sybils = params.n_sybils
    n_noisy = max(0, params.n_curators - n_comp - n_sybils)
    n_comp = params.n_curators - n_noisy - n_sybils
    types = np.array([0] * n_comp + [1] * n_noisy + [2] * n_sybils, dtype=int)
    rng.shuffle(types)

    stakes = np.ones(params.n_curators, dtype=float)
    rep = np.zeros(params.n_curators, dtype=float)
    sybil_mask = types == 2
    attack_errors: list[float] = []
    attack_draft_slots = 0

    total_rounds = params.rounds_buildup + params.rounds_attack
    for round_idx in range(total_rounds):
        draft_scores = stakes + alpha * rep
        drafted = _weighted_sample_without_replacement(
            rng, draft_scores, params.committee_size
        )

        if round_idx >= params.rounds_buildup:
            attack_draft_slots += int((types[drafted] == 2).sum())

        r_true = float(rng.uniform(0.0, 1.0))
        votes = np.empty(len(drafted), dtype=float)
        drafted_types = types[drafted]

        comp_mask = drafted_types == 0
        noisy_mask = drafted_types == 1
        sybil_committee_mask = drafted_types == 2

        if comp_mask.any():
            votes[comp_mask] = _truncate_0_1(
                rng.normal(loc=r_true, scale=params.noise_sigma, size=comp_mask.sum())
            )
        if noisy_mask.any():
            votes[noisy_mask] = rng.uniform(0.0, 1.0, size=noisy_mask.sum())
        if sybil_committee_mask.any():
            if round_idx < params.rounds_buildup:
                votes[sybil_committee_mask] = _truncate_0_1(
                    rng.normal(
                        loc=r_true,
                        scale=params.noise_sigma,
                        size=sybil_committee_mask.sum(),
                    )
                )
            else:
                biased_target = min(1.0, r_true + 0.30)
                votes[sybil_committee_mask] = _truncate_0_1(
                    rng.normal(
                        loc=biased_target,
                        scale=params.noise_sigma * 0.5,
                        size=sybil_committee_mask.sum(),
                    )
                )

        weights = _committee_weights(stakes[drafted], params.coherence_cap_share)
        weight_sum = float(weights.sum())
        if weight_sum > 0:
            mu = float((weights * votes).sum() / weight_sum)
            sigma = float(np.sqrt(((weights * (votes - mu) ** 2).sum() / weight_sum)))
            if sigma >= params.flat_round_stddev_min:
                coherent = np.abs(votes - mu) <= (params.K * sigma)
                incoherent = ~coherent
                incoherent_idx = drafted[incoherent]
                coherent_idx = drafted[coherent]
                slashed = params.slash_rate * stakes[incoherent_idx]
                total_slashed = float(slashed.sum())
                stakes[incoherent_idx] -= slashed
                if total_slashed > 0 and len(coherent_idx) > 0:
                    coherent_stakes = stakes[coherent_idx]
                    coherent_total = float(coherent_stakes.sum())
                    if coherent_total > 0:
                        stakes[coherent_idx] += total_slashed * (
                            coherent_stakes / coherent_total
                        )
                rep[coherent_idx] += 1.0
                if round_idx >= params.rounds_buildup:
                    attack_errors.append(abs(mu - r_true))
        rep *= 1.0 - params.decay_rate

    total_attack_slots = params.rounds_attack * params.committee_size
    return {
        "mean_abs_error_attack": float(np.mean(attack_errors)) if attack_errors else 0.0,
        "final_sybil_stake_share": float(stakes[sybil_mask].sum() / stakes.sum()),
        "attack_draft_share": attack_draft_slots / total_attack_slots,
    }


def run_e4c(params: E4cParams) -> None:
    rows: list[dict] = []
    for alpha in params.alphas:
        with ProcessPoolExecutor() as executor:
            seed_results = list(
                executor.map(
                    functools.partial(_e4c_single_run, params, alpha),
                    range(params.n_seeds),
                )
            )

        errors = np.array([r["mean_abs_error_attack"] for r in seed_results])
        stake_shares = np.array([r["final_sybil_stake_share"] for r in seed_results])
        draft_shares = np.array([r["attack_draft_share"] for r in seed_results])
        rows.append(
            {
                "alpha": alpha,
                "decay_rate": params.decay_rate,
                "n_sybils": params.n_sybils,
                "mean_abs_error_attack_mean": float(errors.mean()),
                "mean_abs_error_attack_ci95": _ci95(errors),
                "final_sybil_stake_share_mean": float(stake_shares.mean()),
                "final_sybil_stake_share_ci95": _ci95(stake_shares),
                "attack_draft_share_mean": float(draft_shares.mean()),
                "attack_draft_share_ci95": _ci95(draft_shares),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "e4c_curator_sybil.csv", index=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.5))
    labels = [f"alpha={a:g}" for a in params.alphas]

    ax1.bar(
        labels,
        df["mean_abs_error_attack_mean"],
        yerr=df["mean_abs_error_attack_ci95"],
        color="#4C72B0",
        capsize=4,
    )
    ax1.set_ylabel("Mean |mu - r| during attack phase")
    ax1.set_title(
        f"E4c: Sybil attack error under draft-only curator reputation (N={params.n_seeds} seeds)"
    )

    ax2.bar(
        labels,
        df["attack_draft_share_mean"],
        yerr=df["attack_draft_share_ci95"],
        color="#C44E52",
        capsize=4,
    )
    ax2.axhline(
        params.n_sybils / params.n_curators,
        color="gray",
        linestyle="--",
        linewidth=0.8,
        label="Population share",
    )
    ax2.set_ylabel("Sybil share of drafted attack seats")
    ax2.set_title(
        f"E4c: Sybil draft amplification after honest buildup (delta={params.decay_rate:g})"
    )
    ax2.legend(frameon=False, fontsize=9)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "e4c_curator_sybil.png", dpi=200)
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
    e4a = pd.read_csv(OUT_DIR / "e4a_author_reputation.csv")
    e4b = pd.read_csv(OUT_DIR / "e4b_curator_entry.csv")
    e4c = pd.read_csv(OUT_DIR / "e4c_curator_sybil.csv")

    e1_sub = e1[e1["stake_over_bounty"] == 0.25].copy()
    e1_sub["p_delta"] = (e1_sub["p_juror_correct"] - 0.8).abs()
    e1_point = e1_sub.sort_values("p_delta").iloc[0]
    e2_point = e2[(e2["K"] == 1.25) & (e2["competent_frac"] == 0.70)].iloc[0]
    e3_point = e3[e3["nonfalsifiable_frac"] == 0.25].iloc[0]
    e1_adv_point = e1_adv[e1_adv["p_juror_correct"] == 0.80].iloc[0]
    e2_adv_point = e2_adv[e2_adv["colluding_frac"] == 0.15].iloc[0]
    e2_adv_base = e2_adv[e2_adv["colluding_frac"] == 0.0].iloc[0]
    e4a_point = e4a.iloc[-1]
    e4b_point = e4b[(e4b["alpha"] == 0.5) & (e4b["decay_rate"] == 0.01)].iloc[0]
    e4c_point = e4c[e4c["alpha"] == 0.5].iloc[0]

    summary = f"""\
### Evaluation snapshot (representative points)

- **E1:** At $p=0.80$ (per-juror), $N={params_e1.n_jurors}$, $S/B=0.25$, challenger EV on a debunking challenge is **{e1_point["ev_false"] / params_e1.bounty:.2f}\\times bounty** after tax and DDR fees, and false-claim survival (one window, $p_\\mathrm{{detect}}={params_e1.p_detect:.2f}$) is **{e1_point["false_survival"]:.2f}**.
- **E2:** At initial competence 0.70 and $K=1.25$, mean relevance error is **{e2_point["mean_abs_error_mean"]:.3f} $\\pm$ {e2_point["mean_abs_error_ci95"]:.3f}** (95% CI, $N={int(e2_point["n_seeds"])}$ seeds), cancelled-round share is **{e2_point["cancelled_round_share_mean"]:.3f}**, and final competent stake share is **{e2_point["final_competent_stake_share_mean"]:.2f} $\\pm$ {e2_point["final_competent_stake_share_ci95"]:.2f}**.
- **E3:** At non-falsifiable share 0.25, bad-item retention is **{e3_point["baseline_bad_item_retention"]:.2f}** under forced binary adjudication versus **{e3_point["defended_bad_item_retention"]:.2f}** with a dedicated `NonFalsifiable` challenge reason.
- **E1-Adv:** A well-funded adversary submitting {int(e1_adv_point["n_attacks"])} false claims at $p=0.80$ achieves survival rate **{e1_adv_point["survival_rate_mean"]:.2f} $\\pm$ {e1_adv_point["survival_rate_ci95"]:.2f}** (95% CI, $N={int(e1_adv_point["n_seeds"])}$ seeds) with cumulative balance **{e1_adv_point["adversary_balance_mean"]:.0f} $\\pm$ {e1_adv_point["adversary_balance_ci95"]:.0f}**.
- **E2-Adv:** A 15% colluding bloc shifts mean relevance error from **{e2_adv_base["mean_abs_error_mean"]:.3f}** to **{e2_adv_point["mean_abs_error_mean"]:.3f} $\\pm$ {e2_adv_point["mean_abs_error_ci95"]:.3f}** and ends with **{e2_adv_point["final_colluder_stake_share_mean"]:.3f} $\\pm$ {e2_adv_point["final_colluder_stake_share_ci95"]:.3f}** stake share.
- **E4a:** By round {int(e4a_point["round"])}, median honest-author reputation reaches **{e4a_point["honest_median_rep"]:.2f}** while median dishonest-author reputation remains at **{e4a_point["dishonest_median_rep"]:.2f}**.
- **E4b:** At $\\alpha=0.5$, $\\delta=0.01$, cash-poor competent curators reach median draft score in **{e4b_point["time_to_entry_mean"]:.0f} $\\pm$ {e4b_point["time_to_entry_ci95"]:.0f}** rounds, with mean relevance error **{e4b_point["mean_abs_error_mean"]:.3f} $\\pm$ {e4b_point["mean_abs_error_ci95"]:.3f}**.
- **E4c:** With draft-only curator reputation at $\\alpha=0.5$, Sybils occupy **{e4c_point["attack_draft_share_mean"]:.3f} $\\pm$ {e4c_point["attack_draft_share_ci95"]:.3f}** of attack-phase committee seats, versus a population share of **{E4cParams().n_sybils / E4cParams().n_curators:.2f}**.
"""
    (OUT_DIR / "eval_summary.md").write_text(summary, encoding="utf-8")


def write_reading_time() -> None:
    import re

    paper = ROOT / "paper.qmd"
    raw = paper.read_text(encoding="utf-8")

    body = raw
    if body.startswith("---"):
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
