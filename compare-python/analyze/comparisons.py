"""Pairwise comparisons of implementations with paired effect sizes and stratified bootstrap confidence intervals.

For each pair (X, Y), we report the probability of improvement P(T_X < T_Y) and the speedup of X over Y (geometric
mean of T_Y / T_X), both computed per task (benchmark and computer) and averaged over tasks with equal weight. All
tasks in the given table are used: run_analysis.py passes one group of tasks (one geometry on one computer) at a time.
"""
import warnings

import numpy as np
import pandas as pd

from algo_metadata import AlgoData, algo_metadata
from load_results import algorithm_columns, tasks
from probability_of_improvement import probability_of_improvement_ci
from speedup import speedup_ci

LINEAR_SUPPORT_SUFFIX = " linear support"
# (variant, base implementation): Nesterov acceleration of HPP-FCL and distance3d
ACCELERATION_PAIRS = [
    ("FCL distance", "FCL distance defaultGJK"),
    ("FCL intersection", "FCL intersection defaultGJK"),
    ("distance3d Nesterov (with acceleration)", "distance3d Nesterov"),
]


def complete_algorithms(df):
    """Implementations with results in every task (otherwise a paired comparison over all tasks is impossible)."""
    task_tables = tasks(df).values()
    complete = [a for a in algorithm_columns(df) if all(t[a].notna().any() for t in task_tables)]
    incomplete = [a for a in algorithm_columns(df) if a not in complete]
    if incomplete:
        warnings.warn(f"Implementations without results in some tasks are not compared: {incomplete}")
    return complete


def typical_time(df, algorithm):
    """Geometric mean over tasks of the median time per case file, used to order implementations."""
    medians = [t[algorithm].median() for t in tasks(df).values()]
    return float(np.exp(np.mean(np.log(medians))))


def compare(df, x, y, n_resamples=5000, confidence_level=0.95, random_state=None):
    """Probability of improvement and speedup of X over Y with confidence intervals."""
    task_tables = list(tasks(df).values())
    times_x = [t[x].to_numpy(dtype=float) for t in task_tables]
    times_y = [t[y].to_numpy(dtype=float) for t in task_tables]
    poi, poi_low, poi_high = probability_of_improvement_ci(times_x, times_y, n_resamples, confidence_level, random_state)
    s, s_low, s_high = speedup_ci(times_x, times_y, n_resamples, confidence_level, random_state)
    return {"x": x, "y": y, "x_label": algo_metadata[x].pretty_name_full, "y_label": algo_metadata[y].pretty_name_full,
            "probability_of_improvement": poi, "poi_ci_low": poi_low, "poi_ci_high": poi_high,
            "speedup": s, "speedup_ci_low": s_low, "speedup_ci_high": s_high}


def _all_pairs(df, algorithms, group, **kwargs):
    """Compare all pairs, X is the implementation with the lower typical time."""
    algorithms = sorted(algorithms, key=lambda a: typical_time(df, a))
    return [{**group, **compare(df, x, y, **kwargs)}
            for i, x in enumerate(algorithms) for y in algorithms[i + 1:]]


def within_language(df, **kwargs):
    """All pairs of implementations with the same language and category."""
    algorithms = complete_algorithms(df)
    rows = []
    for category in AlgoData.Category:
        for language in AlgoData.Language:
            group = [a for a in algorithms
                     if algo_metadata[a].category is category and algo_metadata[a].language is language]
            if len(group) >= 2:
                rows += _all_pairs(df, group, {"category": category.value, "language": language.value}, **kwargs)
    return pd.DataFrame(rows)


def best_per_language(df, **kwargs):
    """Pairs of the fastest implementations (lowest typical time) of each language, per category."""
    algorithms = complete_algorithms(df)
    rows = []
    for category in AlgoData.Category:
        best = []
        for language in AlgoData.Language:
            group = [a for a in algorithms
                     if algo_metadata[a].category is category and algo_metadata[a].language is language]
            if group:
                best.append(min(group, key=lambda a: typical_time(df, a)))
        if len(best) >= 2:
            rows += _all_pairs(df, best, {"category": category.value}, **kwargs)
    return pd.DataFrame(rows)


def variants(df, **kwargs):
    """Variants against their base implementation: linear support function and Nesterov acceleration.

    X is the variant, Y the base implementation (probability of improvement > 0.5 and speedup > 1: the variant is
    faster)."""
    algorithms = set(complete_algorithms(df))
    pairs = [(a, a[:-len(LINEAR_SUPPORT_SUFFIX)], "linear support") for a in sorted(algorithms)
             if a.endswith(LINEAR_SUPPORT_SUFFIX) and a[:-len(LINEAR_SUPPORT_SUFFIX)] in algorithms]
    pairs += [(x, y, "Nesterov acceleration") for x, y in ACCELERATION_PAIRS if x in algorithms and y in algorithms]
    return pd.DataFrame([{"variant": variant, **compare(df, x, y, **kwargs)} for x, y, variant in pairs])


def to_latex(table, caption, label):
    """LaTeX table: X, Y, probability of improvement and speedup with 95 % confidence intervals."""
    def escape(text):
        return text.replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")

    lines = ["\\begin{table}[htbp]", "\\centering", "\\begin{tabular}{llcc}", "\\toprule",
             "X & Y & $P(T_X < T_Y)$ & Speedup of X \\\\", "\\midrule"]
    for row in table.itertuples():
        lines.append(f"{escape(row.x_label)} & {escape(row.y_label)} & "
                     f"{row.probability_of_improvement:.2f} [{row.poi_ci_low:.2f}, {row.poi_ci_high:.2f}] & "
                     f"{row.speedup:.2f} [{row.speedup_ci_low:.2f}, {row.speedup_ci_high:.2f}] \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", f"\\caption{{{caption}}}", f"\\label{{{label}}}", "\\end{table}"]
    return "\n".join(lines)
