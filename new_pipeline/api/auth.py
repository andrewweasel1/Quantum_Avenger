"""Bearer-token gate for the dashboard API.

Disabled by default (``dashboard.auth_enabled: false``) so local development stays
frictionless. When enabled, every ``/api`` route except the health probe requires
``Authorization: Bearer <token>`` matching the ``QA_API_TOKEN`` environment variable —
the token lives only in the environment (never in config files), mirroring the repo's
secrets pattern, and the comparison is constant-time. Fail-closed: auth enabled with
no token configured rejects every request rather than silently allowing them.
"""

import hmac
import os

from fastapi import HTTPException, Request

from new_pipeline.config import get_config

TOKEN_ENV = "QA_API_TOKEN"


def require_auth(request: Request) -> None:
    """FastAPI dependency: 401 unless auth is off or the bearer token matches."""
    if not get_config().dashboard.auth_enabled:
        return
    expected = os.environ.get(TOKEN_ENV, "")
    header = request.headers.get("authorization", "")
    supplied = header[7:].strip() if header.startswith("Bearer ") else ""
    if not (expected and supplied and hmac.compare_digest(supplied, expected)):
        raise HTTPException(
            status_code=401,
            detail="invalid or missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
