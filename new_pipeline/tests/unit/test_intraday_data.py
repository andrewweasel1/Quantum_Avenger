"""Intraday data plane: minute adapter mapping, session calendar, vault resume."""

from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace

from new_pipeline.adapters.market_alpaca import AlpacaIntradayDataSource
from new_pipeline.intraday.calendar import Session, load_sessions, write_fixture
from new_pipeline.intraday.data import filter_to_sessions, load_minutes, months_between, vault_file
from new_pipeline.scripts.ingest_minute_vault import _write_symbol_month, ingest


def _bar(ts, px, vol=100, vwap=None):
    return SimpleNamespace(timestamp=ts, open=px, high=px + 1, low=px - 1,
                           close=px + 0.5, volume=vol, vwap=vwap)


class _FakeClient:
    def __init__(self):
        self.requests = []

    def get_stock_bars(self, request):
        self.requests.append(request)
        data = {}
        for sym in request.symbol_or_symbols:
            if sym == "EMPTY":
                data[sym] = []
            else:
                data[sym] = [_bar(datetime(2026, 3, 2, 14, 30 + i, tzinfo=UTC), 10.0 + i,
                                  vwap=10.25 + i) for i in range(3)]
        return SimpleNamespace(data=data)


def test_intraday_source_maps_bars_and_batches():
    client = _FakeClient()
    src = AlpacaIntradayDataSource("k", "s", client=client)
    src.BATCH_SIZE = 2
    out = src.history_minutes(["AAA", "BBB", "EMPTY"],
                              datetime(2026, 3, 1, tzinfo=UTC), datetime(2026, 4, 1, tzinfo=UTC))
    assert len(client.requests) == 2  # 2+1 symbols at batch size 2
    assert [b.ts.minute for b in out["AAA"]] == [30, 31, 32]
    assert out["AAA"][0].vwap == 10.25 and out["AAA"][0].volume == 100
    assert out["EMPTY"] == []
    # vwap falls back to close when the feed omits it
    client2 = _FakeClient()
    src2 = AlpacaIntradayDataSource("k", "s", client=client2)
    bars = src2.history_minutes(["AAA"], datetime(2026, 3, 1, tzinfo=UTC),
                                datetime(2026, 4, 1, tzinfo=UTC))["AAA"]
    assert bars[0].vwap == 10.25


def test_calendar_roundtrip_and_early_close(tmp_path):
    fixture = tmp_path / "sessions.csv"
    full = Session(date(2026, 3, 2),
                   datetime(2026, 3, 2, 14, 30, tzinfo=UTC),
                   datetime(2026, 3, 2, 21, 0, tzinfo=UTC))
    half = Session(date(2026, 11, 27),
                   datetime(2026, 11, 27, 14, 30, tzinfo=UTC),
                   datetime(2026, 11, 27, 18, 0, tzinfo=UTC))
    write_fixture([full, half], fixture)
    sessions = load_sessions(fixture)
    assert not sessions[date(2026, 3, 2)].is_early_close
    assert sessions[date(2026, 11, 27)].is_early_close  # 13:00 ET close


def test_vault_resume_skips_existing_and_marks_empty(tmp_path):
    class _OneShotSource:
        def __init__(self):
            self.calls = 0

        def history_minutes(self, symbols, start, end):
            self.calls += 1
            from new_pipeline.adapters.base import MinuteBar
            return {s: ([MinuteBar(start + timedelta(minutes=1), 1, 2, 0.5, 1.5, 10, 1.2)]
                        if s != "GHOST" else []) for s in symbols}

    src = _OneShotSource()
    tally = ingest(src, ["AAA", "GHOST"], date(2026, 1, 1), date(2026, 1, 1),
                   tmp_path, sleep=0.0)
    assert tally == {"fetched": 1, "cached": 0, "empty": 1}
    assert vault_file(tmp_path, "GHOST", 2026, 1).exists()  # empty marker written
    tally2 = ingest(src, ["AAA", "GHOST"], date(2026, 1, 1), date(2026, 1, 1),
                    tmp_path, sleep=0.0)
    assert tally2 == {"fetched": 0, "cached": 2, "empty": 0}  # full resume, no refetch
    assert src.calls == 1


def test_loader_filters_window_and_sessions(tmp_path):
    from new_pipeline.adapters.base import MinuteBar

    def mb(h, m):
        return MinuteBar(datetime(2026, 3, 2, h, m, tzinfo=UTC), 1, 2, 0.5, 1.5, 10, 1.2)

    # pre-market bar (13:00 UTC = 8:00 ET), in-session bar, post-close bar
    _write_symbol_month(tmp_path, "AAA", 2026, 3, [mb(13, 0), mb(15, 0), mb(21, 30)])
    frame = load_minutes(tmp_path, ["AAA", "MISSING"],
                         datetime(2026, 3, 1, tzinfo=UTC), datetime(2026, 4, 1, tzinfo=UTC))
    assert frame.height == 3 and set(frame["ticker"].unique()) == {"AAA"}
    sessions = {date(2026, 3, 2): Session(date(2026, 3, 2),
                                          datetime(2026, 3, 2, 14, 30, tzinfo=UTC),
                                          datetime(2026, 3, 2, 21, 0, tzinfo=UTC))}
    regular = filter_to_sessions(frame, sessions)
    assert regular.height == 1 and regular["ts"][0].hour == 15  # extended hours dropped


def test_months_between_spans_year_boundary():
    assert months_between(date(2025, 11, 5), date(2026, 2, 1)) == [
        (2025, 11), (2025, 12), (2026, 1), (2026, 2)]
