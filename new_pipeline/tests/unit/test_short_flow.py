"""FINRA short-volume parse + daily-join attach + per-ticker short-flow features."""

from datetime import date, timedelta

import numpy as np
import polars as pl
from new_pipeline.adapters.fakes import FakeShortVolumeSource
from new_pipeline.data.finra_short_volume import (
    daily_url,
    parse_daily_file,
    trading_days,
)
from new_pipeline.data.short_volume import attach_short_volume
from new_pipeline.features.short_flow import SHORT_FLOW_COLS, add_short_flow_features

_HEADER = "Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market"


def test_parse_daily_file_filters_and_maps():
    text = "\n".join([
        _HEADER,
        "20220103|AAPL|500|10|1000|B,Q,N",   # ratio 0.5
        "20220103|BRK-B|300|0|1200|Q",        # class-share dash -> BRK.B
        "20220103|ZERO|5|0|0|Q",              # zero total -> dropped
        "20220103|OTHER|1|0|100|Q",           # not in universe -> dropped
        "Trailer row, not pipe-delimited",
    ])
    recs = parse_daily_file(text, universe={"AAPL", "BRK.B"})
    assert recs == [
        {"date": "2022-01-03", "ticker": "AAPL", "short_volume": 500, "total_volume": 1000},
        {"date": "2022-01-03", "ticker": "BRK.B", "short_volume": 300, "total_volume": 1200},
    ]


def test_parse_no_universe_keeps_all_valid():
    text = f"{_HEADER}\n20220103|A|1|0|2|Q\n20220103|B|3|0|0|Q"  # B zero-total dropped
    recs = parse_daily_file(text, universe=None)
    assert [r["ticker"] for r in recs] == ["A"]


def test_daily_url_and_trading_days():
    assert daily_url(date(2022, 1, 3)).endswith("CNMSshvol20220103.txt")
    days = trading_days(date(2022, 1, 1), date(2022, 1, 10))  # Sat..Mon
    assert date(2022, 1, 1) not in days and date(2022, 1, 2) not in days  # weekend
    assert all(d.weekday() < 5 for d in days) and date(2022, 1, 3) in days


def _frame(tickers, n=40):
    days = [date(2021, 1, 4) + timedelta(days=i) for i in range(n * 2)]
    days = [d for d in days if d.weekday() < 5][:n]
    return pl.DataFrame({"date": days * len(tickers),
                         "ticker": [t for t in tickers for _ in days]})


def test_attach_daily_join_and_missing_null():
    frame = _frame(["A", "MISS"])
    out = attach_short_volume(frame, FakeShortVolumeSource(["A"]))  # only A has data
    a = out.filter(pl.col("ticker") == "A")
    assert a["short_volume"].null_count() == 0 and a["total_volume"].null_count() == 0
    miss = out.filter(pl.col("ticker") == "MISS")
    assert miss["short_volume"].null_count() == miss.height  # unmatched -> null


def test_attach_tolerates_datetime_date_and_empty_source():
    frame = _frame(["A"]).with_columns(pl.col("date").cast(pl.Datetime))
    out = attach_short_volume(frame, FakeShortVolumeSource(["A"]))
    assert out["short_volume"].null_count() == 0  # datetime key normalized, joined

    empty = attach_short_volume(_frame(["A"]), None)
    assert empty["short_volume"].null_count() == empty.height  # no source -> null cols


def test_short_flow_features_exact_zscore_and_neutral_fill():
    frame = attach_short_volume(_frame(["A"]), FakeShortVolumeSource(["A"])).sort("date")
    out = add_short_flow_features(frame).sort("date")
    assert all(c in out.columns for c in SHORT_FLOW_COLS)
    assert "short_volume" not in out.columns  # raw consumed
    sr = (frame["short_volume"] / frame["total_volume"]).to_numpy()
    i = 30  # exact trailing 21d z-score (sample std, min_samples satisfied)
    win = sr[i - 20:i + 1]
    expected_z = (sr[i] - win.mean()) / win.std(ddof=1)
    np.testing.assert_allclose(out["short_z_21"][i], expected_z, rtol=1e-9)
    np.testing.assert_allclose(out["short_chg_5"][i], sr[i] - sr[i - 5], rtol=1e-12)
    assert out["short_z_21"][:14].to_list() == [0.0] * 14  # warmup neutral (min_samples 15)


def test_short_flow_missing_ticker_all_neutral():
    frame = attach_short_volume(_frame(["MISS"]), FakeShortVolumeSource([]))
    out = add_short_flow_features(frame)
    assert (out["short_ratio"].to_numpy() == 0.5).all()   # median-filled level
    assert (out["short_z_21"].to_numpy() == 0.0).all()    # no unusual signal
    assert (out["short_chg_5"].to_numpy() == 0.0).all()


def test_short_flow_per_ticker_isolation():
    out = add_short_flow_features(
        attach_short_volume(_frame(["A", "B"]), FakeShortVolumeSource(["A", "B"]))
    )
    # A and B have different seeds -> different short_ratio paths (no bleed).
    a = out.filter(pl.col("ticker") == "A").sort("date")["short_ratio"].to_numpy()
    b = out.filter(pl.col("ticker") == "B").sort("date")["short_ratio"].to_numpy()
    assert not np.allclose(a, b)


def test_build_training_frame_materializes_short_flow():
    from new_pipeline.adapters import FakeMarketDataSource
    from new_pipeline.config import get_config, reload_config
    from new_pipeline.tournament.pipeline import build_training_frame

    reload_config()
    cfg = get_config()
    cfg.features.short_flow_features = True
    try:
        frame = build_training_frame(
            ["AAA", "BBB"], {"AAA": "Information Technology", "BBB": "Health Care"},
            date(2021, 1, 1), date(2021, 6, 30),
            source=FakeMarketDataSource(), cfg=cfg,
            short_volume_source=FakeShortVolumeSource(["AAA", "BBB"]),
        )
    finally:
        reload_config()
    assert {"short_ratio", "short_z_21", "short_chg_5"} <= set(frame.columns)
    assert frame["short_ratio"].null_count() == 0  # neutral-filled, never row-dropping
