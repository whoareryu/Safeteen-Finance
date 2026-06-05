from titanic.app.ports.output.walter_roaster_repository import WalterRoasterRepository
from titanic.app.dtos.walter_roaster_dto import WalterRoasterResponse
import logging
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class WalterRoasterPgRepository(WalterRoasterRepository):
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    def introduce_myself(self, query:WalterRoasterResponse):
        return WalterRoasterResponse(
            id=query.id,
            name=query.name,
            memo=query.memo
        )
        

