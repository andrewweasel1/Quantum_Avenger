"""OllamaLLMClient: mapping, parsing, and fail-safe paths (transport injected)."""

import json

import pytest
from new_pipeline.adapters.llm_ollama import OllamaLLMClient
from new_pipeline.config import reload_config


def _client(reply=None, error=None, capture=None):
    def transport(url, payload, timeout):
        if capture is not None:
            capture.append((url, payload, timeout))
        if error is not None:
            raise error
        return {"response": reply}

    return OllamaLLMClient("http://ollama:11434", "qwen-3", timeout=7.5, transport=transport)


def test_verdict_parses_json_reply():
    reply = json.dumps({"stance": "bullish", "rationale": "strong earnings"})
    verdict = _client(reply=reply).verdict("Signal: BUY ...")
    assert verdict.stance == "BULLISH"  # normalized to upper
    assert verdict.rationale == "strong earnings"


def test_verdict_keyword_fallback_for_non_json_reply():
    verdict = _client(reply="I would say BEARISH given the miss.").verdict("prompt")
    assert verdict.stance == "BEARISH"


def test_verdict_unparseable_reply_fails_safe_to_neutral():
    verdict = _client(reply="42").verdict("prompt")
    assert verdict.stance == "NEUTRAL"
    assert "failing safe" in verdict.rationale


def test_verdict_transport_error_fails_safe_to_neutral():
    verdict = _client(error=ConnectionError("refused")).verdict("prompt")
    assert verdict.stance == "NEUTRAL"
    assert "unavailable" in verdict.rationale


def test_request_payload_and_url():
    capture = []
    _client(reply='{"stance": "NEUTRAL", "rationale": ""}', capture=capture).verdict("the prompt")
    url, payload, timeout = capture[0]
    assert url == "http://ollama:11434/api/generate"
    assert payload["model"] == "qwen-3"
    assert payload["stream"] is False and payload["format"] == "json"
    assert payload["options"]["temperature"] == 0.0
    assert payload["prompt"].startswith("the prompt")
    assert timeout == 7.5


def test_sentiment_parses_clamps_and_labels():
    client = _client(reply=json.dumps({"score": 3.0}))
    result = client.sentiment("very good quarter")
    assert result.score == 1.0  # clamped into [-1, 1]
    assert result.label == "bullish"

    assert _client(reply=json.dumps({"score": -0.6})).sentiment("bad").label == "bearish"
    assert _client(reply=json.dumps({"score": 0.05})).sentiment("meh").label == "neutral"


def test_sentiment_failures_degrade_to_neutral_zero():
    for client in (_client(reply="not json"), _client(error=TimeoutError())):
        result = client.sentiment("text")
        assert (result.score, result.label) == (0.0, "neutral")


def test_from_config_uses_fusion_knobs(monkeypatch):
    monkeypatch.setenv("QA_FUSION__OLLAMA_ENDPOINT", "http://gpu-box:11434/")
    monkeypatch.setenv("QA_FUSION__VERDICT_MODEL", "llama3.3")
    monkeypatch.setenv("QA_FUSION__SENTIMENT_TIMEOUT", "12.0")
    cfg = reload_config()
    client = OllamaLLMClient.from_config(cfg)
    assert client._url == "http://gpu-box:11434/api/generate"  # trailing slash stripped
    assert client._model == "llama3.3"
    assert client._timeout == pytest.approx(12.0)
