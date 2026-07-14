from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from plant.adapter.outbound.orm.plant_badge_orm import PlantBadgeORM
from plant.adapter.outbound.orm.user_plant_badge_orm import UserPlantBadgeORM
from plant.app.ports.output.badge_repository import BadgeRepository
from plant.domain.entities.plant_badge_entity import EarnedBadgeEntity, PlantBadgeEntity


def _to_entity(orm: PlantBadgeORM) -> PlantBadgeEntity:
    return PlantBadgeEntity(
        id=orm.id, code=orm.code, name=orm.name, description=orm.description, icon=orm.icon
    )


class BadgePgRepository(BadgeRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_catalog(self) -> list[PlantBadgeEntity]:
        result = await self.session.execute(select(PlantBadgeORM).order_by(PlantBadgeORM.id))
        return [_to_entity(orm) for orm in result.scalars().all()]

    async def list_earned(self, plant_id: int) -> list[EarnedBadgeEntity]:
        stmt = (
            select(UserPlantBadgeORM, PlantBadgeORM)
            .join(PlantBadgeORM, UserPlantBadgeORM.badge_id == PlantBadgeORM.id)
            .where(UserPlantBadgeORM.plant_id == plant_id)
            .order_by(UserPlantBadgeORM.earned_at)
        )
        result = await self.session.execute(stmt)
        return [
            EarnedBadgeEntity(badge=_to_entity(badge_orm), earned_at=earned_orm.earned_at)
            for earned_orm, badge_orm in result.all()
        ]

    async def award_if_missing(self, plant_id: int, code: str) -> bool:
        badge = await self.session.scalar(
            select(PlantBadgeORM).where(PlantBadgeORM.code == code)
        )
        if badge is None:
            return False

        existing = await self.session.scalar(
            select(UserPlantBadgeORM).where(
                UserPlantBadgeORM.plant_id == plant_id,
                UserPlantBadgeORM.badge_id == badge.id,
            )
        )
        if existing is not None:
            return False

        self.session.add(UserPlantBadgeORM(plant_id=plant_id, badge_id=badge.id))
        await self.session.flush()
        return True
