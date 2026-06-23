"""Sample uniqueness & weighting for overlapping labels (López de Prado Ch.4).

Triple-barrier labels span multiple bars (``[i, t1[i]]``), so consecutive labels
share outcome windows and are **not** IID — training on them unweighted
over-counts redundant, highly-overlapping observations and inflates the apparent
sample size. This module derives the standard remedies from the per-sample
event-end positions ``t1`` (absolute positions, ``t1[i] >= i``, as produced by
:func:`cpcv.absolute_t1`):

* :func:`get_concurrency` — how many labels are live at each bar;
* :func:`average_uniqueness` — per label, the mean of ``1/concurrency`` over its span;
* :func:`uniqueness_sample_weights` — normalized training weights (mean 1) fed to
  the XGBoost ``DMatrix`` so overlapping labels are down-weighted;
* :func:`sequential_bootstrap` — a bootstrap that favours low-overlap draws, for
  bagged / meta-labelled resampling.

Pure NumPy. With non-overlapping labels (``t1 == arange``) every weight is 1.0,
so the baseline (unweighted) behaviour is recovered exactly.
"""

import numpy as np


def get_concurrency(t1) -> np.ndarray:
    """Number of labels live at each bar: ``c[b] = #{i : i <= b <= t1[i]}``."""
    t1 = np.asarray(t1, dtype=np.int64)
    n = t1.size
    if n == 0:
        return np.zeros(0, dtype=np.float64)
    starts = np.arange(n)
    ends = np.clip(t1, starts, n - 1)
    diff = np.zeros(n + 1, dtype=np.float64)
    np.add.at(diff, starts, 1.0)
    np.add.at(diff, ends + 1, -1.0)
    return np.cumsum(diff)[:n]


def average_uniqueness(t1) -> np.ndarray:
    """Per-label average uniqueness ``u[i] = mean_{b in [i, t1[i]]} 1/c[b]``."""
    t1 = np.asarray(t1, dtype=np.int64)
    n = t1.size
    if n == 0:
        return np.zeros(0, dtype=np.float64)
    concurrency = get_concurrency(t1)
    inv_c = np.where(concurrency > 0.0, 1.0 / concurrency, 0.0)
    prefix = np.concatenate([[0.0], np.cumsum(inv_c)])
    starts = np.arange(n)
    ends = np.clip(t1, starts, n - 1)
    span_sum = prefix[ends + 1] - prefix[starts]
    span_len = (ends - starts + 1).astype(np.float64)
    return span_sum / span_len


def uniqueness_sample_weights(t1) -> np.ndarray:
    """Training weights = average uniqueness, normalized to mean 1.

    Normalizing to mean 1 keeps the total loss scale (and thus the effective
    regularization / learning rate) comparable to the unweighted baseline.
    """
    uniqueness = average_uniqueness(t1)
    if uniqueness.size == 0:
        return uniqueness
    mean = uniqueness.mean()
    return uniqueness / mean if mean > 0.0 else np.ones(uniqueness.size)


def sequential_bootstrap(t1, size: int | None = None, seed: int = 0) -> np.ndarray:
    """Draw ``size`` indices (default ``len(t1)``) favouring low-overlap samples.

    At each step the draw probability of observation ``i`` is proportional to its
    average uniqueness *given the already-drawn set* (1/(1+already-live count)
    over its span), so redundant, highly-overlapping observations are picked less
    often than uniform bootstrap — López de Prado's sequential bootstrap.
    """
    t1 = np.asarray(t1, dtype=np.int64)
    n = t1.size
    if n == 0:
        return np.zeros(0, dtype=np.int64)
    size = n if size is None else size
    rng = np.random.default_rng(seed)
    starts = np.arange(n)
    ends = np.clip(t1, starts, n - 1)
    span_len = (ends - starts + 1).astype(np.float64)
    drawn_concurrency = np.zeros(n, dtype=np.float64)

    drawn = np.empty(size, dtype=np.int64)
    for step in range(size):
        inv = 1.0 / (drawn_concurrency + 1.0)
        prefix = np.concatenate([[0.0], np.cumsum(inv)])
        avg_u = (prefix[ends + 1] - prefix[starts]) / span_len
        probabilities = avg_u / avg_u.sum()
        choice = int(rng.choice(n, p=probabilities))
        drawn[step] = choice
        drawn_concurrency[choice : ends[choice] + 1] += 1.0
    return drawn
