from fastapi import APIRouter

from silicon_valley.adapter.inbound.api.v1.piper_hendricks_ceo_router import hendricks_ceo_router
from silicon_valley.adapter.inbound.api.v1.piper_gilfoyle_sys_router import gilfoyle_sys_router
from silicon_valley.adapter.inbound.api.v1.piper_dunn_coo_router import dunn_coo_router
from silicon_valley.adapter.inbound.api.v1.piper_dinesh_dash_router import dinesh_dash_router
from silicon_valley.adapter.inbound.api.v1.piper_bighetti_hr_router import bighetti_hr_router

silicon_valley_router = APIRouter(prefix="/silicon-valley", tags=["silicon-valley"])
silicon_valley_router.include_router(hendricks_ceo_router)
silicon_valley_router.include_router(gilfoyle_sys_router)
silicon_valley_router.include_router(dunn_coo_router)
silicon_valley_router.include_router(dinesh_dash_router)
silicon_valley_router.include_router(bighetti_hr_router)

__all__ = [
    "silicon_valley_router",
    "hendricks_ceo_router",
    "gilfoyle_sys_router",
    "dunn_coo_router",
    "dinesh_dash_router",
    "bighetti_hr_router",
]
