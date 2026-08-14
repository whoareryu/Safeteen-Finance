from __future__ import annotations

from core.infra.secret_manager import secret_manager
from ontology.adapter.outbound.s3.s3_image_storage_gateway import S3ImageStorageGateway
from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway

_S3_BUCKET = secret_manager.get_secret("VISION_S3_BUCKET", "")
_AWS_REGION = secret_manager.get_secret("AWS_REGION", "ap-northeast-2")


def get_admin_image_storage_gateway() -> ImageStorageGateway:
    """admin 스포크의 범용 이미지 업로드용 — vision_provider.py와 같은 버킷을 쓰되 prefix로 분리한다."""
    return S3ImageStorageGateway(bucket=_S3_BUCKET, region=_AWS_REGION, prefix="admin")
