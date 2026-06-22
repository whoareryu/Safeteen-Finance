import logging
from sqlalchemy.ext.asyncio import AsyncSession
from silicon_valley.app.ports.output.piper_gilfoyle_sys_port import GilfoyleSysPort
from silicon_valley.app.dtos.piper_gilfoyle_sys_dto import GilfoyleSysQuery, GilfoyleSysResponse

logger = logging.getLogger(__name__)


class GilfoyleSysRepository(GilfoyleSysPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, schema: GilfoyleSysQuery) -> GilfoyleSysResponse:
        logger.info(f"[GilfoyleSysRepository] id={schema.id}")
        return GilfoyleSysResponse(id=schema.id * 10000, name=schema.name)
