from __future__ import annotations

from abc import ABC, abstractmethod


class ImageStorageGateway(ABC):

    @abstractmethod
    async def save(self, filename: str, content_type: str, data: bytes) -> str:
        """이미지를 저장하고 접근 가능한 URL을 반환한다."""
        pass

    @abstractmethod
    async def presigned_url(self, stored_url: str, expires_in: int = 3600) -> str:
        """save()가 반환한 URL을 받아, 그 시점에 실제로 열람 가능한 URL을 반환한다.

        버킷이 퍼블릭 접근을 막고 있으면(Block Public Access) save()가 반환한
        URL 자체는 브라우저에서 403이 난다 — DB에는 save()의 원래 URL을 그대로
        저장해 두고, 응답을 내려줄 때마다 이 메서드로 매번 새로 서명해서 만료
        걱정 없이 최신 URL을 돌려준다.
        """
        pass
