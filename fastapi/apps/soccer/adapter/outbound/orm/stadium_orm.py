"""Soccer 경기장 엔티티."""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base


class Stadium(Base):
    """경기장 — team.stadium_id / schedule.stadium_id 의 참조 대상."""

    __tablename__ = "stadium"

    stadium_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    statdium_name: Mapped[str] = mapped_column(String(40), nullable=False)
    hometeam_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    seat_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    address: Mapped[str | None] = mapped_column(String(60), nullable=True)
    ddd: Mapped[str | None] = mapped_column(String(10), nullable=True)
    tel: Mapped[str | None] = mapped_column(String(10), nullable=True)
