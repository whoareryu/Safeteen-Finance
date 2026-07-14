from __future__ import annotations

from plant.app.dtos.weather_dto import WeatherIngestCommand, WeatherSnapshotResult
from plant.app.ports.input.notification_use_case import NotificationUseCase
from plant.app.ports.input.weather_monitoring_use_case import WeatherMonitoringUseCase
from plant.app.ports.output.weather_api_gateway import WeatherApiGateway
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
        weather_api: WeatherApiGateway,
    ) -> None:
        self._repository = repository
        self._notification = notification
        self._weather_api = weather_api

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
        """실시간으로 외부 날씨 API를 조회해 최신 스냅샷으로 저장하고 반환한다."""
        live = await self._weather_api.fetch_current(region)
        return await self.ingest(
            WeatherIngestCommand(
                region=live.region,
                temp_c=live.temp_c,
                humidity_pct=live.humidity_pct,
                sunlight_desc=live.sunlight_desc,
            )
        )

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
