"""Event-time family: filing clock/drift + news burst (causal, neutral-filled)."""

from datetime import date, timedelta
from types import SimpleNamespace

import numpy as np
import polars as pl
from new_pipeline.features.event_time import (
    FILING_CLOCK_CAP_DAYS,
    add_filing_event_features,
    add_news_burst,
)


def _weekdays(n, start=date(2021, 1, 4)):
    days, d = [], start
    while len(days) < n:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days


def _filing_frame(returns_by_ticker, as_of_by_ticker):
    rows = []
    for ticker, rets in returns_by_ticker.items():
        days = _weekdays(len(rets))
        for i, (day, r) in enumerate(zip(days, rets, strict=True)):
            rows.append({"date": day, "ticker": ticker, "returns": r,
                         "as_of": as_of_by_ticker[ticker](i, day)})
    return pl.DataFrame(rows).with_columns(pl.col("as_of").cast(pl.Date))


def test_filing_clock_exact_and_prefiling_fill():
    r_a = [0.0, 0.01, 0.02, -0.01, 0.005, 0.01, -0.02, 0.03, 0.0, 0.01]
    r_b = [0.02] * 10
    days = _weekdays(10)
    frame = _filing_frame(
        {"A": r_a, "B": r_b},
        {"A": lambda i, d: days[3] if i >= 3 else None,  # files on day idx 3
         "B": lambda i, d: days[2] if i >= 2 else None},
    )
    out = add_filing_event_features(frame)
    a = out.filter(pl.col("ticker") == "A").sort("date")
    cumlog = np.cumsum(np.log1p(r_a))
    # filing day itself: clock at 0, no drift yet
    assert a["days_since_filing"][3] == 0.0 and a["ret_since_filing"][3] == 0.0
    assert a["days_since_filing"][4] == 1.0  # Fri after Thu filing
    assert a["days_since_filing"][5] == 4.0  # Mon: calendar days, not trading days
    np.testing.assert_allclose(
        a["ret_since_filing"][5], np.exp(cumlog[5] - cumlog[3]) - 1.0, rtol=1e-12
    )
    # pre-filing rows neutral-fill instead of nulling (drop_nulls survival)
    assert a["days_since_filing"][:3].to_list() == [FILING_CLOCK_CAP_DAYS] * 3
    assert a["ret_since_filing"][:3].to_list() == [0.0] * 3
    # per-ticker isolation: B anchors to its own day-2 filing
    b = out.filter(pl.col("ticker") == "B").sort("date")
    np.testing.assert_allclose(b["ret_since_filing"][4], 1.02**2 - 1.0, rtol=1e-12)
    assert "as_of" not in out.columns


def test_filing_weekend_anchor_rolls_back_to_prior_close():
    rets = [0.0, 0.01, 0.02, -0.01, 0.005, 0.01, -0.02, 0.03, 0.0, 0.01]
    days = _weekdays(10)
    saturday = date(2021, 1, 9)  # between days[4] (Fri 8th) and days[5] (Mon 11th)
    frame = _filing_frame(
        {"A": rets}, {"A": lambda i, d: saturday if i >= 5 else None}
    )
    out = add_filing_event_features(frame).sort("date")
    assert out["days_since_filing"][5] == 2.0  # Mon 11th minus Sat 9th
    np.testing.assert_allclose(out["ret_since_filing"][5], rets[5], rtol=1e-12)
    assert days[5] - saturday == timedelta(days=2)


def test_filing_stale_clips_to_cap_and_unanchored_drift_is_zero():
    frame = _filing_frame(
        {"A": [0.01] * 6}, {"A": lambda i, d: date(2019, 1, 1)}  # ~2y before history
    )
    out = add_filing_event_features(frame).sort("date")
    assert (out["days_since_filing"].to_numpy() == FILING_CLOCK_CAP_DAYS).all()
    assert (out["ret_since_filing"].to_numpy() == 0.0).all()  # anchor precedes history


def test_news_burst_exact_warmup_and_null_fill():
    days = _weekdays(30)
    counts = [3.0 if i % 7 == 0 else (None if i % 5 == 4 else 0.0) for i in range(30)]
    frame = pl.DataFrame({
        "date": days, "ticker": ["A"] * 30, "news_count": counts,
    })
    out = add_news_burst(frame).sort("date")
    filled = np.array([c if c is not None else 0.0 for c in counts])
    i = 25
    win = filled[i - 20 : i + 1]
    np.testing.assert_allclose(
        out["news_burst_21"][i], (filled[i] - win.mean()) / win.std(ddof=1), rtol=1e-12
    )
    assert out["news_burst_21"][:20].to_list() == [0.0] * 20  # warmup neutral
    assert "news_count" not in out.columns

    quiet = pl.DataFrame({"date": days, "ticker": ["A"] * 30, "news_count": [2.0] * 30})
    assert (add_news_burst(quiet)["news_burst_21"].to_numpy() == 0.0).all()


def test_event_feature_names_gates():
    from new_pipeline.tournament.pipeline import _event_feature_names

    def cfg(event, factors, fusion):
        return SimpleNamespace(
            features=SimpleNamespace(event_features=event, factor_set=list(factors)),
            fusion=SimpleNamespace(enabled=fusion),
        )

    filing = ["days_since_filing", "ret_since_filing", "filing_reaction", "pead_drift"]
    assert _event_feature_names(cfg(False, ["book_to_market"], True)) == []
    assert _event_feature_names(cfg(True, ["book_to_market"], True)) == [
        *filing, "news_burst_21"
    ]
    assert _event_feature_names(cfg(True, ["roe"], False)) == filing
    assert _event_feature_names(cfg(True, [], True)) == ["news_burst_21"]
    assert _event_feature_names(cfg(True, ["mom_12_1"], True)) == ["news_burst_21"]


def test_filing_reaction_causal_mask_and_pead_sign():
    """The 3-day filing reaction must be INVISIBLE until the window has fully
    elapsed (days_since < 7 -> 0.0), exact once visible, and pead_drift must
    carry ret_since_filing with the reaction's sign (incl. negative)."""
    days = _weekdays(60)
    filing = days[10]
    rets = [0.0] * 60
    rets[11], rets[12], rets[13] = -0.05, -0.03, -0.02  # NEGATIVE 3-day reaction
    rets[20] = 0.04  # later drift day
    frame = _filing_frame({"A": rets}, {"A": lambda i, d: filing if d >= filing else None})
    out = add_filing_event_features(frame).sort("date")
    assert out["filing_reaction"][12] == 0.0  # window still open -> masked
    expected = (1 - 0.05) * (1 - 0.03) * (1 - 0.02) - 1.0
    i = 25  # days_since >= 7: visible
    np.testing.assert_allclose(out["filing_reaction"][i], expected, rtol=1e-12)
    # pead = ret_since * sign(reaction) -> NEGATIVE reaction flips the drift sign
    np.testing.assert_allclose(
        out["pead_drift"][i], -out["ret_since_filing"][i], rtol=1e-12
    )
    assert out["filing_reaction"][5] == 0.0 and out["pead_drift"][5] == 0.0  # pre-filing


def test_attach_fundamentals_keep_as_of_flag():
    from new_pipeline.adapters.fakes import FakeFundamentalsSource
    from new_pipeline.data.fundamentals import attach_fundamentals

    frame = pl.DataFrame({
        "ticker": ["AAA", "AAA"], "date": [date(2021, 2, 15), date(2021, 5, 15)],
        "close": [100.0, 100.0],
    })
    assert "as_of" not in attach_fundamentals(frame, FakeFundamentalsSource()).columns
    kept = attach_fundamentals(frame, FakeFundamentalsSource(), keep_as_of=True)
    assert kept["as_of"].dtype == pl.Date and kept["as_of"].null_count() == 0

    class _Empty:
        def history(self, *_args):
            return []

    empty = attach_fundamentals(frame, _Empty(), keep_as_of=True)
    assert "as_of" in empty.columns and empty["as_of"].is_null().all()


def test_attach_sentiment_counts_join_and_empty_path():
    from new_pipeline.tournament.pipeline import _attach_sentiment

    class _Engine:
        def score_headlines(self, texts, batch_size=64):
            return [SimpleNamespace(signed=0.5, confidence=1.0) for _ in texts]

    class _News:
        def __init__(self, items):
            self._items = items

        def fetch(self, symbol, start, end):
            return [i for i in self._items if i.symbol == symbol]

    days = _weekdays(5)  # Jan 4..8
    labeled = pl.DataFrame({
        "date": days, "ticker": ["A"] * 5, "sentiment_score": [0.0] * 5,
    })
    items = [  # 15:00Z == 10:00 New York -> pre-close, same session
        SimpleNamespace(timestamp="2021-01-05T15:00:00Z", headline="x", symbol="A"),
        SimpleNamespace(timestamp="2021-01-05T16:00:00Z", headline="y", symbol="A"),
        SimpleNamespace(timestamp="2021-01-06T15:00:00Z", headline="z", symbol="A"),
    ]
    out = _attach_sentiment(
        labeled, ["A"], _News(items), _Engine(), None, days[0], days[-1],
        attach_counts=True,
    ).sort("date")
    assert out["news_count"].to_list() == [0.0, 2.0, 1.0, 0.0, 0.0]
    assert out["sentiment_score"][1] != 0.0  # score joined alongside the count

    silent = _attach_sentiment(
        labeled, ["A"], _News([]), _Engine(), None, days[0], days[-1],
        attach_counts=True,
    )
    assert silent["news_count"].to_list() == [0.0] * 5  # column present on every path


def test_build_training_frame_materializes_event_columns():
    from new_pipeline.adapters import FakeMarketDataSource
    from new_pipeline.adapters.fakes import FakeFundamentalsSource
    from new_pipeline.config import get_config, reload_config
    from new_pipeline.tournament.pipeline import build_training_frame

    reload_config()
    cfg = get_config()
    cfg.features.event_features = True
    cfg.features.factor_set = ["book_to_market"]
    try:
        frame = build_training_frame(
            ["AAA"], {"AAA": "Information Technology"},
            date(2021, 1, 1), date(2021, 6, 30),
            source=FakeMarketDataSource(), cfg=cfg,
            fundamentals_source=FakeFundamentalsSource(),
        )
    finally:
        reload_config()
    assert {"days_since_filing", "ret_since_filing"} <= set(frame.columns)
    assert "as_of" not in frame.columns
    assert frame["days_since_filing"].null_count() == 0  # filled, never row-dropping
    assert frame["ret_since_filing"].null_count() == 0
    assert "news_burst_21" not in frame.columns  # fusion off -> no news subset
