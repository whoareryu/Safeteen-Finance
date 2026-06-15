"""Admin 매점관리 API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.friday_13th.auth.auth_router import _require_admin
from apps.database import get_sync_db
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant

router = APIRouter(prefix="/gourmet/admin", tags=["gourmet-admin"])


class StoreSummaryResponse(BaseModel):
    restaurants_count: int
    sample: list[dict]


@router.get("/stores/summary", response_model=StoreSummaryResponse)
def read_store_summary(
    as_username: str = Query(..., description="요청자 로그인 아이디"),
    db: Session = Depends(get_sync_db),
):
    """매점관리 — admin 전용 식당 집계."""
    _require_admin(db, as_username)
    restaurants_count = int(
        db.execute(select(func.count()).select_from(Restaurant)).scalar_one() or 0
    )
    rows = db.execute(select(Restaurant).order_by(Restaurant.id).limit(20)).scalars().all()
    sample = [
        {
            "id": r.id,
            "name": r.name,
            "category_label": r.category_label,
            "district": r.district,
            "biz_number": r.biz_number,
        }
        for r in rows
    ]
    return StoreSummaryResponse(
        restaurants_count=restaurants_count,
        sample=sample,
    )
