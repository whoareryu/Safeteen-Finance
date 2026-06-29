from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from restaurant.adapter.inbound.api.schemas.personalized_recommendation_schema import (
    RecommendationCardResponse,
    RecommendationRequest,
)
from restaurant.app.dtos.personalized_recommendation_dto import (
    PersonalizedQuery,
    PreferenceSnapshot,
)
from restaurant.app.ports.input.personalized_recommendation_use_case import (
    PersonalizedRecommendationUseCase,
)
from restaurant.dependencies.personalized_recommendation_provider import (
    get_personalized_recommendation_use_case,
)

personalized_recommendation_router = APIRouter(
    prefix="/gourmet", tags=["gourmet-recommendation"]
)
router = personalized_recommendation_router

_KST = timezone(timedelta(hours=9))


def _current_slot() -> str:
    hour = datetime.now(_KST).hour
    if 6 <= hour < 10:
        return "morning"
    if 10 <= hour < 16:
        return "lunch"
    return "dinner"


@personalized_recommendation_router.post(
    "/recommendation/today", response_model=RecommendationCardResponse
)
def post_today_recommendation(
    payload: RecommendationRequest,
    db: Session = Depends(get_sync_db),
    use_case: PersonalizedRecommendationUseCase = Depends(
        get_personalized_recommendation_use_case
    ),
) -> RecommendationCardResponse:
    slot = payload.time_slot or _current_slot()
    query = PersonalizedQuery(
        preference=PreferenceSnapshot(
            genre_ranking=payload.genre_ranking,
            excluded_restaurant_ids=payload.excluded_ids,
        ),
        time_slot=slot,
        weather=payload.weather,
    )
    try:
        pick = use_case.pick_one(db, query)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return RecommendationCardResponse(
        id=pick.id,
        name=pick.name,
        genre=pick.genre,
        road_address=pick.road_address,
        latitude=pick.latitude,
        longitude=pick.longitude,
        reason=pick.reason,
        time_slot=slot,
    )
