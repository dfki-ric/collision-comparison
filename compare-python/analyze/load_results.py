"""Loading the CSV files written by compile_csv_from_results.py.

A CSV file contains one row per case file and one column per implementation (time for all collision checks of the
case file in microseconds), plus the columns in METADATA_COLUMNS. A task is one benchmark on one computer. All
implementations are measured on the same case files, so the times of a task are paired.
"""
import warnings

import pandas as pd

from algo_metadata import algo_metadata

METADATA_COLUMNS = ["file", "benchmark", "computer", "n_checks", "reference_distance", "n_faces", "target_distance"]
# Geometry of each benchmark: primitive and mesh benchmarks are never aggregated in one comparison.
BENCHMARK_GEOMETRY = {
    "uc1_ur10_collision": "primitives",
    "uc2_ur10_collision": "primitives",
    "uc5_ur10_collision": "primitives",
    "uc6_ur10_collision": "primitives",
    "complex_env_dual_arm_collision": "meshes",
    "complex_env_dual_arm_collision_max256verts": "meshes",
    "icospheres_of_different_vertex_counts": "meshes",
    "icospheres_of_different_high_vertex_counts": "meshes",
    "icospheres_fixed_size_distance_sweep": "meshes",
}


def load_results(csv_paths):
    """Concatenate CSV files (one per benchmark and computer) to one table with one row per case file."""
    df = pd.concat([pd.read_csv(path) for path in csv_paths], ignore_index=True)
    for column in ["benchmark", "computer"]:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' is missing: the CSV files must be written by compile_csv_from_results.py")
    unknown_benchmarks = sorted(set(df["benchmark"]) - set(BENCHMARK_GEOMETRY))
    if unknown_benchmarks:
        raise ValueError(f"Benchmarks without geometry in BENCHMARK_GEOMETRY: {unknown_benchmarks}")
    unknown = [c for c in df.columns if c not in METADATA_COLUMNS and c not in algo_metadata]
    if unknown:
        warnings.warn(f"Columns without metadata in algo_metadata.py are ignored: {unknown}")
    return df


def algorithm_columns(df):
    """Columns that contain runtimes of implementations."""
    return [c for c in df.columns if c in algo_metadata]


def tasks(df):
    """One table per task, i.e., per benchmark and computer, sorted by case file: {(benchmark, computer): table}."""
    return {key: task.sort_values("file") for key, task in df.groupby(["benchmark", "computer"], sort=True)}


def comparison_groups(df):
    """Groups of tasks that are aggregated in comparisons, i.e., per geometry and computer:
    {(geometry, computer): table}. Primitive and mesh benchmarks, and different computers, are never aggregated."""
    geometry = df["benchmark"].map(BENCHMARK_GEOMETRY)
    return {key: group for key, group in df.groupby([geometry, df["computer"]], sort=True)}


def to_long(df):
    """One row per case file and implementation, with the columns time_us, language, category and label."""
    id_columns = [c for c in METADATA_COLUMNS if c in df.columns]
    long = df.melt(id_vars=id_columns, value_vars=algorithm_columns(df), var_name="algorithm", value_name="time_us")
    long["language"] = long["algorithm"].map(lambda a: algo_metadata[a].language.value)
    long["category"] = long["algorithm"].map(lambda a: algo_metadata[a].category.value)
    long["label"] = long["algorithm"].map(lambda a: algo_metadata[a].pretty_name_full)
    return long
