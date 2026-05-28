from __future__ import annotations

import logging
from typing import Any

from apps.titanic.app.ports.input.walter_use_case import WalterUseCasePort
from apps.titanic.app.ports.output.walter_repository import WalterRepository

logger = logging.getLogger(__name__)


class WalterQueryUseCase(WalterUseCasePort):
    """승객 명단 조회 유스케이스."""

    def __init__(self, repository: WalterRepository | None = None) -> None:
        self._repository = repository or WalterRepository()

    def get_passenger_page(self, *, page: int, page_size: int) -> dict[str, Any]:
        logger.info(
            "[Walter 경로] (2/4) Input/UseCase app/use_cases/walter_query.py -> "
            "app/ports/output/walter_repository.py | page=%d page_size=%d",
            page,
            page_size,
        )
        result = self._repository.get_passenger_page(page=page, page_size=page_size)
        total_pages = max(1, (result["total"] + result["page_size"] - 1) // result["page_size"])
        return {
            "items": result["items"],
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": total_pages,
        }
