from __future__ import annotations

import logging

from ....app.ports.output.andrews_blueprint_repository import (
    AndrewsBlueprintRepositoryPort,
    AndrewsBlueprintRepositoryResult,
)

logger = logging.getLogger(__name__)


class AndrewsBlueprintPGRepository(AndrewsBlueprintRepositoryPort):
    """AndrewsBlueprintRepositoryPort 구현."""

    async def get_blueprint(self) -> AndrewsBlueprintRepositoryResult:
        logger.info(
            "[Andrews] adapter/outbound/pg/andrews_blueprint_pg_repository.py"
        )
        return AndrewsBlueprintRepositoryResult(message="Hello, World!")
