from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from core.matrix.grid_neo_theone_base import Base
from core.matrix.gird_oracle_database_manager import IntIdPrimaryKeyMixin

_EMBEDDING_DIM = 1024


class ReceiverORM(Base, IntIdPrimaryKeyMixin):
    __tablename__ = "chef_email_logs"

    sender: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    recipient: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    subject: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    preview: Mapped[str] = mapped_column(Text, nullable=False, default="")
    message_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    embedding: Mapped[list[float] | None] = mapped_column(Vector(_EMBEDDING_DIM), nullable=True)
