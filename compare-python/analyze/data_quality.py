"""Checks of the data quality (see Thilo Umland's thesis, section "Analyzing Data Quality").

- missing_results: case files without a result of an implementation (e.g., crashes)
- constant_overhead: fit of t_total = o + t_pair * n_checks; an overhead o > 0 per case file indicates first-run
  effects, e.g., just-in-time compilation in the first collision check
- lag_correlation: correlation between the times of consecutive case files, which should be independent
- first_run_effect: time of each of the 10 measured runs of a case file relative to their median (C++ and Rust,
  the Python benchmarks only store the median)
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from load_results import algorithm_columns, tasks

LEVEL_COLUMNS = ["n_faces", "target_distance"]


def missing_results(df):
    """Number of case files without a result per task and implementation."""
    rows = []
    for (benchmark, computer), task in tasks(df).items():
        for algorithm in algorithm_columns(df):
            rows.append({"benchmark": benchmark, "computer": computer, "algorithm": algorithm,
                         "case_files": len(task), "missing": int(task[algorithm].isna().sum())})
    return pd.DataFrame(rows)


def _linear_fit(n, t):
    """Least squares fit of t = intercept + slope * n along the last axis."""
    n_centered = n - n.mean(axis=-1, keepdims=True)
    t_mean = t.mean(axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        slope = (n_centered * t).sum(axis=-1) / (n_centered ** 2).sum(axis=-1)
    intercept = t_mean - slope * n.mean(axis=-1)
    return intercept, slope


def constant_overhead(df, n_resamples=5000, confidence_level=0.95, random_state=None):
    """Fit t_total = o + t_pair * n_checks per task and implementation (only tasks with varying n_checks).

    Returns the overhead o per case file in microseconds with a bootstrap confidence interval (case files are
    resampled), the time per collision check t_pair, and o relative to the median time per case file.

    The model assumes that all collision checks cost about the same. This holds roughly for the UR10 use cases
    (primitive shapes), but not for the mesh scenes, in which the cost of a check depends on the meshes: there, the
    intercept does not measure an overhead. first_run_effect() measures first-run effects directly.
    """
    rng = np.random.default_rng(random_state)
    alpha = 1.0 - confidence_level
    rows = []
    for (benchmark, computer), task in tasks(df).items():
        if task["n_checks"].nunique() < 2:
            continue
        for algorithm in algorithm_columns(df):
            valid = task[algorithm].notna()
            n = task.loc[valid, "n_checks"].to_numpy(dtype=float)
            t = task.loc[valid, algorithm].to_numpy(dtype=float)
            if len(t) < 3:
                continue
            overhead, time_per_check = _linear_fit(n, t)
            indices = rng.integers(0, len(t), size=(n_resamples, len(t)))
            resampled_overhead, _ = _linear_fit(n[indices], t[indices])
            ci_low, ci_high = np.nanpercentile(resampled_overhead, [100 * alpha / 2, 100 * (1 - alpha / 2)])
            rows.append({"benchmark": benchmark, "computer": computer, "algorithm": algorithm,
                         "overhead_us": overhead, "ci_low": ci_low, "ci_high": ci_high,
                         "time_per_check_us": time_per_check, "relative_overhead": overhead / np.median(t)})
    return pd.DataFrame(rows)


def lag_correlation(df):
    """Spearman correlation between the times of consecutive case files per task and implementation.

    Case files are run in the order of their numbers. Sweeps are stored level by level, so consecutive case files
    are only compared within a level (same n_faces / target_distance). Values near 0 are expected.
    """
    rows = []
    for (benchmark, computer), task in tasks(df).items():
        levels = [c for c in LEVEL_COLUMNS if c in task.columns and task[c].notna().all()]
        groups = [g for _, g in task.groupby(levels)] if levels else [task]
        for algorithm in algorithm_columns(df):
            correlations, weights = [], []
            for group in groups:
                times = group.sort_values("file")[algorithm]
                if times.notna().sum() < 3:
                    continue
                r = times.corr(times.shift(-1), method="spearman")
                if not np.isnan(r):
                    correlations.append(r)
                    weights.append(len(times))
            if correlations:
                rows.append({"benchmark": benchmark, "computer": computer, "algorithm": algorithm,
                             "lag1_spearman": float(np.average(correlations, weights=weights))})
    return pd.DataFrame(rows)


def _read_runs(case_file_dir: Path):
    """Times of the individual measured runs (in the order in which they ran) per implementation of a case file."""
    runs = {}
    cpp_path = Path(case_file_dir, "cpp_result.json")
    if cpp_path.exists():
        for result in json.load(open(cpp_path))["results"]:
            runs[result["name"]] = [m["elapsed"] for m in result.get("measurements", [])]
    criterion = Path(case_file_dir, "criterion")
    if criterion.exists():
        for name in os.listdir(criterion):
            for sample_path in [Path(criterion, name, "all_cases", "new", "sample.json"),
                                Path(criterion, name, "new", "sample.json")]:
                if sample_path.exists():
                    sample = json.load(open(sample_path))
                    runs[name] = [time / iterations for time, iterations in zip(sample["times"], sample["iters"])]
                    break
    return runs


def first_run_effect(results_dir):
    """Mean time of the k-th measured run relative to the median of all runs of a case file.

    results_dir is the directory with one subdirectory per benchmark (results/<benchmark>/<case file>/), as written
    by scripts/benchmarks/benchmark_dataset.sh. Values above 1 for the first runs indicate an insufficient warm-up.
    Only available for C++ and Rust: the Python benchmarks only store the median.
    """
    ratios = {}
    for benchmark in sorted(os.listdir(results_dir)):
        benchmark_dir = Path(results_dir, benchmark)
        if not benchmark_dir.is_dir():
            continue
        for case_file in os.listdir(benchmark_dir):
            if not case_file.isdigit():
                continue
            for algorithm, times in _read_runs(Path(benchmark_dir, case_file)).items():
                if len(times) == 0:
                    continue
                times = np.asarray(times, dtype=float)
                ratios.setdefault((benchmark, algorithm), []).append(times / np.median(times))
    rows = []
    for (benchmark, algorithm), case_file_ratios in sorted(ratios.items()):
        n_runs = min(len(r) for r in case_file_ratios)
        mean_ratio = np.mean([r[:n_runs] for r in case_file_ratios], axis=0)
        rows.append({"benchmark": benchmark, "algorithm": algorithm, "case_files": len(case_file_ratios),
                     **{f"run_{k + 1}": mean_ratio[k] for k in range(n_runs)}})
    return pd.DataFrame(rows)
