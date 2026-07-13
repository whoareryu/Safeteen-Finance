from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class CareScheduleORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "care_schedules"

    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False)
    last_watered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_watering_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
