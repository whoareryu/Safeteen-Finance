from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.titanic.adapter.outbound.orm.database import Base


class TitanicPassengerModel(Base):
    __tablename__ = "titanic_passengers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    passenger_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    survived: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pclass: Mapped[int | None] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(16), nullable=True)
    age: Mapped[float | None] = mapped_column(Float, nullable=True)
    sib_sp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parch: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ticket: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fare: Mapped[float | None] = mapped_column(Float, nullable=True)
    cabin: Mapped[str | None] = mapped_column(String(64), nullable=True)
    embarked: Mapped[str | None] = mapped_column(String(8), nullable=True)
