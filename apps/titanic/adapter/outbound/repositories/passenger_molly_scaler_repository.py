from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.passenger_molly_scaler_dto import MollyScalerQuery, MollyScalerResponse
from titanic.app.ports.output.passenger_molly_scaler_port import MollyScalerPort

logger = logging.getLogger(__name__)


class MollyScalerRepository(MollyScalerPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, schema: MollyScalerQuery) -> MollyScalerResponse:
        return MollyScalerResponse(id=schema.id * 10000, name=schema.name)

