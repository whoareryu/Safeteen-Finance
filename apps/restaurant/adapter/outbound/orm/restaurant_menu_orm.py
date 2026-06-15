"""매장 메뉴 — Restaurant 1:N (2NF)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin

if TYPE_CHECKING:
    from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant


class RestaurantMenu(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "restaurant_menus"

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(256), default="", server_default="")
    is_signature: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    unit_price: Mapped[int | None] = mapped_column(Integer, nullable=True)

    restaurant: Mapped[Restaurant] = relationship(
        back_populates="menus",
    )
