import logging
from sqlalchemy.ext.asyncio import AsyncSession
from silicon_valley.app.ports.output.piper_dinesh_dash_port import DineshDashPort
from silicon_valley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery, DineshDashResponse

logger = logging.getLogger(__name__)


class DineshDashRepository(DineshDashPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, schema: DineshDashQuery) -> DineshDashResponse:
        logger.info(f"[DineshDashRepository] id={schema.id}")
        return DineshDashResponse(id=schema.id * 10000, name=schema.name)
