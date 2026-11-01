from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.media_asset import MediaDailyUsage, MediaMonthlyBudget

class MediaQuotaExceeded(Exception): pass
class MediaBudgetExceeded(Exception): pass

@dataclass(frozen=True)
class MediaReservation:
    usage_date: object
    month: str
    kind: str
    voice_characters: int
    cost: Decimal

async def reserve_media_usage(db: AsyncSession, user_id: UUID, kind: str, voice_characters: int = 0) -> MediaReservation:
    now = datetime.now(timezone.utc)
    usage_date, month = now.date(), now.strftime("%Y-%m")
    await db.execute(pg_insert(MediaDailyUsage).values(user_id=user_id, usage_date=usage_date, image_count=0, voice_characters=0).on_conflict_do_nothing())
    await db.execute(pg_insert(MediaMonthlyBudget).values(month=month, spent_usd=0).on_conflict_do_nothing())
    usage = await db.scalar(select(MediaDailyUsage).where(MediaDailyUsage.user_id == user_id, MediaDailyUsage.usage_date == usage_date).with_for_update())
    budget = await db.scalar(select(MediaMonthlyBudget).where(MediaMonthlyBudget.month == month).with_for_update())
    if kind == "image":
        if usage.image_count >= settings.media_daily_image_limit:
            raise MediaQuotaExceeded()
        cost = Decimal(str(settings.media_image_estimated_cost_usd))
        usage.image_count += 1
    else:
        if usage.voice_characters + voice_characters > settings.media_daily_voice_characters:
            raise MediaQuotaExceeded()
        cost = Decimal(str(settings.media_voice_estimated_cost_per_1k_chars_usd)) * Decimal(voice_characters) / Decimal(1000)
        usage.voice_characters += voice_characters
    if settings.media_monthly_budget_usd <= 0 or budget.spent_usd + cost > Decimal(str(settings.media_monthly_budget_usd)):
        raise MediaBudgetExceeded()
    budget.spent_usd += cost
    await db.commit()
    return MediaReservation(usage_date, month, kind, voice_characters, cost)

async def release_media_usage(db: AsyncSession, user_id: UUID, reservation: MediaReservation):
    usage = await db.scalar(select(MediaDailyUsage).where(
        MediaDailyUsage.user_id == user_id, MediaDailyUsage.usage_date == reservation.usage_date
    ).with_for_update())
    budget = await db.scalar(select(MediaMonthlyBudget).where(MediaMonthlyBudget.month == reservation.month).with_for_update())
    if usage is not None:
        if reservation.kind == "image":
            usage.image_count = max(0, usage.image_count - 1)
        else:
            usage.voice_characters = max(0, usage.voice_characters - reservation.voice_characters)
    if budget is not None:
        budget.spent_usd = max(Decimal("0"), budget.spent_usd - reservation.cost)
    await db.commit()
