from __future__ import annotations

from plant.app.dtos.diagnosis_dto import DiagnosisUploadCommand
from plant.app.dtos.plant_orchestrator_dto import PlantPipelineResult
from plant.app.dtos.weather_dto import WeatherIngestCommand
from plant.app.ports.input.care_guide_use_case import CareGuideUseCase
from plant.app.ports.input.diagnosis_use_case import DiagnosisUseCase
from plant.app.ports.input.plant_orchestrator_use_case import PlantOrchestratorUseCase
from plant.app.ports.input.weather_monitoring_use_case import WeatherMonitoringUseCase
from plant.app.dtos.care_guide_dto import CareGuideCommand


class PlantOrchestratorInteractor(PlantOrchestratorUseCase):

    def __init__(
        self,
        diagnosis: DiagnosisUseCase,
        care_guide: CareGuideUseCase,
        weather: WeatherMonitoringUseCase,
    ) -> None:
        self._diagnosis = diagnosis
        self._care_guide = care_guide
        self._weather = weather

    async def run_diagnosis_pipeline(self, command: DiagnosisUploadCommand) -> PlantPipelineResult:
        diagnosis_result = await self._diagnosis.diagnose(command)
        care_guide_result = await self._care_guide.generate(
            CareGuideCommand(diagnosis_id=diagnosis_result.id)
        )
        return PlantPipelineResult(diagnosis=diagnosis_result, care_guide=care_guide_result)

    async def run_weather_dispatch(self, command: WeatherIngestCommand) -> PlantPipelineResult:
        weather_result = await self._weather.ingest(command)
        return PlantPipelineResult(weather=weather_result)
