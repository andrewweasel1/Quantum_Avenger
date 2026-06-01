# Phase 6: Dashboard & Monitoring - Detailed Specification

**Duration**: 2 weeks  
**Target Date**: Complete by mid-August (after Phase 5)  
**Success Criteria**: Real-time dashboard live; KPI updates streaming; veto ledger displayed; trade log queryable; 85%+ test coverage

---

## 1. Phase 6 Architecture Overview

### 1.1 System Context (Unified Monitoring & Observability)

```
┌────────────────────────────────────────────────────────────────────┐
│  PHASES 1-5 (Complete): Infrastructure through Live Execution     │
├────────────────────────────────────────────────────────────────────┤
│                           │                                         │
│                           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  PHASE 6: DASHBOARD & MONITORING - UNIFIED VISIBILITY       │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  LAYER 0: DATA PIPELINE (Real-time Streaming)              │  │
│  │  ├─ Veto ledger (Parquet, append-only)                     │  │
│  │  ├─ Trade log (fills, slippage, P&L)                       │  │
│  │  ├─ Position updates (every 100ms)                         │  │
│  │  ├─ Market data feed (price, volume, volatility)           │  │
│  │  └─ Performance metrics (Sharpe, drawdown, win rate)        │  │
│  │                                                              │  │
│  │  LAYER 1: STREAMLIT DASHBOARD (Multi-page)                 │  │
│  │  ├─ Page 1: LIVE MONITOR                                   │  │
│  │  │  ├─ KPI cards (equity, P&L, Sharpe, max DD)            │  │
│  │  │  ├─ Equity curve (real-time chart)                      │  │
│  │  │  ├─ Current positions (table)                           │  │
│  │  │  ├─ Live P&L by position                                │  │
│  │  │  └─ System alerts (anomalies)                           │  │
│  │  │                                                          │  │
│  │  ├─ Page 2: VETO ANALYSIS                                  │  │
│  │  │  ├─ Rejection rate by gate                              │  │
│  │  │  ├─ Top veto reasons (bar chart)                        │  │
│  │  │  ├─ Veto timeline (history)                             │  │
│  │  │  ├─ Symbol rejection breakdown                          │  │
│  │  │  └─ Veto statistics (D/W/M)                             │  │
│  │  │                                                          │  │
│  │  ├─ Page 3: TRADE LOG                                      │  │
│  │  │  ├─ Trade table (sortable, filterable)                  │  │
│  │  │  ├─ Fill details (price, size, commission)              │  │
│  │  │  ├─ Trade P&L (realized, unrealized)                    │  │
│  │  │  ├─ Trade analytics (Sharpe per trade)                  │  │
│  │  │  └─ Trade search (date range, symbol, P&L)              │  │
│  │  │                                                          │  │
│  │  ├─ Page 4: MODEL REGISTRY                                 │  │
│  │  │  ├─ Active champions (sector → model)                   │  │
│  │  │  ├─ Model statistics (DSR, Sharpe, sector)              │  │
│  │  │  ├─ Promotion history (timeline)                        │  │
│  │  │  ├─ Model performance (live vs backtest)                │  │
│  │  │  └─ Model parameters (hyperparameters)                  │  │
│  │  │                                                          │  │
│  │  ├─ Page 5: RISK DASHBOARD                                 │  │
│  │  │  ├─ Account equity + drawdown                           │  │
│  │  │  ├─ Position sizing compliance (vs Kelly)               │  │
│  │  │  ├─ Liquidity assessment (ADV coverage)                 │  │
│  │  │  ├─ Correlation matrix (sector exposures)               │  │
│  │  │  ├─ VaR (Value at Risk) estimation                      │  │
│  │  │  └─ Stress scenarios (rate shock, vol shock)            │  │
│  │  │                                                          │  │
│  │  ├─ Page 6: SETTINGS & CONFIGURATION                       │  │
│  │  │  ├─ Update risk thresholds                              │  │
│  │  │  ├─ Toggle sectors on/off                               │  │
│  │  │  ├─ Download reports (PDF, CSV)                         │  │
│  │  │  ├─ API key management                                  │  │
│  │  │  └─ Notification settings                               │  │
│  │  │                                                          │  │
│  │  └─ SIDEBAR: Navigation + Filters                          │  │
│  │     ├─ Date range picker                                   │  │
│  │     ├─ Symbol selector                                     │  │
│  │     ├─ Sector filter                                       │  │
│  │     └─ View refresh rate                                   │  │
│  │                                                              │  │
│  │  LAYER 2: ALERTING & NOTIFICATIONS                         │  │
│  │  ├─ Real-time alerts (email, Slack, webhook)              │  │
│  │  ├─ Alert types: Execution error, liquidation risk, etc.   │  │
│  │  ├─ Configurable thresholds (drawdown, VaR, etc.)         │  │
│  │  └─ Alert ledger (all alerts logged)                       │  │
│  │                                                              │  │
│  │  LAYER 3: DATA EXPORT & REPORTING                          │  │
│  │  ├─ Download trade log (CSV, Parquet)                      │  │
│  │  ├─ Export performance report (PDF)                        │  │
│  │  ├─ Generate tearsheets (daily/weekly/monthly)             │  │
│  │  ├─ Email reports (scheduled)                              │  │
│  │  └─ API endpoints (real-time metrics)                      │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│       Uses all Phases 1-5 + Real-time data streams                │
│       Produces: Performance dashboards, alerts, reports            │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

```
/new_pipeline/monitoring/          # ✨ NEW: Monitoring module
├── __init__.py
├── dashboard.py                   # ✨ NEW: Streamlit app
├── pages/
│   ├── __init__.py
│   ├── 01_live_monitor.py         # ✨ NEW: Real-time KPIs
│   ├── 02_veto_analysis.py        # ✨ NEW: Rejection patterns
│   ├── 03_trade_log.py            # ✨ NEW: Trade history
│   ├── 04_model_registry.py       # ✨ NEW: Champion models
│   ├── 05_risk_dashboard.py       # ✨ NEW: Risk metrics
│   └── 06_settings.py             # ✨ NEW: Configuration
├── components/
│   ├── __init__.py
│   ├── kpi_cards.py               # ✨ NEW: Metric cards
│   ├── charts.py                  # ✨ NEW: Visualization helpers
│   ├── alerts.py                  # ✨ NEW: Alert system
│   └── data_loaders.py            # ✨ NEW: Cached data fetching
├── data_pipeline.py               # ✨ NEW: Real-time streaming
├── alert_engine.py                # ✨ NEW: Alert triggering
├── report_generator.py            # ✨ NEW: PDF/CSV export
└── tests/
    ├── test_dashboard.py
    ├── test_pages.py
    ├── test_alerts.py
    ├── test_report_generator.py
    └── benchmarks/
        ├── bench_streamlit_render.py
        └── bench_data_loading.py
```

---

## 2. Real-Time Data Pipeline

### 2.1 Theory: Streaming Architecture

**Problem**: Dashboard must update every 100ms without reloading page

**Solution**: Multi-tier caching with Parquet append-only logs
- Veto ledger: Append-only Parquet (fast writes)
- Trade log: Append-only Parquet (fast writes)
- KPI metrics: Cached in-memory (updated every 1 sec)
- Charts: Polars lazy-frames (computed on-demand)

### 2.2 Module: `monitoring/data_pipeline.py`

**File: `monitoring/data_pipeline.py`**

#### 2.2.1 Real-Time Data Manager

**Class: `RealtimeDataManager`**

```python
import polars as pl
from pathlib import Path
from typing import Dict, List, Optional
import time

class RealtimeDataManager:
    """Manage real-time data streaming for dashboard.
    
    Purpose:
        - Load veto ledger (append-only)
        - Load trade log (append-only)
        - Compute KPI metrics (cached)
        - Serve data to Streamlit with minimal latency
    
    Methods:
        get_veto_ledger: Load recent veto records.
        get_trade_log: Load recent trades.
        get_kpi_metrics: Get portfolio metrics.
        get_equity_curve: Get cumulative returns.
    """
    
    def __init__(self, config: AppConfig):
        """Initialize data manager.
        
        Args:
            config: AppConfig with paths.
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # Cache settings
        self.cache_ttl = 1.0  # 1 second cache
        self.cache = {}
        self.cache_timestamp = {}
        
        # Data paths
        self.veto_ledger_path = f"{config.execution.ledger_dir}/veto_ledger.parquet"
        self.trade_log_path = f"{config.execution.ledger_dir}/trade_log.parquet"
        self.position_log_path = f"{config.execution.ledger_dir}/position_log.parquet"
    
    def get_veto_ledger(
        self,
        window_days: int = 7,
        use_cache: bool = True
    ) -> pl.DataFrame:
        """Load veto ledger for recent period.
        
        Args:
            window_days: Days back to query.
            use_cache: Use cache if fresh.
        
        Returns:
            Polars DataFrame with columns:
            - timestamp (datetime)
            - symbol (str)
            - signal (str)
            - entry_price (f64)
            - veto_reason (str)
            - veto_gate (str)
            - position_size (i32)
            - execution_id (str)
        """
        cache_key = f"veto_ledger_{window_days}"
        
        # Check cache
        if use_cache and self._is_cache_fresh(cache_key):
            return self.cache[cache_key]
        
        # Load from Parquet
        if not Path(self.veto_ledger_path).exists():
            return pl.DataFrame()
        
        df = pl.read_parquet(self.veto_ledger_path)
        
        # Filter by date
        cutoff = pl.datetime_range(
            start=pl.datetime.now() - pl.timedelta(days=window_days),
            end=pl.datetime.now(),
            interval="1d"
        )
        
        df = df.filter(pl.col("timestamp") >= cutoff[0])
        
        # Cache
        self.cache[cache_key] = df
        self.cache_timestamp[cache_key] = time.time()
        
        self.logger.debug(f"Loaded {len(df)} veto records")
        
        return df
    
    def get_trade_log(
        self,
        window_days: int = 7,
        use_cache: bool = True
    ) -> pl.DataFrame:
        """Load trade log for recent period.
        
        Args:
            window_days: Days back to query.
            use_cache: Use cache if fresh.
        
        Returns:
            Polars DataFrame with columns:
            - timestamp (datetime)
            - symbol (str)
            - side (str)
            - qty (i32)
            - fill_price (f64)
            - commission (f64)
            - exit_price (f64, optional)
            - pnl (f64)
            - pnl_pct (f64)
        """
        cache_key = f"trade_log_{window_days}"
        
        if use_cache and self._is_cache_fresh(cache_key):
            return self.cache[cache_key]
        
        if not Path(self.trade_log_path).exists():
            return pl.DataFrame()
        
        df = pl.read_parquet(self.trade_log_path)
        
        # Filter by date
        cutoff = pl.datetime.now() - pl.timedelta(days=window_days)
        df = df.filter(pl.col("timestamp") >= cutoff)
        
        self.cache[cache_key] = df
        self.cache_timestamp[cache_key] = time.time()
        
        self.logger.debug(f"Loaded {len(df)} trades")
        
        return df
    
    def get_kpi_metrics(self, use_cache: bool = True) -> Dict[str, float]:
        """Get current portfolio KPI metrics.
        
        Returns:
            {
                'total_equity': float,
                'total_pnl': float,
                'total_pnl_pct': float,
                'cash': float,
                'buying_power': float,
                'sharpe_ratio': float (annualized),
                'max_drawdown': float,
                'win_rate': float,
                'avg_win': float,
                'avg_loss': float,
                'profit_factor': float,
                'num_trades': int,
                'timestamp': datetime
            }
        """
        cache_key = "kpi_metrics"
        
        if use_cache and self._is_cache_fresh(cache_key):
            return self.cache[cache_key]
        
        # Query trade log
        trade_df = self.get_trade_log(window_days=365, use_cache=False)
        
        if len(trade_df) == 0:
            metrics = {
                'total_equity': 0.0,
                'total_pnl': 0.0,
                'total_pnl_pct': 0.0,
                'cash': 0.0,
                'buying_power': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'num_trades': 0,
                'timestamp': pl.datetime.now()
            }
            self.cache[cache_key] = metrics
            self.cache_timestamp[cache_key] = time.time()
            return metrics
        
        # Compute metrics
        pnl_series = trade_df['pnl'].to_numpy()
        
        total_equity = self.config.execution.account_capital + pnl_series.sum()
        total_pnl = pnl_series.sum()
        total_pnl_pct = (total_pnl / self.config.execution.account_capital) * 100
        
        # Sharpe ratio (annualized)
        daily_returns = pnl_series / self.config.execution.account_capital
        sharpe = (np.mean(daily_returns) / np.std(daily_returns, ddof=1)) * np.sqrt(252) if len(daily_returns) > 1 else 0.0
        
        # Drawdown
        cumulative = np.cumsum(pnl_series)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_dd = np.abs(np.min(drawdown)) if len(drawdown) > 0 else 0.0
        
        # Win rate
        wins = np.sum(pnl_series > 0)
        losses = np.sum(pnl_series < 0)
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0.0
        
        # Profit factor
        gross_profit = np.sum(pnl_series[pnl_series > 0])
        gross_loss = np.abs(np.sum(pnl_series[pnl_series < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
        
        avg_win = np.mean(pnl_series[pnl_series > 0]) if np.sum(pnl_series > 0) > 0 else 0.0
        avg_loss = np.mean(pnl_series[pnl_series < 0]) if np.sum(pnl_series < 0) > 0 else 0.0
        
        metrics = {
            'total_equity': float(total_equity),
            'total_pnl': float(total_pnl),
            'total_pnl_pct': float(total_pnl_pct),
            'cash': self.config.execution.account_capital - total_equity,
            'buying_power': self.config.execution.account_capital * 0.95,  # 95% utilization
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_dd),
            'win_rate': float(win_rate),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'profit_factor': float(profit_factor),
            'num_trades': len(trade_df),
            'timestamp': pl.datetime.now()
        }
        
        self.cache[cache_key] = metrics
        self.cache_timestamp[cache_key] = time.time()
        
        return metrics
    
    def get_equity_curve(self, window_days: int = 30) -> pl.DataFrame:
        """Get equity curve over time.
        
        Returns:
            DataFrame with columns:
            - timestamp (datetime)
            - equity (f64)
            - cumulative_pnl (f64)
            - drawdown (f64)
        """
        cache_key = f"equity_curve_{window_days}"
        
        if self._is_cache_fresh(cache_key):
            return self.cache[cache_key]
        
        trade_df = self.get_trade_log(window_days=window_days, use_cache=False)
        
        if len(trade_df) == 0:
            return pl.DataFrame()
        
        # Group by date
        daily_pnl = trade_df.group_by(
            pl.col("timestamp").cast(pl.Date)
        ).agg(
            pl.col("pnl").sum().alias("daily_pnl")
        ).sort("timestamp")
        
        # Compute cumulative
        daily_pnl = daily_pnl.with_columns(
            pl.col("daily_pnl").cumsum().alias("cumulative_pnl")
        ).with_columns(
            (
                self.config.execution.account_capital + 
                pl.col("cumulative_pnl")
            ).alias("equity")
        )
        
        # Compute drawdown
        daily_pnl = daily_pnl.with_columns(
            (
                (
                    pl.col("equity") - 
                    pl.col("equity").max().over(pl.all())
                ) / pl.col("equity").max().over(pl.all())
            ).alias("drawdown")
        )
        
        self.cache[cache_key] = daily_pnl
        self.cache_timestamp[cache_key] = time.time()
        
        return daily_pnl
    
    def _is_cache_fresh(self, cache_key: str) -> bool:
        """Check if cache is still valid.
        
        Args:
            cache_key: Cache key to check.
        
        Returns:
            True if cache exists and is fresh (< 1 second old).
        """
        if cache_key not in self.cache_timestamp:
            return False
        
        age = time.time() - self.cache_timestamp[cache_key]
        return age < self.cache_ttl
    
    def invalidate_cache(self) -> None:
        """Clear all caches (on new trade/veto)."""
        self.cache = {}
        self.cache_timestamp = {}
        self.logger.debug("Cache invalidated")
```

---

## 3. Streamlit Dashboard Main App

### 3.1 Module: `monitoring/dashboard.py`

**File: `monitoring/dashboard.py`**

#### 3.1.1 Dashboard Configuration & Layout

**Function: `configure_dashboard()`**

```python
import streamlit as st
from pathlib import Path

def configure_dashboard() -> None:
    """Configure Streamlit page settings and theme.
    
    Settings:
        - Page layout: wide (maximize space)
        - Theme: dark (better for trading)
        - Title: Quantum Avenger Live Dashboard
        - Icon: 🚀
    """
    st.set_page_config(
        page_title="Quantum Avenger Live Dashboard",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Theme settings
    st.markdown(
        """
        <style>
        [data-testid="stMetricValue"] {
            font-size: 32px;
        }
        [data-testid="stMetricLabel"] {
            font-size: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
```

#### 3.1.2 Sidebar Navigation & Filters

**Function: `render_sidebar()`**

```python
def render_sidebar() -> Dict[str, any]:
    """Render sidebar with navigation and filters.
    
    Returns:
        {
            'page': str (selected page),
            'date_range': (start_date, end_date),
            'symbols': List[str],
            'sectors': List[str],
            'refresh_rate': int (seconds)
        }
    """
    st.sidebar.title("🚀 Quantum Avenger")
    
    # Navigation
    page = st.sidebar.radio(
        "Select Page",
        [
            "01 - Live Monitor",
            "02 - Veto Analysis",
            "03 - Trade Log",
            "04 - Model Registry",
            "05 - Risk Dashboard",
            "06 - Settings"
        ]
    )
    
    st.sidebar.divider()
    
    # Date range filter
    st.sidebar.subheader("📅 Date Range")
    date_range = st.sidebar.date_input(
        "Select dates",
        value=(
            pd.Timestamp.now() - pd.Timedelta(days=7),
            pd.Timestamp.now()
        ),
        max_value=pd.Timestamp.now()
    )
    
    # Symbol filter
    st.sidebar.subheader("📊 Symbols")
    all_symbols = ["All", "AAPL", "MSFT", "GOOG", "TSLA", "AMZN"]
    selected_symbols = st.sidebar.multiselect(
        "Select symbols",
        all_symbols,
        default=["All"]
    )
    
    if "All" in selected_symbols:
        symbols = all_symbols[1:]
    else:
        symbols = selected_symbols
    
    # Sector filter
    st.sidebar.subheader("🏭 Sectors")
    sectors = st.sidebar.multiselect(
        "Select sectors",
        ["Technology", "Finance", "Healthcare", "Energy"],
        default=["Technology", "Finance"]
    )
    
    # Refresh rate
    st.sidebar.subheader("⚡ Performance")
    refresh_rate = st.sidebar.slider(
        "Refresh rate (seconds)",
        min_value=1,
        max_value=10,
        value=1
    )
    
    return {
        'page': page,
        'date_range': date_range,
        'symbols': symbols,
        'sectors': sectors,
        'refresh_rate': refresh_rate
    }
```

---

## 4. KPI Cards Component

### 4.1 Module: `monitoring/components/kpi_cards.py`

**File: `monitoring/components/kpi_cards.py`**

#### 4.1.1 KPI Metric Cards

**Function: `render_kpi_cards()`**

```python
def render_kpi_cards(metrics: Dict[str, float]) -> None:
    """Render top-level KPI cards.
    
    Args:
        metrics: Dictionary from get_kpi_metrics().
    
    Cards:
        1. Total Equity (green/red based on P&L)
        2. Total P&L ($ and %)
        3. Sharpe Ratio (annualized)
        4. Max Drawdown (%)
        5. Win Rate (%)
        6. Profit Factor (>1.5 = good)
    """
    cols = st.columns(6)
    
    # Card 1: Total Equity
    with cols[0]:
        equity_color = "green" if metrics['total_pnl'] > 0 else "red"
        st.metric(
            "💰 Total Equity",
            f"${metrics['total_equity']:,.0f}",
            delta=f"${metrics['total_pnl']:,.0f}",
            delta_color="normal" if metrics['total_pnl'] > 0 else "inverse"
        )
    
    # Card 2: P&L %
    with cols[1]:
        st.metric(
            "📈 P&L %",
            f"{metrics['total_pnl_pct']:.2f}%",
            delta=f"{metrics['total_pnl']:.0f} USD"
        )
    
    # Card 3: Sharpe Ratio
    with cols[2]:
        sharpe_color = "normal" if metrics['sharpe_ratio'] > 1.0 else "inverse"
        st.metric(
            "⚡ Sharpe Ratio",
            f"{metrics['sharpe_ratio']:.2f}",
            delta="Good ✓" if metrics['sharpe_ratio'] > 1.0 else "Needs tuning"
        )
    
    # Card 4: Max Drawdown
    with cols[3]:
        st.metric(
            "📉 Max Drawdown",
            f"{metrics['max_drawdown']*100:.2f}%",
            delta="Within limits" if metrics['max_drawdown'] < 0.20 else "⚠️ Warning"
        )
    
    # Card 5: Win Rate
    with cols[4]:
        st.metric(
            "🎯 Win Rate",
            f"{metrics['win_rate']*100:.1f}%",
            delta=f"{metrics['num_trades']} trades"
        )
    
    # Card 6: Profit Factor
    with cols[5]:
        pf_status = "Good ✓" if metrics['profit_factor'] > 1.5 else "Monitor"
        st.metric(
            "📊 Profit Factor",
            f"{metrics['profit_factor']:.2f}",
            delta=pf_status
        )
```

---

## 5. Live Monitor Page

### 5.1 Module: `monitoring/pages/01_live_monitor.py`

**File: `monitoring/pages/01_live_monitor.py`**

```python
import streamlit as st
from monitoring.data_pipeline import RealtimeDataManager
from monitoring.components.kpi_cards import render_kpi_cards
from monitoring.components.charts import (
    render_equity_curve,
    render_position_heatmap,
    render_pnl_timeline
)

def page_live_monitor(config: AppConfig, filters: Dict) -> None:
    """Live monitoring page with real-time metrics.
    
    Layout:
        1. KPI cards (top)
        2. Equity curve chart (left, 2/3 width)
        3. Current positions table (right, 1/3 width)
        4. P&L timeline (bottom left)
        5. System alerts (bottom right)
    """
    st.title("🔴 Live Monitor")
    
    # Initialize data manager
    data_mgr = RealtimeDataManager(config)
    
    # Get metrics
    metrics = data_mgr.get_kpi_metrics(use_cache=True)
    
    # Row 1: KPI cards
    render_kpi_cards(metrics)
    
    st.divider()
    
    # Row 2: Charts
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Equity Curve")
        equity_df = data_mgr.get_equity_curve(window_days=30)
        render_equity_curve(equity_df)
    
    with col_right:
        st.subheader("💼 Current Positions")
        # Load position table (placeholder)
        positions = get_current_positions()
        st.dataframe(
            positions,
            use_container_width=True,
            hide_index=True
        )
    
    st.divider()
    
    # Row 3: P&L timeline + alerts
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📊 P&L Timeline")
        trade_df = data_mgr.get_trade_log(window_days=7)
        render_pnl_timeline(trade_df)
    
    with col_right:
        st.subheader("🚨 System Alerts")
        alerts = get_recent_alerts()
        if len(alerts) > 0:
            for alert in alerts[:5]:
                with st.container(border=True):
                    st.markdown(f"**{alert['type']}** @ {alert['timestamp']}")
                    st.write(alert['message'])
        else:
            st.info("✓ No alerts")
    
    # Auto-refresh
    st.divider()
    placeholder = st.empty()
    with placeholder.container():
        st.caption(f"Last updated: {pd.Timestamp.now().strftime('%H:%M:%S')}")
    
    import time
    time.sleep(filters.get('refresh_rate', 1))
    st.rerun()

def get_current_positions() -> pl.DataFrame:
    """Fetch current open positions from portfolio."""
    # Placeholder
    return pl.DataFrame({
        'Symbol': ['AAPL', 'MSFT'],
        'Qty': [100, 50],
        'Entry': [150.0, 300.0],
        'Current': [151.5, 305.0],
        'P&L': [150.0, 250.0]
    })

def get_recent_alerts() -> List[Dict]:
    """Fetch recent system alerts."""
    # Placeholder
    return []
```

---

## 6. Veto Analysis Page

### 6.1 Module: `monitoring/pages/02_veto_analysis.py`

```python
import streamlit as st
import plotly.express as px

def page_veto_analysis(config: AppConfig, filters: Dict) -> None:
    """Analyze veto patterns and rejection reasons.
    
    Sections:
        1. Rejection rate (pie chart)
        2. Top veto gates (bar chart)
        3. Top reasons (bar chart)
        4. Symbol-level rejections (heatmap)
        5. Veto timeline (area chart)
        6. Detailed veto ledger (table)
    """
    st.title("🚫 Veto Analysis")
    
    data_mgr = RealtimeDataManager(config)
    veto_df = data_mgr.get_veto_ledger(window_days=filters.get('days', 7))
    
    if len(veto_df) == 0:
        st.info("No veto records found")
        return
    
    st.subheader("📊 Veto Statistics")
    
    # Row 1: Summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Vetoes", len(veto_df))
    
    with col2:
        unique_symbols = veto_df['symbol'].n_unique()
        st.metric("Symbols Affected", unique_symbols)
    
    with col3:
        unique_reasons = veto_df['veto_reason'].n_unique()
        st.metric("Unique Reasons", unique_reasons)
    
    with col4:
        veto_rate = (len(veto_df) / 100) * 100  # Placeholder
        st.metric("Veto Rate", f"{veto_rate:.1f}%")
    
    st.divider()
    
    # Row 2: Charts
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🚪 Rejections by Gate")
        gate_counts = veto_df['veto_gate'].value_counts()
        fig = px.bar(
            x=gate_counts.index,
            y=gate_counts.values,
            labels={'x': 'Gate', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("❌ Top Veto Reasons")
        reason_counts = veto_df['veto_reason'].value_counts().head(10)
        fig = px.bar(
            y=reason_counts.index,
            x=reason_counts.values,
            orientation='h',
            labels={'x': 'Count', 'y': 'Reason'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Row 3: Detailed ledger
    st.subheader("📋 Veto Ledger")
    st.dataframe(
        veto_df.select([
            'timestamp', 'symbol', 'signal', 'veto_gate', 'veto_reason'
        ]).to_pandas(),
        use_container_width=True,
        hide_index=True
    )
```

---

## 7. Trade Log Page

### 7.1 Module: `monitoring/pages/03_trade_log.py`

```python
import streamlit as st
import pandas as pd

def page_trade_log(config: AppConfig, filters: Dict) -> None:
    """Trade history and analysis.
    
    Features:
        1. Trade table (sortable, filterable)
        2. Trade statistics
        3. Trade search (by symbol, date, P&L)
        4. Trade detail view (click to expand)
    """
    st.title("📝 Trade Log")
    
    data_mgr = RealtimeDataManager(config)
    trade_df = data_mgr.get_trade_log(window_days=30)
    
    if len(trade_df) == 0:
        st.info("No trades yet")
        return
    
    # Summary stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Trades", len(trade_df))
    
    with col2:
        winning = (trade_df['pnl'] > 0).sum()
        st.metric("Winning", winning)
    
    with col3:
        losing = (trade_df['pnl'] < 0).sum()
        st.metric("Losing", losing)
    
    with col4:
        total_pnl = trade_df['pnl'].sum()
        st.metric("Total P&L", f"${total_pnl:,.0f}")
    
    with col5:
        avg_pnl = trade_df['pnl'].mean()
        st.metric("Avg P&L", f"${avg_pnl:,.0f}")
    
    st.divider()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_symbol = st.selectbox(
            "Filter by symbol",
            ["All"] + sorted(trade_df['symbol'].unique().to_list())
        )
    
    with col2:
        pnl_filter = st.radio(
            "Filter by result",
            ["All", "Winners", "Losers"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Date (Latest)", "P&L (High)", "P&L (Low)"]
        )
    
    # Apply filters
    filtered_df = trade_df
    
    if selected_symbol != "All":
        filtered_df = filtered_df.filter(pl.col('symbol') == selected_symbol)
    
    if pnl_filter == "Winners":
        filtered_df = filtered_df.filter(pl.col('pnl') > 0)
    elif pnl_filter == "Losers":
        filtered_df = filtered_df.filter(pl.col('pnl') < 0)
    
    # Sort
    if sort_by == "P&L (High)":
        filtered_df = filtered_df.sort('pnl', descending=True)
    elif sort_by == "P&L (Low)":
        filtered_df = filtered_df.sort('pnl', descending=False)
    else:
        filtered_df = filtered_df.sort('timestamp', descending=True)
    
    # Display table
    st.dataframe(
        filtered_df.to_pandas(),
        use_container_width=True,
        hide_index=True
    )
```

---

## 8. Alert System

### 8.1 Module: `monitoring/alert_engine.py`

**File: `monitoring/alert_engine.py`**

```python
from typing import Dict, List, Optional
from enum import Enum

class AlertType(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertEngine:
    """Generate and send real-time alerts.
    
    Methods:
        check_alerts: Evaluate alerting conditions.
        send_alert: Send via email/Slack/webhook.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
    
    def check_alerts(self, metrics: Dict) -> List[Dict]:
        """Check for alerting conditions.
        
        Conditions:
            1. Max drawdown exceeded
            2. Sharpe ratio dropped
            3. Execution error
            4. Liquidity breach
            5. Position sizing violation
        
        Returns:
            List of alerts (if any).
        """
        alerts = []
        
        # Check max drawdown
        max_dd_threshold = self.config.monitoring.max_drawdown_alert
        if metrics['max_drawdown'] > max_dd_threshold:
            alerts.append({
                'type': AlertType.WARNING.value,
                'message': f"Max drawdown {metrics['max_drawdown']:.1%} > threshold {max_dd_threshold:.1%}",
                'timestamp': pd.Timestamp.now()
            })
        
        # Check Sharpe ratio
        sharpe_min = self.config.monitoring.sharpe_min_alert
        if metrics['sharpe_ratio'] < sharpe_min:
            alerts.append({
                'type': AlertType.WARNING.value,
                'message': f"Sharpe ratio {metrics['sharpe_ratio']:.2f} below threshold {sharpe_min:.2f}",
                'timestamp': pd.Timestamp.now()
            })
        
        return alerts
    
    def send_alert(
        self,
        alert: Dict,
        channels: List[str] = ["email", "slack"]
    ) -> None:
        """Send alert via specified channels.
        
        Args:
            alert: Alert dictionary.
            channels: ['email', 'slack', 'webhook'].
        """
        self.logger.warning(f"ALERT: {alert['message']}")
        
        if "email" in channels:
            self._send_email(alert)
        
        if "slack" in channels:
            self._send_slack(alert)
        
        if "webhook" in channels:
            self._send_webhook(alert)
    
    def _send_email(self, alert: Dict) -> None:
        """Send email alert (placeholder)."""
        pass
    
    def _send_slack(self, alert: Dict) -> None:
        """Send Slack alert (placeholder)."""
        pass
    
    def _send_webhook(self, alert: Dict) -> None:
        """Send webhook alert (placeholder)."""
        pass
```

---

## 9. Implementation Checklist - Phase 6

### Week 1: Data Pipeline & Components

- [ ] **Day 1-2**: Real-time data manager
  - [ ] Implement `RealtimeDataManager`
  - [ ] Load veto ledger (Parquet)
  - [ ] Load trade log (Parquet)
  - [ ] Caching strategy (1 sec TTL)

- [ ] **Day 2-3**: KPI computation
  - [ ] Compute Sharpe, drawdown, win rate
  - [ ] Compute equity curve
  - [ ] Unit tests: `test_data_pipeline.py`

- [ ] **Day 3-4**: KPI cards component
  - [ ] Render metric cards
  - [ ] Color coding (green/red)
  - [ ] Delta display

- [ ] **Day 4-5**: Chart components
  - [ ] Equity curve (line chart)
  - [ ] P&L timeline (bar chart)
  - [ ] Veto breakdown (pie chart)

### Week 2: Dashboard Pages & Monitoring

- [ ] **Day 6-7**: Main dashboard app
  - [ ] Streamlit configuration
  - [ ] Sidebar navigation
  - [ ] Page routing

- [ ] **Day 7-8**: Dashboard pages
  - [ ] Live Monitor page (01)
  - [ ] Veto Analysis page (02)
  - [ ] Trade Log page (03)

- [ ] **Day 8-9**: Model Registry + Risk pages
  - [ ] Model Registry page (04)
  - [ ] Risk Dashboard page (05)
  - [ ] Settings page (06)

- [ ] **Day 9-10**: Alerts + optimization
  - [ ] Alert engine
  - [ ] Email/Slack integration
  - [ ] Performance tuning (< 1 sec refresh)
  - [ ] All tests 85%+ coverage

---

## 10. Success Criteria

| Criterion | Test | Expected |
|-----------|------|----------|
| Data pipeline loads | `test_data_load()` | ✓ < 100ms |
| KPI metrics computed | `test_kpi_computation()` | ✓ Correct values |
| Dashboard renders | `test_dashboard_render()` | ✓ No errors |
| Pages load | `test_page_load()` | ✓ All 6 pages work |
| Charts display | `test_chart_render()` | ✓ Interactive |
| Refresh updates | `test_auto_refresh()` | ✓ Every 1 sec |
| Alerts trigger | `test_alert_logic()` | ✓ Correct conditions |
| Export works | `test_export()` | ✓ CSV, PDF generated |

---

## 11. Performance Targets

| Component | Target |
|-----------|--------|
| Dashboard load | < 2 seconds |
| Page render | < 1 second |
| Data refresh | < 100ms |
| Chart rendering | < 500ms |
| Alert checking | < 50ms |

---

## 12. Integration with Phases 1-5 & Handoff to Phase 7

### 12.1 Phase Dependencies

- **Phase 1**: Config, logging, exceptions
- **Phase 2**: Feature engine outputs
- **Phase 3**: Tournament results
- **Phase 4**: DSR thresholds, promotion registry
- **Phase 5**: Veto ledger, trade log, execution data

### 12.2 Outputs for Phase 7 (Hardening)

- Dashboard metrics (for stress testing)
- Performance reports (historical)
- Alert logs (for debugging)

---

## 13. Deliverables Summary - Phase 6

### Codebase
- [ ] `/new_pipeline/monitoring/dashboard.py` (200+ lines)
- [ ] `/new_pipeline/monitoring/data_pipeline.py` (400+ lines)
- [ ] `/new_pipeline/monitoring/pages/*.py` (1000+ lines total)
- [ ] `/new_pipeline/monitoring/components/*.py` (500+ lines total)
- [ ] `/new_pipeline/monitoring/alert_engine.py` (150+ lines)
- [ ] 80+ unit tests

### Live Dashboard
- [ ] Streamlit app running on port 8501
- [ ] 6 interactive pages
- [ ] Real-time metrics updating
- [ ] Alert system functional
- [ ] Export capabilities (CSV, PDF)

### Performance
- [ ] Dashboard load < 2 sec
- [ ] Page render < 1 sec
- [ ] Data refresh < 100ms
- [ ] 85%+ test coverage

---

**Next**: After Phase 6 completion, proceed to [Phase 7: Production Hardening & Deployment](PHASE_7_SPECIFICATION.md) (to be created).

**Previous Phases**:
- [Phase 1: Core Pipeline Infrastructure](PHASE_1_SPECIFICATION.md)
- [Phase 2: Vectorized Quant Engine & Shields](PHASE_2_SPECIFICATION.md)
- [Phase 3: Tournament Backtesting & Model Selection](PHASE_3_SPECIFICATION.md)
- [Phase 4: Statistical Evaluation & Promotion](PHASE_4_SPECIFICATION.md)
- [Phase 5: Live Execution & Orchestration](PHASE_5_SPECIFICATION.md)
