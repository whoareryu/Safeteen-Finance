import logging
from sqlalchemy.ext.asyncio import AsyncSession
from silicon_valley.app.ports.output.piper_bighetti_hr_port import BighettiHrPort
from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery, BighettiHrResponse

logger = logging.getLogger(__name__)


class BighettiHrRepository(BighettiHrPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, schema: BighettiHrQuery) -> BighettiHrResponse:
        logger.info(f"[BighettiHrRepository] id={schema.id}")
        return BighettiHrResponse(id=schema.id * 10000, name=schema.name)
