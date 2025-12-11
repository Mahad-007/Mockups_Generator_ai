import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from app.services.usage_service import ensure_within_limits, usage_summary, DEFAULT_USAGE
from app.models.user import SubscriptionTier


class DummySession:
    async def flush(self):
        return None


class DummyUser:
    def __init__(self, tier=SubscriptionTier.FREE):
        self.subscription_tier = tier
        self.usage_counts = DEFAULT_USAGE.copy()
        self.usage_reset_at = datetime.now(timezone.utc)


@pytest.mark.asyncio
async def test_usage_increment_within_limits():
    user = DummyUser()
    db = DummySession()

    await ensure_within_limits(db, user, "mockups_generated", increment=1)
    assert user.usage_counts["mockups_generated"] == 1


@pytest.mark.asyncio
async def test_usage_limit_enforced():
    user = DummyUser()
    db = DummySession()
    user.usage_counts["mockups_generated"] = 5

    with pytest.raises(HTTPException) as exc:
        await ensure_within_limits(db, user, "mockups_generated", increment=1)
    assert exc.value.status_code == 402


def test_usage_resets_on_new_month():
    user = DummyUser()
    user.usage_counts["mockups_generated"] = 3
    # Simulate previous month
    user.usage_reset_at = datetime.now(timezone.utc) - timedelta(days=40)

    summary = usage_summary(user)
    assert summary["counts"]["mockups_generated"] == 0

