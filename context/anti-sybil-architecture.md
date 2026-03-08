# Anti-Sybil Architecture Proposal

## Overview

**Author:** @Ferit

This proposal outlines a **Two-Phase Anti-Sybil Architecture** designed to protect quadratic funding and curation systems from Sybil attacks (fake identities).

## Progressive Decentralization Strategy

The judgment layer evolves through three stages, following a legal system analogy:

| Stage  | Role      | Actor                        | Speed  | Cost   |
| ------ | --------- | ---------------------------- | ------ | ------ |
| **v1** | **Judge** | Octant Team                  | Fast   | Low    |
| **v2** | **Panel** | Elected Committee            | Medium | Medium |
| **v3** | **Jury**  | Token Holders (Kleros-style) | Slow   | High   |

## Product Scope

### Participants

| Role             | Analogy    | Action                                      | Incentive              |
| ---------------- | ---------- | ------------------------------------------- | ---------------------- |
| **Investigator** | Detective  | Identifies suspects using on-chain analysis | Bounty                 |
| **Challenger**   | Prosecutor | Stakes capital to formally accuse a suspect | Reward (Penalty Share) |
| **Defendant**    | Accused    | Submits defense/counter-evidence            | Avoid Slashing         |
| **Arbiter**      | Judge/Jury | Reviews evidence and renders verdict        | Arbitration Fee        |

_Note: Investigator and Challenger may be the same entity._

## Core User Flows

### Flow 1: Contributor Registration & Staking

1. Contributor stakes via RegenStaker (one account per user).
2. Contributor becomes eligible for full QF matching weight.
3. Any staked contributor can be challenged at any time (no deadline).
4. If challenged → case escalates to judgment layer.

### Flow 2: Investigation → Prosecution Pipeline

1. Investigator identifies suspect based on signals (low Unique Humanity Score, suspicious graph clustering).
2. Investigator prepares evidence dossier.
3. Challenger reviews evidence, decides whether to stake and file charges.
4. Filing charges triggers formal dispute process.

### Flow 3: Trial & Judgment

**v1 (Judge):**

1. Challenger deposits stake + evidence.
2. Defendant can submit defense.
3. Judge (Octant team) reviews within 48-72 hours.
4. Verdict: **Acquitted** or **Guilty**.
5. Losing party forfeits stake.

**v2 (Panel):**

1. Same filing flow.
2. Panel of 5 judges votes.
3. 3-of-5 majority required within 5 days.
4. Losing party forfeits stake + panel fee.

**v3 (Jury):**

1. Same filing flow.
2. Jury pool drawn randomly, weighted by stake.
3. Commit-reveal voting period.
4. Majority verdict.
5. Losing party forfeits stake + juror fees.

### Flow 4: Appeal (v3 only)

1. Losing party can appeal with 2x stake.
2. Larger jury re-tries the case.
3. Exponential cost increase per appeal round.
4. Final appeal: full token holder vote.

## Detection Signals (Investigation Evidence)

Detection is **probabilistic**. It identifies suspects, not convicts. The judgment layer exists because investigative evidence has false positives.

| Signal Type           | Description                            | Strength |
| --------------------- | -------------------------------------- | -------- |
| **Graph Analysis**    | Clustering of funding flows            | High     |
| **On-Chain Behavior** | Transaction timing, gas usage patterns | Medium   |
| **Identity Scores**   | Gitcoin Passport, WorldID, etc.        | Medium   |

## Parameter Configuration

### The Crypto-Economic Foundation

This system works only if:
$$ \text{Cost of attack} > \text{Expected gain from attack} $$

Get this wrong, and attackers farm the matching pool. Get it right, and the system becomes self-enforcing.

### Variables

| Symbol | Definition                        |
| ------ | --------------------------------- |
| $C$    | Total capital of attacker         |
| $n$    | Number of Sybil accounts          |
| $W(n)$ | Total matching weight gained      |
| $X$    | Penalty multiplier (e.g., 2x, 5x) |
| $F$    | Fixed cost of prosecution         |
| $P$    | Probability of getting caught     |

### Attacker Economics

An attacker with capital $C$ splits across $n$ accounts ($C/n$ each).
Quadratic funding weight scales with $\sqrt{\text{contribution}}$.
Total Weight: $W(n) = n \times \sqrt{C/n} = \sqrt{n \cdot C}$

**Insight:** Attacker gain scales superlinearly with $n$.

**Penalty:**
If caught, attacker loses: $\text{penalty} = C \cdot X$

**Expected Value:**
$$ \mathbb{E}[\text{attacker}] = (1 - P) \cdot G(n) - P \cdot C \cdot X $$

Attack is deterred when $\mathbb{E} < 0$:
$$ X > \frac{1 - P}{P} \cdot \frac{G(n)}{C} $$

### Prosecutor Economics

Challenger files one dispute covering $n$ accounts.
**Cost:** $F$
**Reward:** $C \cdot X$ (if successful)

**Expected Value:**
$$ \mathbb{E}[\text{prosecutor}] = P\_{\text{win}} \cdot C \cdot X - F $$

Prosecution is viable when:
$$ X > \frac{F}{P\_{\text{win}} \cdot C} $$

### Combined Constraints on X

**Constraint 1 (Deter attackers):**
$$ X > \frac{1 - P}{P} \cdot \frac{G(n)}{C} $$

**Constraint 2 (Enable prosecutors):**
$$ X > \frac{F}{P\_{\text{win}} \cdot C} $$

**Optimal X:**
$$ X*{\text{min}} = \max\left( \frac{1 - P}{P} \cdot \frac{G(n)}{C}, \frac{F}{P*{\text{win}} \cdot C} \right) $$

**Constraint 3: Accessibility**
$X$ cannot be so high that honest users face unacceptable risk:
$$ X < X*{\text{max}} $$
Where $X*{\text{max}}$ is the maximum stake ratio honest users will tolerate.

**Feasibility condition:**
$$ X*{\text{min}} < X*{\text{max}} $$

If this fails, adjust other parameters ($F$, $P$) until feasible region exists.

## Simulation

**Target:** $X = 20\%$

**Assumed values:**
| Variable | Value |
|---|---|
| Capital ($C$) | $10,000 |
| Sybils ($n$) | 50 |
| Prosecution Cost ($F$) | $100 |
| Win Prob ($P\_{\text{win}}$) | 90% |
| Detection Prob ($P$) | 85% |
| Gain Ratio ($G(n)/C$) | 1.0 |

**Step 1: Prosecutor viability (Constraint 2)**
$$ X > \frac{100}{0.9 \times 10000} \approx 1.1\% $$
At $X = 20\%$, prosecutor profit:
$$ \mathbb{E}[\text{prosecutor}] = 0.9 \times 10000 \times 0.2 - 100 = \$1700 $$
Prosecution is highly viable. ✅

**Step 2: Attacker deterrence (Constraint 1)**
Rearranging for required $P$ given $X = 20\%$:
$$ P > \frac{G(n)/C}{0.2 + G(n)/C} $$

Scenario analysis for different gain ratios $G(n)/C$:
| Gain Ratio | Required P | Note |
|---|---|---|
| 0.5 | 71% | Easy to deter |
| 1.0 | 83% | Moderate |
| 2.0 | 91% | Hard to deter |

**Step 3: Expected values at $X=20\%$, $P=85\%$, $G(n)/C=1.0$**

**Attacker:**
$$ \mathbb{E}[\text{attacker}] = 0.15 \times 10000 - 0.85 \times 2000 = 1500 - 1700 = -\$200 $$
Attack is unprofitable. ✅

**Prosecutor:**
$$ \mathbb{E}[\text{prosecutor}] = \$1700 $$
Prosecution is profitable. ✅

**Step 4: Sensitivity analysis around $X=20\%$**
| X | Attacker EV | Prosecutor EV | Outcome |
|---|---|---|---|
| 10% | +$650 | +$800 | Attack Profitable (Fail) |
| 20% | -$200 | +$1700 | Secure |
| 50% | -$2750 | +$4400 | Very Secure (but User Risk High) |

**Conclusion:**
At $X = 20\%$, the system deters attacks when:

- $P \geq 85\%$ and $G(n)/C \leq 1.0$, or
- $P \geq 90\%$ and $G(n)/C \leq 1.5$

**Critical dependency:** $X=20\%$ requires detection probability $P \geq 85\%$ assuming attackers can extract up to 1× their capital from the matching pool.

## Procedural Principle

**Burden of proof lies on challenger.** Ambiguous cases result in acquittal. This protects honest contributors while making challengers responsible for evidence quality.

## Technical Scope

### Contract Architecture: Swappable Arbiter Pattern

The key design principle: **ContributorRegistry delegates judgment to a replaceable arbiter interface (`IArbiter`)**. This allows upgrading from v1 → v2 → v3 without migrating contributor state.

### Integration Points

- **Investigation Services** → produces suspect list
- **ContributorRegistry** → determines eligibility → feeds into Octant Epoch Snapshot
- **QF Allocation Calculator** ← only innocent contributors receive full matching weight

## Security Considerations

### Attack Vectors & Mitigations by Version

| Attack            | v1 (Judge) | v2 (Panel)     | v3 (Jury)                          |
| ----------------- | ---------- | -------------- | ---------------------------------- |
| **Bribery**       | Trust Team | Trust Majority | P+Epsilon Attack (High Cost)       |
| **Censorship**    | Trust Team | Trust Majority | Appeal System                      |
| **Apathy**        | N/A        | N/A            | Inactivity Penalties               |
| **Spam Disputes** | Deposit    | Deposit + Fee  | Deposit + Fee + Exponential Appeal |

### Trust Assumptions by Version

| Version | Liveness      | Integrity               |
| ------- | ------------- | ----------------------- |
| **v1**  | Team          | Team                    |
| **v2**  | Committee     | Majority of Committee   |
| **v3**  | Token Holders | Economic Majority (51%) |

## Open Questions

1.  **L1 vs L2**: Deploy on mainnet or whereever RegenStaker lives?
2.  **Precedent system**: How do v1/v2 verdicts inform v3 jury decisions?

## References

- [Kleros Whitepaper](https://kleros.io/whitepaper.pdf)
- [Token Curated Registry (TCR) — A Game Theoretic Approach](https://arxiv.org/abs/1809.01756)
