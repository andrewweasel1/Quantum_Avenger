import numpy as np
import pandas as pd
import polars as pl
from new_pipeline.features.markov_regime import (
    MARKOV_FEATURE_NAMES,
    add_markov_regime_features,
    compute_rolling_markov_features,
)


def _price_frame(n: int = 160, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100.0 * np.exp(np.cumsum(rng.normal(0.0005, 0.01, n)))
    return pd.DataFrame(
        {
            "date": pd.date_range("2021-01-01", periods=n, freq="D"),
            "ticker": "AAA",
            "close": close,
        }
    )


def test_markov_features_added_and_bounded():
    df = compute_rolling_markov_features(_price_frame(), lookback=40, n_components=2)
    for name in MARKOV_FEATURE_NAMES:
        assert name in df.columns
    finite = df[list(MARKOV_FEATURE_NAMES)].to_numpy()
    finite = finite[~np.isnan(finite)]
    assert finite.size > 0
    assert (finite >= 0.0).all() and (finite <= 1.0).all()


def test_markov_is_causal_with_leading_nans():
    lookback = 40
    df = compute_rolling_markov_features(_price_frame(), lookback=lookback, n_components=2)
    # the window [i-lookback:i] excludes bar i, so nothing is computed before lookback
    assert df["markov_prob_persist_0"].iloc[:lookback].isna().all()


def test_sentiment_toggle_runs_both_paths():
    frame = _price_frame()
    frame["sentiment"] = np.linspace(-1.0, 1.0, len(frame))
    fused = compute_rolling_markov_features(frame, lookback=40, use_sentiment=True, n_components=2)
    plain = compute_rolling_markov_features(frame, lookback=40, use_sentiment=False, n_components=2)
    assert all(name in fused.columns for name in MARKOV_FEATURE_NAMES)
    assert all(name in plain.columns for name in MARKOV_FEATURE_NAMES)


def test_build_training_frame_markov_then_static_fundamentals():
    """Regression: markov_features=true upcast the Date join key to Datetime via
    its pandas round-trip, crashing the downstream static-fundamentals attach
    (date-vs-datetime) ~4h into a real run. The full chain must now clear."""
    from datetime import date

    from new_pipeline.adapters import FakeMarketDataSource
    from new_pipeline.adapters.fundamentals_static import StaticFundamentalsSource
    from new_pipeline.config import get_config, reload_config
    from new_pipeline.tournament.pipeline import build_training_frame

    reload_config()
    cfg = get_config()
    cfg.fusion.enabled = True
    cfg.fusion.markov_features = True
    cfg.features.factor_set = ["book_to_market", "earnings_yield", "roe"]
    cfg.features.event_features = True
    try:
        frame = build_training_frame(
            ["AAPL", "MSFT"], {"AAPL": "Information Technology", "MSFT": "Information Technology"},
            date(2021, 1, 1), date(2021, 12, 31),
            source=FakeMarketDataSource(), cfg=cfg,
            fundamentals_source=StaticFundamentalsSource(
                "new_pipeline/data/fundamentals/snapshots.csv"
            ),
        )
    finally:
        reload_config()
    assert frame.schema["date"] == pl.Date  # key not silently upcast
    for col in ("markov_prob_persist_0", "book_value_per_share", "days_since_filing"):
        assert col in frame.columns
    assert frame.filter(pl.col("book_value_per_share").is_not_null()).height > 0  # joined


def test_polars_wrapper_preserves_date_dtype():
    """The pandas round-trip must not upcast the Date join key to Datetime:
    downstream fundamentals/regime consumers compare it against date literals
    and a silent Datetime broke a 4-hour run (date vs datetime TypeError)."""
    from datetime import date

    frame = pl.DataFrame({
        "date": pl.date_range(date(2021, 1, 1), date(2021, 6, 30), "1d", eager=True),
        "ticker": "AAA",
        "close": 100.0 * np.exp(np.cumsum(np.random.default_rng(1).normal(0, 0.01, 181))),
    })
    assert frame.schema["date"] == pl.Date
    out = add_markov_regime_features(frame, lookback=40)
    assert out.schema["date"] == pl.Date  # invariant across the stage
    assert all(name in out.columns for name in MARKOV_FEATURE_NAMES)
