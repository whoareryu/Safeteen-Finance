from __future__ import annotations

import asyncio
import logging
import uuid

import boto3

from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway

logger = logging.getLogger(__name__)


class S3ImageStorageGateway(ImageStorageGateway):
    """AWS S3 버킷에 이미지를 저장하는 게이트웨이."""

    def __init__(self, bucket: str, region: str, prefix: str = "vision") -> None:
        self._bucket = bucket
        self._prefix = prefix
        # 리전 엔드포인트를 명시하지 않으면 presigned URL이 전역 엔드포인트로
        # 생성되어, 리전 엔드포인트로 307 리다이렉트되는 과정에서 SigV4 서명이
        # 깨져 403이 난다 — put_object 등 다른 호출에는 영향 없다.
        self._client = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=f"https://s3.{region}.amazonaws.com",
        )

    async def save(self, filename: str, content_type: str, data: bytes) -> str:
        return await asyncio.to_thread(self._save_sync, filename, content_type, data)

    def _save_sync(self, filename: str, content_type: str, data: bytes) -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        key = f"{self._prefix}/{uuid.uuid4().hex}.{ext}"
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        logger.info("[S3ImageStorageGateway] 업로드 완료 → s3://%s/%s", self._bucket, key)
        return f"https://{self._bucket}.s3.{self._client.meta.region_name}.amazonaws.com/{key}"

    async def presigned_url(self, stored_url: str, expires_in: int = 3600) -> str:
        """버킷이 Block Public Access라 save()가 돌려준 URL은 그대로 열람 불가(403).

        저장된 URL에서 key만 뽑아 매번 새로 서명한 URL을 만든다 — DB에는 save()의
        원래 URL을 그대로 두고, 응답 내려줄 때만 이걸로 감싼다.
        """
        return await asyncio.to_thread(self._presign_sync, stored_url, expires_in)

    def _presign_sync(self, stored_url: str, expires_in: int) -> str:
        prefix = f"https://{self._bucket}.s3.{self._client.meta.region_name}.amazonaws.com/"
        if not stored_url.startswith(prefix):
            # 이 게이트웨이가 만든 URL이 아니면(예전 로컬 저장 URL 등) 서명할 수 없으니 그대로 반환.
            return stored_url
        key = stored_url[len(prefix):]
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )
