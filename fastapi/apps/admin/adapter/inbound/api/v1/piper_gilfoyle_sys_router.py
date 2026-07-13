from fastapi import APIRouter, Depends

from admin.adapter.inbound.api.schemas.piper_gilfoyle_sys_schema import GilfoyleSysSchema
from admin.app.dtos.piper_gilfoyle_sys_dto import GilfoyleSysResponse
from admin.app.ports.input.piper_gilfoyle_sys_use_case import GilfoyleSysUseCase
from admin.dependencies.piper_gilfoyle_sys_provider import get_gilfoyle_sys_use_case

'''
버트람 길포일 (Bertram Gilfoyle)
Pied Piper 시스템 아키텍트. 사탄주의자이자 서버·보안·인프라 전문가.
감정 표현이 없고 냉소적이지만 기술적으로는 최고 수준.
'''
gilfoyle_sys_router = APIRouter(prefix="/gilfoyle", tags=["gilfoyle"])

@gilfoyle_sys_router.get("/myself")
async def introduce_myself(
    gilfoyle: GilfoyleSysUseCase = Depends(get_gilfoyle_sys_use_case)
) -> GilfoyleSysResponse:

    return await gilfoyle.introduce_myself(
        GilfoyleSysSchema(
            id=2,
            name="버트람 길포일 (Bertram Gilfoyle)"
        )
    )
