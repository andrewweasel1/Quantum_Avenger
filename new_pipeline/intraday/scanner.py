"""Scanner signals and ranking variants for the intraday stack.

Every signal is causal at the session open (09:30): built from strictly-prior
daily aggregates, except the session OPEN price itself, which is known before
any opening range completes. `build_signal_frame` materializes the whole menu
once per run; `scan_day` ranks the eligible set under a named weighting.

The weightings in :data:`VARIANTS` are the scanner's TRIAL FAMILY — running
more than one in an official run multiplies the trial count the deflation
must pay for, exactly like the ORB construction axes. They are pre-registered
here rather than searched ad hoc.
"""

from __future__ import annotations

import numpy as np
import polars as pl

# name -> whether a HIGH value is the preferred end of the ranking.
SIGNALS: dict[str, bool] = {
    "gap_abs": True,        # |open vs prior close| — overnight dislocation
    "gap_up": True,         # signed gap (long-only ORB wants upside dislocation)
    "rvol": True,           # prior-day dollar volume vs its own 20d median
    "adv_dollar": True,     # 20d median dollar volume — depth
    "price": True,          # prior close; higher price = tighter relative spread
    "atr_pct": True,        # 20d mean (high-low)/close — room for a breakout to run
    "range_pct": True,      # prior-day range/close — yesterday's expansion
    "spread_bps": False,    # Corwin-Schultz estimate — LOW is tradable (cost)
    "ret_5d": True,         # 5-session momentum context
    "gap_vs_market": True,  # gap net of the equal-weight market gap (idiosyncratic)
}

# Pre-registered scanner weightings. "attention" reproduces the v1 default.
# The union pseudo-variants: not weightings but consensus aggregations of
# several, resolved in scan_day_union / scan_day_union_v2.
UNION_VARIANT = "union"
UNION_V2_VARIANT = "union_v2"
UNION_MEMBERS = ("attention", "tradable", "cheap_gap")
# union_v2's backbone ranker: the scanner meanrev_v5 showed beats every other
# on 19/32 constructions (43.1 net bps at z2.5 vs 17.7-25.5). v2 exists
# because v1's blended-score tiebreak averaged in the WEAKER rankers' opinions
# and so demoted attention's best idiosyncratic picks.
UNION_V2_PRIMARY = "attention"
# Consensus is drawn from a WIDER per-member window than the final budget.
# It has to be: unanimity within each member's top-N is by construction a
# subset of the primary's own top-N, so filling the remainder from the primary
# would return the primary's list exactly — a no-op. At 2x, names all three
# scanners rate top-100 can be promoted ahead of the primary's own ranks 51+,
# which is the only way the rule can differ from `attention` at all.
UNION_V2_POOL_MULT = 2

VARIANTS: dict[str, dict[str, float]] = {
    "attention": {"gap_abs": 1.0, "rvol": 1.0, "adv_dollar": 1.0},
    "tradable": {"adv_dollar": 1.0, "spread_bps": 1.0, "price": 1.0},
    "dislocation": {"gap_up": 1.0, "gap_vs_market": 1.0, "rvol": 1.0},
    "volatility": {"atr_pct": 1.0, "range_pct": 1.0, "rvol": 1.0},
    "cheap_gap": {"gap_up": 1.0, "spread_bps": 1.0, "adv_dollar": 1.0},
}


def build_signal_frame(daily: pl.DataFrame, window: int = 20) -> pl.DataFrame:
    """(date, ticker, <SIGNALS>, eligible) from session-daily aggregates.

    Trailing statistics are shifted one session so nothing on day T leans on
    day T's own tape; the sole same-day input is ``open``. ``eligible`` applies
    the liquidity/price floors (a name must be tradable before it can rank)."""
    from new_pipeline.features.microstructure import corwin_schultz

    frames = []
    for ticker, sub in daily.sort("date").group_by("ticker", maintain_order=True):
        name = ticker if isinstance(ticker, str) else ticker[0]
        cs = corwin_schultz(sub["high"].to_numpy(), sub["low"].to_numpy(), window=window)
        frames.append(sub.with_columns(
            pl.lit(name).alias("ticker"),
            pl.Series("_cs_bps", np.roll(cs, 1) * 1e4),  # strictly prior
        ))
    if not frames:
        return pl.DataFrame(schema={"date": pl.Date, "ticker": pl.Utf8, "eligible": pl.Boolean,
                                    **{s: pl.Float64 for s in SIGNALS}})
    frame = pl.concat(frames).sort(["ticker", "date"])

    prev = lambda col: pl.col(col).shift(1).over("ticker")  # noqa: E731
    frame = frame.with_columns(
        prev("close").alias("_prev_close"),
        prev("high").alias("_prev_high"),
        prev("low").alias("_prev_low"),
        prev("dollar_vol").alias("_prev_dv"),
        pl.col("dollar_vol").rolling_median(window_size=window).shift(1)
        .over("ticker").alias("_adv"),
        ((pl.col("high") - pl.col("low")) / pl.col("close"))
        .rolling_mean(window_size=window).shift(1).over("ticker").alias("_atr_pct"),
        (pl.col("close") / pl.col("close").shift(5) - 1.0).shift(1)
        .over("ticker").alias("_ret_5d"),
    ).with_columns(
        (pl.col("open") / pl.col("_prev_close") - 1.0).alias("_gap"),
    )
    # Idiosyncratic gap: today's gap net of the cross-section's median gap.
    frame = frame.with_columns(
        (pl.col("_gap") - pl.col("_gap").median().over("date")).alias("_gap_vs_mkt"))

    return frame.select(
        "date", "ticker",
        pl.col("_gap").abs().alias("gap_abs"),
        pl.col("_gap").alias("gap_up"),
        (pl.col("_prev_dv") / pl.col("_adv")).alias("rvol"),
        pl.col("_adv").alias("adv_dollar"),
        pl.col("_prev_close").alias("price"),
        pl.col("_atr_pct").alias("atr_pct"),
        ((pl.col("_prev_high") - pl.col("_prev_low")) / pl.col("_prev_close")).alias("range_pct"),
        pl.col("_cs_bps").alias("spread_bps"),
        pl.col("_ret_5d").alias("ret_5d"),
        pl.col("_gap_vs_mkt").alias("gap_vs_market"),
        pl.lit(True).alias("eligible"),
    )


def apply_floors(signals: pl.DataFrame, min_adv_dollars: float,
                 min_price: float) -> pl.DataFrame:
    return signals.with_columns(
        ((pl.col("adv_dollar") >= min_adv_dollars) & (pl.col("price") >= min_price))
        .fill_null(False).alias("eligible"))


def scan_day(signals: pl.DataFrame, day, top_n: int,
             weights: dict[str, float] | str = "attention") -> list[str]:
    """Top-``top_n`` tickers for ``day`` under a named or explicit weighting.

    Score = weighted mean of cross-sectional percentile ranks, with each
    signal oriented so HIGH percentile is always the preferred end (a
    ``SIGNALS`` entry of False, e.g. spread, is inverted). Ties break by
    ticker so a rerun reproduces the pick list exactly."""
    if weights == UNION_VARIANT:
        return scan_day_union(signals, day, top_n)
    if weights == UNION_V2_VARIANT:
        return scan_day_union_v2(signals, day, top_n)
    scored = score_day(signals, day, weights)
    if scored.is_empty():
        return []
    return (scored.sort(["_score", "ticker"], descending=[True, False])
            ["ticker"].head(top_n).to_list())


def score_day(signals: pl.DataFrame, day, weights: dict | str) -> pl.DataFrame:
    """(ticker, _score) for one session under a weighting. Scores are means of
    cross-sectional percentile ranks, so they are already comparable ACROSS
    weightings — which is what lets the union blend them without rescaling."""
    if isinstance(weights, str):
        weights = VARIANTS[weights]
    day_frame = signals.filter((pl.col("date") == day) & pl.col("eligible"))
    used = [s for s in weights if s in SIGNALS]
    day_frame = day_frame.drop_nulls(used)
    if day_frame.is_empty():
        return pl.DataFrame(schema={"ticker": pl.Utf8, "_score": pl.Float64})
    n = day_frame.height
    total = sum(abs(w) for w in weights.values()) or 1.0
    score = pl.lit(0.0)
    for signal, weight in weights.items():
        pct = pl.col(signal).rank("average") / n
        if not SIGNALS[signal]:  # low-is-better -> invert so high always wins
            pct = 1.0 - pct
        score = score + weight * pct
    return day_frame.with_columns((score / total).alias("_score")).select("ticker", "_score")


def scan_day_union(signals: pl.DataFrame, day, top_n: int,
                   members: tuple[str, ...] = UNION_MEMBERS,
                   per_member_n: int | None = None) -> list[str]:
    """Consensus-first union of several weightings.

    Every member ranks the eligible set; a name's AGREEMENT is how many members
    put it in their own top-``per_member_n``. Picks are ordered by agreement
    first, then by the mean of the member scores (all are percentile means in
    [0, 1], so averaging them needs no rescaling), then by ticker.

    REJECTED by meanrev_v5 — kept for reproducibility, not in the standing
    spec. Priced against its own members it won 0 of 32 constructions and beat
    the best member on none, netting 25.5 bps against `attention`'s 43.1.

    The motivating v4 statistic (2-3 scanner agreement netting 38.6 / 34.0 bps
    against 17.2 for solo picks) pooled events ACROSS the three books, so
    "solo" mixed attention-only picks with the weaker rankers' — it showed
    consensus beating the AVERAGE scanner, not the best one. `attention` alone
    nets 43.1, above the consensus bucket.

    The coverage argument was also wrong: 438 distinct events across three
    50-name scanners versus 275 for one is three scanners' capacity, not a
    property of consensus. A single top-N scanner admits N names however it
    orders them — v5 measured the union at 8,331 events against attention's
    8,685."""
    per_member_n = per_member_n or top_n
    scores, picked = {}, {}
    for member in members:
        frame = score_day(signals, day, member)
        if frame.is_empty():
            continue
        scores[member] = dict(frame.iter_rows())
        picked[member] = set(
            frame.sort(["_score", "ticker"], descending=[True, False])
            ["ticker"].head(per_member_n).to_list())
    if not scores:
        return []
    candidates = set().union(*picked.values()) if picked else set()
    ranked = []
    for ticker in candidates:
        agreement = sum(ticker in sel for sel in picked.values())
        blended = sum(s.get(ticker, 0.0) for s in scores.values()) / len(scores)
        ranked.append((agreement, blended, ticker))
    ranked.sort(key=lambda r: (-r[0], -r[1], r[2]))
    return [ticker for _, _, ticker in ranked[:top_n]]


def _ranked(signals: pl.DataFrame, day, weights) -> list[str]:
    """Full eligible ranking under one weighting, best first."""
    frame = score_day(signals, day, weights)
    if frame.is_empty():
        return []
    return (frame.sort(["_score", "ticker"], descending=[True, False])
            ["ticker"].to_list())


def scan_day_union_v2(signals: pl.DataFrame, day, top_n: int,
                      members: tuple[str, ...] = UNION_MEMBERS,
                      primary: str = UNION_V2_PRIMARY,
                      pool_n: int | None = None) -> list[str]:
    """Unanimous consensus first, then the primary scanner's own order.

    Differs from :func:`scan_day_union` in what breaks ties BELOW the consensus
    tier. v1 used the blended mean of all three member scores, which averages
    in the weaker rankers and demotes the primary's best idiosyncratic picks —
    meanrev_v5 measured the cost: 25.5 net bps against `attention`'s 43.1, and
    a book keeping only 61% of attention's events but 75-76% of the other two's.
    v2 keeps the consensus signal but hands every remaining slot to the primary
    ranker outright, so it can only ever hold consensus names plus attention's
    own picks.

    Consensus is unanimity within each member's top ``pool_n`` (default
    ``UNION_V2_POOL_MULT * top_n``), NOT within top_n. Unanimity at top_n would
    be a subset of the primary's top_n, making the whole rule a no-op that
    returns the primary's list reordered.

    Ordering: consensus names in the primary's rank order, then the primary's
    remaining names in its own order. Ordering only reaches the book through
    ``max_concurrent``, which binds at low entry-z and not at z2.5."""
    pool_n = pool_n or top_n * UNION_V2_POOL_MULT
    rankings = {m: _ranked(signals, day, m) for m in members}
    primary_rank = rankings.get(primary) or _ranked(signals, day, primary)
    if not primary_rank:
        return []
    pools = [set(r[:pool_n]) for r in rankings.values() if r]
    consensus = set.intersection(*pools) if pools else set()
    order = {t: i for i, t in enumerate(primary_rank)}
    # Consensus names the primary cannot rank at all sort last among consensus.
    picks = sorted(consensus, key=lambda t: order.get(t, len(order)))[:top_n]
    seen = set(picks)
    for ticker in primary_rank:
        if len(picks) >= top_n:
            break
        if ticker not in seen:
            picks.append(ticker)
            seen.add(ticker)
    return picks[:top_n]


def signal_ic(ledger: pl.DataFrame, signals: pl.DataFrame,
              outcome: str = "gross_bps", min_names: int = 5) -> dict:
    """Per-session cross-sectional IC of every signal against realized trade
    outcomes — the read-only diagnostic that answers "what should the scanner
    look at?" WITHOUT spending trials. Sessions with fewer than ``min_names``
    trades are skipped (a 2-name cross-section has no rank information).

    Returns {signal: {mean_ic, ic_t_stat, n_sessions, hit_rate}} where
    hit_rate is the share of sessions with a positive IC."""
    joined = ledger.join(signals, left_on=["day", "ticker"], right_on=["date", "ticker"],
                         how="inner")
    out = {}
    for signal in SIGNALS:
        ics = []
        for _, sub in joined.drop_nulls([signal, outcome]).group_by("day"):
            if sub.height < min_names:
                continue
            x = sub[signal].rank("average").to_numpy()
            y = sub[outcome].rank("average").to_numpy()
            if x.std() == 0 or y.std() == 0:
                continue
            ics.append(float(np.corrcoef(x, y)[0, 1]))
        if not ics:
            continue
        arr = np.asarray(ics)
        se = arr.std(ddof=1) / np.sqrt(arr.size) if arr.size > 1 else float("inf")
        out[signal] = {
            "mean_ic": float(arr.mean()),
            "ic_t_stat": float(arr.mean() / se) if se > 0 else 0.0,
            "n_sessions": int(arr.size),
            "hit_rate": float((arr > 0).mean()),
        }
    return dict(sorted(out.items(), key=lambda kv: -abs(kv[1]["mean_ic"])))
