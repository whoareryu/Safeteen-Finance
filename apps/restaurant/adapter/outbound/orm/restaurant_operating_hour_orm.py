"""요일별 영업 시간 (1NF — 요일당 1행)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin

if TYPE_CHECKING:
    from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant


class RestaurantOperatingHour(IntIdPrimaryKeyMixin, Base):
    """weekday: 0=월 … 6=일 (Python weekday)."""

    __tablename__ = "restaurant_operating_hours"
    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "weekday",
            name="uq_restaurant_operating_hours_day",
        ),
    )

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant.id", ondelete="CASCADE"),
        index=True,
    )
    weekday: Mapped[int] = mapped_column(Integer)
    open_time: Mapped[str | None] = mapped_column(String(8), nullable=True)
    close_time: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    note: Mapped[str] = mapped_column(String(256), default="", server_default="")

    restaurant: Mapped[Restaurant] = relationship(back_populates="operating_hours")
