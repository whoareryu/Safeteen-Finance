import logging
from sqlalchemy.ext.asyncio import AsyncSession
from titanic.app.ports.output.passenger_isidor_couple_repository import IsidorCoupleRepository
from titanic.app.dtos.passenger_isidor_couple_dto import IsidorCoupleQuery, IsidorCoupleResponse

logger = logging.getLogger(__name__)


class IsidorCouplePGRepository(IsidorCoupleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: IsidorCoupleQuery) -> IsidorCoupleResponse:
        logger.info(f"[IsidorCouplePGRepository] id={query.id}")
        return IsidorCoupleResponse(id=query.id * 10000, name=query.name)
