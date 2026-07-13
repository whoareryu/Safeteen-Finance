from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db

from plant.app.ports.input.plant_orchestrator_use_case import PlantOrchestratorUseCase
from plant.app.use_cases.plant_orchestrator_interactor import PlantOrchestratorInteractor
from plant.dependencies.care_guide_provider import get_care_guide_use_case
from plant.dependencies.diagnosis_provider import get_diagnosis_use_case
from plant.dependencies.weather_monitoring_provider import get_weather_monitoring_use_case


def get_plant_orchestrator_use_case(
    db: AsyncSession = Depends(get_db),
) -> PlantOrchestratorUseCase:
    return PlantOrchestratorInteractor(
        diagnosis=get_diagnosis_use_case(db=db),
        care_guide=get_care_guide_use_case(db=db),
        weather=get_weather_monitoring_use_case(db=db),
    )
