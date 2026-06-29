from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from restaurant.adapter.inbound.api.schemas.gourmet_schema import RestaurantDetailResponse
from restaurant.dependencies.restaurant_detail_provider import get_restaurant_detail_use_case
from restaurant.app.use_cases.restaurant_detail_interactor import RestaurantDetailInteractor

router = APIRouter(prefix="/gourmet", tags=["gourmet"])


@router.get("/official-store/{store_id}", response_model=RestaurantDetailResponse)
def read_official_store_detail(
    store_id: int,
    db: Session = Depends(get_sync_db),
    detail_service: RestaurantDetailInteractor = Depends(get_restaurant_detail_use_case),
):
    """공공·정제 테이블 통합 상세 (Adapter 체인)."""
    detail = detail_service.get_detail(db, store_id)
    return RestaurantDetailResponse(**detail)


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantDetailResponse)
def read_restaurant_detail(
    restaurant_id: int,
    db: Session = Depends(get_sync_db),
    detail_service: RestaurantDetailInteractor = Depends(get_restaurant_detail_use_case),
):
    """식당 상세 — ``RestaurantDetailInteractor`` (다형 Adapter)."""
    detail = detail_service.get_detail(db, restaurant_id)
    return RestaurantDetailResponse(**detail)
