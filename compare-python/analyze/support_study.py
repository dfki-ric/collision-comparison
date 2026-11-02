"""Study of the support function for meshes on the icosphere benchmarks (icospheres_of_different_vertex_counts and
icospheres_threshold_sweep, a finer sweep of small icospheres for the threshold; the case files of both are combined
per mesh size).

Compares three variants of the support function of each implementation (see compare-cpp/collider.h): linear search
over all vertices, hill climbing over the vertex graph, and hill climbing that starts at cached extreme vertices of a
3x3x3 grid of directions (as in MuJoCo).

Outputs (in --output):
- support_study.csv: median time per query for each implementation, support variant, and number of vertices
- support_study_speedup.csv, support_study.tex: speedup of each variant relative to hill climbing (geometric mean of the
  paired ratios over the case files), for all case files and for case files with at most --max-vertices vertices
  (the dual-arm meshes have at most 9043), and the fastest variant
- support_study_thresholds.csv: threshold for an adaptive support function (plain hill climbing for small meshes, hill
  climbing with cached extremes for large meshes): the number of vertices at which the median times of both variants
  cross for the last time (interpolated between the icosphere sizes on a log-log scale)
- support_study.pdf/.tif/.png: median time per query against the number of vertices

Usage: python support_study.py <CSV files of the study> [--output DIR]
"""
import argparse
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from figures import STYLE, TEXT_SECONDARY, GRID, FULL_WIDTH, _save, _tick_label
from load_results import latex_escape, load_results

ICOSPHERE_BENCHMARKS = ["icospheres_of_different_vertex_counts", "icospheres_threshold_sweep"]
VARIANTS = ["linear", "hill climbing", "cached extremes"]
VARIANT_LABELS = {"linear": "Linear", "hill climbing": "Hill climbing", "cached extremes": "Cached extremes"}
# one hue from light to dark and a marker per variant, so that the variants can be told apart without color
VARIANT_STYLE = {"linear": ("#b0aea8", "o"), "hill climbing": ("#6f6d68", "s"), "cached extremes": ("#0b0b0b", "^")}


def _family(title, default, default_variant="hill climbing"):
    """Columns of the support variants of an implementation: the default benchmark name has no suffix."""
    suffixes = {"linear": " linear support", "hill climbing": " hill climbing", "cached extremes": " cached extremes"}
    columns = {variant: default + suffix for variant, suffix in suffixes.items()}
    columns[default_variant] = default
    return title, columns


FAMILIES = [
    _family("libccd: intersection", "libccd intersection"),
    _family("HPP-FCL Nest.: intersection", "FCL intersection"),
    _family("HPP-FCL: intersection", "FCL intersection defaultGJK"),
    _family("MuJoCo: intersection", "MuJoCo intersection", default_variant="cached extremes"),
    _family("OpenGJK: distance", "openGJK distance"),
    _family("HPP-FCL Nest.: distance", "FCL distance"),
    _family("HPP-FCL: distance", "FCL distance defaultGJK"),
    _family("MuJoCo: distance", "MuJoCo distance", default_variant="cached extremes"),
]


# implementations with our own support functions, which get an adaptive support function (see thresholds())
ADAPTIVE = ["libccd: intersection", "OpenGJK: distance"]


def _vertices(n_faces):
    # closed triangle meshes of genus 0 (Euler): V - E + F = 2 with E = 3 F / 2
    return (n_faces / 2 + 2).astype(int)


def medians(df):
    rows = []
    vertices = _vertices(df["n_faces"])
    for title, columns in FAMILIES:
        for variant, column in columns.items():
            if column not in df:
                continue
            times = df[column] / df["n_checks"]
            for n, group in times.groupby(vertices):
                rows.append({"implementation": title, "variant": variant, "vertices": n,
                             "median_us": group.median(), "n_files": group.notna().sum()})
    return pd.DataFrame(rows)


def speedups(df, max_vertices):
    rows = []
    vertices = _vertices(df["n_faces"])
    for title, columns in FAMILIES:
        baseline = columns["hill climbing"]
        if baseline not in df:
            continue
        row = {"implementation": title}
        for variant, column in columns.items():
            if column not in df or df[column].isna().all():
                continue
            ratio = np.log(df[baseline] / df[column])
            row[f"{variant} (all)"] = np.exp(ratio.mean())
            row[f"{variant} (<= {max_vertices})"] = np.exp(ratio[vertices <= max_vertices].mean())
        candidates = {v: row.get(f"{v} (<= {max_vertices})", np.nan) for v in VARIANTS}
        row["fastest"] = max(candidates, key=lambda v: -np.inf if np.isnan(candidates[v]) else candidates[v])
        rows.append(row)
    return pd.DataFrame(rows)


def thresholds(table, small="hill climbing", large="cached extremes"):
    """Crossover of two support variants: above the largest size at which the variant for small meshes is faster,
    the log of the ratio of the median times is interpolated linearly in the log of the number of vertices to the next
    size. (The linear search is never faster than plain hill climbing in the study, so it is not used.)"""
    rows = []
    for title, _ in FAMILIES:
        family = table[table["implementation"] == title].pivot(index="vertices", columns="variant", values="median_us")
        if small not in family or large not in family:
            continue
        log_ratio = np.log(family[small] / family[large]).dropna()  # > 0: variant for small meshes slower
        if (log_ratio > 0).all() or (log_ratio <= 0).all():
            rows.append({"implementation": title, "threshold_vertices": np.nan,
                         "small_faster_up_to": log_ratio.index[-1] if (log_ratio <= 0).all() else np.nan,
                         "large_faster_from": log_ratio.index[0] if (log_ratio > 0).all() else np.nan})
            continue
        # last size at which the variant for small meshes is faster
        i = np.flatnonzero(log_ratio.to_numpy() <= 0)[-1]
        if i == len(log_ratio) - 1:
            n_low = n_high = log_ratio.index[i]
            threshold = n_low
        else:
            n_low, n_high = log_ratio.index[i], log_ratio.index[i + 1]
            r_low, r_high = log_ratio.iloc[i], log_ratio.iloc[i + 1]
            t = -r_low / (r_high - r_low)
            threshold = np.exp(np.log(n_low) + t * (np.log(n_high) - np.log(n_low)))
        rows.append({"implementation": title, "threshold_vertices": int(np.floor(threshold)),
                     "small_faster_up_to": n_low, "large_faster_from": n_high})
    return pd.DataFrame(rows)


def speedup_latex(table, max_vertices, threshold):
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r" & \multicolumn{2}{c}{Linear} & \multicolumn{2}{c}{Cached extremes} & & \\",
        r"Implementation & all & $\leq$\," + f"{max_vertices:,}".replace(",", r"\,") + " vertices & all & $\\leq$\\,"
        + f"{max_vertices:,}".replace(",", r"\,") + r" vertices & Fastest & Threshold \\",
        r"\midrule",
    ]
    thresholds_by_implementation = dict(zip(threshold["implementation"], threshold["threshold_vertices"]))
    for _, row in table.iterrows():
        cells = [f"{row.get(f'{v} ({k})', np.nan):.2f}" for v in ("linear", "cached extremes")
                 for k in ("all", f"<= {max_vertices}")]
        n = thresholds_by_implementation.get(row["implementation"], np.nan)
        threshold_cell = f"{int(n)}" if row["implementation"] in ADAPTIVE and n == n else "--"
        lines.append(" & ".join([latex_escape(row["implementation"])] + cells
                                + [VARIANT_LABELS[row["fastest"]], threshold_cell]) + r" \\")
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\caption{Support function for meshes on the icosphere benchmark: speedup relative to hill climbing (geometric "
        r"mean of the paired ratios of runtimes over the case files; $>1$: faster than hill climbing), for all case "
        r"files and for icospheres with at most " + f"{max_vertices:,}".replace(",", r"\,")
        + r" vertices (the meshes of the dual-arm scene have at most 9\,043 vertices). Fastest: fastest variant for "
        r"at most " + f"{max_vertices:,}".replace(",", r"\,") + r" vertices. Threshold: libccd and OpenGJK use our "
        r"own support functions and get an adaptive one: hill climbing for meshes with at most this number of "
        r"vertices, hill climbing with cached extremes for larger meshes (last crossover of the median times).}",
        r"\label{tab:support-study}",
        r"\end{table}",
    ]
    return "\n".join(lines) + "\n"


def plot(table, path):
    """One row per query (intersection, distance) and one panel per implementation."""
    titles = [title for title, _ in FAMILIES if title in set(table["implementation"])]
    rows = [[t for t in titles if t.endswith(": intersection")], [t for t in titles if t.endswith(": distance")]]
    n_cols = max(len(r) for r in rows)
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(2, n_cols, figsize=(FULL_WIDTH, 3.4), squeeze=False, sharex=True)
        for row_axes, row_titles, query in zip(axes, rows, ["Intersection", "Distance"]):
            for ax, title in zip(row_axes, row_titles):
                for variant in VARIANTS:
                    rows_ = table[(table["implementation"] == title) & (table["variant"] == variant)]
                    if rows_.empty:
                        continue
                    color, marker = VARIANT_STYLE[variant]
                    ax.plot(np.log10(rows_["vertices"]), np.log10(rows_["median_us"]), color=color, marker=marker,
                            markersize=2.5, linewidth=1.0, label=VARIANT_LABELS[variant])
                ax.set_title(title.split(":")[0])
                ax.grid(axis="y", color=GRID, linewidth=0.5)
                low, high = ax.get_ylim()
                ticks = np.arange(np.ceil(low), np.floor(high) + 1)
                ax.set_yticks(ticks, [_tick_label(t) for t in ticks])
                xticks = np.arange(1, 6)
                ax.set_xticks(xticks, [_tick_label(t) for t in xticks])
            for ax in row_axes[len(row_titles):]:
                ax.set_visible(False)
            row_axes[0].set_ylabel(f"{query}\ntime per query [µs]")
        for ax in axes[-1]:
            ax.set_xlabel("Vertices")
        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.02),
                   labelcolor=TEXT_SECONDARY)
        fig.tight_layout(rect=(0, 0.06, 1, 1))
        _save(fig, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv_files", nargs="+", help="CSV files of the icosphere benchmark")
    parser.add_argument("--max-vertices", type=int, default=10000,
                        help="Largest mesh for the selection of the fastest variant (default: 10000)")
    parser.add_argument("--output", default="support_study_output", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    out = lambda name: Path(args.output, name)
    df = load_results(args.csv_files)
    df = df[df["benchmark"].isin(ICOSPHERE_BENCHMARKS)]

    table = medians(df)
    table.to_csv(out("support_study.csv"), index=False)
    speedup = speedups(df, args.max_vertices)
    speedup.to_csv(out("support_study_speedup.csv"), index=False)
    threshold = thresholds(table)
    threshold.to_csv(out("support_study_thresholds.csv"), index=False)
    with open(out("support_study.tex"), "w") as f:
        f.write(speedup_latex(speedup, args.max_vertices, threshold))
    plot(table, out("support_study.pdf"))
    print(speedup.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print(threshold.to_string(index=False))
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
