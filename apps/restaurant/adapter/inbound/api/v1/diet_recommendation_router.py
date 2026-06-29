from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from restaurant.adapter.inbound.api.schemas.diet_recommendation_schema import (
    DietResponse,
    DietRestaurant,
)
from restaurant.app.dtos.diet_recommendation_dto import DietQuery
from restaurant.app.ports.input.diet_recommendation_use_case import (
    DietRecommendationUseCase,
)
from restaurant.dependencies.diet_recommendation_provider import (
    get_diet_recommendation_use_case,
)

diet_recommendation_router = APIRouter(prefix="/gourmet", tags=["gourmet-diet"])
router = diet_recommendation_router


@diet_recommendation_router.get("/diet", response_model=DietResponse)
def read_diet(
    diet_type: str = Query("high_protein"),
    district: str | None = Query(None),
    db: Session = Depends(get_sync_db),
    use_case: DietRecommendationUseCase = Depends(get_diet_recommendation_use_case),
) -> DietResponse:
    view = use_case.recommend(db, DietQuery(diet_type=diet_type, district=district))
    return DietResponse(
        diet_type=view.diet_type,
        restaurants=[DietRestaurant(**r) for r in view.restaurants],
    )
