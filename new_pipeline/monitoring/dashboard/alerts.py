"""Threshold alert engine for the dashboard (Phase 6).

Pure function over the computed KPIs so it is unit-testable without a UI.
"""

from dataclasses import dataclass

from new_pipeline.monitoring.dashboard.realtime import Performance, VetoSummary


@dataclass
class Alert:
    severity: str  # "warning" | "critical"
    message: str


def check_alerts(
    performance: Performance,
    veto_summary: VetoSummary,
    *,
    max_drawdown: float = 0.15,
    min_sharpe: float = 0.0,
    max_veto_rate: float = 0.5,
) -> list[Alert]:
    alerts: list[Alert] = []
    if performance.max_drawdown < -abs(max_drawdown):
        alerts.append(
            Alert("critical", f"Max drawdown {performance.max_drawdown:.1%} breached "
                              f"the {abs(max_drawdown):.0%} limit")
        )
    if performance.sharpe < min_sharpe:
        alerts.append(Alert("warning", f"Sharpe {performance.sharpe:.2f} below {min_sharpe:.2f}"))
    if veto_summary.veto_rate > max_veto_rate:
        alerts.append(
            Alert("warning", f"Veto rate {veto_summary.veto_rate:.0%} exceeds "
                            f"{max_veto_rate:.0%}")
        )
    return alerts
