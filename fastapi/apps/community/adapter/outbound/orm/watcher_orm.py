from __future__ import annotations

from core.infra.database_manager import Base


class WatcherORM(Base):
    __abstract__ = True
