from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse
from titanic.app.ports.output.passenger_rose_model_port import RoseModelPort

logger = logging.getLogger(__name__)


class RoseModelRepository(RoseModelPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, schema: RoseModelQuery) -> RoseModelResponse:
        return RoseModelResponse(id=schema.id * 10000, name=schema.name)
