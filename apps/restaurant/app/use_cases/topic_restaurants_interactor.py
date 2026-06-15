"""주제 slug 단위 맛집 목록."""

from __future__ import annotations

from restaurant.data.category_topics import TopicDef, find_topic_by_slug
from restaurant.app.use_cases.restaurant_browse_interactor import (
    browse_category_of,
    bounded_restaurant_slice,
    pick_mixed_by_category,
    rows_to_card_summaries,
)
from sqlalchemy.orm import Session
from restaurant.app.ports.input.topic_restaurants_use_case import TopicRestaurantsUseCase
from restaurant.adapter.inbound.api.schemas.topic_restaurants_schema import TopicRestaurantsSchema
from restaurant.app.dtos.topic_restaurants_dto import TopicRestaurantsQuery, TopicRestaurantsResponse
from restaurant.app.ports.output.topic_restaurants_repository import TopicRestaurantsRepository


TOPIC_POOL_SIZE = 10_000


def get_topic_restaurants(
    db: Session,
    topic_slug: str,
    *,
    user_lat: float | None = None,
    user_lng: float | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[TopicDef, list[dict], dict] | None:
    topic = find_topic_by_slug(topic_slug)
    if topic is None:
        return None

    cat_filter = topic.category_slugs[0] if len(topic.category_slugs) == 1 else None
    pool = bounded_restaurant_slice(
        db,
        limit_rows=TOPIC_POOL_SIZE,
        category_slug=cat_filter,
    )
    if topic.category_slugs:
        allowed = set(topic.category_slugs)
        pool = [r for r in pool if browse_category_of(r)[0] in allowed]

    picks = pick_mixed_by_category(pool, topic.slug, limit=min(len(pool), offset + limit + 40))
    total = len(picks)
    page_rows = picks[offset : offset + limit]
    cards = rows_to_card_summaries(
        page_rows,
        user_lat=user_lat,
        user_lng=user_lng,
        with_category=True,
    )
    meta = {
        "offset": offset,
        "limit": limit,
        "total": total,
        "has_more": offset + len(cards) < total,
    }
    return topic, cards, meta


class TopicRestaurantsInteractor(TopicRestaurantsUseCase):
    def __init__(self, repository: TopicRestaurantsRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: TopicRestaurantsSchema) -> TopicRestaurantsResponse:
        return await self.repository.introduce_myself(
            TopicRestaurantsQuery(id=schema.id, name=schema.name)
        )
