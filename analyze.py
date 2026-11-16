"""Reproduce the Cookie Cats retention experiment on all assigned players."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

GROUPS = ("gate_30", "gate_40")
METRICS = ("retention_1", "retention_7")
REQUIRED = ("userid", "version", "sum_gamerounds", *METRICS)


def load_players(path):
    """Reject invalid records rather than silently dropping assigned players."""
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = set(REQUIRED) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    frame = frame.loc[:, list(REQUIRED)].copy()
    if frame.empty or frame.eq("").any().any():
        raise ValueError("The dataset is empty or contains missing values.")
    for column in ("userid", "sum_gamerounds"):
        if not frame[column].str.fullmatch(r"[0-9]+").all():
            raise ValueError(f"{column} must contain non-negative integers.")
        frame[column] = frame[column].astype("int64")
    if frame.userid.duplicated().any():
        raise ValueError("Duplicate player IDs are not allowed.")
    if not frame.version.isin(GROUPS).all():
        raise ValueError("Unexpected experiment group.")
    if set(frame.version) != set(GROUPS):
        raise ValueError("Both experiment groups must contain players.")
    for metric in METRICS:
        values = frame[metric].str.lower()
        if not values.isin(("true", "false")).all():
            raise ValueError(f"{metric} must contain True/False flags.")
        frame[metric] = values.eq("true")
    return frame


def compare(frame, metric, rng, iterations=10_000):
    """Two-sided pooled z-test, unpooled Wald CI, and percentile bootstrap."""
    if iterations < 100:
        raise ValueError("Use at least 100 bootstrap iterations.")
    groups = [frame.loc[frame.version.eq(group), metric] for group in GROUPS]
    n = np.array([len(group) for group in groups])
    successes = np.array([int(group.sum()) for group in groups])
    if (n == 0).any() or (successes < 5).any() or ((n - successes) < 5).any():
        raise ValueError("At least five retained and non-retained players per group required.")
    rates = successes / n
    delta = rates[1] - rates[0]
    pooled = successes.sum() / n.sum()
    null_se = np.sqrt(pooled * (1 - pooled) * (1 / n).sum())
    margin = stats.norm.ppf(0.975) * np.sqrt((rates * (1 - rates) / n).sum())
    # Resampling binary observations is exactly a binomial draw using the
    # empirical rate; no players-by-iterations array is needed.
    samples = (rng.binomial(n[1], rates[1], iterations) / n[1]
               - rng.binomial(n[0], rates[0], iterations) / n[0])
    return {
        "players": dict(zip(GROUPS, n.tolist())),
        "retained": dict(zip(GROUPS, successes.tolist())),
        "rates": dict(zip(GROUPS, rates.tolist())),
        "difference_pp": float(100 * delta),
        "relative_change_pct": float(100 * delta / rates[0]),
        "p_value": float(2 * stats.norm.sf(abs(delta / null_se))),
        "ci_95_pp": (100 * np.array([delta - margin, delta + margin])).tolist(),
        "bootstrap_ci_95_pp": np.quantile(100 * samples, [0.025, 0.975]).tolist(),
        "bootstrap_fraction_gate30_higher": float(np.mean(samples < 0)),
    }, samples


def analyze(frame, iterations=10_000, seed=42):
    rng = np.random.default_rng(seed)
    retention, samples = {}, {}
    for metric in METRICS:
        retention[metric], samples[metric] = compare(frame, metric, rng, iterations)
    max_rounds = int(frame.sum_gamerounds.max())
    sensitivity = {}
    for label, subset in {
        "without_max_rounds": frame.loc[frame.sum_gamerounds.lt(max_rounds)],
        "positive_rounds_only": frame.loc[frame.sum_gamerounds.gt(0)],
    }.items():
        sensitivity[label], _ = compare(subset, "retention_7", rng, iterations)
    engagement = {}
    for group in GROUPS:
        rounds = frame.loc[frame.version.eq(group), "sum_gamerounds"]
        trimmed = rounds.loc[rounds.lt(max_rounds)]
        engagement[group] = {"mean": float(rounds.mean()), "median": float(rounds.median()),
                             "p99": float(rounds.quantile(0.99)),
                             "mean_without_global_max": float(trimmed.mean())}
    counts = [int(frame.version.eq(group).sum()) for group in GROUPS]
    allocation = stats.chisquare(counts)
    results = {
        "config": {"seed": seed, "bootstrap_iterations": iterations,
                   "difference_direction": "gate_40 minus gate_30", "alpha": 0.05,
                   "primary_metric": "retention_7", "analysis_type": "retrospective reproduction"},
        "validation": {"rows": len(frame), "duplicate_ids": 0, "missing_values": 0,
                       "zero_round_players": int(frame.sum_gamerounds.eq(0).sum()),
                       "maximum_rounds": max_rounds,
                       "players_at_maximum": int(frame.sum_gamerounds.eq(max_rounds).sum())},
        "allocation": {"assumed_split": [0.5, 0.5], "counts": dict(zip(GROUPS, counts)),
                       "chi_square": float(allocation.statistic), "p_value": float(allocation.pvalue),
                       "flag_at_0_05": bool(allocation.pvalue < 0.05)},
        "retention": retention, "engagement": engagement, "sensitivity": sensitivity,
    }
    return results, samples


def plot_results(frame, results, samples, output):
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), layout="constrained")
    for ax, metric, label in zip(axes, METRICS, ("Day 1", "Day 7 (primary)")):
        item = results["retention"][metric]
        ax.hist(100 * samples[metric], bins=65, color="#426B93", alpha=0.85)
        ax.axvline(0, color="#9D382C", linestyle="--", label="No difference")
        ax.axvline(item["difference_pp"], color="#142F45", label="Observed difference")
        ax.set(title=label, xlabel="Gate 40 minus gate 30 (percentage points)", ylabel="Resamples")
        ax.legend(fontsize=9)
    fig.suptitle(f"Retention differences across {results['config']['bootstrap_iterations']:,} bootstrap resamples")
    fig.savefig(output / "retention_bootstrap.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
    bins = np.linspace(0, np.log1p(frame.sum_gamerounds.max()), 65)
    for group, color in zip(GROUPS, ("#426B93", "#CB7951")):
        values = frame.loc[frame.version.eq(group), "sum_gamerounds"]
        ax.hist(np.log1p(values), bins=bins, histtype="step", linewidth=1.6, label=group, color=color)
    ax.set(title="Game rounds are highly skewed", xlabel="log(1 + game rounds)", ylabel="Players")
    ax.legend()
    fig.savefig(output / "game_rounds.png", dpi=160)
    plt.close(fig)


def markdown_report(results):
    rows = ["# Cookie Cats analysis results", "",
            "Retrospective reproduction; differences are gate 40 minus gate 30. "
            "Every assigned player is included in the primary analysis.", "",
            "| Metric | Gate 30 | Gate 40 | Difference | 95% normal CI | p-value |",
            "|---|---:|---:|---:|---:|---:|"]
    for metric in METRICS:
        item = results["retention"][metric]
        low, high = item["ci_95_pp"]
        rows.append(f"| {metric} | {item['rates']['gate_30']:.2%} | {item['rates']['gate_40']:.2%} | "
                    f"{item['difference_pp']:+.2f} pp | {low:+.2f} to {high:+.2f} pp | {item['p_value']:.4f} |")
    allocation = results["allocation"]
    rows += ["", f"Allocation check, assuming 50/50: p = {allocation['p_value']:.4f}. "
             "This needs assignment logs to investigate, and does not prove faulty randomization.", "",
             "## Sensitivity checks", ""]
    for label, item in results["sensitivity"].items():
        rows.append(f"- {label}: Day 7 difference {item['difference_pp']:+.2f} pp, p = {item['p_value']:.4f}.")
    primary = results["retention"]["retention_7"]
    if primary["p_value"] < 0.05 and primary["difference_pp"] < 0:
        decision = "Keep the gate at level 30 pending investigation of allocation and revenue trade-offs."
    elif primary["p_value"] < 0.05:
        decision = "Gate 40 has higher Day 7 retention; investigate allocation and revenue before rollout."
    else:
        decision = "The test does not establish a Day 7 retention difference at the 5% level."
    rows += ["", "## Recommendation", "", decision, "", "## Interpretation limits", "",
             "- Day 7 is the decision metric for this reproduction; no historical preregistration is claimed.",
             "- Day 1 is supporting evidence. A non-significant result does not establish equivalence.",
             "- The bootstrap fraction favoring gate 30 is not a probability that it is truly better.",
             "- Positive-round players are a post-assignment subset; that check is descriptive, not a new causal estimate.",
             "- No revenue, assignment logs, gate exposure, or longer-term outcomes are available.",
             "- The large game-round observation is not proven to be an error; exclusion is only a sensitivity check.", ""]
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=Path("data/cookie_cats.csv"))
    parser.add_argument("--iterations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("reports"))
    args = parser.parse_args()
    try:
        frame = load_players(args.csv_path)
        results, samples = analyze(frame, args.iterations, args.seed)
    except (ValueError, OSError, OverflowError) as error:
        parser.error(str(error))
    results["data_sha256"] = hashlib.sha256(args.csv_path.read_bytes()).hexdigest()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    report = markdown_report(results)
    (args.output / "results.md").write_text(report, encoding="utf-8")
    plot_results(frame, results, samples, args.output / "figures")
    print(report)


if __name__ == "__main__":
    main()
