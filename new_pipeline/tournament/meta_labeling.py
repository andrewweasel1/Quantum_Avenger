"""Meta-labeling — a secondary act/size model on the primary signal (offense roadmap P3).

López de Prado Ch.3: the primary model fixes the *side* (here the per-sector booster's
``P(win) > confidence_threshold`` ⇒ a long/flat signal); a secondary "meta" model,
trained **only on the bars where the primary fired**, predicts whether that bet is a
true win (its triple-barrier outcome). Acting only when the primary fires **and** the
meta model is confident raises **precision** (kills false positives) at some recall —
and the meta probability is a natural bet size.

Adopt the meta filter only if it beats the primary out-of-sample (F1 or precision).
The training step is injected as a ``fit_proba_fn`` so the evaluation logic here stays
pure/offline and deterministic; the director supplies an XGBoost-backed fit that reuses
the same uniqueness weights as the primary. See ``docs/OFFENSE_ROADMAP.md`` (P3) and
``docs/quantitative_math.md`` Part II §G.
"""

from dataclasses import dataclass

import numpy as np

MIN_FIRED_TRAIN = 8  # need enough fired training bars to learn the meta filter
MIN_FIRED_TEST = 3  # and enough fired test bars to evaluate it


def primary_signal(proba, threshold) -> np.ndarray:
    """Primary act/flat signal: 1 where P(win) exceeds the confidence threshold."""
    return (np.asarray(proba, dtype=np.float64) > threshold).astype(np.int64)


def precision_recall_f1(y_true, y_pred) -> tuple[float, float, float]:
    """Precision / recall / F1 for the positive (acted-and-won) class."""
    truth = np.asarray(y_true) > 0.5
    pred = np.asarray(y_pred) > 0.5
    tp = int(np.sum(pred & truth))
    fp = int(np.sum(pred & ~truth))
    fn = int(np.sum(~pred & truth))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


@dataclass(frozen=True)
class MetaVerdict:
    """Primary-alone vs. meta-filtered, scored out-of-sample (all reporting-only)."""

    precision_primary: float
    recall_primary: float
    f1_primary: float
    precision_meta: float
    recall_meta: float
    f1_meta: float
    improved: bool


def meta_filtered_signal(primary_test_signal, meta_proba_test, meta_threshold) -> np.ndarray:
    """Final signal: act only where the primary fired AND meta P(win) > threshold."""
    fired = np.asarray(primary_test_signal) == 1
    confident = np.asarray(meta_proba_test, dtype=np.float64) > meta_threshold
    return (fired & confident).astype(np.int64)


def evaluate_meta_labeling(
    test_outcomes, test_primary_signal, meta_proba_test, meta_threshold=0.5, criterion="f1"
) -> MetaVerdict:
    """Score primary-alone vs. the meta-filtered signal on the OOS test split.

    ``test_outcomes`` are triple-barrier results (1=win). ``improved`` is True when the
    chosen ``criterion`` (``"f1"`` | ``"precision"``) rises; for precision we also
    require recall to stay positive so an empty filter is never counted as a win.
    """
    p_p, r_p, f_p = precision_recall_f1(test_outcomes, test_primary_signal)
    meta_signal = meta_filtered_signal(test_primary_signal, meta_proba_test, meta_threshold)
    p_m, r_m, f_m = precision_recall_f1(test_outcomes, meta_signal)
    improved = (p_m > p_p and r_m > 0.0) if criterion == "precision" else f_m > f_p
    return MetaVerdict(p_p, r_p, f_p, p_m, r_m, f_m, improved)


def run_meta_labeling(
    train_x,
    train_outcomes,
    test_x,
    test_outcomes,
    train_primary_signal,
    test_primary_signal,
    fit_proba_fn,
    meta_threshold=0.5,
    criterion="f1",
    weights=None,
    min_fired_train=MIN_FIRED_TRAIN,
    min_fired_test=MIN_FIRED_TEST,
):
    """Train the meta model on the fired training subset and evaluate vs. the primary.

    ``fit_proba_fn(X, y, sample_weight) -> (predict: X -> proba)`` trains the secondary
    classifier. Returns ``(MetaVerdict, meta_predict)`` or ``None`` when the fired
    subsets are too thin, or the fired outcomes are single-class, to meta-label.
    """
    train_mask = np.asarray(train_primary_signal) == 1
    n_fired_test = int(np.sum(np.asarray(test_primary_signal) == 1))
    fired_y = np.asarray(train_outcomes)[train_mask]
    if (
        int(train_mask.sum()) < min_fired_train
        or n_fired_test < min_fired_test
        or np.unique(fired_y).size < 2  # meta needs both wins and losses to learn
    ):
        return None
    weight = None if weights is None else np.asarray(weights)[train_mask]
    meta_predict = fit_proba_fn(np.asarray(train_x)[train_mask], fired_y, weight)
    verdict = evaluate_meta_labeling(
        test_outcomes, test_primary_signal, meta_predict(test_x), meta_threshold, criterion
    )
    return verdict, meta_predict
