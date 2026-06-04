from titanic.app.ports.output.walter_roaster_repository import WalterRoasterRepository
from titanic.app.dtos.walter_roaster_dto import WalterRoasterQuery
import logging

logger = logging.getLogger(__name__)

class WalterRoasterPgRepository(WalterRoasterRepository):
    
    def __init__(self):
        pass

    def introduce_myself(self, query:WalterRoasterQuery):
        
        logger.info("######################################################")
        logger.info("🍤[월터 레포지토리] 월터의 자기소개글을 유스케이스에서 가져온 내용")
        logger.info(f"🍗월터의 자기소개글: {query.memo}")
        logger.info(f"🥩월터의 이름: {query.name}")
        logger.info(f"🍙월터의 ID: {query.id}")
        logger.info("######################################################")
        
        pass
        
