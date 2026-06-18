import logging
from sqlalchemy.ext.asyncio import AsyncSession
from titanic.app.ports.output.passenger_isidor_couple_port import IsidorCouplePort
from titanic.app.dtos.passenger_isidor_couple_dto import IsidorCoupleQuery, IsidorCoupleResponse

logger = logging.getLogger(__name__)


class IsidorCoupleRepository(IsidorCouplePort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, schema: IsidorCoupleQuery) -> IsidorCoupleResponse:
        logger.info(f"[IsidorCoupleRepository] id={schema.id}")
        return IsidorCoupleResponse(id=schema.id * 10000, name=schema.name)
