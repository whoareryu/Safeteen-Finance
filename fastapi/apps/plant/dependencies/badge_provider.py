from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db

from plant.adapter.outbound.pg.badge_pg_repository import BadgePgRepository
from plant.app.ports.output.badge_repository import BadgeRepository


def get_badge_repository(db: AsyncSession = Depends(get_db)) -> BadgeRepository:
    return BadgePgRepository(session=db)
