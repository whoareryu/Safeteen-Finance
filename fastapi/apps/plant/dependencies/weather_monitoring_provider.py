from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db

from plant.adapter.outbound.pg.weather_snapshot_pg_repository import WeatherSnapshotPgRepository
from plant.app.ports.input.weather_monitoring_use_case import WeatherMonitoringUseCase
from plant.app.use_cases.weather_monitoring_interactor import WeatherMonitoringInteractor
from plant.dependencies.notification_provider import get_notification_use_case


def get_weather_monitoring_use_case(
    db: AsyncSession = Depends(get_db),
) -> WeatherMonitoringUseCase:
    return WeatherMonitoringInteractor(
        repository=WeatherSnapshotPgRepository(session=db),
        notification=get_notification_use_case(db=db),
    )
