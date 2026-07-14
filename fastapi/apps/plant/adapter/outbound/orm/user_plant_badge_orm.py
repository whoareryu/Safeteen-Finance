from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class UserPlantBadgeORM(IntIdPrimaryKeyMixin, Base):
    """식물별 뱃지 획득 기록."""

    __tablename__ = "user_plant_badges"

    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False)
    badge_id: Mapped[int] = mapped_column(ForeignKey("plant_badges.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
