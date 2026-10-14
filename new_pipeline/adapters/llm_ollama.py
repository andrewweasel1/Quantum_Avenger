"""Live LLM client against an Ollama server (verdict + sentiment).

Stdlib-urllib only — no new dependency — with the HTTP transport injectable so
every mapping/parsing path is unit-tested offline. Replies are requested in
Ollama's JSON mode and parsed defensively; any transport failure or unparseable
reply degrades to a NEUTRAL verdict / 0.0 sentiment. NEUTRAL is rejected by the
grader, so the fail-safe direction is always "no trade", never an exception in
the middle of a session. The LLM still performs no math (G1) — stance and
rationale only; every quantity flows through the deterministic tools/Shield.
"""

import json
import urllib.request

from new_pipeline.adapters.base import LLMClient, SentimentResult, Verdict

_STANCES = ("BULLISH", "BEARISH", "NEUTRAL")
_VERDICT_SUFFIX = (
    '\n\nRespond ONLY with JSON: {"stance": "BULLISH" | "BEARISH" | "NEUTRAL", '
    '"rationale": "<one line>"}'
)
_SENTIMENT_PROMPT = (
    "Score the sentiment of this financial text between -1.0 (maximally bearish) "
    "and 1.0 (maximally bullish).\n\nTEXT:\n{text}\n\n"
    'Respond ONLY with JSON: {{"score": <float>, "label": "bullish" | "bearish" | "neutral"}}'
)


def _post_json(url: str, payload: dict, timeout: float) -> dict:  # pragma: no cover - egress
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class OllamaLLMClient(LLMClient):
    """``LLMClient`` over Ollama's ``/api/generate`` (temperature 0, JSON mode)."""

    def __init__(self, endpoint: str, model: str, timeout: float = 30.0, transport=None):
        self._url = endpoint.rstrip("/") + "/api/generate"
        self._model = model
        self._timeout = timeout
        self._transport = transport or _post_json

    @classmethod
    def from_config(cls, cfg) -> "OllamaLLMClient":
        fusion = cfg.fusion
        return cls(
            fusion.ollama_endpoint,
            fusion.verdict_model or fusion.llm_model_name,
            timeout=fusion.sentiment_timeout,
        )

    def verdict(self, prompt: str) -> Verdict:
        reply = self._generate(prompt + _VERDICT_SUFFIX)
        if reply is None:
            return Verdict("NEUTRAL", "llm unavailable - failing safe to no-trade")
        stance, rationale = _parse_verdict(reply)
        return Verdict(stance, rationale)

    def sentiment(self, text: str) -> SentimentResult:
        reply = self._generate(_SENTIMENT_PROMPT.format(text=text))
        if reply is None:
            return SentimentResult(0.0, "neutral")
        return _parse_sentiment(reply)

    def _generate(self, prompt: str) -> str | None:
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.0},
        }
        try:
            data = self._transport(self._url, payload, self._timeout)
            return str(data.get("response", ""))
        except Exception:
            return None


def _parse_verdict(reply: str) -> tuple[str, str]:
    try:
        data = json.loads(reply)
    except (ValueError, TypeError):
        data = None
    if isinstance(data, dict):  # JSON but not an object (e.g. "42") falls through
        stance = str(data.get("stance", "")).upper()
        if stance in _STANCES:
            return stance, str(data.get("rationale", ""))[:300]
    upper = reply.upper()
    for stance in _STANCES:  # keyword fallback for models that ignore JSON mode
        if stance in upper:
            return stance, reply.strip()[:300]
    return "NEUTRAL", "unparseable llm reply - failing safe to no-trade"


def _parse_sentiment(reply: str) -> SentimentResult:
    try:
        data = json.loads(reply)
        if not isinstance(data, dict):
            return SentimentResult(0.0, "neutral")
        score = max(-1.0, min(1.0, float(data.get("score", 0.0))))
    except (ValueError, TypeError):
        return SentimentResult(0.0, "neutral")
    label = "bullish" if score > 0.1 else "bearish" if score < -0.1 else "neutral"
    return SentimentResult(score, label)
