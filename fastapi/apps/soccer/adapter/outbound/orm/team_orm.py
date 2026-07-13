"""Soccer 구단 엔티티."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base


class Team(Base):
    """구단 — stadium 참조, player.team_id 의 참조 대상."""

    __tablename__ = "team"

    team_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    region_name: Mapped[str] = mapped_column(String(10), nullable=False)
    team_name: Mapped[str] = mapped_column(String(40), nullable=False)
    e_team_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    orig_yyyy: Mapped[str | None] = mapped_column(String(10), nullable=True)
    zip_code1: Mapped[str | None] = mapped_column(String(10), nullable=True)
    zip_code2: Mapped[str | None] = mapped_column(String(10), nullable=True)
    address: Mapped[str | None] = mapped_column(String(80), nullable=True)
    ddd: Mapped[str | None] = mapped_column(String(10), nullable=True)
    tel: Mapped[str | None] = mapped_column(String(10), nullable=True)
    fax: Mapped[str | None] = mapped_column(String(10), nullable=True)
    homepage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    owner: Mapped[str | None] = mapped_column(String(10), nullable=True)
    stadium_id: Mapped[str | None] = mapped_column(
        ForeignKey("stadium.stadium_id"), nullable=True
    )
