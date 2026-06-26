"""A JSON response that survives the engine's non-finite floats.

Quant metrics legitimately go infinite/NaN (a zero-variance champion's Sortino, an
``inf`` haircut Sharpe when the trial count makes the adjusted t-ratio explode).
Starlette's ``JSONResponse`` renders with ``allow_nan=False`` and would 500 on those;
the browser's ``JSON.parse`` rejects the non-standard ``Infinity`` token too. So the
API coerces every non-finite float to ``null`` before serialising — the front-end
already renders ``null`` metrics as an em dash.
"""

import math

from starlette.responses import JSONResponse


def json_safe(obj):
    """Recursively replace inf/-inf/NaN floats with ``None`` (JSON ``null``)."""
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {key: json_safe(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(value) for value in obj]
    return obj


class SafeJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return super().render(json_safe(content))
