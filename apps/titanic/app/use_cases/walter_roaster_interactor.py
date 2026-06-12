from titanic.app.ports.input.walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.dtos.walter_roaster_dto import WalterRoasterQuery
from titanic.app.ports.output.walter_roaster_repository import WalterRoasterRepository
from apps.titanic.adapter.inbound.api.schemas.crew_walter_roaster_schema import WalterRoasterSchema
import logging
from titanic.adapter.outbound.pg.walter_roaster_pg_repository import WalterRoasterPgRepository

logger = logging.getLogger(__name__)

class WalterRoasterInteractor(WalterRoasterUseCase):
    
    def __init__(self):
        pass

    def introduce_myself(self, schema:WalterRoasterSchema):
        # 스키마에 저장된 정보를 쿼리에 옮겨 담는 코드 구현
        query = WalterRoasterQuery(
            id = schema.id,
            name = schema.name,
            memo = schema.memo
        )
        logger.info("######################################################")
        logger.info("🍤[월터 유스케이스] 월터의 자기소개글을 라우터에서 가져온 내용")
        logger.info(f"🍗월터의 자기소개글: {query.memo}")
        logger.info(f"🥩월터의 이름: {query.name}")
        logger.info(f"🍙월터의 ID: {query.id}")
        logger.info("######################################################")

        walter : WalterRoasterRepository = WalterRoasterPgRepository()
        walter.introduce_myself(query)

        pass

