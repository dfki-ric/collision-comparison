"""Figures for the paper: runtime distributions, slowdown charts and heatmaps of the probability of improvement.

All figures share one print style: no titles (captions belong to the paper), no frames, recessive axes, and direct
labels instead of legends where possible.

Every figure is written twice: as PDF (vector graphics for LaTeX) and as TIFF for the submission to Frontiers, which
accepts TIFF, JPEG and EPS (RGB, 300 dpi at final size), but not PDF. Figures are made at their final size (at most
180 mm wide, the width of two columns) with text of at least 8 pt, so they must be included without scaling. Figures
with two panels (e.g., primitives and meshes) are one file with the panels A and B, as required for the submission.
"""
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.textpath import TextPath
from matplotlib.ticker import FixedFormatter, FixedLocator, LogLocator, NullFormatter

from algo_metadata import algo_metadata
from load_results import benchmark_label

# Languages: first three slots of a colorblind-safe categorical palette, plus a marker per language so that the
# language is not encoded by color alone.
LANGUAGE_COLORS = {"C++": "#2a78d6", "Rust": "#eb6834", "Python": "#1baf7a"}
LANGUAGE_MARKERS = {"C++": "o", "Rust": "s", "Python": "^"}
TEXT = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
AXIS = "#898781"
GRID = "#e6e5e1"
# Diverging red (row tends to be slower) - neutral gray (equally fast) - blue (row tends to be faster)
PROBABILITY_CMAP = LinearSegmentedColormap.from_list("poi", ["#e34948", "#f0efec", "#2a78d6"])
CATEGORIES = ["Intersection", "Distance"]

STYLE = {
    "font.size": 8,
    "font.family": "sans-serif",
    "axes.edgecolor": AXIS,
    "axes.linewidth": 0.6,
    "axes.labelcolor": TEXT_SECONDARY,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.titlecolor": TEXT,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "xtick.color": AXIS,
    "xtick.labelcolor": TEXT_SECONDARY,
    "xtick.major.width": 0.6,
    "xtick.minor.width": 0.4,
    "xtick.major.size": 3,
    "xtick.minor.size": 1.5,
    "ytick.left": False,
    "ytick.labelcolor": TEXT,
    "legend.frameon": False,
    "legend.fontsize": 8,
    "pdf.fonttype": 42,  # embed TrueType fonts (editable text in the PDF)
}
SUBMISSION_DPI = 300
PNG_DPI = 150
FULL_WIDTH = 177 / 25.4  # inch: two columns in Frontiers journals are 180 mm, labels may extend the figure slightly
PANEL_LABEL_SIZE = 10


def _save(fig, path):
    """Save the figure as PDF at path, as RGB TIFF (LZW-compressed, 300 dpi) and as PNG (150 dpi, for READMEs) next to
    it, and close it."""
    path = Path(path)
    options = {"bbox_inches": "tight", "pad_inches": 0.02, "facecolor": "white"}
    fig.savefig(path, **options)
    fig.savefig(path.with_suffix(".png"), dpi=PNG_DPI, **options)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=SUBMISSION_DPI, **options)
    plt.close(fig)
    buffer.seek(0)
    with Image.open(buffer) as image:
        image.convert("RGB").save(path.with_suffix(".tif"), compression="tiff_lzw",
                                  dpi=(SUBMISSION_DPI, SUBMISSION_DPI))


def _language_legend(fig, languages):
    """Legend of the languages above the panels of a figure, right-aligned (none for a single language)."""
    languages = [l for l in LANGUAGE_COLORS if l in set(languages)]
    if len(languages) < 2:
        return
    handles = [Line2D([], [], color=LANGUAGE_COLORS[l], marker=LANGUAGE_MARKERS[l], linestyle="", markersize=5)
               for l in languages]
    fig.legend(handles, languages, loc="outside upper right", ncol=len(languages), handletextpad=0.1,
               columnspacing=1.2, borderaxespad=0.0, labelcolor=TEXT_SECONDARY)


def _text_width(text, size=8, weight="normal"):
    """Width of a text in inches (for layouts in inches)."""
    prop = FontProperties(family=STYLE["font.family"], size=size, weight=weight)
    return TextPath((0, 0), text, prop=prop).get_extents().width / 72.0


def _panel_figure(n_panels, height):
    """Figure of full width (two columns) with n_panels side-by-side subfigures, labeled A, B, ... if n_panels > 1."""
    fig = plt.figure(figsize=(FULL_WIDTH, height), layout="constrained")
    if n_panels == 1:
        return fig, [fig]
    panels = list(np.atleast_1d(fig.subfigures(1, n_panels, wspace=0.03)))
    for letter, panel in zip("ABCDEFGH", panels):
        panel.suptitle(letter, x=0.0, ha="left", fontsize=PANEL_LABEL_SIZE, fontweight="bold", color=TEXT)
    return fig, panels


def _category_axes(container, table):
    """One panel per category (intersection above distance) in a figure or subfigure, with heights proportional to
    the number of rows."""
    categories = [c for c in CATEGORIES if c in set(table["category"])]
    heights = [len(table[table["category"] == c]) for c in categories]
    axes = container.subplots(len(categories), 1, sharex=True, squeeze=False,
                              gridspec_kw={"height_ratios": heights})
    return categories, axes[:, 0]


def _category_height(tables, row_height):
    """Figure height for the largest of the tables (rows of all categories plus titles and the x axis)."""
    rows = max(len(t) for t in tables)
    n_categories = max(len(set(t["category"])) for t in tables)
    return row_height * rows + 0.35 * n_categories + 0.5


def _decade_ticks(low, high):
    """Labeled ticks of a log axis from 10^low to 10^high: every decade, every second decade for more than six
    decades, and 1, 2, 5 times a decade for less than one and a half decades."""
    decades = np.arange(np.ceil(low), np.floor(high) + 1)
    if high - low < 1.5:
        ticks = np.log10(np.outer(10.0 ** np.arange(np.floor(low), np.ceil(high) + 1), [1, 2, 5]).ravel())
        return [t for t in ticks if low <= t <= high]
    step = 2 if len(decades) > 7 else 1
    return list(decades[decades % step == 0])


def _tick_label(exponent):
    if float(exponent).is_integer():
        return f"$10^{{{int(exponent)}}}$"
    return f"{10.0 ** exponent:.2g}"


def _decade_axis(ax, low, high, label, axis_high=None):
    """Log x axis (data in linear units) with labeled ticks (see _decade_ticks()) and unlabeled minor ticks.

    axis_high : float, optional
        End of the axis line and the ticks if the axis extends beyond the data (space for labels), default: high
    """
    ax.set_xscale("log")
    axis_high = high if axis_high is None else axis_high
    ticks = _decade_ticks(np.log10(low), np.log10(axis_high))
    ax.xaxis.set_major_locator(FixedLocator(10.0 ** np.array(ticks)))
    ax.xaxis.set_major_formatter(FixedFormatter([_tick_label(t) for t in ticks]))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10)))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlim(low, high)
    if axis_high < high:
        ax.xaxis.set_minor_locator(FixedLocator([t for t in ax.xaxis.get_minor_locator().tick_values(low, axis_high)
                                                 if t <= axis_high]))
        ax.spines["bottom"].set_bounds(low, axis_high)
    ax.set_xlabel(label, loc="right")


def _format_factor(value, unit="×"):
    """Three significant digits (with trailing zeros, except for exactly 1), no decimals from 100."""
    if value >= 100:
        return f"{value:.0f}{unit}"
    return f"{value:#.3g}{unit}" if value != 1 else f"1{unit}"


def slowdown_chart(tables, path, xlabel, titles=None):
    """Dot chart of slowdown factors (log scale), one panel per category. The confidence intervals are not shown
    (they are mostly narrower than the markers, see comparisons.slowdown_to_latex()); a bracket joins implementations
    whose typical runtimes cannot be distinguished (column tie_with_next, optional).

    tables : DataFrame or list of DataFrames (one panel A, B, ... per table) with the columns category, label,
    language, slowdown, and optionally tie_with_next (see comparisons.speedup_vs_fastest() and
    comparisons.linear_support_slowdown()).
    titles : list of str, optional
        Title of each panel, e.g., the geometry.
    """
    tables = [tables] if isinstance(tables, pd.DataFrame) else list(tables)
    with plt.rc_context(STYLE):
        fig, panels = _panel_figure(len(tables), _category_height(tables, row_height=0.17))
        panel_labels = []
        for k, (panel, table) in enumerate(zip(panels, tables)):
            categories, axes = _category_axes(panel, table)
            labels = []
            for ax, category in zip(axes, categories):
                rows = table[table["category"] == category].sort_values("slowdown", ascending=False)
                y = np.arange(len(rows))
                row_labels = []
                for yi, row in zip(y, rows.itertuples()):
                    color = LANGUAGE_COLORS[row.language]
                    ax.plot(row.slowdown, yi, marker=LANGUAGE_MARKERS[row.language], color=color, markersize=4,
                            linestyle="")
                    label = ax.annotate(_format_factor(row.slowdown), (row.slowdown, yi), xytext=(4, 0),
                                        textcoords="offset points", va="center", color=TEXT_SECONDARY)
                    # the labels are fitted into the axes below instead of shrinking the axes
                    label.set_in_layout(False)
                    row_labels.append(label)
                    labels.append((ax, label, row.slowdown))
                # rows are sorted from slow (bottom) to fast (top): a tie of a row with the next slower one is a
                # bracket to the label of the row below
                ties = rows["tie_with_next"].to_numpy() if "tie_with_next" in rows else np.zeros(len(rows), bool)
                for i in range(1, len(rows)):
                    if ties[i]:
                        bracket = ax.annotate("", xy=(1.0, 0.5), xycoords=row_labels[i], xytext=(1.0, 0.5),
                                              textcoords=row_labels[i - 1],
                                              arrowprops={"arrowstyle": "-", "color": TEXT_SECONDARY,
                                                          "linewidth": 0.9, "shrinkA": 2, "shrinkB": 2,
                                                          "connectionstyle": "bar,fraction=0.3"})
                        bracket.set_in_layout(False)
                ax.axvline(1.0, color=AXIS, linewidth=0.6, zorder=0)
                ax.set_yticks(y, rows["label"])
                ax.set_ylim(-0.7, len(rows) - 0.3)
                ax.set_title(category if titles is None or ax is not axes[0] else f"{titles[k]}: {category}")
                ax.tick_params(axis="x", which="both", bottom=ax is axes[-1])
                ax.spines["bottom"].set_visible(ax is axes[-1])
            _decade_axis(axes[-1], 0.8, table["slowdown"].max() * 4.0, xlabel)
            panel_labels.append((axes[-1], labels))
        _language_legend(fig, set().union(*(set(t["language"]) for t in tables)))
        _fit_labels(fig, panel_labels, 0.8, xlabel)
        _save(fig, path)


def _fit_labels(fig, panel_labels, low, xlabel):
    """Extend the log x axis of each panel so that the value labels next to the points end inside the axes.

    panel_labels : list of (axis with the x label, list of (axis, label, x of the point))"""
    fig.draw_without_rendering()
    for x_axis, labels in panel_labels:
        # the axis line ends at the first decade above the data, the labels extend further
        axis_high = 10.0 ** np.ceil(np.log10(max(x for _, _, x in labels)))
        decades = np.log10(x_axis.get_xlim()[1] / low)
        for ax, label, x in labels:
            width = ax.get_window_extent().width
            # label and space for a bracket of a tie
            label_width = label.get_window_extent().x1 - ax.transData.transform((x, 0))[0] + 10 * fig.dpi / 72.0
            # position of the point (fraction of the axis) at which the label ends at 98 % of the axis
            fraction = (0.98 * width - label_width) / width
            if fraction > 0:
                decades = max(decades, np.log10(x / low) / fraction)
        axis_high = max(axis_high, low * 10.0)
        _decade_axis(x_axis, low, low * 10.0 ** decades, xlabel, axis_high=axis_high)
        # label only the first and the last decade if the decades are too narrow for their labels (points)
        if x_axis.get_window_extent().width / decades * 72.0 / fig.dpi < 20:
            ticks = [0.0, np.log10(axis_high)]
            x_axis.xaxis.set_major_locator(FixedLocator(10.0 ** np.array(ticks)))
            x_axis.xaxis.set_major_formatter(FixedFormatter([_tick_label(t) for t in ticks]))


def slowdown_by_query_chart(tables, path, xlabel):
    """Dot chart of slowdown factors (log scale) with one panel per category (A: intersection, B: distance) and one
    column per geometry. The columns share the implementation axis, ordered by the first table, so that the rows can
    be compared across geometries. Brackets at the right edge of a column join implementations whose typical runtimes
    cannot be distinguished (tie_with_next with the next slower implementation of that geometry, which is not
    necessarily the next row).

    tables : list of (title, DataFrame) with the columns category, label, language, slowdown, tie_with_next (see
        comparisons.speedup_vs_fastest()), one column per table
    """
    panels = []
    for category in CATEGORIES:
        rows = [table[table["category"] == category] for _, table in tables]
        order = rows[0].sort_values("slowdown")["label"].tolist()
        order += sorted(set().union(*(set(r["label"]) for r in rows)) - set(order))
        panels.append((category, rows, order))
    row_height = 0.165
    heights = [len(order) * row_height + 0.45 for _, _, order in panels]
    with plt.rc_context(STYLE):
        fig = plt.figure(figsize=(FULL_WIDTH, sum(heights) + 0.5), layout="constrained")
        subfigs = fig.subfigures(len(panels), 1, height_ratios=heights, hspace=0.04)
        for letter, subfig, (category, rows, order) in zip("ABCDEFGH", subfigs, panels):
            subfig.suptitle(f"{letter}  {category}", x=0.0, ha="left", fontsize=PANEL_LABEL_SIZE, fontweight="bold",
                            color=TEXT)
            axes = subfig.subplots(1, len(tables), sharey=True, squeeze=False)[0]
            y = {label: i for i, label in enumerate(order)}
            for k, (ax, (title, _), table) in enumerate(zip(axes, tables, rows)):
                for i in range(0, len(order), 2):
                    ax.axhspan(i - 0.5, i + 0.5, color=GRID, alpha=0.45, linewidth=0, zorder=-1)
                for row in table.itertuples():
                    ax.plot(row.slowdown, y[row.label], marker=LANGUAGE_MARKERS[row.language],
                            color=LANGUAGE_COLORS[row.language], markersize=4, linestyle="")
                    ax.annotate(_format_factor(row.slowdown), (row.slowdown, y[row.label]), xytext=(4, 0),
                                textcoords="offset points", va="center", color=TEXT_SECONDARY)
                for label in sorted(set(order) - set(table["label"])):  # not benchmarked with this geometry
                    ax.annotate("n/a", (0.02, y[label]), xycoords=("axes fraction", "data"), va="center", color=AXIS)
                # brackets of ties, moved to the left if they overlap
                ordered = table.sort_values("slowdown")
                brackets = []
                for faster, slower in zip(ordered.itertuples(), ordered.iloc[1:].itertuples()):
                    if not faster.tie_with_next:
                        continue
                    low, high = sorted((y[faster.label], y[slower.label]))
                    x = 0.98 - 0.04 * sum(1 for l, h in brackets if l <= high and low <= h)
                    brackets.append((low, high))
                    ax.plot([x - 0.025, x, x, x - 0.025], [low, low, high, high], transform=ax.get_yaxis_transform(),
                            color=TEXT_SECONDARY, linewidth=0.9, clip_on=False)
                ax.axvline(1.0, color=AXIS, linewidth=0.6, zorder=0)
                ax.set_title(title, loc="left")
                # the same axis in all columns: 1 to 10^4, with space for the labels of the points
                _decade_axis(ax, 0.8, 2.5e4, xlabel if k == len(tables) - 1 else "", axis_high=1e4)
                ax.set_ylim(len(order) - 0.5, -0.5)
            axes[0].set_yticks(range(len(order)), order)
        _language_legend(fig, set().union(*(set(t["language"]) for _, t in tables)))
        _save(fig, path)


def _task_medians(long, benchmarks, computer):
    """Runtimes and medians of one benchmark or of several benchmarks together (list)."""
    benchmarks = [benchmarks] if isinstance(benchmarks, str) else benchmarks
    task = long[long["benchmark"].isin(benchmarks) & (long["computer"] == computer)].dropna(subset=["time_us"])
    medians = task.groupby(["category", "algorithm", "language"])["time_us"].median().reset_index()
    medians["label"] = medians["algorithm"].map(lambda a: algo_metadata[a].pretty_name)
    return task, medians


def violin_plot(long, tasks, path, titles=None):
    """Runtime distributions of all implementations in a task (log scale), one panel per category, sorted by median
    and colored by language.

    tasks : (benchmark, computer) or list of (benchmark, computer), one panel A, B, ... per task. The benchmark can
        also be a list of benchmarks: the case files of all of them are shown together.
    titles : list of str, optional
        Title of each panel, e.g., the benchmark.
    """
    tasks = [tasks] if isinstance(tasks, tuple) else list(tasks)
    data = [_task_medians(long, benchmark, computer) for benchmark, computer in tasks]
    with plt.rc_context(STYLE):
        fig, panels = _panel_figure(len(tasks), _category_height([m for _, m in data], row_height=0.2))
        for k, (panel, (task, medians)) in enumerate(zip(panels, data)):
            categories, axes = _category_axes(panel, medians)
            for ax, category in zip(axes, categories):
                rows = medians[medians["category"] == category].sort_values("time_us", ascending=False)
                y = np.arange(len(rows))
                times = [np.log10(task.loc[task["algorithm"] == a, "time_us"].to_numpy())
                         for a in rows["algorithm"]]
                parts = ax.violinplot(times, positions=y, vert=False, widths=0.85, showextrema=False)
                for body, language in zip(parts["bodies"], rows["language"]):
                    body.set_facecolor(LANGUAGE_COLORS[language])
                    body.set_edgecolor("none")
                    body.set_alpha(0.75)
                ax.plot(np.log10(rows["time_us"]), y, linestyle="", marker="|", markersize=6, markeredgewidth=1.2,
                        color="white")
                ax.set_yticks(y, rows["label"])
                ax.set_ylim(-0.7, len(rows) - 0.3)
                ax.set_title(category if titles is None or ax is not axes[0] else f"{titles[k]}: {category}")
                ax.tick_params(axis="x", which="both", bottom=ax is axes[-1])
                ax.spines["bottom"].set_visible(ax is axes[-1])
            all_times = np.log10(task["time_us"].to_numpy())
            low, high = np.floor(all_times.min()), np.ceil(all_times.max())
            ticks = _decade_ticks(low, high)
            axes[-1].xaxis.set_major_locator(FixedLocator(ticks))
            axes[-1].xaxis.set_minor_locator(
                FixedLocator(np.log10(np.outer(10.0 ** np.arange(low, high), np.arange(1, 10)).ravel())))
            axes[-1].set_xticklabels([_tick_label(t) for t in ticks])
            axes[-1].set_xlim(low, high)
            axes[-1].set_xlabel("Time per case file [µs] (white: median)", loc="right")
        _language_legend(fig, set().union(*(set(m["language"]) for _, m in data)))
        _save(fig, path)


def _format_probability(value):
    """Probability in percent without decimals (fits into a heatmap cell at 8 pt); 100 and 0 only for exact values."""
    text = f"{100.0 * value:.0f}"
    if text == "100" and value < 1.0:
        return ">99"
    if text == "0" and value > 0.0:
        return "<1"
    return text


def probability_heatmaps(matrices, path):
    """Heatmaps of P(T_row < T_column), one panel per category and language (see
    comparisons.probability_of_improvement_matrices()).

    Implementations are sorted from fast to slow, and only the upper triangle is shown: the lower triangle is
    redundant, P(T_column < T_row) = 1 - P(T_row < T_column). The panel title is placed above the row labels.
    Panels are placed in inches, so that all cells have the same size, with margins for the row labels (left) and the
    vertical column labels (top) of each panel."""
    if not matrices:
        return
    cell, gap = 0.28, 0.14  # inch
    panels = list(matrices.items())
    n_cols = min(2, len(panels))
    n_rows = int(np.ceil(len(panels) / n_cols))
    sizes, lefts, tops = np.zeros((n_rows, n_cols)), np.zeros((n_rows, n_cols)), np.zeros((n_rows, n_cols))
    for k, ((category, language), matrix) in enumerate(panels):
        r, c = divmod(k, n_cols)
        sizes[r, c] = len(matrix) - 1
        # the left margin holds the row labels and the title (top left corner)
        lefts[r, c] = max([_text_width(label) for label in matrix.index[:-1]]
                          + [_text_width(f"{category}, {language}", weight="bold")]) + 0.08
        tops[r, c] = max(_text_width(label) for label in matrix.columns[1:]) + 0.08
    left, top = lefts.max(axis=0), tops.max(axis=1)
    widths, heights = left + cell * sizes.max(axis=0) + gap, top + cell * sizes.max(axis=1) + gap
    note_height = 0.2
    fig_width, fig_height = widths.sum() - gap, heights.sum() - gap + note_height
    with plt.rc_context(STYLE):
        fig = plt.figure(figsize=(fig_width, fig_height))
        for k, ((category, language), matrix) in enumerate(panels):
            r, c = divmod(k, n_cols)
            n = len(matrix) - 1
            x0 = widths[:c].sum() + left[c]
            y0 = fig_height - heights[:r].sum() - top[r] - cell * n
            ax = fig.add_axes((x0 / fig_width, y0 / fig_height, cell * n / fig_width, cell * n / fig_height))
            upper = matrix.iloc[:-1, 1:].to_numpy(dtype=float)
            upper[np.tril_indices(n, -1)] = np.nan
            ax.pcolormesh(np.ma.masked_invalid(upper), cmap=PROBABILITY_CMAP, vmin=0, vmax=1,
                          edgecolors="white", linewidth=1.2)
            for i in range(n):
                for j in range(i, n):
                    value = upper[i, j]
                    ax.text(j + 0.5, i + 0.5, _format_probability(value), ha="center", va="center",
                            color="white" if abs(value - 0.5) > 0.3 else TEXT)
            ax.set_xlim(0, n)
            ax.set_ylim(n, 0)
            ax.xaxis.tick_top()
            ax.set_xticks(np.arange(n) + 0.5, matrix.columns[1:], rotation=90)
            ax.set_yticks(np.arange(n) + 0.5, matrix.index[:-1])
            ax.tick_params(axis="both", length=0, labelcolor=TEXT, pad=2)
            ax.spines["bottom"].set_visible(False)
            # title in the top left corner of the heatmap: above the row labels, left of the column labels
            fig.text((x0 - 0.04) / fig_width, (y0 + cell * n + 0.06) / fig_height,
                     f"{category}, {language}", ha="right", va="bottom", fontweight="bold", color=TEXT)
        fig.text(0.0, 0.0, "Cell: probability (%) that the row implementation is faster than the column implementation.",
                 color=TEXT_SECONDARY, va="bottom")
        _save(fig, path)


def first_run_plot(first_run, path):
    """Time of the k-th measured run relative to the median of the runs of a case file (mean over case files), one
    panel per benchmark and one line per implementation (see data_quality.first_run_effect())."""
    if len(first_run) == 0:
        return
    run_columns = [c for c in first_run.columns if c.startswith("run_")]
    runs = np.arange(1, len(run_columns) + 1)
    benchmarks = list(dict.fromkeys(first_run["benchmark"]))
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, len(benchmarks), sharey=True, squeeze=False, figsize=(FULL_WIDTH, 2.0),
                                 layout="constrained")
        for ax, benchmark in zip(axes[0], benchmarks):
            rows = first_run[first_run["benchmark"] == benchmark]
            for row in rows.itertuples(index=False):
                meta = algo_metadata.get(row.algorithm)
                color = LANGUAGE_COLORS[meta.language.value] if meta else AXIS
                ax.plot(runs, [getattr(row, c) for c in run_columns], color=color, linewidth=0.8, alpha=0.6)
            ax.axhline(1.0, color=AXIS, linewidth=0.6, zorder=0)
            ax.set_title(benchmark_label(benchmark))
            ax.set_xticks([1, runs[-1]])
            ax.set_xlabel("Measured run")
        axes[0, 0].spines["left"].set_visible(True)
        axes[0, 0].tick_params(axis="y", left=True, labelcolor=TEXT_SECONDARY)
        axes[0, 0].set_ylabel("Time / median")
        _language_legend(fig, [algo_metadata[a].language.value for a in first_run["algorithm"] if a in algo_metadata])
        _save(fig, path)
