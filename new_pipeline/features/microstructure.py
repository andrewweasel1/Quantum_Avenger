"""Microstructure / liquidity estimators from OHLCV (offense roadmap P1, §E).

Cheap proxies for the cost of trading, estimable without tick data:

* **Roll measure** — effective spread from the negative serial covariance of price
  changes: ``2·√(-Cov(Δpₜ, Δpₜ₋₁))`` (0 when the covariance is non-negative).
* **Corwin–Schultz** — bid–ask spread from consecutive high/low ranges.
* **Kyle's λ proxy** — price impact: the rolling regression slope of Δp on signed
  volume (tick-rule sign), i.e. how far price moves per unit of signed flow.

Per-ticker rolling windows (numpy kernels); leading rows are null. Complements the
existing ``spread_pct`` / ``roll_spread`` / ``amihud``. See ``docs/quantitative_math.md``
Part II §E.
"""

import numpy as np
import polars as pl

MICRO_FEATURE_NAMES = ("roll_measure", "corwin_schultz", "kyle_lambda")
_DEN_CS = 3.0 - 2.0 * np.sqrt(2.0)


def _rolling_mean(values, window) -> np.ndarray:
    out = np.full(values.size, np.nan)
    for t in range(window - 1, values.size):
        win = values[t - window + 1 : t + 1]
        finite = win[np.isfinite(win)]
        if finite.size:
            out[t] = float(finite.mean())
    return out


def roll_measure(close, window=20) -> np.ndarray:
    """Roll (1984) effective spread from the serial covariance of price changes."""
    close = np.asarray(close, dtype=np.float64)
    delta = np.diff(close, prepend=close[0])
    out = np.full(close.size, np.nan)
    for t in range(window, close.size):
        current = delta[t - window + 1 : t + 1]
        lagged = delta[t - window : t]
        cov = float(np.cov(current, lagged)[0, 1])
        out[t] = 2.0 * np.sqrt(-cov) if cov < 0.0 else 0.0
    return out


def corwin_schultz(high, low, window=20) -> np.ndarray:
    """Corwin–Schultz (2012) spread from consecutive two-day high/low ranges, then
    averaged over ``window`` (negative per-pair spreads floored at 0)."""
    high = np.asarray(high, dtype=np.float64)
    low = np.asarray(low, dtype=np.float64)
    hl_sq = np.log(high / low) ** 2
    per_pair = np.full(high.size, np.nan)
    for t in range(1, high.size):
        beta = hl_sq[t] + hl_sq[t - 1]
        high_2d, low_2d = max(high[t], high[t - 1]), min(low[t], low[t - 1])
        gamma = np.log(high_2d / low_2d) ** 2
        alpha = (np.sqrt(2.0 * beta) - np.sqrt(beta)) / _DEN_CS - np.sqrt(gamma / _DEN_CS)
        spread = 2.0 * (np.exp(alpha) - 1.0) / (1.0 + np.exp(alpha))
        per_pair[t] = max(spread, 0.0)
    return _rolling_mean(per_pair, window)


def kyle_lambda(close, volume, window=20) -> np.ndarray:
    """Kyle's λ proxy: rolling regression slope of Δp on signed volume (tick-rule)."""
    close = np.asarray(close, dtype=np.float64)
    volume = np.asarray(volume, dtype=np.float64)
    delta = np.diff(close, prepend=close[0])
    signed_volume = np.sign(delta) * volume
    out = np.full(close.size, np.nan)
    for t in range(window, close.size):
        x = signed_volume[t - window + 1 : t + 1]
        y = delta[t - window + 1 : t + 1]
        var_x = float(np.var(x))
        out[t] = float(np.cov(x, y)[0, 1] / var_x) if var_x > 0.0 else 0.0
    return out


def add_microstructure(ticker_frame: pl.DataFrame, window: int = 20) -> pl.DataFrame:
    """Append the Roll / Corwin–Schultz / Kyle-λ columns to one ticker's date-sorted frame."""
    close = ticker_frame["close"].to_numpy()
    return ticker_frame.with_columns(
        pl.Series("roll_measure", roll_measure(close, window)),
        pl.Series(
            "corwin_schultz",
            corwin_schultz(ticker_frame["high"].to_numpy(), ticker_frame["low"].to_numpy(), window),
        ),
        pl.Series("kyle_lambda", kyle_lambda(close, ticker_frame["volume"].to_numpy(), window)),
    )
