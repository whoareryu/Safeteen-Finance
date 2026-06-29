"""GPS 방문 확인 API — X-User-Id 인증 (기획서 4-2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.auth.dependencies import get_current_user
from apps.auth.user_model import User
from apps.database import get_sync_db
from user.adapter.inbound.api.schemas.visit_rating_schema import (
    VisitConfirmRequest,
    VisitResponse,
)
from user.app.dtos.visit_rating_dto import VisitConfirmCommand
from user.app.ports.input.visit_rating_use_case import VisitRatingUseCase
from user.dependencies.visit_rating_provider import get_visit_rating_use_case

visit_rating_router = APIRouter(prefix="/gourmet/visits", tags=["gourmet-visits"])
router = visit_rating_router


@visit_rating_router.post("", response_model=VisitResponse)
def confirm_visit(
    body: VisitConfirmRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    use_case: VisitRatingUseCase = Depends(get_visit_rating_use_case),
) -> VisitResponse:
    view = use_case.confirm_visit(
        db,
        user,
        VisitConfirmCommand(
            restaurant_id=body.restaurant_id,
            rating=body.rating,
            latitude=body.latitude,
            longitude=body.longitude,
        ),
    )
    return VisitResponse(
        restaurant_id=view.restaurant_id,
        rating=view.rating,
        confirmed=view.confirmed,
    )
