from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.diagnosis_dto import DiagnosisResult, DiagnosisUploadCommand


class DiagnosisUseCase(ABC):
    """Inbound 입력 포트 — 잎사귀 사진 업로드 기반 품종·증상 진단."""

    @abstractmethod
    async def diagnose(self, command: DiagnosisUploadCommand) -> DiagnosisResult:
        pass

    @abstractmethod
    async def get(self, diagnosis_id: int) -> DiagnosisResult:
        pass
