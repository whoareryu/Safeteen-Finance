from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db
from ontology.dependencies.sommelier_graph_provider import get_sommelier_use_case

from plant.adapter.outbound.llm.plant_llm_adapter import PlantLlmAdapter
from plant.adapter.outbound.pg.care_prescription_pg_repository import CarePrescriptionPgRepository
from plant.adapter.outbound.pg.diagnosis_pg_repository import DiagnosisPgRepository
from plant.app.ports.input.care_guide_use_case import CareGuideUseCase
from plant.app.use_cases.care_guide_interactor import CareGuideInteractor

_LLM = PlantLlmAdapter()


def get_care_guide_use_case(db: AsyncSession = Depends(get_db)) -> CareGuideUseCase:
    return CareGuideInteractor(
        diagnosis_repository=DiagnosisPgRepository(session=db),
        care_prescription_repository=CarePrescriptionPgRepository(session=db),
        llm=_LLM,
        sommelier=get_sommelier_use_case(),
    )
