"""Usage tracking and limits."""
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, SubscriptionTier

DEFAULT_USAGE = {
    "mockups_generated": 0,
    "exports": 0,
    "brands_created": 0,
}

USAGE_LIMITS = {
    SubscriptionTier.FREE: {"mockups_generated": 5, "exports": 10, "brands_created": 1},
    SubscriptionTier.PRO: {"mockups_generated": 100, "exports": 200, "brands_created": 10},
    SubscriptionTier.AGENCY: {"mockups_generated": None, "exports": None, "brands_created": 50},
}


def _reset_if_needed(user: User):
    now = datetime.now(timezone.utc)
    if not user.usage_reset_at or (
        user.usage_reset_at.year != now.year or user.usage_reset_at.month != now.month
    ):
        user.usage_counts = DEFAULT_USAGE.copy()
        user.usage_reset_at = now


def _get_limits(user: User) -> Dict[str, Optional[int]]:
    return USAGE_LIMITS.get(user.subscription_tier or SubscriptionTier.FREE, USAGE_LIMITS[SubscriptionTier.FREE])


async def ensure_within_limits(db: AsyncSession, user: User, key: str, increment: int = 1):
    """Check and increment usage, raising if limits exceeded."""
    _reset_if_needed(user)
    usage = user.usage_counts or DEFAULT_USAGE.copy()
    limits = _get_limits(user)

    current = usage.get(key, 0)
    limit = limits.get(key)

    if limit is not None and current + increment > limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Limit reached for {key.replace('_', ' ')}. Upgrade your plan.",
        )

    usage[key] = current + increment
    user.usage_counts = usage
    await db.flush()


def usage_summary(user: User) -> dict:
    _reset_if_needed(user)
    usage = user.usage_counts or DEFAULT_USAGE.copy()
    limits = _get_limits(user)
    return {
        "tier": (user.subscription_tier or SubscriptionTier.FREE).value,
        "counts": usage,
        "limits": limits,
        "resets_at": user.usage_reset_at,
    }

