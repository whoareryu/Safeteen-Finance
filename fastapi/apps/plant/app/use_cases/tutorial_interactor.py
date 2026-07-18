from __future__ import annotations

from datetime import datetime, timezone

from ontology.app.ports.output.image_storage_gateway import ImageStorageGateway

from plant.app.dtos.tutorial_dto import (
    TutorialCreateCommand,
    TutorialMoveLightCommand,
    TutorialStateResult,
)
from plant.app.ports.input.tutorial_use_case import TutorialUseCase
from plant.app.ports.output.photo_cache_repository import PhotoCacheRepository
from plant.app.ports.output.pixabay_image_gateway import PixabayImageGateway
from plant.app.ports.output.tutorial_repository import TutorialRepository
from plant.app.ports.output.weather_api_gateway import WeatherApiGateway
from plant.domain.entities.photo_cache_entity import PhotoCacheEntity
from plant.domain.entities.tutorial_plant_entity import TutorialPlantEntity
from plant.domain.value_objects.growth_stage import compute_growth_stage
from plant.domain.value_objects.tutorial_state import (
    LIGHT_PARTIAL,
    LIGHT_SHADE,
    LIGHT_SUN,
    STATUS_HEALTHY,
    STATUS_NUTRIENT_LOW,
    STATUS_OVERWATERED,
    STATUS_THIRSTY,
    build_photo_query,
    compute_status,
    find_species,
)

_ACTION_POINTS = 5
_WATER_GAIN = 40.0
_NUTRIENT_GAIN = 40.0
_DRY_DAY_MOISTURE_DECAY_PER_DAY = 25.0
_NORMAL_MOISTURE_DECAY_PER_DAY = 12.0
_NUTRIENT_DECAY_PER_DAY = 8.0
_DRY_HUMIDITY_THRESHOLD_PCT = 40.0

_WATER_OK_MSG = "물을 줬어요! 수분이 보충되었어요 💧"
_WATER_OVERWATERED_MSG = "물을 너무 많이 줬어요! 흙이 질척해요 😥"
_NUTRIENT_OK_MSG = "영양제를 줬어요! 영양이 채워졌어요 🌱"
_CREATE_MSG = "새 식물을 심었어요! 잘 돌봐주세요 🌱"

_CHECK_LEAVES_MESSAGES = {
    STATUS_HEALTHY: "잎이 건강하고 흙도 촉촉해요. 아주 잘 돌보고 있어요 🌿",
    STATUS_THIRSTY: "흙이 말라있어요. 물을 줘야 할 때예요 💧",
    STATUS_OVERWATERED: "흙이 너무 젖어있어요. 잠시 물주기를 쉬어주세요 😥",
    STATUS_NUTRIENT_LOW: "잎에 영양이 부족해 보여요. 영양제를 줘볼까요? 🌱",
}


class TutorialInteractor(TutorialUseCase):

    def __init__(
        self,
        tutorial_repository: TutorialRepository,
        photo_cache_repository: PhotoCacheRepository,
        pixabay: PixabayImageGateway,
        storage: ImageStorageGateway,
        weather_api: WeatherApiGateway,
    ) -> None:
        self._tutorial_repository = tutorial_repository
        self._photo_cache_repository = photo_cache_repository
        self._pixabay = pixabay
        self._storage = storage
        self._weather_api = weather_api

    async def create(self, command: TutorialCreateCommand) -> TutorialStateResult:
        species = find_species(command.species_name)
        if species is None:
            raise ValueError(f"지원하지 않는 식물 종류입니다: {command.species_name}")

        entity = await self._tutorial_repository.save(
            TutorialPlantEntity(
                id=None,
                owner_user_id=command.owner_user_id,
                species_name=command.species_name,
                region=command.region,
                last_weather_sync_at=datetime.now(timezone.utc),
            )
        )
        return await self._to_result(entity, feedback=_CREATE_MSG)

    async def get(self, tutorial_plant_id: int) -> TutorialStateResult:
        entity = await self._load_synced(tutorial_plant_id)
        return await self._to_result(entity)

    async def get_active_for_owner(self, owner_user_id: int) -> TutorialStateResult | None:
        entity = await self._tutorial_repository.get_by_owner(owner_user_id)
        if entity is None:
            return None
        entity = await self._sync_weather_decay(entity)
        return await self._to_result(entity)

    async def water(self, tutorial_plant_id: int) -> TutorialStateResult:
        entity = await self._load_synced(tutorial_plant_id)
        entity.soil_moisture_pct = min(100.0, entity.soil_moisture_pct + _WATER_GAIN)
        entity.last_watered_at = datetime.now(timezone.utc)
        entity = await self._apply_points_and_save(entity)

        status = compute_status(entity.soil_moisture_pct, entity.nutrient_pct)
        feedback = _WATER_OVERWATERED_MSG if status == STATUS_OVERWATERED else _WATER_OK_MSG
        return await self._to_result(entity, feedback=feedback)

    async def add_nutrient(self, tutorial_plant_id: int) -> TutorialStateResult:
        entity = await self._load_synced(tutorial_plant_id)
        entity.nutrient_pct = min(100.0, entity.nutrient_pct + _NUTRIENT_GAIN)
        entity.last_fertilized_at = datetime.now(timezone.utc)
        entity = await self._apply_points_and_save(entity)
        return await self._to_result(entity, feedback=_NUTRIENT_OK_MSG)

    async def move_light(self, command: TutorialMoveLightCommand) -> TutorialStateResult:
        entity = await self._load_synced(command.tutorial_plant_id)
        entity.light_position = command.light_position
        entity.last_light_moved_at = datetime.now(timezone.utc)
        entity = await self._apply_points_and_save(entity)

        feedback = await self._light_feedback(entity)
        return await self._to_result(entity, feedback=feedback)

    async def check_leaves(self, tutorial_plant_id: int) -> TutorialStateResult:
        entity = await self._load_synced(tutorial_plant_id)
        status = compute_status(entity.soil_moisture_pct, entity.nutrient_pct)
        return await self._to_result(entity, feedback=_CHECK_LEAVES_MESSAGES[status])

    # ── 내부 헬퍼 ──────────────────────────────────────────────────────

    async def _load_synced(self, tutorial_plant_id: int) -> TutorialPlantEntity:
        entity = await self._tutorial_repository.get(tutorial_plant_id)
        return await self._sync_weather_decay(entity)

    async def _apply_points_and_save(self, entity: TutorialPlantEntity) -> TutorialPlantEntity:
        entity.points += _ACTION_POINTS
        entity.growth_stage = compute_growth_stage(entity.points)
        return await self._tutorial_repository.update(entity)

    async def _sync_weather_decay(self, entity: TutorialPlantEntity) -> TutorialPlantEntity:
        last_sync = entity.last_weather_sync_at or entity.created_at or datetime.now(timezone.utc)
        now = datetime.now(timezone.utc)
        elapsed_days = (now - last_sync).days
        if elapsed_days < 1:
            return entity

        is_dry_day = False
        try:
            weather = await self._weather_api.fetch_current(entity.region)
            is_dry_day = weather.humidity_pct < _DRY_HUMIDITY_THRESHOLD_PCT
        except ValueError:
            pass

        moisture_decay = (_DRY_DAY_MOISTURE_DECAY_PER_DAY if is_dry_day else _NORMAL_MOISTURE_DECAY_PER_DAY) * elapsed_days
        entity.soil_moisture_pct = max(0.0, entity.soil_moisture_pct - moisture_decay)
        entity.nutrient_pct = max(0.0, entity.nutrient_pct - _NUTRIENT_DECAY_PER_DAY * elapsed_days)
        entity.last_weather_sync_at = now
        return await self._tutorial_repository.update(entity)

    async def _light_feedback(self, entity: TutorialPlantEntity) -> str:
        try:
            weather = await self._weather_api.fetch_current(entity.region)
        except ValueError:
            return f"{entity.light_position}(으)로 옮겼어요."

        is_sunny = "맑" in weather.sunlight_desc
        is_cloudy = "흐" in weather.sunlight_desc or "구름" in weather.sunlight_desc

        if is_sunny and entity.light_position == LIGHT_SUN:
            return "잘했어요! 오늘처럼 맑은 날엔 양지가 딱이에요 ☀️"
        if is_cloudy and entity.light_position in (LIGHT_SHADE, LIGHT_PARTIAL):
            return "좋은 선택이에요! 흐린 날엔 그늘도 괜찮아요 ☁️"
        if is_sunny and entity.light_position == LIGHT_SHADE:
            return "오늘처럼 맑은 날엔 조금 더 밝은 곳이 좋아요 💡"
        return f"{entity.light_position}(으)로 옮겼어요."

    async def _to_result(self, entity: TutorialPlantEntity, feedback: str | None = None) -> TutorialStateResult:
        status = compute_status(entity.soil_moisture_pct, entity.nutrient_pct)
        photo_url = await self._resolve_photo(entity.species_name, entity.growth_stage, status)
        return TutorialStateResult(
            id=entity.id,  # type: ignore[arg-type]
            owner_user_id=entity.owner_user_id,
            species_name=entity.species_name,
            region=entity.region,
            growth_stage=entity.growth_stage,
            soil_moisture_pct=entity.soil_moisture_pct,
            nutrient_pct=entity.nutrient_pct,
            light_position=entity.light_position,
            points=entity.points,
            status=status,
            photo_url=photo_url,
            feedback=feedback,
        )

    async def _resolve_photo(self, species_name: str, growth_stage: str, status_key: str) -> str:
        cached = await self._photo_cache_repository.find(species_name, growth_stage, status_key)
        if cached is not None:
            return cached.image_url

        species = find_species(species_name)
        query_keyword = species.query_keyword if species is not None else species_name
        query = build_photo_query(query_keyword, growth_stage, status_key)

        photo = await self._pixabay.fetch_photo(query)
        if photo is None:
            return ""

        filename = f"{species_name}-{growth_stage}-{status_key}.jpg"
        url = await self._storage.save(filename, photo.content_type, photo.data)
        await self._photo_cache_repository.save(
            PhotoCacheEntity(
                id=None,
                species_name=species_name,
                growth_stage=growth_stage,
                status_key=status_key,
                image_url=url,
                pixabay_source_id=photo.source_id,
            )
        )
        return url
