from new_pipeline.monitoring.dashboard.alerts import check_alerts
from new_pipeline.monitoring.dashboard.realtime import Performance, VetoSummary


def _perf(sharpe=1.0, drawdown=-0.05):
    return Performance(
        total_pnl=0.1,
        sharpe=sharpe,
        max_drawdown=drawdown,
        win_rate=0.6,
        profit_factor=2.0,
        equity_curve=[1.0],
    )


def _veto(rate=0.1):
    return VetoSummary(total=10, executed=9, vetoed=1, veto_rate=rate, by_gate={"shield": 1})


def test_no_alerts_when_healthy():
    assert check_alerts(_perf(), _veto()) == []


def test_drawdown_breach_is_critical():
    alerts = check_alerts(_perf(drawdown=-0.25), _veto(), max_drawdown=0.15)
    assert any(alert.severity == "critical" for alert in alerts)


def test_low_sharpe_warns():
    alerts = check_alerts(_perf(sharpe=-0.5), _veto(), min_sharpe=0.0)
    assert any("Sharpe" in alert.message for alert in alerts)


def test_high_veto_rate_warns():
    alerts = check_alerts(_perf(), _veto(rate=0.8), max_veto_rate=0.5)
    assert any("Veto rate" in alert.message for alert in alerts)
