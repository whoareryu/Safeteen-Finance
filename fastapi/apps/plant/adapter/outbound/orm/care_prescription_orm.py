from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class CarePrescriptionORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "care_prescriptions"

    diagnosis_record_id: Mapped[int] = mapped_column(ForeignKey("diagnosis_records.id"), nullable=False)
    prescription_text: Mapped[str] = mapped_column(Text, nullable=False)
    llm_model: Mapped[str] = mapped_column(String, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
