"""Simple in-memory rate limiter (per-process)."""
import time
from fastapi import HTTPException, status

# key -> list[timestamps]
_requests: dict[str, list[float]] = {}


def rate_limit(key: str, limit: int = 10, window_seconds: int = 60):
    """Basic sliding window rate limit."""
    now = time.time()
    window_start = now - window_seconds
    timestamps = _requests.get(key, [])
    # Drop old entries
    timestamps = [t for t in timestamps if t >= window_start]

    if len(timestamps) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down.",
        )

    timestamps.append(now)
    _requests[key] = timestamps

