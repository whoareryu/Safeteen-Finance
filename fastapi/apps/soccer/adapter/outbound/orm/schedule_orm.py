"""Soccer 경기 일정 엔티티."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base


class Schedule(Base):
    """경기 일정 — (sche_date, stadium_id) 복합 PK."""

    __tablename__ = "schedule"

    sche_date: Mapped[str] = mapped_column(String(10), primary_key=True)
    stadium_id: Mapped[str] = mapped_column(
        ForeignKey("stadium.stadium_id"), primary_key=True
    )
    gubun: Mapped[str | None] = mapped_column(String(10), nullable=True)
    hometeam_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    awayteam_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
