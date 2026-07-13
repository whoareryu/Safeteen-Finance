from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class WeatherSnapshotORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "weather_snapshots"

    region: Mapped[str] = mapped_column(String, nullable=False, index=True)
    temp_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_pct: Mapped[float] = mapped_column(Float, nullable=False)
    sunlight_desc: Mapped[str] = mapped_column(String, nullable=False)
    is_dry_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
