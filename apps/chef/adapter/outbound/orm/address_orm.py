from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.matrix.grid_neo_theone_base import Base


class ContactORM(Base):
    __tablename__ = "chef_contacts"

    id:            Mapped[str | None] = mapped_column(String, primary_key=True, nullable=False, index=True)
    first_name:    Mapped[str | None] = mapped_column(String, nullable=False, default="")
    last_name:     Mapped[str | None] = mapped_column(String, nullable=True,  default="")
    middle_name:   Mapped[str | None] = mapped_column(String, nullable=True,  default="")
    nickname:      Mapped[str | None] = mapped_column(String, nullable=True,  default="")
    email:         Mapped[str | None] = mapped_column(String, nullable=False, default="")
    phone:         Mapped[str | None] = mapped_column(String, nullable=True,  default="")
    company:       Mapped[str | None] = mapped_column(String, nullable=True,  default="")
    company_title: Mapped[str | None] = mapped_column(String, nullable=True,  default="")
    birthday:      Mapped[str | None] = mapped_column(String, nullable=True,  default="")
    notes:         Mapped[str | None] = mapped_column(String, nullable=True,  default="")
    labels:        Mapped[str | None] = mapped_column(String, nullable=True,  default="")
