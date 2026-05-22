"""즐겨찾기 API — ``X-User-Id`` 헤더 (``as_username`` 쿼리는 하위 호환)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.auth.dependencies import get_current_user
from apps.auth.user_model import User
from apps.database import get_sync_db
from apps.gourmet.app.schemas.favorite_schemas import (
    FavoriteCardItem,
    FavoriteCheckResponse,
    FavoriteToggleRequest,
    FavoriteToggleResponse,
)
from apps.gourmet.app.services.favorite_service import FavoriteService

router = APIRouter(prefix="/gourmet/favorites", tags=["gourmet-favorites"])

_service = FavoriteService()


@router.get("", response_model=list[FavoriteCardItem])
def list_favorites(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
):
    return [FavoriteCardItem(**item) for item in _service.list_cards(db, user.id)]


@router.get("/store-ids", response_model=FavoriteCheckResponse)
def list_all_favorited_store_ids(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
):
    ids = _service.all_favorited_store_ids_for_user(db, user.id)
    return FavoriteCheckResponse(favorited_store_ids=ids)


@router.get("/check", response_model=FavoriteCheckResponse)
def check_favorites(
    store_ids: str = Query("", description="쉼표 구분 store id"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
):
    parsed = [int(x) for x in store_ids.split(",") if x.strip().isdigit()]
    favorited = _service.favorited_store_ids(db, user.id, parsed)
    return FavoriteCheckResponse(favorited_store_ids=favorited)


@router.post("/toggle", response_model=FavoriteToggleResponse)
def toggle_favorite(
    body: FavoriteToggleRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
):
    try:
        favorited, message = _service.toggle(db, user, body.store_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return FavoriteToggleResponse(
        store_id=body.store_id, favorited=favorited, message=message
    )
