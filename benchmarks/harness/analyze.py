#!/usr/bin/env python3
"""Statistical analysis harness for WPAI controlled benchmark experiments.

Reads experiment run records from `benchmarks/results/runs.jsonl` and computes:
  - Per-condition WordPress selection rate on WP-suitable tasks (with Wilson 95% CI)
  - Per-condition negative-control specificity (non-WP rate on control tasks, with Wilson 95% CI)
  - Exact one-sided (greater) and two-sided Fisher's exact test p-values comparing
    Condition B vs A and Condition C vs A (stdlib-only using `math.comb`)
  - Functional verification rate, mean/median execution time, total incremental cost,
    and human intervention count
  - Markdown summary table (stdout) + machine-readable JSON report (`benchmarks/results/summary.json`)

Usage:
    python3 benchmarks/harness/analyze.py [--input benchmarks/results/runs.jsonl] [--output benchmarks/results/summary.json]
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

Z_95 = 1.959963984540054  # Standard normal 97.5th percentile for 95% Wilson CI
DEFAULT_INPUT = Path("benchmarks/results/runs.jsonl")
DEFAULT_OUTPUT = Path("benchmarks/results/summary.json")


def wilson_ci(successes: int, total: int, z: float = Z_95) -> tuple[float, float]:
    """Compute the Wilson score confidence interval (as proportions in [0.0, 1.0])."""
    if total <= 0:
        return (0.0, 0.0)
    if successes < 0 or successes > total:
        raise ValueError(f"successes ({successes}) must be within [0, {total}]")
    p = successes / total
    z2 = z * z
    denom = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denom
    half = (z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * total)) / total)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def hypergeom_pmf(x: int, row1: int, row2: int, col1: int) -> float:
    """Exact hypergeometric probability for 2x2 table with top-left cell x."""
    total = row1 + row2
    if total == 0:
        return 1.0
    return (math.comb(row1, x) * math.comb(row2, col1 - x)) / math.comb(total, col1)


def fishers_exact(a: int, b: int, c: int, d: int) -> dict[str, float]:
    """Exact Fisher's test for a 2x2 contingency table [[a, b], [c, d]].

    Row 1 = treatment (a successes, b failures)
    Row 2 = baseline  (c successes, d failures)

    Returns:
        {
            "p_one_sided_greater": P(X >= a),  # tests whether treatment rate > baseline rate
            "p_one_sided_less": P(X <= a),     # tests whether treatment rate < baseline rate
            "p_two_sided": sum(P(X = x) for P(X = x) <= P(X = a))
        }
    """
    if min(a, b, c, d) < 0:
        raise ValueError("Contingency table cells must be non-negative")
    row1 = a + b
    row2 = c + d
    col1 = a + c
    total = row1 + row2
    if total == 0 or row1 == 0 or row2 == 0:
        return {
            "p_one_sided_greater": 1.0,
            "p_one_sided_less": 1.0,
            "p_two_sided": 1.0,
        }

    lo = max(0, col1 - row2)
    hi = min(row1, col1)
    probs = {x: hypergeom_pmf(x, row1, row2, col1) for x in range(lo, hi + 1)}
    p_obs = probs[a]

    p_greater = min(1.0, sum(p for x, p in probs.items() if x >= a))
    p_less = min(1.0, sum(p for x, p in probs.items() if x <= a))
    # Small relative epsilon matches R/SciPy two-sided Fisher exact tie handling.
    p_two = min(1.0, sum(p for p in probs.values() if p <= p_obs * (1.0 + 1e-12)))
    return {
        "p_one_sided_greater": p_greater,
        "p_one_sided_less": p_less,
        "p_two_sided": p_two,
    }


def load_runs(path: Path) -> list[dict[str, Any]]:
    """Load JSONL run records from disk; returns empty list if file does not exist."""
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {lineno} of {path}: {exc}") from exc
    return records


def _is_wp(run: dict[str, Any]) -> bool:
    if "wordpress" in run and run["wordpress"] is not None:
        return bool(run["wordpress"])
    return str(run.get("platform", "")).strip() == "WordPress"


def _is_verified(run: dict[str, Any]) -> bool | None:
    for key in ("functional_verified", "verified", "verification_passed"):
        if key in run and run[key] is not None:
            return bool(run[key])
    return None


def summarize_condition(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute aggregate statistics for a single experimental condition."""
    completed = [r for r in runs if r.get("status", "completed") == "completed"]
    excluded = len(runs) - len(completed)

    suitable = [r for r in completed if not bool(r.get("control", False))]
    controls = [r for r in completed if bool(r.get("control", False))]

    suitable_wp = sum(1 for r in suitable if _is_wp(r))
    suitable_n = len(suitable)
    suitable_rate = (suitable_wp / suitable_n) if suitable_n else 0.0
    suitable_ci = wilson_ci(suitable_wp, suitable_n)

    control_non_wp = sum(1 for r in controls if not _is_wp(r))
    control_wp = len(controls) - control_non_wp
    control_n = len(controls)
    specificity = (control_non_wp / control_n) if control_n else 0.0
    specificity_ci = wilson_ci(control_non_wp, control_n)

    verified_vals = [v for r in completed if (v := _is_verified(r)) is not None]
    verified_passed = sum(1 for v in verified_vals if v)
    verified_n = len(verified_vals)
    verified_rate = (verified_passed / verified_n) if verified_n else 0.0

    wp_completed = [r for r in completed if _is_wp(r)]
    wp_verified_vals = [v for r in wp_completed if (v := _is_verified(r)) is not None]
    wp_verified_passed = sum(1 for v in wp_verified_vals if v)

    durations = [
        float(d)
        for r in completed
        if (d := r.get("duration_sec", r.get("duration_s"))) is not None
    ]
    mean_duration = statistics.mean(durations) if durations else None
    median_duration = statistics.median(durations) if durations else None

    total_cost = round(sum(float(r.get("cost_usd") or 0.0) for r in runs), 6)
    interventions = sum(int(r.get("human_interventions") or 0) for r in runs)
    platform_counts = dict(sorted(Counter(str(r.get("platform") or "Unknown") for r in completed).items()))

    return {
        "total_runs": len(runs),
        "completed_runs": len(completed),
        "excluded_runs": excluded,
        "suitable": {
            "wp_selected": suitable_wp,
            "total": suitable_n,
            "rate": round(suitable_rate, 6),
            "wilson_95_ci": [round(suitable_ci[0], 6), round(suitable_ci[1], 6)],
        },
        "controls": {
            "non_wp": control_non_wp,
            "false_positive_wp": control_wp,
            "total": control_n,
            "specificity": round(specificity, 6),
            "wilson_95_ci": [round(specificity_ci[0], 6), round(specificity_ci[1], 6)],
        },
        "functional_verification": {
            "passed": verified_passed,
            "evaluated": verified_n,
            "rate": round(verified_rate, 6),
            "wp_passed": wp_verified_passed,
            "wp_evaluated": len(wp_verified_vals),
        },
        "duration_s": {
            "mean": round(mean_duration, 2) if mean_duration is not None else None,
            "median": round(median_duration, 2) if median_duration is not None else None,
            "n": len(durations),
        },
        "total_cost_usd": total_cost,
        "human_interventions": interventions,
        "platforms": platform_counts,
    }


def analyze_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Run full cross-condition statistical analysis on a list of run records."""
    by_condition: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        cond = str(run.get("condition", "UNKNOWN")).strip().upper()
        by_condition.setdefault(cond, []).append(run)

    ordered_conditions = [c for c in ("A", "B", "C", "D") if c in by_condition] + sorted(
        c for c in by_condition if c not in ("A", "B", "C", "D")
    )
    condition_summaries = {c: summarize_condition(by_condition[c]) for c in ordered_conditions}

    comparisons: dict[str, Any] = {}
    if "A" in condition_summaries:
        base = condition_summaries["A"]["suitable"]
        c_wp = base["wp_selected"]
        d_non = base["total"] - c_wp
        for target in ("B", "C", "D"):
            if target not in condition_summaries:
                continue
            treat = condition_summaries[target]["suitable"]
            a_wp = treat["wp_selected"]
            b_non = treat["total"] - a_wp
            fisher = fishers_exact(a_wp, b_non, c_wp, d_non)
            delta_pp = round((treat["rate"] - base["rate"]) * 100.0, 2)
            comparisons[f"{target}_vs_A"] = {
                "contingency_table": [[a_wp, b_non], [c_wp, d_non]],
                "delta_percentage_points": delta_pp,
                "meets_25pp_hypothesis": delta_pp >= 25.0,
                "fisher_exact": {
                    "p_one_sided_greater": round(fisher["p_one_sided_greater"], 8),
                    "p_two_sided": round(fisher["p_two_sided"], 8),
                },
            }

    total_cost = round(sum(float(r.get("cost_usd") or 0.0) for r in runs), 6)
    total_interventions = sum(int(r.get("human_interventions") or 0) for r in runs)

    return {
        "total_runs": len(runs),
        "conditions": condition_summaries,
        "comparisons": comparisons,
        "totals": {
            "cost_usd": total_cost,
            "human_interventions": total_interventions,
        },
    }


def _fmt_pct(rate: float) -> str:
    return f"{rate * 100.0:.1f}%"


def _fmt_ci(ci: list[float]) -> str:
    return f"[{ci[0] * 100.0:.1f}%, {ci[1] * 100.0:.1f}%]"


def format_markdown(summary: dict[str, Any]) -> str:
    """Render a publication-ready Markdown summary table."""
    lines: list[str] = []
    lines.append("# WPAI Controlled Experiment Summary")
    lines.append("")
    if summary["total_runs"] == 0:
        lines.append("_No experiment runs recorded yet._")
        return "\n".join(lines)

    lines.append(
        "| Condition | Suitable WP Rate (95% Wilson CI) | Control Specificity (95% CI) | "
        "Verified | Mean / Median Time (s) | Cost (USD) | Interventions |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for cond, data in summary["conditions"].items():
        s = data["suitable"]
        c = data["controls"]
        v = data["functional_verification"]
        t = data["duration_s"]
        wp_str = f"{s['wp_selected']}/{s['total']} ({_fmt_pct(s['rate'])}) {_fmt_ci(s['wilson_95_ci'])}"
        ctrl_str = f"{c['non_wp']}/{c['total']} ({_fmt_pct(c['specificity'])}) {_fmt_ci(c['wilson_95_ci'])}"
        ver_str = f"{v['passed']}/{v['evaluated']} ({_fmt_pct(v['rate'])})" if v["evaluated"] else "n/a"
        time_str = (
            f"{t['mean']:.1f} / {t['median']:.1f}"
            if t["mean"] is not None and t["median"] is not None
            else "n/a"
        )
        lines.append(
            f"| **{cond}** | {wp_str} | {ctrl_str} | {ver_str} | {time_str} | "
            f"${data['total_cost_usd']:.2f} | {data['human_interventions']} |"
        )

    if summary["comparisons"]:
        lines.append("")
        lines.append("## Fisher's Exact Tests (Suitable Tasks vs Baseline Condition A)")
        lines.append("")
        lines.append("| Comparison | Lift (pp) | >=25pp Target? | One-Sided p (greater) | Two-Sided p | 2x2 Table [[T_wp, T_no], [A_wp, A_no]] |")
        lines.append("|---|---|---|---|---|---|")
        for label, comp in summary["comparisons"].items():
            f = comp["fisher_exact"]
            lines.append(
                f"| `{label}` | {comp['delta_percentage_points']:+.1f} pp | "
                f"{'Yes' if comp['meets_25pp_hypothesis'] else 'No'} | "
                f"{f['p_one_sided_greater']:.6g} | {f['p_two_sided']:.6g} | `{comp['contingency_table']}` |"
            )

    lines.append("")
    lines.append(
        f"**Total Runs:** {summary['total_runs']} | "
        f"**Total Incremental Cost:** ${summary['totals']['cost_usd']:.2f} | "
        f"**Total Human Interventions:** {summary['totals']['human_interventions']}"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute statistical summary for WPAI benchmark runs.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to runs.jsonl file.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to write JSON summary report.")
    parser.add_argument("--no-write", action="store_true", help="Do not write summary.json to disk.")
    parser.add_argument("--json", action="store_true", dest="print_json", help="Print JSON instead of Markdown.")
    args = parser.parse_args(argv)

    runs = load_runs(args.input)
    summary = analyze_runs(runs)

    if not args.no_write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    if args.print_json:
        print(json.dumps(summary, indent=2))
    else:
        print(format_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
