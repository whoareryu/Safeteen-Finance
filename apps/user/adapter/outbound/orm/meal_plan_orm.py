"""마이페이지 식비 플랜."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin
from restaurant.adapter.outbound.orm.gourmet_entity_orm import UserOwnedEntityMixin


class MealPlan(IntIdPrimaryKeyMixin, UserOwnedEntityMixin, Base):
    __tablename__ = "meal_plans"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    monthly_budget: Mapped[int] = mapped_column(Integer)
    spent_amount: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    period_start: Mapped[date] = mapped_column(Date, index=True)
    period_end: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
