from fastapi import APIRouter

from admin.adapter.inbound.api.v1.pdf_loader_router import pdf_loader_router
from admin.adapter.inbound.api.v1.s3_image_upload_router import s3_image_upload_router

admin_app_router = APIRouter(prefix="/admin", tags=["admin-app"])
admin_app_router.include_router(pdf_loader_router)
admin_app_router.include_router(s3_image_upload_router)

__all__ = [
    "admin_app_router",
    "pdf_loader_router",
    "s3_image_upload_router",
]
