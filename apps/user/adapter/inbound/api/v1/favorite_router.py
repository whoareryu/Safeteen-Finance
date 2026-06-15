"""즐겨찾기 API — ``X-User-Id`` 헤더 (``as_username`` 쿼리는 하위 호환)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from apps.friday_13th.auth.dependencies import get_current_user
from apps.friday_13th.auth.user_model import User
from user.adapter.inbound.api.schemas.favorite_schema import (
    FavoriteCardItem,
    FavoriteCheckResponse,
    FavoriteToggleRequest,
    FavoriteToggleResponse,
)
from user.app.dtos.favorite_dto import FavoriteCheckQuery, FavoriteToggleCommand
from user.app.ports.input.favorite_use_case import FavoriteUseCase
from user.dependencies.favorite_provider import get_favorite_use_case

favorite_router = APIRouter(prefix="/gourmet/favorites", tags=["gourmet-favorites"])

# 하위 호환
router = favorite_router


@favorite_router.get("", response_model=list[FavoriteCardItem])
def list_favorites(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    favorite: FavoriteUseCase = Depends(get_favorite_use_case),
):
    return [FavoriteCardItem(**item) for item in favorite.list_cards(db, user.id)]


@favorite_router.get("/store-ids", response_model=FavoriteCheckResponse)
def list_all_favorited_store_ids(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    favorite: FavoriteUseCase = Depends(get_favorite_use_case),
):
    ids = favorite.all_favorited_store_ids_for_user(db, user.id)
    return FavoriteCheckResponse(favorited_store_ids=ids)


@favorite_router.get("/check", response_model=FavoriteCheckResponse)
def check_favorites(
    store_ids: str = Query("", description="쉼표 구분 store id"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    favorite: FavoriteUseCase = Depends(get_favorite_use_case),
):
    parsed = [int(x) for x in store_ids.split(",") if x.strip().isdigit()]
    favorited = favorite.favorited_store_ids(
        db, FavoriteCheckQuery(user_id=user.id, store_ids=parsed)
    )
    return FavoriteCheckResponse(favorited_store_ids=favorited)


@favorite_router.post("/toggle", response_model=FavoriteToggleResponse)
def toggle_favorite(
    body: FavoriteToggleRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    favorite: FavoriteUseCase = Depends(get_favorite_use_case),
):
    favorited, message = favorite.toggle(
        db, user, FavoriteToggleCommand(store_id=body.store_id)
    )
    return FavoriteToggleResponse(
        store_id=body.store_id, favorited=favorited, message=message
    )

from user.adapter.inbound.api.schemas.favorite_schema import FavoriteSchema
from user.app.dtos.favorite_dto import FavoriteResponse


@favorite_router.get("/myself")
async def introduce_myself(
    use_case: FavoriteUseCase = Depends(get_favorite_use_case),
) -> FavoriteResponse:
    return await use_case.introduce_myself(FavoriteSchema(id=1, name="즐겨찾기"))
