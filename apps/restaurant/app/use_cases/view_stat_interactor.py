"""매장 조회 수 기록·조회."""

from __future__ import annotations

import datetime
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.orm.restaurant_view_stat_orm import RestaurantViewStat
from restaurant.app.ports.input.view_stat_use_case import ViewStatUseCase
from restaurant.adapter.inbound.api.schemas.view_stat_schema import ViewStatSchema
from restaurant.app.dtos.view_stat_dto import ViewStatQuery, ViewStatResponse
from restaurant.app.ports.output.view_stat_repository import ViewStatRepository


logger = logging.getLogger(__name__)


def record_restaurant_view(db: Session, restaurant_id: int) -> RestaurantViewStat:
    """조회 1회 증가 (없으면 행 생성)."""
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise ValueError(f"restaurant_id={restaurant_id} 를 찾을 수 없습니다.")

    stat = db.execute(
        select(RestaurantViewStat).where(
            RestaurantViewStat.restaurant_id == restaurant_id
        )
    ).scalar_one_or_none()

    now = datetime.datetime.now(datetime.timezone.utc)

    if stat is None:
        stat = RestaurantViewStat(
            restaurant_id=restaurant_id,
            view_count=1,
            first_viewed_at=now,
            last_viewed_at=now,
        )
        db.add(stat)
    else:
        stat.view_count += 1
        stat.last_viewed_at = now
        if stat.first_viewed_at is None:
            stat.first_viewed_at = now

    db.commit()
    db.refresh(stat)
    logger.info(
        "[gourmet] 조회 기록 — restaurant_id=%s name=%s view_count=%s",
        restaurant_id,
        restaurant.name,
        stat.view_count,
    )
    return stat


def get_view_stat(db: Session, restaurant_id: int) -> RestaurantViewStat | None:
    return db.execute(
        select(RestaurantViewStat).where(
            RestaurantViewStat.restaurant_id == restaurant_id
        )
    ).scalar_one_or_none()


def list_view_stats(
    db: Session, *, limit: int = 50, order_by_views: bool = True
) -> list[tuple[Restaurant, RestaurantViewStat]]:
    stmt = (
        select(Restaurant, RestaurantViewStat)
        .join(RestaurantViewStat, Restaurant.id == RestaurantViewStat.restaurant_id)
    )
    if order_by_views:
        stmt = stmt.order_by(RestaurantViewStat.view_count.desc())
    stmt = stmt.limit(limit)
    rows = db.execute(stmt).all()
    return [(r, s) for r, s in rows]


class ViewStatInteractor(ViewStatUseCase):
    def __init__(self, repository: ViewStatRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: ViewStatSchema) -> ViewStatResponse:
        return await self.repository.introduce_myself(
            ViewStatQuery(id=schema.id, name=schema.name)
        )
