"""Paper-session guards + bracket-order construction (daily path regression)."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from new_pipeline.adapters.broker_alpaca import AlpacaBroker
from new_pipeline.scripts.intraday_paper_session import _champion_combo, _intraday_keys


def _receipt():
    return SimpleNamespace(status=SimpleNamespace(value="accepted"), id="x", symbol="AAA",
                           qty="5", side=SimpleNamespace(value="buy"),
                           limit_price=None, filled_avg_price=None)


def test_bracket_order_attaches_legs_and_daily_path_unchanged():
    client = MagicMock()
    client.submit_order.return_value = _receipt()
    broker = AlpacaBroker("k", "s", client=client)
    broker.submit_order({"symbol": "AAA", "qty": 5, "side": "buy", "tif": "day",
                         "limit_price": 10.5, "stop_loss": 9.8, "take_profit": 12.4})
    req = client.submit_order.call_args.kwargs["order_data"]
    assert req.order_class.value == "bracket"
    assert req.stop_loss.stop_price == 9.8 and req.take_profit.limit_price == 12.4
    # daily executor dict (no bracket keys) builds a plain order, no order_class legs
    broker.submit_order({"symbol": "AAA", "qty": 5, "side": "sell", "tif": "day"})
    plain = client.submit_order.call_args.kwargs["order_data"]
    assert getattr(plain, "stop_loss", None) is None
    assert getattr(plain, "take_profit", None) is None


def test_intraday_key_guards(monkeypatch):
    monkeypatch.delenv("QA_ALPACA_INTRADAY__API_KEY", raising=False)
    monkeypatch.delenv("QA_ALPACA_INTRADAY__SECRET_KEY", raising=False)
    with pytest.raises(SystemExit, match="DEDICATED paper account"):
        _intraday_keys()
    monkeypatch.setenv("QA_ALPACA_INTRADAY__API_KEY", "AKLIVEKEY")
    monkeypatch.setenv("QA_ALPACA_INTRADAY__SECRET_KEY", "s")
    with pytest.raises(SystemExit, match="not a PAPER key"):
        _intraday_keys()
    monkeypatch.setenv("QA_ALPACA_INTRADAY__API_KEY", "PKSAME")
    monkeypatch.setenv("QA_ALPACA__API_KEY", "PKSAME")
    with pytest.raises(SystemExit, match="never share an account"):
        _intraday_keys()
    monkeypatch.setenv("QA_ALPACA_INTRADAY__API_KEY", "PKDEDICATED")
    assert _intraday_keys() == ("PKDEDICATED", "s")


def test_champion_combo_requires_promotion(tmp_path):
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"promotions": [], "active_champions": {}}))
    with pytest.raises(SystemExit, match="not promoted"):
        _champion_combo(registry)
    manifest = tmp_path / "cand.json"
    manifest.write_text(json.dumps({"best_params": {"combo": "k15|or_mid|2R"}}))
    registry.write_text(json.dumps({
        "promotions": [], "active_champions": {"Intraday ORB": str(manifest)}}))
    combo, _ = _champion_combo(registry)
    assert (combo.k_minutes, combo.stop_style, combo.target_r) == (15, "or_mid", 2.0)
