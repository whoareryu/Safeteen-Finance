"""매장–태그 N:M (1NF)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin

if TYPE_CHECKING:
    from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
    from restaurant.adapter.outbound.orm.tag_orm import Tag


class RestaurantTag(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "restaurant_tags"
    __table_args__ = (
        UniqueConstraint("restaurant_id", "tag_id", name="uq_restaurant_tags_pair"),
    )

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant.id", ondelete="CASCADE"),
        index=True,
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        index=True,
    )

    restaurant: Mapped[Restaurant] = relationship(back_populates="tag_links")
    tag: Mapped[Tag] = relationship(back_populates="restaurant_links")
