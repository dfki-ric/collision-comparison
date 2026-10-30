"""Probability of improvement with stratified bootstrap confidence intervals.

Adapted from rliable (Agarwal et al., 2021, "Deep Reinforcement Learning at the Edge of the Statistical Precipice",
https://github.com/google-research/rliable) for paired measurements: all implementations are measured on the same
test cases, so the runtimes of two implementations on a test case form a pair. rliable compares independent runs
instead.

The probability of improvement of implementation X over implementation Y is the probability that X is faster than Y
on a test case, P(T_X < T_Y). It is computed per task (e.g., per use case or benchmark) and averaged over tasks, so
that every task has the same weight. Confidence intervals are computed with a stratified bootstrap: test cases are
resampled with replacement within each task, and the two runtimes of a test case stay together (as in rliable's
StratifiedBootstrap).
"""
import numpy as np


def _as_tasks(times):
    """A list or tuple of arrays has one array per task, anything else (e.g., one array or pandas Series) is one task."""
    if isinstance(times, (list, tuple)) and len(times) > 0 and np.ndim(times[0]) > 0:
        return [np.asarray(t, dtype=float) for t in times]
    return [np.asarray(times, dtype=float)]


def _wins_per_task(times_x, times_y):
    """Per task: 1 if X is faster than Y on a test case, 0.5 for equal runtimes, 0 if Y is faster.

    Test cases with a missing runtime (NaN) of X or Y are removed.
    """
    tasks_x = _as_tasks(times_x)
    tasks_y = _as_tasks(times_y)
    if len(tasks_x) != len(tasks_y):
        raise ValueError(f"Number of tasks differs: {len(tasks_x)} != {len(tasks_y)}")

    wins_per_task = []
    for task, (x, y) in enumerate(zip(tasks_x, tasks_y)):
        if x.shape != y.shape or x.ndim != 1:
            raise ValueError(f"Task {task}: expected two 1D arrays of the same length, got {x.shape} and {y.shape}")
        valid = ~(np.isnan(x) | np.isnan(y))
        if not np.any(valid):
            raise ValueError(f"Task {task}: no test case with runtimes of both implementations")
        x, y = x[valid], y[valid]
        wins_per_task.append(np.where(x < y, 1.0, np.where(x == y, 0.5, 0.0)))
    return wins_per_task


def probability_of_improvement(times_x, times_y):
    """Probability that implementation X is faster than implementation Y on the same test case.

    Parameters
    ----------
    times_x, times_y : array-like or list of array-like
        Runtimes of X and Y, either one array (one task) or a list with one array per task.
        Element i of both arrays of a task must belong to the same test case.
        Test cases with a missing runtime (NaN) are ignored.

    Returns
    -------
    probability : float
        P(T_X < T_Y) averaged over tasks (equal runtimes count as 0.5).
        Values above 0.5 mean that X tends to be faster.
    """
    return float(np.mean([np.mean(wins) for wins in _wins_per_task(times_x, times_y)]))


def probability_of_improvement_ci(times_x, times_y, n_resamples=5000, confidence_level=0.95, random_state=None):
    """Probability of improvement of X over Y with a stratified paired bootstrap confidence interval.

    Parameters
    ----------
    times_x, times_y : array-like or list of array-like
        See probability_of_improvement().
    n_resamples : int, optional (default: 5000)
        Number of bootstrap resamples.
    confidence_level : float, optional (default: 0.95)
        Confidence level of the percentile interval.
    random_state : int or np.random.Generator, optional
        Seed or random number generator.

    Returns
    -------
    probability : float
        Probability of improvement of X over Y, see probability_of_improvement().
    ci_low, ci_high : float
        Bounds of the percentile bootstrap confidence interval.
    """
    rng = np.random.default_rng(random_state)
    wins_per_task = _wins_per_task(times_x, times_y)

    resampled = np.zeros(n_resamples)
    for wins in wins_per_task:
        # resample test cases within the task, x and y of a test case stay together
        indices = rng.integers(0, len(wins), size=(n_resamples, len(wins)))
        resampled += wins[indices].mean(axis=1)
    resampled /= len(wins_per_task)

    alpha = 1.0 - confidence_level
    ci_low, ci_high = np.percentile(resampled, [100.0 * alpha / 2.0, 100.0 * (1.0 - alpha / 2.0)])
    point = float(np.mean([np.mean(wins) for wins in wins_per_task]))
    return point, float(ci_low), float(ci_high)
