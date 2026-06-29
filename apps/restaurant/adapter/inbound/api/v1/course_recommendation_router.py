from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from restaurant.adapter.inbound.api.schemas.course_recommendation_schema import (
    CourseResponse,
    CourseStopResponse,
)
from restaurant.app.dtos.course_recommendation_dto import CourseQuery
from restaurant.app.ports.input.course_recommendation_use_case import (
    CourseRecommendationUseCase,
)
from restaurant.dependencies.course_recommendation_provider import (
    get_course_recommendation_use_case,
)

course_recommendation_router = APIRouter(prefix="/gourmet", tags=["gourmet-course"])
router = course_recommendation_router


@course_recommendation_router.get("/course", response_model=CourseResponse)
def read_course(
    district: str = Query(..., min_length=1),
    party_type: str = Query("couple"),
    db: Session = Depends(get_sync_db),
    use_case: CourseRecommendationUseCase = Depends(get_course_recommendation_use_case),
) -> CourseResponse:
    view = use_case.recommend(db, CourseQuery(district=district, party_type=party_type))
    return CourseResponse(
        district=view.district,
        stops=[
            CourseStopResponse(slot=s.slot, restaurant_id=s.restaurant_id, name=s.name)
            for s in view.stops
        ],
    )
