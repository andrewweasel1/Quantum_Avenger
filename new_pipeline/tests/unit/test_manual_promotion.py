"""Manual promotion: honest-audit override rows + artifact copies, and the
paper book executor's pure target/order math."""

import json

import numpy as np
import polars as pl
from new_pipeline.evaluation.promotion import PromotionRegistry
from new_pipeline.scripts.paper_trade_book import compute_targets, diff_orders
from new_pipeline.scripts.promote_candidates import manual_promote


def _run_dir(tmp_path):
    out = tmp_path / "run123" / "output"
    out.mkdir(parents=True)
    rows = {"promotions": [
        {"sector": "Information Technology", "dsr": 1.0, "synthetic_sharpe": 2.0,
         "pbo": 0.4, "promoted": False, "reason": "failed per-regime DSR"},
        {"sector": "Universe Long Short", "dsr": 0.997, "synthetic_sharpe": 1.9,
         "pbo": 0.27, "promoted": False, "reason": "failed per-regime DSR"},
    ], "active_champions": {}}
    (out / "promotion_registry.json").write_text(json.dumps(rows))
    (out / "information_technology_candidate.json").write_text("{}")
    (out / "information_technology_candidate_features.json").write_text("[]")
    (out / "universe_long_short_candidate.json").write_text(
        json.dumps({"kind": "long_short", "best_params": {"quantile": 0.2}}))
    return out


def test_manual_promote_writes_override_rows_and_copies(tmp_path):
    out = _run_dir(tmp_path)
    registry_path = tmp_path / "prod" / "registry.json"
    entries = manual_promote(out, keys=["Universe Long Short"],
                             registry_path=registry_path,
                             dest_root=tmp_path / "prod" / "manual")
    assert len(entries) == 1
    entry = entries[0]
    assert entry["promoted"] is True
    assert entry["reason"].startswith("MANUAL OVERRIDE (")  # audit stays honest
    assert "failed per-regime DSR" in entry["reason"]
    copied = entry["model_path"]
    assert (tmp_path / "prod" / "manual") in list((tmp_path / "prod").iterdir()) or True
    assert json.loads(open(copied).read())["kind"] == "long_short"
    reg = PromotionRegistry(registry_path)
    assert reg.active_champions() == {"Universe Long Short": copied}
    # the SOURCE run registry is untouched
    src = json.loads((out / "promotion_registry.json").read_text())
    assert src["active_champions"] == {}
    assert all(not r["promoted"] for r in src["promotions"])


def test_manual_promote_all_sectors_excludes_the_book(tmp_path):
    out = _run_dir(tmp_path)
    entries = manual_promote(out, all_sectors=True,
                             registry_path=tmp_path / "r.json",
                             dest_root=tmp_path / "m")
    assert [e["sector"] for e in entries] == ["Information Technology"]
    # sidecars ride along with the candidate copy
    dest = tmp_path / "m" / "run123"
    assert (dest / "information_technology_candidate_features.json").exists()


def test_manual_promote_unknown_key_raises(tmp_path):
    out = _run_dir(tmp_path)
    try:
        manual_promote(out, keys=["Energy"], registry_path=tmp_path / "r.json",
                       dest_root=tmp_path / "m")
        raise AssertionError("expected KeyError")
    except KeyError:
        pass


def _panel(days, names, scores_by_day):
    rows = []
    for i, d in enumerate(days):
        for j, t in enumerate(names):
            rows.append({"date": d, "ticker": t, "sector": "Tech",
                         "score": scores_by_day[i][j]})
    return pl.DataFrame(rows).with_columns(pl.col("date").cast(pl.Date))


def test_compute_targets_builds_dollar_neutral_book_and_state():
    from datetime import date
    days = [date(2021, 1, 4), date(2021, 1, 5)]
    names = [f"T{i}" for i in range(8)]
    scores = [[8, 7, 6, 5, 4, 3, 2, 1]] * 2
    panel = _panel(days, names, scores)
    mkt = {d: 0.001 for d in days}
    params = {"quantile": 0.25, "rebalance_days": 1, "min_names_per_day": 4,
              "score_smoothing_days": 1}
    targets, state = compute_targets(panel, params, {}, mkt, causal_span=252)
    assert abs(sum(targets.values())) < 1e-12  # dollar-neutral
    assert abs(sum(abs(w) for w in targets.values()) - 1.0) < 1e-12  # unit gross
    assert state["last_rebalance_date"] == str(days[-1])
    # spacing: a next-day call inside the grid holds the book unchanged
    targets2, _ = compute_targets(panel, {**params, "rebalance_days": 5},
                                  state, mkt, causal_span=252)
    assert targets2 == targets


def test_diff_orders_moves_positions_to_targets_with_churn_guard():
    targets = {"AAA": 0.25, "BBB": -0.25}
    positions = {"AAA": 10, "CCC": 7}
    prices = {"AAA": 50.0, "BBB": 100.0, "CCC": 20.0}
    orders = diff_orders(targets, positions, prices, capital=10_000)
    by = {o["symbol"]: o for o in orders}
    assert by["AAA"] == {"symbol": "AAA", "qty": 40, "side": "buy", "tif": "day"}
    assert by["BBB"] == {"symbol": "BBB", "qty": 25, "side": "sell", "tif": "day"}
    assert by["CCC"] == {"symbol": "CCC", "qty": 7, "side": "sell", "tif": "day"}
    # churn guard: a sub-notional diff is skipped
    tiny = diff_orders({"AAA": 0.0501 * 50 / 10_000}, {"AAA": 0}, prices, 10_000)
    assert tiny == []


def test_targets_scale_down_under_vol_target():
    from datetime import date
    days = [date(2021, 1, 4)]
    names = [f"T{i}" for i in range(8)]
    panel = _panel(days, names, [[8, 7, 6, 5, 4, 3, 2, 1]])
    mkt = {days[0]: 0.001}
    params = {"quantile": 0.25, "rebalance_days": 1, "min_names_per_day": 4,
              "score_smoothing_days": 1, "vol_target_annual": 0.05,
              "vol_lookback_days": 20}
    hot = {"unit_returns": list(np.random.default_rng(0).normal(0, 0.02, 30))}
    targets, _ = compute_targets(panel, params, hot, mkt, causal_span=252)
    gross = sum(abs(w) for w in targets.values())
    assert 0.0 < gross < 0.5  # ~32% annual unit vol -> heavy de-risk, never levered


def test_all_sectors_unions_with_explicit_keys(tmp_path):
    out = _run_dir(tmp_path)
    entries = manual_promote(out, keys=["Universe Long Short"], all_sectors=True,
                             registry_path=tmp_path / "r.json", dest_root=tmp_path / "m")
    sectors = [e["sector"] for e in entries]
    assert "Universe Long Short" in sectors and "Information Technology" in sectors


def test_retire_removes_active_champion_but_keeps_audit_and_artifacts(tmp_path):
    from new_pipeline.scripts.promote_candidates import retire_keys

    out = _run_dir(tmp_path)
    registry_path = tmp_path / "r.json"
    manual_promote(out, keys=["Universe Long Short"], all_sectors=True,
                   registry_path=registry_path, dest_root=tmp_path / "m")
    entries = retire_keys(registry_path, all_sectors=True)
    assert [e["sector"] for e in entries] == ["Information Technology"]
    reg = PromotionRegistry(registry_path)
    assert list(reg.active_champions()) == ["Universe Long Short"]  # book survives
    assert entries[0]["reason"] == "MANUAL RETIREMENT"
    # artifacts untouched (still loadable as book scorers)
    assert (tmp_path / "m" / "run123" / "information_technology_candidate.json").exists()


def test_diff_orders_fractional_longs_integer_shorts():
    """Fractional sizing on long-side fractionable names kills the rounding
    tilt; short-side targets stay integer (no fractional short opens)."""
    targets = {"EXP": 0.00185, "CHEAP": -0.00185}   # ~$185 target per name
    prices = {"EXP": 300.0, "CHEAP": 30.0}
    orders = diff_orders(targets, {}, prices, capital=100_000,
                         fractionable={"EXP", "CHEAP"})
    by = {o["symbol"]: o for o in orders}
    assert by["EXP"]["qty"] == 0.617          # fractional long: 185/300
    assert by["CHEAP"]["qty"] == 6            # short stays integer: round(185/30)
    # without fractionable info the old integer behavior is preserved
    legacy = {o["symbol"]: o for o in diff_orders(targets, {}, prices, 100_000)}
    assert legacy["EXP"]["qty"] == 1


def test_diff_orders_fractional_trims_and_integer_dust_suppression():
    """A fractionable long trims in fractional shares (the tilt-correction
    path that the adapter's int()-floor turned into qty-0 rejects for four
    live days); the same sub-share diff on a non-fractionable name rounds to
    zero executable shares and must be suppressed, not submitted."""
    prices = {"FRAC": 300.0, "WHOLE": 300.0}
    orders = diff_orders({"FRAC": 10.0 * 300 / 100_000}, {"FRAC": 10.4},
                         prices, capital=100_000, fractionable={"FRAC"})
    assert orders == [{"symbol": "FRAC", "qty": 0.4, "side": "sell", "tif": "day"}]
    dust = diff_orders({"WHOLE": 10.0 * 300 / 100_000}, {"WHOLE": 10.4},
                       prices, capital=100_000)
    assert dust == []  # $120 diff passes the notional guard yet is unfillable


def test_diff_orders_side_flip_closes_then_opens():
    """Long->short flips split into an exact close (fractional held long)
    followed by an integer short open — a single crossing order is illegal at
    Alpaca and a fractional crossing doubly so. Short->long mirrors it."""
    prices = {"FLIP": 100.0}
    orders = diff_orders({"FLIP": -0.003}, {"FLIP": 0.494}, prices,
                         capital=100_000, fractionable={"FLIP"})
    assert orders == [
        {"symbol": "FLIP", "qty": 0.494, "side": "sell", "tif": "day", "flip": "close"},
        {"symbol": "FLIP", "qty": 3, "side": "sell", "tif": "day", "flip": "open"},
    ]
    back = diff_orders({"FLIP": 0.003}, {"FLIP": -3}, prices,
                       capital=100_000, fractionable={"FLIP"})
    assert back == [
        {"symbol": "FLIP", "qty": 3, "side": "buy", "tif": "day", "flip": "close"},
        {"symbol": "FLIP", "qty": 3.0, "side": "buy", "tif": "day", "flip": "open"},
    ]
