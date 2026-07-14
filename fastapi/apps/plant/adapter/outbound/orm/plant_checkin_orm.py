from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class PlantCheckinORM(IntIdPrimaryKeyMixin, Base):
    """일일 출석체크 — 사진 1장당 1건."""

    __tablename__ = "plant_checkins"

    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False)
    photo_url: Mapped[str] = mapped_column(String, nullable=False)
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False)
    health_score: Mapped[float] = mapped_column(Float, nullable=False)
    points_earned: Mapped[int] = mapped_column(Integer, nullable=False)
    streak_day: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
