from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin


class TitanicPersonORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "titanic_persons"

    passenger_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    gender: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    age: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    sib_sp: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    parch: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    survived: Mapped[str] = mapped_column(String(8), nullable=False, default="")

    bookings: Mapped[list["TitanicBookingORM"]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
    )


