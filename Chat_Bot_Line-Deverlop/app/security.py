import os
from secrets import compare_digest

from fastapi import Header, HTTPException


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    expected = os.getenv("BORC_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="API key is not configured")
    if not x_api_key or not compare_digest(x_api_key.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Invalid API key")
