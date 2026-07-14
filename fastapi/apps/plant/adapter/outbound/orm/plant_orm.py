from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin
from plant.domain.value_objects.growth_stage import SPROUT


class PlantORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "plants"

    owner_user_id: Mapped[int | None] = mapped_column(nullable=True)
    nickname: Mapped[str] = mapped_column(String, nullable=False)
    species_name: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str] = mapped_column(String, nullable=False)
    growth_stage: Mapped[str] = mapped_column(String(10), nullable=False, default=SPROUT)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    streak_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_checkin_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
