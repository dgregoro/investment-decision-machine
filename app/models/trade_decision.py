from datetime import UTC, datetime

from sqlalchemy import JSON, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import DecisionStatus, DecisionType


def utc_now() -> datetime:
    return datetime.now(UTC)


class TradeDecision(Base):
    """Structured trade / position decision payload (human-led, no execution hooks here)."""

    __tablename__ = "trade_decisions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    symbol: Mapped[str | None] = mapped_column(String(32))
    decision_type: Mapped[DecisionType | None] = mapped_column(
        SAEnum(DecisionType, native_enum=False, length=16),
    )
    status: Mapped[DecisionStatus] = mapped_column(
        SAEnum(DecisionStatus, native_enum=False, length=16),
        insert_default=DecisionStatus.draft,
    )

    created_at: Mapped[datetime] = mapped_column(insert_default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(insert_default=utc_now, onupdate=utc_now)

    thesis_summary: Mapped[str | None] = mapped_column(String(8192))
    time_horizon: Mapped[str | None] = mapped_column(String(512))
    confidence_score: Mapped[float] = mapped_column(default=0.5)
    signal_sources: Mapped[list[str]] = mapped_column(JSON, insert_default=list)
    assumptions: Mapped[list[str]] = mapped_column(JSON, insert_default=list)
    invalidation_conditions: Mapped[list[str]] = mapped_column(JSON, insert_default=list)
    counter_arguments: Mapped[list[str]] = mapped_column(JSON, insert_default=list)
    max_position_size_pct: Mapped[float | None] = mapped_column()
    planned_entry_price: Mapped[float | None] = mapped_column()
    planned_exit_conditions: Mapped[list[str]] = mapped_column(JSON, insert_default=list)
    max_loss_pct: Mapped[float | None] = mapped_column()
    notes: Mapped[str] = mapped_column(String(16384), default="")
