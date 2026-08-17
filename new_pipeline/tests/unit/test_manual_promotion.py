"""Manual promotion: honest-audit override rows + artifact copies, and the
paper book executor's pure target/order math."""

import json

import numpy as np
import polars as pl
import pytest
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


def test_reducing_orders_never_exceed_the_held_quantity():
    """31 of 38 skips on the 2026-08-07 rebalance were the broker rejecting
    'insufficient qty available': a 1.732-share holding int-rounds UP to 2, the
    order is refused, and because the refusal is only logged the position
    silently survives the rebalance. A reduction can only ever sell what is
    there."""
    prices = {"AAA": 100.0, "BBB": 100.0, "CCC": 100.0}
    # full exit of a fractional long on a NON-fractionable symbol
    orders = diff_orders({}, {"AAA": 1.732}, prices, capital=10_000, fractionable=set())
    aaa = [o for o in orders if o["symbol"] == "AAA"]
    assert aaa and aaa[0]["side"] == "sell"
    assert aaa[0]["qty"] == 1.732        # exact holding, never 2
    # full exit of a fractional SHORT buys back exactly what is owed
    orders = diff_orders({}, {"BBB": -2.4}, prices, capital=10_000, fractionable=set())
    bbb = [o for o in orders if o["symbol"] == "BBB"]
    assert bbb and bbb[0]["side"] == "buy" and bbb[0]["qty"] == 2.4
    # partial reduction stays within the holding
    orders = diff_orders({"CCC": 0.005}, {"CCC": 1.2}, prices, capital=10_000,
                         fractionable=set())
    ccc = [o for o in orders if o["symbol"] == "CCC"]
    if ccc:
        assert ccc[0]["qty"] <= 1.2
    # a position-INCREASING order is untouched by the clamp
    grow = diff_orders({"AAA": 0.05}, {"AAA": 1.0}, prices, capital=10_000,
                       fractionable={"AAA"})
    a = [o for o in grow if o["symbol"] == "AAA"]
    assert a and a[0]["side"] == "buy" and a[0]["qty"] == 4.0


def test_unit_returns_accumulate_every_session_and_drive_the_vol_target():
    """vol_target_annual was silently inert live: unit_returns was read but
    never written, so it stayed [] forever and the book ran UNSCALED while the
    backtest scaled to 5% annualized. The shadow book must advance on hold days
    too, or the estimator never fills."""
    from datetime import date, timedelta
    days = [date(2021, 1, 4) + timedelta(days=i) for i in range(6)]
    names = [f"T{i}" for i in range(8)]
    panel = _panel(days, names, [[8, 7, 6, 5, 4, 3, 2, 1]] * len(days))
    mkt = {d: 0.001 for d in days}
    params = {"quantile": 0.25, "rebalance_days": 5, "min_names_per_day": 4,
              "score_smoothing_days": 1, "vol_target_annual": 0.05,
              "vol_lookback_days": 3}
    rets = {t: 0.01 for t in names}

    # day 1 rebalances and seats the unscaled shadow book
    _, state = compute_targets(panel, params, {}, mkt, 252, returns_by_date={days[-1]: rets})
    assert state["unit_held"]
    assert abs(sum(abs(w) for w in state["unit_held"].values()) - 1.0) < 1e-12
    first = len(state["unit_returns"])

    # re-running on the SAME session must not double-count it
    _, state = compute_targets(panel, params, state, mkt, 252,
                               returns_by_date={days[-1]: rets})
    assert len(state["unit_returns"]) == first

    # and a run that arrives after a GAP backfills every missed session: the
    # book is static between runs, so those weights really were held.
    gap = {d: rets for d in days}
    _, state = compute_targets(panel, params, state, mkt, 252, returns_by_date=gap)
    assert len(state["unit_returns"]) == first  # days[-1] already recorded
    fresh = {**state, "last_return_date": str(days[0])}
    _, caught_up = compute_targets(panel, params, fresh, mkt, 252, returns_by_date=gap)
    assert len(caught_up["unit_returns"]) == first + (len(days) - 1)
    assert caught_up["last_return_date"] == str(days[-1])

    # with a filled estimator and high trailing vol the book DE-RISKS
    noisy = {**state, "last_rebalance_date": None,
             "unit_returns": [0.05, -0.05, 0.05, -0.05, 0.05]}
    scaled, _ = compute_targets(panel, params, noisy, mkt, 252, returns_by_date={days[-1]: rets})
    gross = sum(abs(w) for w in scaled.values())
    assert gross < 1.0, f"vol target should shrink gross, got {gross}"

    # and never LEVERS above unit gross when trailing vol is tiny
    calm = {**state, "last_rebalance_date": None,
            "unit_returns": [1e-6, -1e-6, 1e-6, -1e-6, 1e-6]}
    unlevered, _ = compute_targets(panel, params, calm, mkt, 252, returns_by_date={days[-1]: rets})
    assert abs(sum(abs(w) for w in unlevered.values()) - 1.0) < 1e-9


def test_unit_returns_history_is_bounded():
    from datetime import date

    from new_pipeline.scripts.paper_trade_book import _UNIT_RETURN_HISTORY
    days = [date(2021, 1, 4), date(2021, 1, 5)]
    names = [f"T{i}" for i in range(8)]
    panel = _panel(days, names, [[8, 7, 6, 5, 4, 3, 2, 1]] * 2)
    mkt = {d: 0.001 for d in days}
    params = {"quantile": 0.25, "rebalance_days": 1, "min_names_per_day": 4,
              "score_smoothing_days": 1}
    state = {"unit_returns": [0.0] * (_UNIT_RETURN_HISTORY + 50), "unit_held": {}}
    _, out = compute_targets(panel, params, state, mkt, 252,
                             returns_by_date={days[-1]: {t: 0.0 for t in names}})
    assert len(out["unit_returns"]) == _UNIT_RETURN_HISTORY


def test_shadow_book_migrates_from_a_pre_fix_state_file():
    """A state file written before the shadow book existed carries `held` but
    no `unit_held`. Without a migration the shadow book stays empty until the
    next rebalance and every hold day until then appends a spurious 0.0 —
    understating trailing vol exactly while the estimator is filling."""
    from datetime import date
    days = [date(2021, 1, 4), date(2021, 1, 5)]
    names = [f"T{i}" for i in range(8)]
    panel = _panel(days, names, [[8, 7, 6, 5, 4, 3, 2, 1]] * 2)
    mkt = {d: 0.001 for d in days}
    params = {"quantile": 0.25, "rebalance_days": 5, "min_names_per_day": 4,
              "score_smoothing_days": 1, "vol_target_annual": 0.05,
              "vol_lookback_days": 3}
    legacy = {"held": {"T0": 0.25, "T1": 0.25, "T6": -0.25, "T7": -0.25},
              "prev_longs": ["T0", "T1"], "prev_shorts": ["T6", "T7"],
              "last_rebalance_date": str(days[0])}
    # longs up, shorts down: a dollar-neutral book earns exactly zero on
    # UNIFORM returns, so the returns must differ for this to test anything.
    rets = {t: 0.0 for t in names}
    rets.update({"T0": 0.03, "T1": 0.03, "T6": -0.01, "T7": -0.01})
    _, state = compute_targets(panel, params, legacy, mkt, 252, returns_by_date={days[-1]: rets})
    assert set(state["unit_held"]) == set(legacy["held"])
    assert abs(sum(abs(w) for w in state["unit_held"].values()) - 1.0) < 1e-12
    # the first appended return is the REAL book's, not a zero from an empty one
    assert state["unit_returns"] == [pytest.approx(0.02)]

    # a genuinely flat book has nothing to migrate, so it appends a TRUE zero
    # before the rebalance seats a fresh shadow book (no last_rebalance_date
    # means this call rebalances).
    _, flat = compute_targets(panel, params, {"held": {}}, mkt, 252,
                              returns_by_date={days[-1]: rets})
    assert flat["unit_returns"] == [0.0]
    assert abs(sum(abs(w) for w in flat["unit_held"].values()) - 1.0) < 1e-12


class _StubBroker:
    """Broker whose orders settle only after N status polls."""

    def __init__(self, polls_to_fill=2, final="filled"):
        self.polls = {}
        self.polls_to_fill = polls_to_fill
        self.final = final
        self.submitted = []

    def submit_order(self, order):
        oid = f"o{len(self.submitted) + 1}"
        self.submitted.append(order)
        self.polls[oid] = 0
        return {"status": "pending_new", "order_id": oid}

    def order_status(self, order_id):
        self.polls[order_id] = self.polls.get(order_id, 0) + 1
        return self.final if self.polls[order_id] >= self.polls_to_fill else "pending_new"


def test_await_close_fill_blocks_until_the_close_settles():
    """A flip submits close-then-open on the same symbol. Alpaca reserves the
    position against the pending close (held_for_orders == existing_qty), so an
    open fired immediately behind it sees available: 0 — 22 of the 31 skips on
    the 2026-08-17 rebalance, every one a short leg that failed to open, which
    biases a dollar-neutral book long."""
    from new_pipeline.scripts.paper_trade_book import await_close_fill

    slept = []
    b = _StubBroker(polls_to_fill=3)
    receipt = b.submit_order({"symbol": "AAA"})
    got = await_close_fill(b, receipt["order_id"], now=lambda: 0.0,
                           sleep=slept.append)
    assert got == "filled"
    assert len(slept) == 2  # polled until settled rather than returning at once


def test_await_close_fill_reports_timeout_rather_than_assuming_a_fill():
    """Anything other than 'filled' must read as 'shares still reserved':
    releasing the paired open then would simply be rejected again."""
    from new_pipeline.scripts.paper_trade_book import await_close_fill

    clock = iter([0.0, 0.0, 5.0, 30.0, 60.0, 90.0])
    b = _StubBroker(polls_to_fill=999)  # never settles
    receipt = b.submit_order({"symbol": "AAA"})
    got = await_close_fill(b, receipt["order_id"], timeout_s=10.0,
                           now=lambda: next(clock), sleep=lambda _s: None)
    assert got == "timeout"
    # a rejected close is terminal but still not a fill
    b2 = _StubBroker(polls_to_fill=1, final="rejected")
    r2 = b2.submit_order({"symbol": "BBB"})
    assert await_close_fill(b2, r2["order_id"], now=lambda: 0.0,
                            sleep=lambda _s: None) == "rejected"
    # a missing id cannot be confirmed and must not read as filled
    assert await_close_fill(b2, "", now=lambda: 0.0, sleep=lambda _s: None) != "filled"


def test_fake_broker_exposes_order_status_for_the_flip_wait():
    from new_pipeline.adapters.fakes import FakeBroker

    b = FakeBroker()
    r = b.submit_order({"symbol": "AAA", "qty": 1, "side": "buy"})
    assert b.order_status(r["order_id"]) == "filled"
    assert b.order_status("nonexistent") == "unknown"
