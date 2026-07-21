from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db

from plant.adapter.outbound.pg.badge_pg_repository import BadgePgRepository
from plant.adapter.outbound.pg.care_schedule_pg_repository import CareSchedulePgRepository
from plant.adapter.outbound.pg.plant_checkin_pg_repository import PlantCheckinPgRepository
from plant.adapter.outbound.pg.plant_pg_repository import PlantPgRepository
from plant.app.ports.input.checkin_use_case import CheckinUseCase
from plant.app.ports.output.plant_checkin_repository import PlantCheckinRepository
from plant.app.use_cases.checkin_interactor import CheckinInteractor
from plant.dependencies.diagnosis_provider import (
    _get_image_storage_gateway,
    _get_species_classifier,
)


def get_checkin_repository(db: AsyncSession = Depends(get_db)) -> PlantCheckinRepository:
    return PlantCheckinPgRepository(session=db)


def get_checkin_use_case(db: AsyncSession = Depends(get_db)) -> CheckinUseCase:
    return CheckinInteractor(
        plant_repository=PlantPgRepository(session=db),
        checkin_repository=PlantCheckinPgRepository(session=db),
        badge_repository=BadgePgRepository(session=db),
        care_schedule_repository=CareSchedulePgRepository(session=db),
        species_classifier=_get_species_classifier(),
        storage=_get_image_storage_gateway(),
    )
