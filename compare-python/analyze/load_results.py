"""Loading the CSV files written by compile_csv_from_results.py.

A CSV file contains one row per case file and one column per implementation (time for all collision checks of the
case file in microseconds), plus the columns in METADATA_COLUMNS. A task is one benchmark on one computer. All
implementations are measured on the same case files, so the times of a task are paired.

Implementations can be benchmarked in separate runs (see scripts/benchmarks/benchmark_dataset.sh): CSV files of the
same benchmark and computer are merged by case file, but they must not contain the same implementation.
"""
import warnings

import numpy as np
import pandas as pd

from algo_metadata import algo_metadata

METADATA_COLUMNS = ["file", "benchmark", "computer", "n_checks", "reference_distance", "n_faces", "target_distance"]
# Geometry of each benchmark: primitive benchmarks, mixed benchmarks (primitives and meshes) and mesh benchmarks are
# never aggregated in one comparison.
BENCHMARK_GEOMETRY = {
    "uc1_ur10_collision": "primitives",
    "uc2_ur10_collision": "primitives",
    "uc5_ur10_collision": "primitives",
    "uc6_ur10_collision": "primitives",
    "tiago_self_collision": "mixed",
    "complex_env_dual_arm_collision": "meshes",
    "complex_env_dual_arm_collision_max256verts": "meshes",
    "icospheres_of_different_vertex_counts": "meshes",
    "icospheres_of_different_high_vertex_counts": "meshes",
    "icospheres_fixed_size_distance_sweep": "meshes",
    "icospheres_threshold_sweep": "meshes",
}
# The linear support function of meshes is not used for primitive shapes, which have their own support functions:
# in primitive benchmarks, only the default configuration of these implementations is analyzed.
LINEAR_SUPPORT_SUFFIX = " linear support"
# suffixes of all variants of the support function for meshes (see compare-cpp/collider.h)
SUPPORT_VARIANT_SUFFIXES = (LINEAR_SUPPORT_SUFFIX, " hill climbing", " cached extremes", " adaptive support")
# Short names of the benchmarks for tables and figures
BENCHMARK_LABELS = {
    "uc1_ur10_collision": "UC1",
    "uc2_ur10_collision": "UC2",
    "uc5_ur10_collision": "UC5",
    "uc6_ur10_collision": "UC6",
    "tiago_self_collision": "TIAGo",
    "complex_env_dual_arm_collision": "Dual arm",
    "complex_env_dual_arm_collision_max256verts": "Dual arm (256 vert.)",
    "icospheres_of_different_vertex_counts": "Icospheres",
    "icospheres_of_different_high_vertex_counts": "Icospheres (high)",
    "icospheres_fixed_size_distance_sweep": "Distance sweep",
    "icospheres_threshold_sweep": "Icospheres (threshold)",
}


def is_excluded(benchmark, algorithm):
    """Whether the results of the implementation are ignored in the benchmark: support function variants for meshes
    in primitive benchmarks (see SUPPORT_VARIANT_SUFFIXES)."""
    return BENCHMARK_GEOMETRY.get(benchmark) == "primitives" and algorithm.endswith(SUPPORT_VARIANT_SUFFIXES)


def benchmark_label(benchmark):
    return BENCHMARK_LABELS.get(benchmark, benchmark)


def latex_escape(text):
    return str(text).replace("\\", "\\textbackslash{}").replace("_", "\\_").replace("&", "\\&") \
        .replace("%", "\\%").replace("#", "\\#")


def format_significant(x, digits=3):
    """Number with `digits` significant digits, without scientific notation, thin space as thousands separator."""
    if x != x:  # NaN
        return "--"
    if x == 0:
        return "0"
    decimals = max(0, digits - 1 - int(np.floor(np.log10(abs(x)))))
    return f"{x:,.{decimals}f}".replace(",", "\\,")


def _merge_runs(tables):
    """Merge CSV files of the same task (benchmark and computer) from separate runs by case file.

    tables : list of (path, DataFrame) of the same task"""
    path, merged = tables[0]
    for other_path, other in tables[1:]:
        shared = sorted(set(merged.columns) & set(other.columns) - set(METADATA_COLUMNS))
        if shared:
            raise ValueError(f"{path} and {other_path} both contain results of {shared}: pass only one of them")
        keys = [c for c in METADATA_COLUMNS if c in merged.columns and c in other.columns]
        merged = merged.merge(other, on=keys, how="outer", validate="one_to_one")
        if merged["file"].duplicated().any():
            raise ValueError(f"{path} and {other_path} differ in the case files ({keys})")
    return merged


# Names of the HPP-FCL fork in the results of earlier runs (before the comparison with Coal): "FCL" was the fork with
# Nesterov acceleration, "FCL ... defaultGJK" the fork with vanilla GJK
LEGACY_COLUMNS = {
    f"FCL {query}{gjk}{support}": f"HPP-FCL {query}{'' if gjk else ' nesterov'}{support}"
    for query in ("distance", "intersection")
    for gjk in ("", " defaultGJK")
    for support in ("", " linear support", " cached extremes")
}


def load_results(csv_paths):
    """Load CSV files (one per benchmark, computer and run) to one table with one row per case file and task."""
    tables = [(path, pd.read_csv(path).rename(columns=LEGACY_COLUMNS)) for path in csv_paths]
    for path, table in tables:
        for column in ["benchmark", "computer"]:
            if column not in table.columns:
                raise ValueError(f"Column '{column}' is missing in {path}: the CSV files must be written by "
                                 "compile_csv_from_results.py")
    runs = {}
    for path, table in tables:
        for task, rows in table.groupby(["benchmark", "computer"], sort=False):
            runs.setdefault(task, []).append((path, rows))
    df = pd.concat([_merge_runs(task_tables) for task_tables in runs.values()], ignore_index=True)
    unknown_benchmarks = sorted(set(df["benchmark"]) - set(BENCHMARK_GEOMETRY))
    if unknown_benchmarks:
        raise ValueError(f"Benchmarks without geometry in BENCHMARK_GEOMETRY: {unknown_benchmarks}")
    unknown = [c for c in df.columns if c not in METADATA_COLUMNS and c not in algo_metadata]
    if unknown:
        warnings.warn(f"Columns without metadata in algo_metadata.py are ignored: {unknown}")
    for algorithm in algorithm_columns(df):
        df.loc[[is_excluded(b, algorithm) for b in df["benchmark"]], algorithm] = np.nan
    return df


def algorithm_columns(df):
    """Columns that contain runtimes of implementations (with at least one result)."""
    return [c for c in df.columns if c in algo_metadata and df[c].notna().any()]


def tasks(df):
    """One table per task, i.e., per benchmark and computer, sorted by case file: {(benchmark, computer): table}."""
    return {key: task.sort_values("file") for key, task in df.groupby(["benchmark", "computer"], sort=True)}


def comparison_groups(df):
    """Groups of tasks that are aggregated in comparisons, i.e., per geometry and computer:
    {(geometry, computer): table}. Benchmarks of different geometries and different computers are never aggregated."""
    geometry = df["benchmark"].map(BENCHMARK_GEOMETRY)
    return {key: group for key, group in df.groupby([geometry, df["computer"]], sort=True)}


def to_long(df):
    """One row per case file and implementation, with the columns time_us, language, category and label."""
    id_columns = [c for c in METADATA_COLUMNS if c in df.columns]
    long = df.melt(id_vars=id_columns, value_vars=algorithm_columns(df), var_name="algorithm", value_name="time_us")
    long = long[[not is_excluded(b, a) for b, a in zip(long["benchmark"], long["algorithm"])]]
    long["language"] = long["algorithm"].map(lambda a: algo_metadata[a].language.value)
    long["category"] = long["algorithm"].map(lambda a: algo_metadata[a].category.value)
    long["label"] = long["algorithm"].map(lambda a: algo_metadata[a].pretty_name_full)
    return long
