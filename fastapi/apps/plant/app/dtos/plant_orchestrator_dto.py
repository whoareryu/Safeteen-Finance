from __future__ import annotations

from dataclasses import dataclass

from plant.app.dtos.care_guide_dto import CareGuideResult
from plant.app.dtos.diagnosis_dto import DiagnosisResult, DiagnosisUploadCommand
from plant.app.dtos.notification_dto import NotificationResult
from plant.app.dtos.weather_dto import WeatherIngestCommand, WeatherSnapshotResult


@dataclass(frozen=True)
class PlantPipelineCommand:
    upload: DiagnosisUploadCommand | None = None
    weather: WeatherIngestCommand | None = None


@dataclass(frozen=True)
class PlantPipelineResult:
    diagnosis: DiagnosisResult | None = None
    care_guide: CareGuideResult | None = None
    weather: WeatherSnapshotResult | None = None
    notifications: list[NotificationResult] | None = None
