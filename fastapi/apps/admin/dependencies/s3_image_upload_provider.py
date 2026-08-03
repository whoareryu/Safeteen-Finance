from __future__ import annotations

from fastapi import Depends

from admin.app.ports.input.s3_image_upload_use_case import S3ImageUploadUseCase
from admin.app.use_cases.s3_image_upload_interactor import S3ImageUploadInteractor
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway
from ontology.dependencies.image_storage_provider import get_admin_image_storage_gateway


def get_s3_image_upload_use_case(
    storage: ImageStorageGateway = Depends(get_admin_image_storage_gateway),
) -> S3ImageUploadUseCase:
    return S3ImageUploadInteractor(storage=storage)
