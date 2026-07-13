from __future__ import annotations

from plant.adapter.inbound.api.schemas.weather_schema import (
    WeatherIngestRequest,
    WeatherSnapshotResponse,
)
from plant.app.dtos.weather_dto import WeatherIngestCommand, WeatherSnapshotResult


def to_command(request: WeatherIngestRequest) -> WeatherIngestCommand:
    return WeatherIngestCommand(
        region=request.region,
        temp_c=request.temp_c,
        humidity_pct=request.humidity_pct,
        sunlight_desc=request.sunlight_desc,
    )


def to_response(result: WeatherSnapshotResult) -> WeatherSnapshotResponse:
    return WeatherSnapshotResponse(
        id=result.id,
        region=result.region,
        temp_c=result.temp_c,
        humidity_pct=result.humidity_pct,
        sunlight_desc=result.sunlight_desc,
        is_dry_day=result.is_dry_day,
    )
