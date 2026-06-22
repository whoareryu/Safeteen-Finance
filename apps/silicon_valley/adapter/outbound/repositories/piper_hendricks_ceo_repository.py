import logging
from sqlalchemy.ext.asyncio import AsyncSession
from silicon_valley.app.ports.output.piper_hendricks_ceo_port import HendricksCeoPort
from silicon_valley.app.dtos.piper_hendricks_ceo_dto import HendricksCeoQuery, HendricksCeoResponse

logger = logging.getLogger(__name__)


class HendricksCeoRepository(HendricksCeoPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, schema: HendricksCeoQuery) -> HendricksCeoResponse:
        logger.info(f"[HendricksCeoRepository] id={schema.id}")
        return HendricksCeoResponse(id=schema.id * 10000, name=schema.name)
