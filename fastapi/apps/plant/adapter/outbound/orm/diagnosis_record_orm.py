from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class DiagnosisRecordORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "diagnosis_records"

    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False)
    photo_url: Mapped[str] = mapped_column(String, nullable=False)
    detected_species: Mapped[str] = mapped_column(String, nullable=False)
    species_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    symptom_label: Mapped[str] = mapped_column(String, nullable=False)
    symptom_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    diagnosed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
