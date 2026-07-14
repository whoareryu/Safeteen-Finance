from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db

from plant.adapter.outbound.llm.plant_llm_adapter import PlantLlmAdapter
from plant.adapter.outbound.pg.plant_pg_repository import PlantPgRepository
from plant.app.ports.input.register_plant_use_case import RegisterPlantUseCase
from plant.app.ports.output.plant_repository import PlantRepository
from plant.app.use_cases.register_plant_interactor import RegisterPlantInteractor
from plant.dependencies.diagnosis_provider import _get_species_yolo_use_case

_LLM = PlantLlmAdapter(model="exaone3.5:2.4b")


def get_plant_repository(db: AsyncSession = Depends(get_db)) -> PlantRepository:
    return PlantPgRepository(session=db)


def get_register_plant_use_case(db: AsyncSession = Depends(get_db)) -> RegisterPlantUseCase:
    return RegisterPlantInteractor(
        plant_repository=PlantPgRepository(session=db),
        llm=_LLM,
        yolo=_get_species_yolo_use_case(),
    )
