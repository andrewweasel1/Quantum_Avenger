from new_pipeline.evaluation.promotion import PromotionRegistry, assess_promotion
from new_pipeline.execution.trade_log import TradeLog, TradeRecord
from new_pipeline.monitoring.dashboard.views import model_registry_view, risk_view


def test_model_registry_view(tmp_path):
    path = tmp_path / "reg.json"
    registry = PromotionRegistry(path)
    registry.record(assess_promotion("Energy", 0.97, 0.2), model_path="/m/e.json")
    view = model_registry_view(path)
    assert view["active_champions"] == {"Energy": "/m/e.json"}
    assert len(view["promotions"]) == 1


def test_model_registry_view_missing(tmp_path):
    assert model_registry_view(tmp_path / "none.json") == {
        "active_champions": {},
        "promotions": [],
    }


def test_risk_view(tmp_path):
    path = tmp_path / "trades.parquet"
    log = TradeLog(path)
    log.append(TradeRecord("AAPL", "buy", 10, 100.0, "filled", "o1"))  # +1000
    log.append(TradeRecord("MSFT", "buy", 5, 100.0, "filled", "o2"))  # +500
    log.append(TradeRecord("AAPL", "sell", 2, 100.0, "filled", "o3"))  # -200 -> AAPL 800

    view = risk_view(path)
    assert view.position_count == 2
    assert abs(view.gross_exposure - 1300.0) < 1e-6
    assert abs(view.largest_position - 800.0) < 1e-6
    assert abs(view.concentration - 800.0 / 1300.0) < 1e-9


def test_risk_view_empty(tmp_path):
    assert risk_view(tmp_path / "none.parquet").gross_exposure == 0.0
