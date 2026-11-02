"""Statistics of the benchmark data: pairs per case file, shape pairs, intersections and distances.

Usage (from compare-python/analyze):
    python case_statistics.py [--data ../../data] [--first 1] [--last 1000] [--output case_statistics_output]

The statistics only depend on the case files (data/<benchmark>/<benchmark>_<i>.json), not on the results. Only the case
files <first> to <last> are used, as in scripts/benchmarks/benchmark_<benchmark>.sh. A pair is one collision check
(two colliders); it intersects if the reference distance (distance3d) is 0.

Output files:
- case_statistics_pairs.csv: one row per pair (benchmark, case file, shape pair, distance, intersection, vertices)
- case_statistics.csv, case_statistics.tex: one row per benchmark (table for the paper)
- case_statistics.pdf/.tif/.png: (A) pairs per case file, (B) share of intersecting pairs, (C) distance of separated pairs
"""
import argparse
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from figures import AXIS, FULL_WIDTH, PANEL_LABEL_SIZE, STYLE, TEXT, TEXT_SECONDARY, _save, _tick_label
from load_results import BENCHMARK_GEOMETRY, benchmark_label, format_significant, latex_escape

PAPER_BENCHMARKS = ["uc1_ur10_collision", "uc2_ur10_collision", "uc5_ur10_collision", "uc6_ur10_collision",
                    "complex_env_dual_arm_collision"]
# shape pairs in the order of the table columns (abbreviation, sorted shape types)
SHAPE_PAIRS = {"B–B": ("Box", "Box"), "B–C": ("Box", "Cylinder"), "B–S": ("Box", "Sphere"),
               "C–C": ("Cylinder", "Cylinder"), "C–S": ("Cylinder", "Sphere"), "S–S": ("Sphere", "Sphere"),
               "M–M": ("Mesh", "Mesh")}
SHAPE_NAMES = {"B": "box", "C": "cylinder", "S": "sphere", "M": "mesh"}
VIOLIN_COLOR = "#a9a8a2"


def count_vertices(mesh_path, cache):
    """Number of vertices in an OBJ file (cached, the same meshes are used in many case files)."""
    if mesh_path not in cache:
        with open(mesh_path) as f:
            cache[mesh_path] = sum(1 for line in f if line.startswith("v "))
    return cache[mesh_path]


def load_pairs(data_dir, benchmarks, first, last):
    """One row per pair of colliders in the case files first to last of each benchmark."""
    rows, vertices = [], {}
    for benchmark in benchmarks:
        for i in range(first, last + 1):
            with open(Path(data_dir, benchmark, f"{benchmark}_{i}.json")) as f:
                cases = json.load(f)
            for case in cases:
                row = {"benchmark": benchmark, "file": i, "case": case["case"], "distance": case["distance"]}
                types = []
                for k, key in enumerate(["collider1", "collider2"]):
                    collider = case[key]
                    types.append(collider["type"])
                    if "mesh_path" in collider:
                        # mesh paths are relative to the data directory
                        row[f"vertices{k + 1}"] = count_vertices(Path(data_dir, collider["mesh_path"]), vertices)
                        row[f"mesh{k + 1}"] = collider["mesh_path"]
                row["shape_pair"] = "–".join(t[0] for t in sorted(types))
                rows.append(row)
    pairs = pd.DataFrame(rows)
    pairs["intersecting"] = pairs["distance"] <= 0.0
    return pairs


def summary(pairs):
    """One row per benchmark: case files, pairs, pairs per case file, intersections, distances and shape pairs."""
    rows = []
    for benchmark, b in pairs.groupby("benchmark", sort=False):
        per_file = b.groupby("file").size()
        separated = b.loc[~b["intersecting"], "distance"]
        row = {"benchmark": benchmark, "geometry": BENCHMARK_GEOMETRY[benchmark], "case_files": len(per_file),
               "pairs": len(b), "pairs_per_file_median": per_file.median(), "pairs_per_file_min": per_file.min(),
               "pairs_per_file_max": per_file.max(), "intersecting": b["intersecting"].mean(),
               "distance_median": separated.median(), "distance_q25": separated.quantile(0.25),
               "distance_q75": separated.quantile(0.75), "distance_max": separated.max()}
        shares = b["shape_pair"].value_counts(normalize=True)
        row.update({name: shares.get(name, 0.0) for name in SHAPE_PAIRS})
        if "mesh1" in b and b["mesh1"].notna().any():
            meshes = pd.concat([b[["mesh1", "vertices1"]].set_axis(["mesh", "vertices"], axis=1),
                                b[["mesh2", "vertices2"]].set_axis(["mesh", "vertices"], axis=1)]).dropna()
            vertices = meshes.drop_duplicates("mesh")["vertices"]
            row.update({"meshes": len(vertices), "vertices_min": vertices.min(),
                        "vertices_median": vertices.median(), "vertices_max": vertices.max()})
        rows.append(row)
    return pd.DataFrame(rows)


def _percent(x):
    if x == 0:
        return "--"
    return "$<$0.1" if x < 0.001 else f"{100 * x:.1f}" if x < 0.1 else f"{100 * x:.0f}"


def to_latex(table):
    """Table of the benchmark data: one row per benchmark."""
    shape_pairs = [name for name in SHAPE_PAIRS if table[name].max() > 0]
    lines = ["\\begin{table}[htbp]", "\\centering", "\\small", "\\setlength{\\tabcolsep}{4pt}",
             "\\begin{tabular}{lrrrrr" + "r" * len(shape_pairs) + "}", "\\toprule",
             " & & & & & & \\multicolumn{" + str(len(shape_pairs)) + "}{c}{Shape pairs (\\%)} \\\\",
             "\\cmidrule(lr){7-" + str(6 + len(shape_pairs)) + "}",
             "Benchmark & Files & Pairs & Pairs/file & Inters.\\ (\\%) & Distance (cm) & "
             + " & ".join(name.replace("–", "--") for name in shape_pairs) + " \\\\", "\\midrule"]
    for _, row in table.iterrows():
        pairs_per_file = (f"{row['pairs_per_file_median']:g} "
                          f"({row['pairs_per_file_min']}--{row['pairs_per_file_max']})")
        distance = (f"{format_significant(100 * row['distance_median'], 2)} "
                    f"({format_significant(100 * row['distance_q25'], 2)}--"
                    f"{format_significant(100 * row['distance_q75'], 2)})")
        cells = [latex_escape(benchmark_label(row["benchmark"])), str(row["case_files"]),
                 f"{row['pairs']:,}".replace(",", "\\,"), pairs_per_file, f"{100 * row['intersecting']:.0f}", distance]
        cells += [_percent(row[name]) for name in shape_pairs]
        lines.append(" & ".join(cells) + " \\\\")
    legend = ", ".join(f"{a}: {SHAPE_NAMES[a]}" for a in sorted({c for name in shape_pairs for c in name.split("–")}))
    caption = ("Benchmark data. A pair is one collision check of two colliders; it intersects if the reference "
               "distance is 0. Files: case files; pairs/file: pairs per case file, median (range); inters.: "
               "intersecting pairs; distance: distance of separated pairs, median (interquartile range). "
               f"Shape pairs: {legend}.")
    if "meshes" in table:
        caption += "".join(
            f" The {int(row['meshes'])} meshes of {latex_escape(benchmark_label(row['benchmark']))} have "
            f"{int(row['vertices_min'])}--{int(row['vertices_max'])} vertices "
            f"(median {row['vertices_median']:g})."
            for _, row in table[table["meshes"].notna()].iterrows())
    lines += ["\\bottomrule", "\\end{tabular}", f"\\caption{{{caption}}}", "\\label{tab:benchmark-data}",
              "\\end{table}"]
    return "\n".join(lines)


def _violins(ax, values, y, log=False):
    data = [np.log10(v) if log else v for v in values]
    parts = ax.violinplot(data, positions=y, vert=False, widths=0.8, showextrema=False)
    for body in parts["bodies"]:
        body.set_facecolor(VIOLIN_COLOR)
        body.set_edgecolor("none")
        body.set_alpha(1.0)
    medians = [np.median(d) for d in data]
    ax.plot(medians, y, linestyle="", marker="|", markersize=6, markeredgewidth=1.2, color=TEXT)


def plot(pairs, benchmarks, path):
    """(A) pairs per case file, (B) share of intersecting pairs, (C) distance of separated pairs, one row per
    benchmark (top to bottom in the order of benchmarks)."""
    y = np.arange(len(benchmarks))[::-1]
    groups = [pairs[pairs["benchmark"] == b] for b in benchmarks]
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 3, sharey=True, figsize=(FULL_WIDTH, 0.22 * len(benchmarks) + 0.75),
                                 layout="constrained", gridspec_kw={"width_ratios": [1.0, 0.7, 1.3]})
        # A: pairs per case file
        _violins(axes[0], [g.groupby("file").size().to_numpy() for g in groups], y)
        axes[0].set_xlim(0, None)
        axes[0].set_xlabel("Pairs per case file (black: median)", loc="right")
        # B: share of intersecting pairs
        shares = [100 * g["intersecting"].mean() for g in groups]
        axes[1].barh(y, shares, height=0.6, color=VIOLIN_COLOR)
        for yi, share in zip(y, shares):
            axes[1].annotate(f"{share:.0f} %", (share, yi), xytext=(3, 0), textcoords="offset points", va="center",
                             color=TEXT_SECONDARY)
        axes[1].set_xlim(0, 100)
        axes[1].set_xticks([0, 50, 100])
        axes[1].set_xlabel("Intersecting pairs (%)", loc="right")
        # C: distance of separated pairs (log scale)
        distances = [g.loc[~g["intersecting"], "distance"].to_numpy() for g in groups]
        _violins(axes[2], distances, y, log=True)
        # the violins are drawn in log10 units: ticks at every decade
        ticks = np.arange(np.floor(np.log10(min(d.min() for d in distances))),
                          np.ceil(np.log10(max(d.max() for d in distances))) + 1)
        axes[2].set_xticks(ticks, [_tick_label(t) for t in ticks])
        axes[2].set_xticks(np.log10(np.outer(10.0 ** ticks[:-1], np.arange(2, 10)).ravel()), minor=True)
        axes[2].set_xlim(ticks[0], ticks[-1])
        axes[2].set_xlabel("Distance of separated pairs (m, black: median)", loc="right")

        axes[0].set_yticks(y, [benchmark_label(b) for b in benchmarks])
        axes[0].set_ylim(-0.6, len(benchmarks) - 0.4)
        for letter, ax in zip("ABC", axes):
            ax.set_title(letter, fontsize=PANEL_LABEL_SIZE, color=TEXT, loc="left")
            ax.tick_params(axis="y", length=0)
            ax.grid(axis="x", color=AXIS, alpha=0.2, linewidth=0.5)
            ax.set_axisbelow(True)
        _save(fig, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", default="../../data", help="Directory with one directory of case files per benchmark")
    parser.add_argument("--benchmarks", nargs="+", default=PAPER_BENCHMARKS, help="Benchmarks (default: paper)")
    parser.add_argument("--first", type=int, default=1, help="First case file")
    parser.add_argument("--last", type=int, default=1000, help="Last case file")
    parser.add_argument("--output", default="case_statistics_output", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    out = lambda name: Path(args.output, name)
    pairs = load_pairs(args.data, args.benchmarks, args.first, args.last)
    pairs.to_csv(out("case_statistics_pairs.csv"), index=False)
    table = summary(pairs)
    table.to_csv(out("case_statistics.csv"), index=False)
    with open(out("case_statistics.tex"), "w") as f:
        f.write(to_latex(table))
    plot(pairs, args.benchmarks, out("case_statistics.pdf"))
    print(table.to_string())
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
