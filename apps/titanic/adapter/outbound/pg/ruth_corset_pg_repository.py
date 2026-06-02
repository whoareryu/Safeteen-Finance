from __future__ import annotations

import logging

from ....app.ports.output.ruth_corset_repository import (
    RuthCorsetRepositoryPort,
    RuthCorsetRepositoryResult,
)

logger = logging.getLogger(__name__)


class RuthCorsetPGRepository(RuthCorsetRepositoryPort):
    """RuthCorsetRepositoryPort 구현."""

    async def get_corset(self) -> RuthCorsetRepositoryResult:
        logger.info("[Ruth] adapter/outbound/pg/ruth_corset_pg_repository.py")
        return RuthCorsetRepositoryResult(message="Hello, World!")
