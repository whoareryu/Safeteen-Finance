from __future__ import annotations

import logging

from ....app.ports.output.jack_sketch_repository import (
    JackSketchRepositoryPort,
    JackSketchRepositoryResult,
)

logger = logging.getLogger(__name__)


class JackSketchPGRepository(JackSketchRepositoryPort):
    """JackSketchRepositoryPort 구현."""

    async def get_sketch(self) -> JackSketchRepositoryResult:
        logger.info("[Jack] adapter/outbound/pg/jack_sketch_pg_repository.py")
        return JackSketchRepositoryResult(message="Hello, World!")
