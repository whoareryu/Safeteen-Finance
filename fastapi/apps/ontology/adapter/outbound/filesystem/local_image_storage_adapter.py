from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway


class LocalImageStorageAdapter(ImageStorageGateway):
    """S3(VISION_S3_BUCKET) 자격증명 발급 전까지 이미지를 로컬 디스크에 저장하는 임시 게이트웨이.

    plant 앱의 동명 어댑터와 동일한 역할이지만, 허브(ontology)가 스포크(plant) 코드를
    직접 import할 수 없어(스타 토폴로지 규칙) 별도로 둔다.
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
