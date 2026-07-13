from fastapi import APIRouter, Depends

from admin.adapter.inbound.api.schemas.piper_dunn_coo_schema import DunnCooSchema
from admin.app.dtos.piper_dunn_coo_dto import DunnCooResponse
from admin.app.ports.input.piper_dunn_coo_use_case import DunnCooUseCase
from admin.dependencies.piper_dunn_coo_provider import get_dunn_coo_use_case

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
