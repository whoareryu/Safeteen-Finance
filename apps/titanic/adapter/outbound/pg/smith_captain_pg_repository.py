from __future__ import annotations

import logging

from ....app.ports.output.smith_captain_repository import (
    SmithCaptainRepositoryPort,
    SmithCaptainRepositoryResult,
)

logger = logging.getLogger(__name__)


class SmithCaptainPGRepository(SmithCaptainRepositoryPort):
    """SmithCaptainRepositoryPort 구현."""

    async def get_captain(self) -> SmithCaptainRepositoryResult:
        logger.info("[Smith] adapter/outbound/pg/smith_captain_pg_repository.py")
        return SmithCaptainRepositoryResult(message="Hello, World!")
