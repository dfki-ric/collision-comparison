"""Paired speedup with stratified bootstrap confidence intervals.

The speedup of implementation X over implementation Y is the geometric mean of the time ratios T_Y / T_X on the same
test cases. It is computed per task (e.g., per benchmark) and averaged over tasks with equal weight (geometric mean),
like the probability of improvement. Confidence intervals are computed with the same stratified paired bootstrap:
test cases are resampled with replacement within each task, and the two runtimes of a test case stay together.
"""
import numpy as np

from probability_of_improvement import _as_tasks


def _log_ratios_per_task(times_x, times_y):
    """Per task: log(T_Y / T_X) for all test cases with runtimes of both implementations."""
    tasks_x = _as_tasks(times_x)
    tasks_y = _as_tasks(times_y)
    if len(tasks_x) != len(tasks_y):
        raise ValueError(f"Number of tasks differs: {len(tasks_x)} != {len(tasks_y)}")

    log_ratios_per_task = []
    for task, (x, y) in enumerate(zip(tasks_x, tasks_y)):
        if x.shape != y.shape or x.ndim != 1:
            raise ValueError(f"Task {task}: expected two 1D arrays of the same length, got {x.shape} and {y.shape}")
        valid = ~(np.isnan(x) | np.isnan(y))
        if not np.any(valid):
            raise ValueError(f"Task {task}: no test case with runtimes of both implementations")
        if np.any(x[valid] <= 0) or np.any(y[valid] <= 0):
            raise ValueError(f"Task {task}: runtimes must be positive")
        log_ratios_per_task.append(np.log(y[valid]) - np.log(x[valid]))
    return log_ratios_per_task


def speedup(times_x, times_y):
    """Speedup of implementation X over implementation Y (geometric mean of T_Y / T_X).

    Parameters
    ----------
    times_x, times_y : array-like or list of array-like
        Runtimes of X and Y, either one array (one task) or a list with one array per task.
        Element i of both arrays of a task must belong to the same test case.
        Test cases with a missing runtime (NaN) are ignored.

    Returns
    -------
    speedup : float
        Values above 1 mean that X is faster, e.g., 2 means that Y needs twice as long.
    """
    return float(np.exp(np.mean([np.mean(r) for r in _log_ratios_per_task(times_x, times_y)])))


def speedup_ci(times_x, times_y, n_resamples=5000, confidence_level=0.95, random_state=None):
    """Speedup of X over Y with a stratified paired bootstrap confidence interval.

    Parameters
    ----------
    times_x, times_y : array-like or list of array-like
        See speedup().
    n_resamples : int, optional (default: 5000)
        Number of bootstrap resamples.
    confidence_level : float, optional (default: 0.95)
        Confidence level of the percentile interval.
    random_state : int or np.random.Generator, optional
        Seed or random number generator.

    Returns
    -------
    speedup : float
        Speedup of X over Y, see speedup().
    ci_low, ci_high : float
        Bounds of the percentile bootstrap confidence interval.
    """
    rng = np.random.default_rng(random_state)
    log_ratios_per_task = _log_ratios_per_task(times_x, times_y)

    resampled = np.zeros(n_resamples)
    for log_ratios in log_ratios_per_task:
        indices = rng.integers(0, len(log_ratios), size=(n_resamples, len(log_ratios)))
        resampled += log_ratios[indices].mean(axis=1)
    resampled /= len(log_ratios_per_task)

    alpha = 1.0 - confidence_level
    ci_low, ci_high = np.exp(np.percentile(resampled, [100.0 * alpha / 2.0, 100.0 * (1.0 - alpha / 2.0)]))
    point = float(np.exp(np.mean([np.mean(r) for r in log_ratios_per_task])))
    return point, float(ci_low), float(ci_high)
