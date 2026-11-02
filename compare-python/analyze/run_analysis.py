"""Analysis of benchmark results: data quality, runtime distributions and pairwise comparisons.

Usage (from compare-python/analyze):
    python run_analysis.py CSV [CSV ...] [--results-dir ../../results] [--output analysis_output]

Every CSV file (written by compile_csv_from_results.py) contains the results of one benchmark on one computer, which
is one task. The comparisons are computed separately for each geometry (primitive or mesh benchmarks, see
BENCHMARK_GEOMETRY in load_results.py) and computer, and averaged over the tasks of the group with equal weight.

Output files:
- data_quality_missing.csv, data_quality_overhead.csv, data_quality_lag.csv: data-quality checks
- data_quality_appendix.tex: LaTeX tables of the data-quality checks
- data_quality_first_run.csv/.pdf: first-run effect (only with --results-dir)
- summary.csv, summary_<benchmark>_<computer>.tex: median, quartiles, upper percentiles and maximum
- violin_<benchmark>_<computer>.pdf: runtime distributions
- violin_<computer>.pdf: runtime distributions of the primitive (A) and the mesh benchmarks (B), see PAPER_VIOLIN_PANELS
- comparisons_within_language_<geometry>_<computer>.csv/.tex, comparisons_best_per_language_<geometry>_<computer>.csv/.tex,
  comparisons_variants_<geometry>_<computer>.csv/.tex (linear support), comparisons_nesterov_<geometry>_<computer>.csv/.tex
- speedup_vs_fastest_<geometry>_<computer>.csv/.tex, speedup_vs_fastest_<computer>.pdf: slowdown of every
  implementation relative to the fastest one (table with confidence intervals; figure panels: primitives, meshes)
- linear_support_<geometry>_<computer>.csv, linear_support_<computer>.pdf: slowdown of the linear support function
  relative to the logarithmic one (panels: primitives, meshes)
- effect_sizes_<geometry>_<computer>.pdf: heatmaps of the probability of improvement within each language
Every figure (.pdf, for LaTeX) is also written as .tif (RGB, 300 dpi) for the submission and as .png (150 dpi) for
READMEs. Figures are made at their final size (at most 180 mm wide): include them in LaTeX without scaling.
"""
import argparse
import os
from pathlib import Path

import data_quality
import descriptive
import comparisons
import figures
from load_results import load_results, tasks, comparison_groups, to_long

GEOMETRY_TITLES = {"primitives": "Primitives", "meshes": "Meshes"}
# panels of the violin plot in the paper: title and benchmarks, primitives (A: UC1, 2, 5, 6) and meshes (B: dual arm)
PAPER_VIOLIN_PANELS = [
    (GEOMETRY_TITLES["primitives"],
     ["uc1_ur10_collision", "uc2_ur10_collision", "uc5_ur10_collision", "uc6_ur10_collision"]),
    (GEOMETRY_TITLES["meshes"], ["complex_env_dual_arm_collision"]),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv_files", nargs="+", help="CSV files written by compile_csv_from_results.py")
    parser.add_argument("--results-dir", default=None,
                        help="Raw results (results/<benchmark>/<case file>/) for the first-run check")
    parser.add_argument("--output", default="analysis_output", help="Output directory")
    parser.add_argument("--resamples", type=int, default=5000, help="Number of bootstrap resamples")
    parser.add_argument("--seed", type=int, default=0, help="Seed of the bootstrap")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    out = lambda name: Path(args.output, name)
    df = load_results(args.csv_files)
    print(f"{len(df)} case files in {len(tasks(df))} tasks: {list(tasks(df))}")

    # 4. data quality
    missing = data_quality.missing_results(df)
    missing.to_csv(out("data_quality_missing.csv"), index=False)
    overhead = data_quality.constant_overhead(df, n_resamples=args.resamples, random_state=args.seed)
    overhead.to_csv(out("data_quality_overhead.csv"), index=False)
    lag = data_quality.lag_correlation(df)
    lag.to_csv(out("data_quality_lag.csv"), index=False)
    with open(out("data_quality_appendix.tex"), "w") as f:
        f.write(data_quality.appendix_latex(missing, overhead, lag))
    if args.results_dir is not None:
        first_run = data_quality.first_run_effect(args.results_dir)
        first_run.to_csv(out("data_quality_first_run.csv"), index=False)
        figures.first_run_plot(first_run, out("data_quality_first_run.pdf"))

    # 5. runtime distributions
    long = to_long(df)
    summary = descriptive.summary(long)
    summary.to_csv(out("summary.csv"), index=False)
    for benchmark, computer in tasks(df):
        figures.violin_plot(long, (benchmark, computer), out(f"violin_{benchmark}_{computer}.pdf"))
        with open(out(f"summary_{benchmark}_{computer}.tex"), "w") as f:
            f.write(descriptive.summary_to_latex(summary, benchmark, computer,
                                                 f"tab:summary-{benchmark.replace('_', '-')}-{computer}"))

    for computer in sorted(df["computer"].unique()):
        # panels with the benchmarks that exist on this computer
        panels = [(title, [b for b in benchmarks if (b, computer) in tasks(df)])
                  for title, benchmarks in PAPER_VIOLIN_PANELS]
        panels = [(title, benchmarks) for title, benchmarks in panels if benchmarks]
        if panels:
            figures.violin_plot(long, [(benchmarks, computer) for _, benchmarks in panels],
                                out(f"violin_{computer}.pdf"), titles=[title for title, _ in panels])

    # 6. pairwise comparisons, separately per geometry (primitives or meshes) and computer
    options = {"n_resamples": args.resamples, "random_state": args.seed}
    panels = {}  # computer -> list of (geometry, slowdown vs. fastest, linear support slowdown)
    for (geometry, computer), group in comparison_groups(df).items():
        benchmarks = sorted(group["benchmark"].unique())
        print(f"Comparisons for {geometry} on {computer}: {benchmarks}")
        variants = comparisons.variants(group, **options)
        nesterov = comparisons.nesterov(group, **options)
        for name, table, caption in [
            ("within_language", comparisons.within_language(group, **options),
             "Pairwise comparison of implementations of the same language"),
            ("best_per_language", comparisons.best_per_language(group, **options),
             "Pairwise comparison of the fastest implementation of each language"),
            ("variants", variants,
             "Linear support function (X) compared to the logarithmic one (Y)"),
            ("nesterov", nesterov,
             "Nesterov-accelerated GJK (X) compared to vanilla GJK (Y) of the same library"),
        ]:
            if len(table) == 0:  # e.g., no linear support function in primitive benchmarks
                continue
            suffix = f"{name}_{geometry}_{computer}"
            table.to_csv(out(f"comparisons_{suffix}.csv"), index=False)
            caption += (f" ({geometry} on {computer}). Probability of improvement and speedup of X over Y"
                        " (paired, averaged over tasks) with 95\\,\\% bootstrap confidence intervals.")
            with open(out(f"comparisons_{suffix}.tex"), "w") as f:
                f.write(comparisons.to_latex(table, caption, f"tab:comparisons-{suffix.replace('_', '-')}"))

        # figures of the comparisons
        suffix = f"{geometry}_{computer}"
        slowdown = comparisons.speedup_vs_fastest(group, **options)
        slowdown.to_csv(out(f"speedup_vs_fastest_{suffix}.csv"), index=False)
        with open(out(f"speedup_vs_fastest_{suffix}.tex"), "w") as f:
            f.write(comparisons.slowdown_to_latex(
                slowdown, f"Slowdown of each implementation relative to the fastest implementation of the same query "
                f"type ({geometry} on {computer}): geometric mean of the paired ratios of runtimes, averaged over "
                "tasks, with 95\\,\\% bootstrap confidence intervals. $^{\\approx}$: the typical runtime cannot "
                "be distinguished from the next implementation in the order (the confidence interval of their paired "
                "speedup includes 1).", f"tab:slowdown-{geometry}-{computer}"))
        linear = comparisons.linear_support_slowdown(variants)
        linear.to_csv(out(f"linear_support_{suffix}.csv"), index=False)
        panels.setdefault(computer, []).append((geometry, slowdown, linear))
        figures.probability_heatmaps(comparisons.probability_of_improvement_matrices(group),
                                     out(f"effect_sizes_{suffix}.pdf"))

    # slowdown figures with one panel per geometry (primitives first)
    for computer, computer_panels in panels.items():
        computer_panels.sort(key=lambda p: list(GEOMETRY_TITLES).index(p[0]))
        titles = [GEOMETRY_TITLES[geometry] for geometry, _, _ in computer_panels]
        figures.slowdown_chart([s for _, s, _ in computer_panels], out(f"speedup_vs_fastest_{computer}.pdf"),
                               "Slowdown relative to the fastest implementation", titles)
        linear = [(t, l) for t, (_, _, l) in zip(titles, computer_panels) if len(l) > 0]
        if linear:
            figures.slowdown_chart([l for _, l in linear], out(f"linear_support_{computer}.pdf"),
                                   "Slowdown of the linear support function", [t for t, _ in linear])
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
