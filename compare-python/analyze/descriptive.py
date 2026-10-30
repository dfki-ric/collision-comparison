"""Descriptive statistics of the runtime distributions: summary table and violin plots."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

LANGUAGE_COLORS = {"C++": "#1b9e77", "Rust": "#d95f02", "Python": "#7570b3"}


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


def violin_plot(long, benchmark, computer, path):
    """Violin plot of the runtime distributions of all implementations in one task (log scale), grouped by category
    and sorted by median, colored by language."""
    task = long[(long["benchmark"] == benchmark) & (long["computer"] == computer)].dropna(subset=["time_us"])
    medians = task.groupby(["category", "label"])["time_us"].median().reset_index()
    medians = medians.sort_values(["category", "time_us"])
    labels = list(medians["label"])
    data = [np.log10(task.loc[task["label"] == label, "time_us"].to_numpy()) for label in labels]
    languages = [task.loc[task["label"] == label, "language"].iloc[0] for label in labels]

    fig, ax = plt.subplots(figsize=(8, 0.35 * len(labels) + 1.5))
    positions = np.arange(len(labels))[::-1]
    parts = ax.violinplot(data, positions=positions, vert=False, widths=0.8, showmedians=True, showextrema=False)
    for body, language in zip(parts["bodies"], languages):
        body.set_facecolor(LANGUAGE_COLORS.get(language, "grey"))
        body.set_edgecolor("black")
        body.set_alpha(0.7)
    parts["cmedians"].set_color("black")
    ax.set_yticks(positions)
    ax.set_yticklabels(labels)
    ticks = np.arange(np.floor(min(d.min() for d in data)), np.ceil(max(d.max() for d in data)) + 1)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"$10^{{{int(t)}}}$" for t in ticks])
    ax.set_xlabel("Time per case file [µs]")
    ax.set_title(f"{benchmark} ({computer})")
    ax.grid(axis="x", alpha=0.3)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, alpha=0.7) for c in LANGUAGE_COLORS.values()]
    ax.legend(handles, LANGUAGE_COLORS.keys(), loc="lower right")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
