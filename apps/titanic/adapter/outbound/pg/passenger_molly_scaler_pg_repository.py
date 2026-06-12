from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.passenger_molly_scaler_dto import MollyScalerQuery, MollyScalerResponse
from titanic.app.ports.output.passenger_molly_scaler_repository import MollyScalerRepository

logger = logging.getLogger(__name__)


class MollyScalerPGRepository(MollyScalerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: MollyScalerQuery) -> MollyScalerResponse:
        return MollyScalerResponse(id=query.id * 10000, name=query.name)

