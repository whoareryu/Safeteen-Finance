"""식비 지출 내역 — meal_plans 1:N (기획서 4-3)."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class MealPlanExpense(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "meal_plan_expenses"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    meal_plan_id: Mapped[int] = mapped_column(
        ForeignKey("meal_plans.id", ondelete="CASCADE"), index=True
    )
    restaurant_id: Mapped[int | None] = mapped_column(
        ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )
    amount: Mapped[int] = mapped_column(Integer)
    spent_on: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
