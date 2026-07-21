"""관리자 대시보드·사용자 관리 — RBAC(role=admin) 전용 엔드포인트."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.auth.dependencies import require_admin
from apps.auth.user_model import User
from apps.auth.user_role import UserRole
from apps.database import get_sync_db

admin_router = APIRouter(prefix="/auth/admin", tags=["admin"])


class AdminUserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    email: str
    role: str
    region: str | None = None
    created_at: datetime
    last_login_at: datetime | None = None


class UpdateRoleRequest(BaseModel):
    role: UserRole


class AdminStatsResponse(BaseModel):
    total_users: int
    admin_count: int
    new_today: int
    new_this_week: int


def _to_response(user: User) -> AdminUserResponse:
    return AdminUserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        role=user.role.value if isinstance(user.role, UserRole) else str(user.role),
        region=user.region,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )


@admin_router.get("/stats", response_model=AdminStatsResponse)
def get_stats(
    db: Session = Depends(get_sync_db),
    _admin: User = Depends(require_admin),
) -> AdminStatsResponse:
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    total_users = db.execute(select(func.count()).select_from(User)).scalar_one()
    admin_count = db.execute(
        select(func.count()).select_from(User).where(User.role == UserRole.admin)
    ).scalar_one()
    new_today = db.execute(
        select(func.count()).select_from(User).where(User.created_at >= today_start)
    ).scalar_one()
    new_this_week = db.execute(
        select(func.count()).select_from(User).where(User.created_at >= week_start)
    ).scalar_one()

    return AdminStatsResponse(
        total_users=total_users,
        admin_count=admin_count,
        new_today=new_today,
        new_this_week=new_this_week,
    )


@admin_router.get("/users", response_model=list[AdminUserResponse])
def list_users(
    db: Session = Depends(get_sync_db),
    _admin: User = Depends(require_admin),
) -> list[AdminUserResponse]:
    users = db.execute(select(User).order_by(User.created_at.desc())).scalars().all()
    return [_to_response(u) for u in users]


@admin_router.patch("/users/{user_id}/role", response_model=AdminUserResponse)
def update_role(
    user_id: int,
    body: UpdateRoleRequest,
    db: Session = Depends(get_sync_db),
    admin: User = Depends(require_admin),
) -> AdminUserResponse:
    if user_id == admin.id and body.role != UserRole.admin:
        raise HTTPException(status_code=400, detail="본인의 관리자 권한은 스스로 해제할 수 없습니다.")

    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    target.role = body.role
    db.flush()
    return _to_response(target)
