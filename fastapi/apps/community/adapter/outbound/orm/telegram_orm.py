from __future__ import annotations
from core.infra.database_manager import Base


class TelegramORM(Base):
    __abstract__ = True
