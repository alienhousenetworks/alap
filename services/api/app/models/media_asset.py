import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class MediaAsset(Base):
    __tablename__ = "media_assets"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class MediaDailyUsage(Base):
    __tablename__ = "media_daily_usage"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    usage_date: Mapped[date] = mapped_column(Date, nullable=False)
    image_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    voice_characters: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    __table_args__ = (UniqueConstraint("user_id", "usage_date", name="uq_media_daily_user_date"),)

class MediaMonthlyBudget(Base):
    __tablename__ = "media_monthly_budgets"
    month: Mapped[str] = mapped_column(String(7), primary_key=True)
    spent_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
