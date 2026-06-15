"""매장 연락·외부 URL (보강 API 적재, 1NF)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin

if TYPE_CHECKING:
    from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant


class RestaurantContact(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "restaurant_contacts"

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    place_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_note: Mapped[str] = mapped_column(Text, default="", server_default="")

    restaurant: Mapped[Restaurant] = relationship(back_populates="contact")
