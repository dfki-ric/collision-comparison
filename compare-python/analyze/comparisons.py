"""Pairwise comparisons of implementations with paired effect sizes and stratified bootstrap confidence intervals.

For each pair (X, Y), we report the probability of improvement P(T_X < T_Y) and the speedup of X over Y (geometric
mean of T_Y / T_X), both computed per task (benchmark and computer) and averaged over tasks with equal weight. All
tasks in the given table are used: run_analysis.py passes one group of tasks (one geometry on one computer) at a time.
"""
import warnings

import numpy as np
import pandas as pd

from algo_metadata import AlgoData, algo_metadata
from load_results import LINEAR_SUPPORT_SUFFIX, algorithm_columns, latex_escape, tasks
from probability_of_improvement import probability_of_improvement, probability_of_improvement_ci
from speedup import speedup_ci

# (Nesterov-accelerated GJK, vanilla GJK) of the same library
NESTEROV_PAIRS = [
    ("FCL intersection", "FCL intersection defaultGJK"),
    ("FCL intersection linear support", "FCL intersection defaultGJK linear support"),
    ("FCL distance", "FCL distance defaultGJK"),
    ("FCL distance linear support", "FCL distance defaultGJK linear support"),
    ("collision-rs_nasterov_gjk", "collision-rs_distance_gjk"),
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
    """Linear support function against the logarithmic one of the same implementation.

    X is the variant, Y the base implementation (probability of improvement > 0.5 and speedup > 1: the variant is
    faster)."""
    algorithms = set(complete_algorithms(df))
    pairs = [(a, a[:-len(LINEAR_SUPPORT_SUFFIX)]) for a in sorted(algorithms)
             if a.endswith(LINEAR_SUPPORT_SUFFIX) and a[:-len(LINEAR_SUPPORT_SUFFIX)] in algorithms]
    return pd.DataFrame([{"variant": "linear support", **compare(df, x, y, **kwargs)} for x, y in pairs])


def nesterov(df, **kwargs):
    """Nesterov-accelerated GJK (X) against vanilla GJK (Y) of the same library (speedup > 1: Nesterov is faster)."""
    algorithms = set(complete_algorithms(df))
    return pd.DataFrame([{"variant": "Nesterov acceleration", **compare(df, x, y, **kwargs)}
                         for x, y in NESTEROV_PAIRS if x in algorithms and y in algorithms])


def speedup_vs_fastest(df, n_resamples=5000, confidence_level=0.95, random_state=None):
    """Slowdown of every implementation relative to the fastest implementation (lowest typical time) of its category.

    The slowdown of X is the speedup of the fastest implementation over X (geometric mean of T_X / T_fastest, paired,
    averaged over tasks), e.g., 2 means that X needs twice as long. The fastest implementation has a slowdown of 1."""
    algorithms = complete_algorithms(df)
    task_tables = list(tasks(df).values())
    rows = []
    for category in AlgoData.Category:
        group = [a for a in algorithms if algo_metadata[a].category is category]
        if not group:
            continue
        fastest = min(group, key=lambda a: typical_time(df, a))
        times_fastest = [t[fastest].to_numpy(dtype=float) for t in task_tables]
        for a in group:
            if a == fastest:
                slowdown = low = high = 1.0
            else:
                times_a = [t[a].to_numpy(dtype=float) for t in task_tables]
                slowdown, low, high = speedup_ci(times_fastest, times_a, n_resamples, confidence_level, random_state)
            rows.append({"category": category.value, "algorithm": a, "label": algo_metadata[a].pretty_name,
                         "language": algo_metadata[a].language.value, "fastest": algo_metadata[fastest].pretty_name,
                         "slowdown": slowdown, "ci_low": low, "ci_high": high})
    return pd.DataFrame(rows)


def linear_support_slowdown(variants_table):
    """Slowdown of the linear support function relative to the logarithmic one (T_linear / T_logarithmic), from the
    table of variants()."""
    rows = []
    for row in variants_table.itertuples():
        base = algo_metadata[row.y]
        rows.append({"category": base.category.value, "algorithm": row.y, "label": base.pretty_name,
                     "language": base.language.value, "slowdown": 1.0 / row.speedup,
                     "ci_low": 1.0 / row.speedup_ci_high, "ci_high": 1.0 / row.speedup_ci_low})
    return pd.DataFrame(rows)


def probability_of_improvement_matrices(df):
    """Pairwise probabilities of improvement within each category and language (with at least two implementations).

    Returns {(category, language): matrix}, where matrix.loc[A, B] = P(T_A < T_B), averaged over tasks. Rows and
    columns are labels of the implementations, sorted by typical time (fastest first)."""
    algorithms = complete_algorithms(df)
    task_tables = list(tasks(df).values())
    matrices = {}
    for category in AlgoData.Category:
        for language in AlgoData.Language:
            group = sorted([a for a in algorithms if algo_metadata[a].category is category
                            and algo_metadata[a].language is language], key=lambda a: typical_time(df, a))
            if len(group) < 2:
                continue
            labels = [algo_metadata[a].pretty_name for a in group]
            matrix = pd.DataFrame(np.nan, index=labels, columns=labels)
            for i, a in enumerate(group):
                for j, b in enumerate(group):
                    if i != j:
                        matrix.iloc[i, j] = probability_of_improvement(
                            [t[a].to_numpy(dtype=float) for t in task_tables],
                            [t[b].to_numpy(dtype=float) for t in task_tables])
            matrices[(category.value, language.value)] = matrix
    return matrices


def to_latex(table, caption, label):
    """LaTeX table: X, Y, probability of improvement and speedup with 95 % confidence intervals."""
    escape = latex_escape

    lines = ["\\begin{table}[htbp]", "\\centering", "\\begin{tabular}{llcc}", "\\toprule",
             "X & Y & $P(T_X < T_Y)$ & Speedup of X \\\\", "\\midrule"]
    for row in table.itertuples():
        lines.append(f"{escape(row.x_label)} & {escape(row.y_label)} & "
                     f"{row.probability_of_improvement:.2f} [{row.poi_ci_low:.2f}, {row.poi_ci_high:.2f}] & "
                     f"{row.speedup:.2f} [{row.speedup_ci_low:.2f}, {row.speedup_ci_high:.2f}] \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", f"\\caption{{{caption}}}", f"\\label{{{label}}}", "\\end{table}"]
    return "\n".join(lines)
