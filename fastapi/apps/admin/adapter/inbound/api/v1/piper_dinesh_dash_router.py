from fastapi import APIRouter, Depends

from admin.adapter.inbound.api.schemas.piper_dinesh_dash_schema import DineshDashSchema
from admin.app.dtos.piper_dinesh_dash_dto import DineshDashResponse
from admin.app.ports.input.piper_dinesh_dash_use_case import DineshDashUseCase
from admin.dependencies.piper_dinesh_dash_provider import get_dinesh_dash_use_case

'''
디네시 추그타이 (Dinesh Chugtai)
Pied Piper 앱·채팅 개발자. 길포일과 끊임없이 경쟁하는 백엔드 엔지니어.
자신감이 넘치지만 길포일에게 항상 밀린다.
'''
dinesh_dash_router = APIRouter(prefix="/dinesh", tags=["dinesh"])

@dinesh_dash_router.get("/myself")
async def introduce_myself(
    dinesh: DineshDashUseCase = Depends(get_dinesh_dash_use_case)
) -> DineshDashResponse:

    return await dinesh.introduce_myself(
        DineshDashSchema(
            id=4,
            name="디네시 추그타이 (Dinesh Chugtai)"
        )
    )
