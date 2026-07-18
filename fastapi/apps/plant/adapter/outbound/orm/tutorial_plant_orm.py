from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin
from plant.domain.value_objects.growth_stage import SPROUT
from plant.domain.value_objects.tutorial_state import LIGHT_PARTIAL


class TutorialPlantORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "tutorial_plants"

    owner_user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    species_name: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str] = mapped_column(String, nullable=False)
    growth_stage: Mapped[str] = mapped_column(String(10), nullable=False, default=SPROUT)
    soil_moisture_pct: Mapped[float] = mapped_column(Float, nullable=False, default=70.0)
    nutrient_pct: Mapped[float] = mapped_column(Float, nullable=False, default=70.0)
    light_position: Mapped[str] = mapped_column(String(10), nullable=False, default=LIGHT_PARTIAL)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_watered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_fertilized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_light_moved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_weather_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
