from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol

from apps.titanic.adapter.outbound.pg.walter_pg_repository import WalterPgRepository

logger = logging.getLogger(__name__)


class WalterRepositoryPort(Protocol):
    """유스케이스가 의존하는 출력 포트 계약."""

    def get_passenger_page(self, *, page: int, page_size: int) -> dict[str, Any]: ...


@dataclass
class WalterRepositoryResult:
    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int


class WalterRepository(WalterRepositoryPort):
    def __init__(self) -> None:
        self._pg_repository = WalterPgRepository()

    def get_passenger_page(self, *, page: int, page_size: int) -> dict[str, Any]:
        logger.info(
            "[Walter 경로] (3/4) Output port app/ports/output/walter_repository.py -> "
            "adapter/outbound/pg/walter_pg_repository.py | page=%d page_size=%d",
            page,
            page_size,
        )
        result = self._pg_repository.get_passenger_page(page=page, page_size=page_size)
        return {
            "items": result.items,
            "total": result.total,
            "page": result.page,
            "page_size": result.page_size,
        }
