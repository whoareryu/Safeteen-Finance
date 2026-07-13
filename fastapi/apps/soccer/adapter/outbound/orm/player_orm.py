"""Soccer 선수 엔티티 — pgvector 스카우팅 임베딩 컬럼 포함."""

from __future__ import annotations

import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base

PLAYER_EMBEDDING_DIM = 1536


class Player(Base):
    """선수 — team 참조, 스카우팅 리포트/플레이 스타일 임베딩(player_embedding) 보유."""

    __tablename__ = "player"

    player_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    player_name: Mapped[str] = mapped_column(String(20), nullable=False)
    e_player_name: Mapped[str | None] = mapped_column(String(40), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(30), nullable=True)
    join_yyyy: Mapped[str | None] = mapped_column(String(10), nullable=True)
    position: Mapped[str | None] = mapped_column(String(10), nullable=True)
    back_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nation: Mapped[str | None] = mapped_column(String(20), nullable=True)
    birth_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    solar: Mapped[str | None] = mapped_column(String(10), nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight: Mapped[int | None] = mapped_column(Integer, nullable=True)
    team_id: Mapped[str | None] = mapped_column(
        ForeignKey("team.team_id"), nullable=True
    )
    player_embedding: Mapped[list[float] | None] = mapped_column(
        Vector(PLAYER_EMBEDDING_DIM), nullable=True
    )
