from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.database import Base, IntIdPrimaryKeyMixin


class TitanicBookingORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "titanic_bookings"

    person_id: Mapped[int] = mapped_column(
        ForeignKey("titanic_persons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pclass: Mapped[str] = mapped_column(String(8), nullable=False, default="")
    ticket: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    fare: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    cabin: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    embarked: Mapped[str] = mapped_column(String(8), nullable=False, default="")

    person: Mapped["TitanicPersonORM"] = relationship(back_populates="bookings")
