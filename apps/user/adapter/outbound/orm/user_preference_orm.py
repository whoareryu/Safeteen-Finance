"""온보딩 취향 마스터 — users 1:1 (기획서 3-1)."""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class UserPreference(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    genre_ranking: Mapped[list] = mapped_column(JSON, default=list)
    dining_mode: Mapped[str] = mapped_column(String(16), default="", server_default="")
    portion: Mapped[str] = mapped_column(String(16), default="", server_default="")
    allergies: Mapped[list] = mapped_column(JSON, default=list)
    avoid_foods: Mapped[list] = mapped_column(JSON, default=list)
    use_budget: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    monthly_budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
