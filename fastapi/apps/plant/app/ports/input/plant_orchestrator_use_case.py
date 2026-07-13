from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.plant_orchestrator_dto import PlantPipelineResult
from plant.app.dtos.diagnosis_dto import DiagnosisUploadCommand
from plant.app.dtos.weather_dto import WeatherIngestCommand


class PlantOrchestratorUseCase(ABC):
    """[진단 에이전트]/[환경 에이전트]/[알림 에이전트]를 조합하는 plant 내부 코디네이터."""

    @abstractmethod
    async def run_diagnosis_pipeline(self, command: DiagnosisUploadCommand) -> PlantPipelineResult:
        """사진 진단 → 케어 처방까지 한 번에 실행한다."""
        pass

    @abstractmethod
    async def run_weather_dispatch(self, command: WeatherIngestCommand) -> PlantPipelineResult:
        """날씨 수신 → (건조일이면) 알림 발송까지 한 번에 실행한다."""
        pass
