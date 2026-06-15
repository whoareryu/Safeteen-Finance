"""AI·주제 태그 마스터 — JSONB ai_tags 1NF 분리."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin

if TYPE_CHECKING:
    from restaurant.adapter.outbound.orm.restaurant_tag_orm import RestaurantTag


class Tag(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "tags"

    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(128), default="", server_default="")

    restaurant_links: Mapped[list[RestaurantTag]] = relationship(back_populates="tag")
