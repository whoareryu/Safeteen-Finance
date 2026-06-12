from __future__ import annotations
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from core.matrix.grid_neo_theone_base import Base
from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerORM
from sqlalchemy.orm import relationship

class RoseModelORM(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    passenger_id: Mapped[str | None] = mapped_column(String, ForeignKey("passengers.passenger_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pclass: Mapped[str | None] = mapped_column(String, nullable=False, default="")
    ticket: Mapped[str | None] = mapped_column(String, nullable=False, default="")
    fare: Mapped[str | None] = mapped_column(String, nullable=False, default="")
    cabin: Mapped[str | None] = mapped_column(String, nullable=False, default="")
    embarked: Mapped[str | None] = mapped_column(String, nullable=False, default="")

    person: Mapped["JackTrainerORM"] = relationship()
