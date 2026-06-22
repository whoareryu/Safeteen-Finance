import logging
from sqlalchemy.ext.asyncio import AsyncSession
from silicon_valley.app.ports.output.piper_dunn_coo_port import DunnCooPort
from silicon_valley.app.dtos.piper_dunn_coo_dto import DunnCooQuery, DunnCooResponse

logger = logging.getLogger(__name__)


class DunnCooRepository(DunnCooPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, schema: DunnCooQuery) -> DunnCooResponse:
        logger.info(f"[DunnCooRepository] id={schema.id}")
        return DunnCooResponse(id=schema.id * 10000, name=schema.name)
