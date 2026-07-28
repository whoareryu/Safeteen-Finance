from fastapi import APIRouter

from admin.adapter.inbound.api.v1.piper_hendricks_ceo_router import hendricks_ceo_router
from admin.adapter.inbound.api.v1.piper_gilfoyle_sys_router import gilfoyle_sys_router
from admin.adapter.inbound.api.v1.piper_dunn_coo_router import dunn_coo_router
from admin.adapter.inbound.api.v1.piper_dinesh_dash_router import dinesh_dash_router
from admin.adapter.inbound.api.v1.piper_bighetti_hr_router import bighetti_hr_router
from admin.adapter.inbound.api.v1.pdf_loader_router import pdf_loader_router
from admin.adapter.inbound.api.v1.langchain_chat_router import langchain_chat_router

admin_app_router = APIRouter(prefix="/admin", tags=["admin-app"])
admin_app_router.include_router(hendricks_ceo_router)
admin_app_router.include_router(gilfoyle_sys_router)
admin_app_router.include_router(dunn_coo_router)
admin_app_router.include_router(dinesh_dash_router)
admin_app_router.include_router(bighetti_hr_router)
admin_app_router.include_router(pdf_loader_router)
admin_app_router.include_router(langchain_chat_router)

__all__ = [
    "admin_app_router",
    "hendricks_ceo_router",
    "gilfoyle_sys_router",
    "dunn_coo_router",
    "dinesh_dash_router",
    "bighetti_hr_router",
    "pdf_loader_router",
    "langchain_chat_router",
]
