from __future__ import annotations

import logging

from ....app.ports.output.cal_pistol_repository import (
    CalPistolRepositoryPort,
    CalPistolRepositoryResult,
)

logger = logging.getLogger(__name__)


class CalPistolPGRepository(CalPistolRepositoryPort):
    """CalPistolRepositoryPort 구현."""

    async def get_cal_pistol(self) -> CalPistolRepositoryResult:
        logger.info("[Cal] adapter/outbound/pg/cal_pistol_pg_repository.py")
        return CalPistolRepositoryResult(message="Hello, World!")
