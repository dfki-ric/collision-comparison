"""Analysis of benchmark results: data quality, runtime distributions and pairwise comparisons.

Usage (from compare-python/analyze):
    python run_analysis.py CSV [CSV ...] [--results-dir ../../results] [--output analysis_output]

Every CSV file (written by compile_csv_from_results.py) contains the results of one benchmark on one computer, which
is one task. The comparisons are averaged over all tasks of the given CSV files with equal weight, so the selection
of CSV files determines the aggregation (e.g., only the UR10 use cases, or one computer).

Output files:
- data_quality_missing.csv, data_quality_overhead.csv, data_quality_lag.csv, data_quality_first_run.csv
- summary.csv and violin_<benchmark>_<computer>.pdf
- comparisons_within_language.csv/.tex, comparisons_best_per_language.csv/.tex, comparisons_variants.csv/.tex
"""
import argparse
import os
from pathlib import Path

import data_quality
import descriptive
import comparisons
from load_results import load_results, tasks, to_long


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
    data_quality.missing_results(df).to_csv(out("data_quality_missing.csv"), index=False)
    data_quality.constant_overhead(df, n_resamples=args.resamples, random_state=args.seed).to_csv(
        out("data_quality_overhead.csv"), index=False)
    data_quality.lag_correlation(df).to_csv(out("data_quality_lag.csv"), index=False)
    if args.results_dir is not None:
        data_quality.first_run_effect(args.results_dir).to_csv(out("data_quality_first_run.csv"), index=False)

    # 5. runtime distributions
    long = to_long(df)
    descriptive.summary(long).to_csv(out("summary.csv"), index=False)
    for benchmark, computer in tasks(df):
        descriptive.violin_plot(long, benchmark, computer, out(f"violin_{benchmark}_{computer}.pdf"))

    # 6. pairwise comparisons
    options = {"n_resamples": args.resamples, "random_state": args.seed}
    for name, table, caption in [
        ("within_language", comparisons.within_language(df, **options),
         "Pairwise comparison of implementations of the same language."),
        ("best_per_language", comparisons.best_per_language(df, **options),
         "Pairwise comparison of the fastest implementation of each language."),
        ("variants", comparisons.variants(df, **options),
         "Variants (X) compared to their base implementation (Y)."),
    ]:
        table.to_csv(out(f"comparisons_{name}.csv"), index=False)
        caption += (" Probability of improvement and speedup of X over Y (paired, averaged over tasks)"
                    " with 95\\,\\% bootstrap confidence intervals.")
        with open(out(f"comparisons_{name}.tex"), "w") as f:
            f.write(comparisons.to_latex(table, caption, f"tab:comparisons-{name.replace('_', '-')}"))
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
