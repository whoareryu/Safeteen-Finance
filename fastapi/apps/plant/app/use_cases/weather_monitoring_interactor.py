from __future__ import annotations

from plant.app.dtos.weather_dto import WeatherIngestCommand, WeatherSnapshotResult
from plant.app.ports.input.notification_use_case import NotificationUseCase
from plant.app.ports.input.weather_monitoring_use_case import WeatherMonitoringUseCase
from plant.app.ports.output.weather_snapshot_repository import WeatherSnapshotRepository
from plant.domain.entities.weather_snapshot_entity import WeatherSnapshotEntity

_DRY_HUMIDITY_THRESHOLD_PCT = 40.0


def _is_dry_day(humidity_pct: float) -> bool:
    return humidity_pct < _DRY_HUMIDITY_THRESHOLD_PCT


class WeatherMonitoringInteractor(WeatherMonitoringUseCase):

    def __init__(
        self,
        repository: WeatherSnapshotRepository,
        notification: NotificationUseCase,
    ) -> None:
        self._repository = repository
        self._notification = notification

    async def ingest(self, command: WeatherIngestCommand) -> WeatherSnapshotResult:
        is_dry_day = _is_dry_day(command.humidity_pct)
        snapshot = await self._repository.save(
            WeatherSnapshotEntity(
                id=None,
                region=command.region,
                temp_c=command.temp_c,
                humidity_pct=command.humidity_pct,
                sunlight_desc=command.sunlight_desc,
                is_dry_day=is_dry_day,
            )
        )

        if is_dry_day:
            await self._notification.dispatch_for_region(command.region, snapshot)

        return self._to_result(snapshot)

    async def get_current(self, region: str) -> WeatherSnapshotResult:
        snapshot = await self._repository.find_latest(region)
        if snapshot is None:
            raise ValueError(f"{region} 지역의 날씨 데이터가 없습니다")
        return self._to_result(snapshot)

    @staticmethod
    def _to_result(snapshot: WeatherSnapshotEntity) -> WeatherSnapshotResult:
        return WeatherSnapshotResult(
            id=snapshot.id,  # type: ignore[arg-type]
            region=snapshot.region,
            temp_c=snapshot.temp_c,
            humidity_pct=snapshot.humidity_pct,
            sunlight_desc=snapshot.sunlight_desc,
            is_dry_day=snapshot.is_dry_day,
        )
