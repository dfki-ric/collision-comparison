"""Descriptive statistics of the runtime distributions (the violin plots are in figures.py)."""
import pandas as pd

from load_results import benchmark_label, format_significant, latex_escape



def summary(long):
    """Median, quartiles, upper quantiles (relevant for real-time applications), mean and maximum per task and
    implementation, in microseconds per case file."""
    def statistics(times):
        times = times.dropna()
        return pd.Series({
            "case_files": len(times),
            "median": times.median(), "q25": times.quantile(0.25), "q75": times.quantile(0.75),
            "q95": times.quantile(0.95), "q99": times.quantile(0.99), "mean": times.mean(), "max": times.max(),
        })
    keys = ["benchmark", "computer", "category", "language", "algorithm", "label"]
    return long.groupby(keys)["time_us"].apply(statistics).unstack().reset_index()


def summary_to_latex(summary_table, benchmark, computer, label):
    """LaTeX table of the summary statistics of one task: implementations grouped by category, sorted by median."""
    task = summary_table[(summary_table["benchmark"] == benchmark) & (summary_table["computer"] == computer)]
    lines = ["\\begin{table}[htbp]", "\\centering", "\\small", "\\begin{tabular}{lrrrrr}", "\\toprule",
             "Implementation & Median & IQR & 95\\,\\% & 99\\,\\% & Max. \\\\"]
    for category in ["Intersection", "Distance"]:
        rows = task[task["category"] == category].sort_values("median")
        if len(rows) == 0:
            continue
        lines += ["\\midrule", f"\\multicolumn{{6}}{{l}}{{\\textit{{{category}}}}} \\\\"]
        for row in rows.itertuples():
            name = latex_escape(row.label.rsplit(" [", 1)[0] if row.label.endswith(("[dist]", "[bool]")) else row.label)
            lines.append(f"{name} & {format_significant(row.median)} & "
                         f"{format_significant(row.q25)}--{format_significant(row.q75)} & "
                         f"{format_significant(row.q95)} & {format_significant(row.q99)} & "
                         f"{format_significant(row.max)} \\\\")
    caption = (f"Time per case file in \\textmu s ({latex_escape(benchmark_label(benchmark))} on "
               f"{latex_escape(computer)}): median, interquartile range (IQR), 95th and 99th percentile, and maximum "
               "over all case files.")
    lines += ["\\bottomrule", "\\end{tabular}", f"\\caption{{{caption}}}", f"\\label{{{label}}}", "\\end{table}"]
    return "\n".join(lines)

