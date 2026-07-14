from __future__ import annotations

from fastapi import APIRouter, Depends

from plant.adapter.inbound.api.schemas.badge_schema import (
    BadgeItemResponse,
    LeaderboardEntryResponse,
)
from plant.app.ports.output.badge_repository import BadgeRepository
from plant.app.ports.output.plant_repository import PlantRepository
from plant.dependencies.badge_provider import get_badge_repository
from plant.dependencies.register_plant_provider import get_plant_repository

badge_router = APIRouter(tags=["plant-badges"])


@badge_router.get("/my-plants/{plant_id}/badges", summary="식물별 뱃지 카탈로그 + 획득 여부")
async def list_badges(
    plant_id: int,
    repository: BadgeRepository = Depends(get_badge_repository),
) -> list[BadgeItemResponse]:
    catalog = await repository.list_catalog()
    earned = await repository.list_earned(plant_id)
    earned_by_code = {e.badge.code: e.earned_at for e in earned}
    return [
        BadgeItemResponse(
            code=badge.code,
            name=badge.name,
            description=badge.description,
            icon=badge.icon,
            earned=badge.code in earned_by_code,
            earned_at=earned_by_code.get(badge.code),
        )
        for badge in catalog
    ]


@badge_router.get("/leaderboard", summary="식물집사 포인트 랭킹")
async def leaderboard(
    limit: int = 20,
    repository: PlantRepository = Depends(get_plant_repository),
) -> list[LeaderboardEntryResponse]:
    top = await repository.list_top_by_points(limit)
    return [
        LeaderboardEntryResponse(
            rank=i + 1,
            plant_id=p.id,  # type: ignore[arg-type]
            nickname=p.nickname,
            species_name=p.species_name,
            points=p.points,
            growth_stage=p.growth_stage,
        )
        for i, p in enumerate(top)
    ]
