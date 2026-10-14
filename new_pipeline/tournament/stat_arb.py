"""Statistical arbitrage: cointegration + Ornstein-Uhlenbeck mean reversion (P5, §C).

A market-neutral second strategy family. Engle-Granger: regress one price series on
another (OLS hedge ratio), then test the residual *spread* for stationarity with an
augmented Dickey-Fuller t-stat — a stationary spread means the pair is cointegrated.
The spread is modelled as an Ornstein-Uhlenbeck process (its AR(1) decay gives a
mean-reversion half-life), and traded by a causal z-score rule (enter when the spread
is stretched, exit near the mean). Each traded pair yields a **date-indexed** return
stream — a sleeve the P4 portfolio layer can combine *exactly* (no truncation).

Self-contained (numpy + scipy lstsq) — statsmodels is not a dependency. See
``docs/quantitative_math.md`` Part II §C.
"""

from dataclasses import dataclass

import numpy as np

from new_pipeline.tournament.ols import ols, with_intercept

# Asymptotic ADF 5% critical value (constant, no trend): spread is stationary below it.
ADF_CRITICAL_5PCT = -2.86


def adf_tstat(series, lags=1) -> float:
    """Augmented Dickey-Fuller t-statistic on the lagged-level coefficient.

    Regresses Δyₜ = α + γ·yₜ₋₁ + Σ δᵢ·Δyₜ₋ᵢ + εₜ and returns t(γ̂). A strongly
    negative value ⇒ mean-reverting (stationary); near 0 ⇒ a unit root (random walk).
    Returns 0.0 (treated as non-stationary) when the series is too short or singular.
    """
    y = np.asarray(series, dtype=np.float64)
    diff = np.diff(y)
    n = diff.size - lags
    if n < 8:
        return 0.0
    response = diff[lags:]
    lag_diffs = [diff[lags - lag : diff.size - lag] for lag in range(1, lags + 1)]
    design = with_intercept(y[lags:-1], *lag_diffs)  # lagged level is column 0
    beta, rss, rank = ols(design, response)
    if rank < design.shape[1]:
        return 0.0
    dof = n - design.shape[1]
    sigma2 = rss / dof if dof > 0 else 0.0
    try:
        cov = sigma2 * np.linalg.inv(design.T @ design)
    except np.linalg.LinAlgError:  # pragma: no cover - rank check above guards this
        return 0.0
    se = np.sqrt(cov[0, 0])
    return float(beta[0] / se) if se > 0 else 0.0


@dataclass(frozen=True)
class CointegrationResult:
    hedge_ratio: float
    intercept: float
    adf_tstat: float
    half_life: float
    cointegrated: bool


def engle_granger(y, x, lags=1, adf_threshold=ADF_CRITICAL_5PCT):
    """Engle-Granger test of ``y`` on ``x``: returns ``(CointegrationResult, spread)``.

    ``spread = y - (intercept + hedge_ratio·x)``; ``cointegrated`` is True when the
    spread's ADF t-stat is below ``adf_threshold`` (stationary) with a positive hedge.
    """
    y = np.asarray(y, dtype=np.float64)
    x = np.asarray(x, dtype=np.float64)
    coef, _, _ = ols(with_intercept(x), y)
    hedge, intercept = float(coef[0]), float(coef[1])
    spread = y - (intercept + hedge * x)
    tstat = adf_tstat(spread, lags)
    result = CointegrationResult(
        hedge_ratio=hedge,
        intercept=intercept,
        adf_tstat=tstat,
        half_life=ou_half_life(spread),
        cointegrated=tstat < adf_threshold and hedge > 0.0,
    )
    return result, spread


def ou_half_life(spread) -> float:
    """OU mean-reversion half-life from the spread's AR(1) decay: ``-ln(2)/b`` where
    ``ΔSₜ = a + b·Sₜ₋₁``. Returns ``inf`` when the spread is not mean-reverting (b ≥ 0)."""
    s = np.asarray(spread, dtype=np.float64)
    if s.size < 3:
        return float("inf")
    coef, _, _ = ols(with_intercept(s[:-1]), np.diff(s))
    b = float(coef[0])
    return -np.log(2.0) / b if b < 0.0 else float("inf")


def _rolling_zscore(spread, window) -> np.ndarray:
    """Causal rolling z-score: zₜ uses the spread over ``[t-window+1, t]`` (no look-ahead)."""
    s = np.asarray(spread, dtype=np.float64)
    z = np.full(s.size, np.nan)
    for t in range(window - 1, s.size):
        win = s[t - window + 1 : t + 1]
        std = win.std()
        if std > 0.0:
            z[t] = (s[t] - win.mean()) / std
    return z


def mean_reversion_returns(spread, entry_z=2.0, exit_z=0.5, window=20) -> np.ndarray:
    """Causal z-score mean-reversion P&L on the spread, standardized to unit-ish scale.

    Enter long when zₜ < -entry_z (spread cheap), short when zₜ > entry_z; exit when
    |z| < exit_z. The position decided at t earns Δspread at t+1 (no look-ahead);
    returns are scaled by σ(Δspread) so sleeves are comparable in the portfolio layer.
    """
    s = np.asarray(spread, dtype=np.float64)
    z = _rolling_zscore(s, window)
    position = np.zeros(s.size)
    current = 0
    for t in range(s.size):
        if not np.isnan(z[t]):
            if current == 0:
                current = -1 if z[t] > entry_z else 1 if z[t] < -entry_z else 0
            elif abs(z[t]) < exit_z:
                current = 0
        position[t] = current
    delta = np.diff(s, prepend=s[0])
    scale = np.std(delta) or 1.0
    returns = np.zeros(s.size)
    returns[1:] = position[:-1] * delta[1:] / scale  # position from t-1 earns Δspread at t
    return returns


def find_cointegrated_pairs(price_panel, tickers, lags=1, adf_threshold=ADF_CRITICAL_5PCT):
    """Engle-Granger over every column pair of ``price_panel`` (T x N, a column per
    ticker). Returns cointegrated pairs as dicts sorted by ADF t-stat (most stationary
    first); each carries the tickers, hedge ratio, ADF t-stat, and OU half-life."""
    panel = np.asarray(price_panel, dtype=np.float64)
    pairs = []
    for i in range(panel.shape[1]):
        for j in range(i + 1, panel.shape[1]):
            result, _ = engle_granger(panel[:, i], panel[:, j], lags, adf_threshold)
            if result.cointegrated:
                pairs.append(
                    {
                        "y": tickers[i], "x": tickers[j],
                        "hedge_ratio": result.hedge_ratio,
                        "adf_tstat": result.adf_tstat,
                        "half_life": result.half_life,
                    }
                )
    return sorted(pairs, key=lambda pair: pair["adf_tstat"])
