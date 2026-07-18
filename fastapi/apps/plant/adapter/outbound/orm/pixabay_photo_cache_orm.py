from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class PixabayPhotoCacheORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "pixabay_photo_caches"
    __table_args__ = (
        UniqueConstraint("species_name", "growth_stage", "status_key", name="uq_pixabay_photo_cache_combo"),
    )

    species_name: Mapped[str] = mapped_column(String, nullable=False)
    growth_stage: Mapped[str] = mapped_column(String(10), nullable=False)
    status_key: Mapped[str] = mapped_column(String(20), nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)
    pixabay_source_id: Mapped[str] = mapped_column(String, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
