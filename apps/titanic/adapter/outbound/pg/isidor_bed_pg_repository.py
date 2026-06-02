from __future__ import annotations

import logging

from ....app.ports.output.isidor_bed_repository import (
    IsidorBedRepositoryPort,
    IsidorBedRepositoryResult,
)

logger = logging.getLogger(__name__)


class IsidorBedPGRepository(IsidorBedRepositoryPort):
    """IsidorBedRepositoryPort 구현."""

    async def get_bed(self) -> IsidorBedRepositoryResult:
        logger.info("[Isidor] adapter/outbound/pg/isidor_bed_pg_repository.py")
        return IsidorBedRepositoryResult(message="Hello, World!")
