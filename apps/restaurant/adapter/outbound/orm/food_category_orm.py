"""음식 장르 마스터 — ``restaurant.category_id`` FK 대상 (2NF)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin

if TYPE_CHECKING:
    from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant


class FoodCategory(IntIdPrimaryKeyMixin, Base):
    """카테고리 1 — N 매장 (Restaurant *belongs to* FoodCategory)."""

    __tablename__ = "food_categories"

    slug: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(32), default="", server_default="")

    restaurants: Mapped[list[Restaurant]] = relationship(
        back_populates="category",
    )
