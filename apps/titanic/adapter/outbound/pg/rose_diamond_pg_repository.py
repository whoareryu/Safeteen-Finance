from __future__ import annotations

import logging

from ....app.ports.output.rose_diamond_repository import (
    RoseDiamondRepositoryPort,
    RoseDiamondRepositoryResult,
)

logger = logging.getLogger(__name__)


class RoseDiamondPGRepository(RoseDiamondRepositoryPort):
    """RoseDiamondRepositoryPort 구현."""

    async def get_diamond(self) -> RoseDiamondRepositoryResult:
        logger.info("[Rose] adapter/outbound/pg/rose_diamond_pg_repository.py")
        return RoseDiamondRepositoryResult(message="Hello, World!")
