"""즐겨찾기 — User ↔ Restaurant N:M 연결."""

from __future__ import annotations

from datetime import datetime, timezone

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin
from restaurant.adapter.outbound.orm.gourmet_entity_orm import UserOwnedEntityMixin

if TYPE_CHECKING:
    from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant


class Favorite(IntIdPrimaryKeyMixin, UserOwnedEntityMixin, Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "restaurant_id", name="uq_favorites_user_restaurant"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant.id", ondelete="CASCADE"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    restaurant: Mapped[Restaurant] = relationship(
        "Restaurant",
        foreign_keys=[restaurant_id],
    )
