"""Offline tests for the GDELT news/tone adapter (fake HTTP session)."""

import json
from datetime import date
from types import SimpleNamespace

import polars as pl
import pytest

from new_pipeline.adapters.news_gdelt import (
    GdeltClient,
    GdeltNewsSource,
    fetch_tone_series,
    sector_tone_frame,
)
from new_pipeline.core.exceptions import NewsSourceError


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(params)
        status, body = self.responses.pop(0)
        return SimpleNamespace(status_code=status, text=body)


def _client(responses):
    client = GdeltClient(session=_JsonSession(responses))
    return client


class _JsonSession(FakeSession):
    def get(self, url, params=None, timeout=None):
        self.calls.append(params)
        status, body = self.responses.pop(0)
        return SimpleNamespace(
            status_code=status,
            text=body,
            json=lambda: json.loads(body),
        )


def _tone_payload(points):
    return json.dumps(
        {"timeline": [{"data": [{"date": f"{d:%Y%m%d}T120000Z", "value": v} for d, v in points]}]}
    )


def test_fetch_tone_series_parses_daily_points(monkeypatch):
    monkeypatch.setattr("new_pipeline.adapters.news_gdelt.MIN_REQUEST_INTERVAL", 0.0)
    payload = _tone_payload([(date(2026, 1, 2), 1.5), (date(2026, 1, 3), -0.5)])
    series = fetch_tone_series("test", date(2026, 1, 1), date(2026, 1, 5), _client([(200, payload)]))
    assert series["date"].to_list() == [date(2026, 1, 2), date(2026, 1, 3)]
    assert series["tone"].to_list() == [1.5, -0.5]


def test_client_retries_429_then_succeeds(monkeypatch):
    monkeypatch.setattr("new_pipeline.adapters.news_gdelt.MIN_REQUEST_INTERVAL", 0.0)
    monkeypatch.setattr("new_pipeline.adapters.news_gdelt.time.sleep", lambda _s: None)
    payload = _tone_payload([(date(2026, 1, 2), 1.0)])
    series = fetch_tone_series(
        "test", date(2026, 1, 1), date(2026, 1, 5), _client([(429, ""), (200, payload)])
    )
    assert series.height == 1


def test_client_raises_after_exhausted_retries(monkeypatch):
    monkeypatch.setattr("new_pipeline.adapters.news_gdelt.MIN_REQUEST_INTERVAL", 0.0)
    monkeypatch.setattr("new_pipeline.adapters.news_gdelt.time.sleep", lambda _s: None)
    with pytest.raises(NewsSourceError):
        fetch_tone_series(
            "test", date(2026, 1, 1), date(2026, 1, 2), _client([(429, "")] * 10)
        )


def test_sector_tone_frame_zscores_and_falls_back(monkeypatch):
    monkeypatch.setattr("new_pipeline.adapters.news_gdelt.MIN_REQUEST_INTERVAL", 0.0)
    market = _tone_payload([(date(2026, 1, 2), 1.0), (date(2026, 1, 3), 3.0)])
    energy = _tone_payload([(date(2026, 1, 2), -2.0), (date(2026, 1, 3), 2.0)])
    client = _client([(200, market), (200, energy)])
    frame = sector_tone_frame(["Energy", "Unmapped Sector"], date(2026, 1, 1), date(2026, 1, 5), client)
    energy_rows = frame.filter(pl.col("gics_sector") == "Energy").sort("date")
    # z-scored: mean 0, symmetric around it
    assert energy_rows["sentiment_score"].to_list() == pytest.approx([-0.7071, 0.7071], abs=1e-3)
    # unmapped sector falls back to the market series (z-scored the same way)
    fallback = frame.filter(pl.col("gics_sector") == "Unmapped Sector").sort("date")
    assert fallback.height == 2


def test_headlines_maps_articles(monkeypatch):
    monkeypatch.setattr("new_pipeline.adapters.news_gdelt.MIN_REQUEST_INTERVAL", 0.0)
    body = json.dumps(
        {"articles": [{"title": "Apple ships", "seendate": "20260102T130000Z"}]}
    )
    source = GdeltNewsSource({"AAPL": "Apple Inc."}, client=_client([(200, body)]))
    items = source.headlines("AAPL", date(2026, 1, 2))
    assert items[0].headline == "Apple ships"
    assert items[0].symbol == "AAPL"
