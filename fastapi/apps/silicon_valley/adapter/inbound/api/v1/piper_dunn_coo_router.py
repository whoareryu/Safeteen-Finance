from fastapi import APIRouter, Depends

from silicon_valley.adapter.inbound.api.schemas.piper_dunn_coo_schema import DunnCooSchema
from silicon_valley.app.dtos.piper_dunn_coo_dto import DunnCooResponse
from silicon_valley.app.ports.input.piper_dunn_coo_use_case import DunnCooUseCase
from silicon_valley.dependencies.piper_dunn_coo_provider import get_dunn_coo_use_case

'''
재러드 던 (Jared Dunn)
Pied Piper COO. 본명 Donald Dunn. 전 Hooli 직원으로 리처드를 따라 이직.
과도하게 긍정적이고 헌신적인 운영 책임자.
'''
dunn_coo_router = APIRouter(prefix="/dunn", tags=["dunn"])

@dunn_coo_router.get("/myself")
async def introduce_myself(
    dunn: DunnCooUseCase = Depends(get_dunn_coo_use_case)
) -> DunnCooResponse:

    return await dunn.introduce_myself(
        DunnCooSchema(
            id=3,
            name="재러드 던 (Jared Dunn)"
        )
    )
