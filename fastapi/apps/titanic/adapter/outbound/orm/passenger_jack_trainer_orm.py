from __future__ import annotations
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from core.matrix.grid_neo_theone_base import Base 


class JackTrainerORM(Base):
    __tablename__ = "passengers"

    
    passenger_id: Mapped[str | None] = mapped_column(String,primary_key=True, nullable=False, index=True)
    name: Mapped[str | None ] = mapped_column(String, nullable=False, default="")
    gender: Mapped[str | None] = mapped_column(String, nullable=False, default="")
    age: Mapped[str | None] = mapped_column(String, nullable=False, default="")
    sib_sp: Mapped[str | None] = mapped_column(String, nullable=False, default="")
    parch: Mapped[str | None] = mapped_column(String, nullable=False, default="")
    survived: Mapped[str | None] = mapped_column(String, nullable=False, default="")

