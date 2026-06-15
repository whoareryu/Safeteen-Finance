"""로그인 사용자 일별 추천 1곳 로그."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin
from restaurant.adapter.outbound.orm.gourmet_entity_orm import UserOwnedEntityMixin


class DailyRecommendation(IntIdPrimaryKeyMixin, UserOwnedEntityMixin, Base):
    __tablename__ = "daily_recommendations"
    __table_args__ = (
        UniqueConstraint("user_id", "recommended_on", name="uq_daily_rec_user_date"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant.id", ondelete="CASCADE"),
        index=True,
    )
    meal_plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    recommended_on: Mapped[date] = mapped_column(Date, index=True)
    pick_reason: Mapped[str] = mapped_column(Text, default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
