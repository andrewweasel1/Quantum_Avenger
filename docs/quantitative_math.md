# Quantum Sentinel: Quantitative & Mathematical Frameworks

## 1. Dynamic Hydrodynamic Slippage
Do not use fixed-basis-point slippage assumptions in backtesting. Slippage ($S$) expands during illiquid or high-volatility environments and must be modeled as a function of order size ($Q$), rolling market volume ($V$), and rolling volatility ($\sigma$).

The algorithm calculates slippage (in basis points) using the standard hydrodynamic market impact model:
$$ S \approx c \cdot \sigma \cdot \sqrt{\frac{Q}{V}} $$
- $c$: A constant calibration factor.
- **Implementation Constraint:** Enforce a safety override. If the estimated $S > 50.0$ bps, the `Numba` Risk Manager must veto the trade.

## 2. Deflated Sharpe Ratio (DSR)
Generic metrics (Accuracy, standard Sharpe Ratio) are inadequate. The system evaluates strategy tournaments strictly using the Deflated Sharpe Ratio to correct for non-Normal return distributions and Multiple Testing Selection Bias (False Discovery Rate).

The DSR evaluates the standard Sharpe Ratio ($\widehat{SR}$) against a benchmark threshold ($SR_0$) derived from:
- **Skewness ($\gamma_3$)** and **Kurtosis ($\gamma_4$)**: Adjusting for asymmetric tail risks.
- **Minimum Backtest Length (MinBTL):** Ensuring the sample size is statistically significant given the number of strategy variations tested.

Threshold for model promotion to the live trading sandbox: $DSR > 0.95$.

## 3. Asymmetric Financial Loss Function
Standard ML objective functions (like Log-Loss or MSE) treat all errors equally. In trading, a False Positive (FP) initiates a trade that loses capital, whereas a False Negative (FN) is merely a missed opportunity. 

When configuring XGBoost or LightGBM algorithms, implement a custom gradient/hessian objective function that penalizes False Positives significantly higher than False Negatives:
$$ Penalty(FP) = 5 \times Penalty(FN) $$
This mathematically forces the model to prioritize capital preservation and drawdown control over maximum hit rate.

## 4. Volatility Regime Tagging
To determine dynamic lookback windows for cross-asset correlation, the system continuously tracks market regimes. 
- A 15-minute rolling volatility is computed. 
- This value is compared against the 80th percentile of its historical rolling distribution.
- If the current metric exceeds the 80th percentile, the regime state flips to `high_vol`, dynamically shortening calculation lookback windows to prioritize recent, highly volatile price action over stale historical data.