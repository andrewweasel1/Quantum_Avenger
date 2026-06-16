"""Sentiment feature stage: anonymize -> score -> causal daily aggregate -> join.

Pipeline position:  news -> [THIS STAGE] -> daily sentiment table
                                                  |
                          feature_compiler / build_training_frame  (cheap join)

Decoupled from the per-asset math pass so the (heavy) FinBERT engine runs once in
a bounded batch rather than inside every Dask partition. Dependency-injected:
hand it a ``SentimentEngine`` (``score_headlines`` -> ``SentimentScore`` with
``.signed`` / ``.confidence``) and an ``Anonymizer`` (``anonymize_batch`` ->
results with ``.text``), so the vectorized temporal logic is unit-testable with
deterministic fakes.

Look-ahead discipline (G5): news at timestamp tau is assigned to the first
SESSION whose close it precedes; post-close news rolls to the next trading day.
The resulting ``sentiment[D]`` is "information available by the close of D". The
final t+1 shift that turns a feature into a tradeable signal happens downstream
(the label/signal stage and build_observation_matrix's lag) -- never shift twice.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

_DAILY_COLUMNS = [
    "date", "ticker", "sentiment", "sent_confidence", "news_count", "sentiment_dispersion",
]


@dataclass(frozen=True)
class SentimentStageConfig:
    tz: str = "America/New_York"
    session_close_hour: int = 16  # post-16:00 local news rolls to the next session
    halflife_days: float = 3.0  # decay of stale sentiment toward neutral
    mask_for_scorer: bool = False  # FinBERT trained WITH names; mask only for the LLM
    batch_size: int = 64


class SentimentFeatureBuilder:
    """Vectorized news -> daily sentiment table; engine + anonymizer injected."""

    def __init__(self, anonymizer, engine, config: SentimentStageConfig | None = None) -> None:
        self.anonymizer = anonymizer
        self.engine = engine
        self.cfg = config or SentimentStageConfig()

    # ------------------------------------------------------------------ public
    def build_daily_sentiment(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """``news_df``: ['timestamp', 'text', and ('ticker' or 'tickers'[list])].
        Returns tidy ['date','ticker','sentiment','sent_confidence','news_count',
        'sentiment_dispersion']."""
        if news_df.empty:
            return pd.DataFrame(columns=_DAILY_COLUMNS)

        df = news_df.copy()
        ts = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert(self.cfg.tz)

        # 1. Anonymize once (audit map + multi-entity resolution).
        results = self.anonymizer.anonymize_batch(df["text"].astype(str).tolist())
        clean = [r.text for r in results]
        # Score raw text by default (FinBERT prior); masked text only if requested.
        text_for_scorer = clean if self.cfg.mask_for_scorer else df["text"].astype(str).tolist()

        # 2. Score per document.
        scores = self.engine.score_headlines(text_for_scorer, batch_size=self.cfg.batch_size)
        df["sentiment"] = np.fromiter(
            (s.signed for s in scores), dtype=np.float64, count=len(scores)
        )
        df["confidence"] = np.fromiter(
            (s.confidence for s in scores), dtype=np.float64, count=len(scores)
        )

        # 3. Causal session assignment (vectorized).
        df["effective_date"] = self._effective_session_date(ts)

        # 4. Explode multi-ticker articles AFTER scoring (no recompute).
        if "tickers" in df.columns:
            df = df.explode("tickers").rename(columns={"tickers": "ticker"})
        df = df.dropna(subset=["ticker"])

        # 5. Confidence-weighted daily aggregation.
        df["_w_signed"] = df["sentiment"] * df["confidence"]
        grp = df.groupby(["ticker", "effective_date"], sort=False)
        agg = grp.agg(
            _wsum=("_w_signed", "sum"),
            _csum=("confidence", "sum"),
            news_count=("sentiment", "size"),
            sentiment_dispersion=("sentiment", "std"),
        ).reset_index()

        agg["sentiment"] = np.where(agg["_csum"] > 0, agg["_wsum"] / agg["_csum"], 0.0)
        agg["sent_confidence"] = agg["_csum"] / agg["news_count"]
        agg["sentiment_dispersion"] = agg["sentiment_dispersion"].fillna(0.0)  # single-item day
        agg = agg.rename(columns={"effective_date": "date"})
        return agg[_DAILY_COLUMNS]

    def attach_to_bars(self, bars_df: pd.DataFrame, daily_sentiment: pd.DataFrame) -> pd.DataFrame:
        """Left-join daily sentiment onto price bars and fill no-news days with
        exponentially decayed prior sentiment + a staleness counter.
        Contemporaneous join only -- the t+1 signal shift is downstream."""
        bars = bars_df.copy()
        bars["date"] = pd.to_datetime(bars["date"]).dt.normalize()
        ds = daily_sentiment.copy()
        ds["date"] = pd.to_datetime(ds["date"]).dt.normalize()

        merged = bars.merge(ds, on=["ticker", "date"], how="left").sort_values(["ticker", "date"])
        merged["sentiment_raw"] = merged["sentiment"]  # NaN on no-news days
        merged["news_count"] = merged["news_count"].fillna(0).astype(int)
        merged["sentiment_dispersion"] = merged["sentiment_dispersion"].fillna(0.0)
        return self._decay_fill(merged)

    # ----------------------------------------------------------------- private
    def _effective_session_date(self, ts: pd.Series) -> pd.Series:
        """Pre-close news -> same session (rolled off weekends); post-close ->
        next business day. Pass an exchange holiday calendar in production."""
        local_dates = ts.dt.normalize().values.astype("datetime64[D]")
        after_close = (ts.dt.hour >= self.cfg.session_close_hour).values
        same = np.busday_offset(local_dates, 0, roll="forward")
        nextb = np.busday_offset(local_dates, 1, roll="forward")
        eff = np.where(after_close, nextb, same)
        return pd.to_datetime(eff)

    def _decay_fill(self, merged: pd.DataFrame) -> pd.DataFrame:
        """Per ticker: carry the last observed sentiment but decay it toward
        neutral with a half-life, exposing staleness. Stale news must not read as
        today's signal, so we never raw-ffill."""
        g = merged.groupby("ticker", sort=False)
        last_valid = g["sentiment_raw"].ffill()
        last_conf = g["sent_confidence"].ffill()

        has_news = merged["sentiment_raw"].notna()
        block = has_news.groupby(merged["ticker"]).cumsum()  # increments on each news day
        staleness = merged.groupby(["ticker", block]).cumcount().astype(float)

        decay = np.power(0.5, staleness / self.cfg.halflife_days)
        merged["sentiment"] = (last_valid * decay).fillna(0.0)  # no prior news -> neutral
        merged["sent_confidence"] = (last_conf * decay).fillna(0.0)
        merged["sentiment_staleness"] = staleness.where(has_news.cumsum() > 0, np.nan)
        return merged
