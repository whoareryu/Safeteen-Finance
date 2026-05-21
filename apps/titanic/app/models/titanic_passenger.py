"""Kaggle Titanic CSV → Neon ``titanic_passengers``."""

from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class TitanicPassenger(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "titanic_passengers"

    passenger_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    survived: Mapped[int] = mapped_column(Integer, index=True)
    pclass: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(Text)
    sex: Mapped[str] = mapped_column(String(16))
    age: Mapped[float | None] = mapped_column(Float, nullable=True)
    sib_sp: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    parch: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    ticket: Mapped[str] = mapped_column(String(64), default="", server_default="")
    fare: Mapped[float | None] = mapped_column(Float, nullable=True)
    cabin: Mapped[str] = mapped_column(String(64), default="", server_default="")
    embarked: Mapped[str] = mapped_column(String(8), default="", server_default="")
