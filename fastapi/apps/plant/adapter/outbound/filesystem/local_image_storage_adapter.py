from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway


class LocalImageStorageAdapter(ImageStorageGateway):
    """S3 버킷 발급 전까지 진단 사진을 로컬 디스크에 저장하는 임시 게이트웨이.

    PLANT_S3_BUCKET 발급 후에는 S3ImageStorageGateway로 교체한다.
    """

    def __init__(self, base_dir: Path, public_base_url: str, url_prefix: str) -> None:
        self._base_dir = base_dir
        self._public_base_url = public_base_url.rstrip("/")
        self._url_prefix = url_prefix.strip("/")
        self._base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, filename: str, content_type: str, data: bytes) -> str:
        return await asyncio.to_thread(self._save_sync, filename, data)

    def _save_sync(self, filename: str, data: bytes) -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        key = f"{uuid.uuid4().hex}.{ext}"
        (self._base_dir / key).write_bytes(data)
        return f"{self._public_base_url}/{self._url_prefix}/{key}"

    async def presigned_url(self, stored_url: str, expires_in: int = 3600) -> str:
        """StaticFiles로 이미 공개 서빙 중이라 서명이 필요 없다 — 그대로 반환."""
        return stored_url
