"""CSV/외부 소스 적재 Template Method."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from sqlalchemy.orm import Session

from restaurant.app.ports.output.restaurant_repository import IRestaurantRepository

logger = logging.getLogger(__name__)


class BaseRestaurantImporter(ABC):
    """고정 흐름: 비우기(선택) → 행 처리 → 청크 flush."""

    def __init__(
        self,
        repository: IRestaurantRepository,
        *,
        chunk_size: int = 1000,
    ) -> None:
        self._repo = repository
        self._chunk_size = chunk_size

    def import_file(
        self,
        db: Session,
        source: Path,
        *,
        replace_all: bool = True,
    ) -> tuple[int, int]:
        if not source.is_file():
            raise FileNotFoundError(str(source))

        deleted = self._clear_existing(db) if replace_all else 0
        pending = []
        inserted = 0
        skipped = 0

        for entity in self._iter_entities(source):
            if entity is None:
                skipped += 1
                continue
            pending.append(entity)
            if len(pending) >= self._chunk_size:
                inserted += self._repo.bulk_insert(db, pending, commit=True)
                pending.clear()

        if pending:
            inserted += self._repo.bulk_insert(db, pending, commit=True)

        self._after_import(db, source, inserted=inserted, deleted=deleted, skipped=skipped)
        return inserted, deleted

    def _clear_existing(self, db: Session) -> int:
        return self._repo.delete_all(db)

    @abstractmethod
    def _iter_entities(self, source: Path):
        """서브클래스: 소스별 행 → ORM 엔티티."""
        raise NotImplementedError

    def _after_import(
        self,
        db: Session,
        source: Path,
        *,
        inserted: int,
        deleted: int,
        skipped: int,
    ) -> None:
        logger.info(
            "[gourmet import] source=%s inserted=%s deleted=%s skipped=%s",
            source,
            inserted,
            deleted,
            skipped,
        )
