from __future__ import annotations

import logging

from ....app.ports.output.hartley_violin_repository import (
    HartleyViolinRepositoryPort,
    HartleyViolinRepositoryResult,
)

logger = logging.getLogger(__name__)


class HartleyViolinPGRepository(HartleyViolinRepositoryPort):
    """HartleyViolinRepositoryPort 구현."""

    async def get_violin(self) -> HartleyViolinRepositoryResult:
        logger.info(
            "[Hartley] adapter/outbound/pg/hartley_violin_pg_repository.py"
        )
        return HartleyViolinRepositoryResult(message="Hello, World!")
