from __future__ import annotations

from fastapi import APIRouter, Depends

from plant.adapter.inbound.mappers.weather_mapper import to_command, to_response
from plant.adapter.inbound.api.schemas.weather_schema import (
    WeatherIngestRequest,
    WeatherSnapshotResponse,
)
from plant.app.ports.input.weather_monitoring_use_case import WeatherMonitoringUseCase
from plant.dependencies.weather_monitoring_provider import get_weather_monitoring_use_case

weather_router = APIRouter(prefix="/weather", tags=["plant-weather"])


@weather_router.post("/ingest", summary="n8n 날씨 허브 웹훅 수신")
async def ingest_weather(
    request: WeatherIngestRequest,
    use_case: WeatherMonitoringUseCase = Depends(get_weather_monitoring_use_case),
) -> WeatherSnapshotResponse:
    result = await use_case.ingest(to_command(request))
    return to_response(result)


@weather_router.get("/current", summary="지역별 최신 날씨 조회")
async def get_current_weather(
    region: str,
    use_case: WeatherMonitoringUseCase = Depends(get_weather_monitoring_use_case),
) -> WeatherSnapshotResponse:
    result = await use_case.get_current(region)
    return to_response(result)
