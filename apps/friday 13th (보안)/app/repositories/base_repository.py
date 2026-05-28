import logging
from typing import TypeVar

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository:
    """공통 DB 세션 — add 후 flush·commit 으로 즉시 INSERT."""

    def __init__(self, db: Session):
        self._db = db

    def _insert_now(self, entity: T) -> T:
        """세션에 추가 후 바로 DB에 반영(commit)."""
        try:
            self._db.add(entity)
            self._db.flush()
            self._db.commit()
            self._db.refresh(entity)
            return entity
        except Exception:
            self._db.rollback()
            logger.exception("[secom.repository] INSERT 실패 — rollback 수행")
            raise
