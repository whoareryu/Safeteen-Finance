from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.raw_content_entity import RawContentEntity


class ContentStoragePort(ABC):
    """Outbound 출력 포트 — QLoRA 학습용 JSONL 로컬 저장소."""

    @abstractmethod
    def save(self, content: RawContentEntity) -> str:
        """저장된 파일 경로를 반환한다."""
        pass
