from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.database import Base, IntIdPrimaryKeyMixin


class TelegramMessageORM(IntIdPrimaryKeyMixin, Base):
    __tablename__ = "telegram_messages"

    text: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
