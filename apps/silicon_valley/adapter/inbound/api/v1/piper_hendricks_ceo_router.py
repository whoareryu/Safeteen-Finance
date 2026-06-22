from fastapi import APIRouter, Depends

from silicon_valley.adapter.inbound.api.schemas.piper_hendricks_ceo_schema import HendricksCeoSchema
from silicon_valley.app.dtos.piper_hendricks_ceo_dto import HendricksCeoResponse
from silicon_valley.app.ports.input.piper_hendricks_ceo_use_case import HendricksCeoUseCase
from silicon_valley.dependencies.piper_hendricks_ceo_provider import get_hendricks_ceo_use_case

'''
리처드 헨드릭스 (Richard Hendricks)
Pied Piper의 CEO. 중간 아웃(Middle-Out) 압축 알고리즘을 발명한 천재 개발자.
Hooli의 빅 헤드 스캔들을 피해 독립하여 자신의 회사를 세운다.
'''
hendricks_ceo_router = APIRouter(prefix="/hendricks", tags=["hendricks"])

@hendricks_ceo_router.get("/myself")
async def introduce_myself(
    hendricks: HendricksCeoUseCase = Depends(get_hendricks_ceo_use_case)
) -> HendricksCeoResponse:

    return await hendricks.introduce_myself(
        HendricksCeoSchema(
            id=1,
            name="리처드 헨드릭스 (Richard Hendricks)"
        )
    )
