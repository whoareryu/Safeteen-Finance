from titanic.app.ports.output.crew_walter_roaster_repository import WalterRoasterRepository
from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterResponse
from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterQuery
import logging
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class WalterRoasterPgRepository(WalterRoasterRepository):
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def introduce_myself(self, query: WalterRoasterQuery) -> WalterRoasterResponse:
        logger.info(f"[WalterRoasterPgRepository] introduce_myself 진입 | request_data={query}")
        response: WalterRoasterResponse = WalterRoasterResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴"
        )
        return response
    