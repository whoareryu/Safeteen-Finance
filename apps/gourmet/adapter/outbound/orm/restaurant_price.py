"""매장별 1인 추정 식대 — Restaurant 1:1 (2NF)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin

if TYPE_CHECKING:
    from gourmet.adapter.outbound.orm.restaurant import Restaurant


class RestaurantPrice(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "restaurant_prices"
    __table_args__ = (
        UniqueConstraint("restaurant_id", name="uq_restaurant_prices_restaurant_id"),
    )

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        index=True,
    )
    avg_price: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    restaurant: Mapped[Restaurant] = relationship(
        back_populates="price",
        uselist=False,
    )
