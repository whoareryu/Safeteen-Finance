from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.auth.app.dtos.mobile_auth_dto import MobileUserRecord
from apps.auth.app.ports.output.mobile_user_repository_port import MobileUserRepositoryPort
from apps.auth.user_model import User
from apps.auth.user_provisioning import create_oauth_user, find_existing_user
from apps.auth.user_role import UserRole


def _to_record(user: User) -> MobileUserRecord:
    role = user.role.value if isinstance(user.role, UserRole) else str(user.role)
    return MobileUserRecord(id=user.id, role=role)


class SqlAlchemyMobileUserRepository(MobileUserRepositoryPort):

    def __init__(self, db: Session) -> None:
        self._db = db

    def find_existing(self, *, provider: str, sub: str, email: str) -> MobileUserRecord | None:
        user = find_existing_user(self._db, provider=provider, sub=sub, email=email)
        return _to_record(user) if user is not None else None

    def find_by_id(self, user_id: int) -> MobileUserRecord | None:
        user = self._db.get(User, user_id)
        return _to_record(user) if user is not None else None

    def nickname_exists(self, nickname: str) -> bool:
        exists = self._db.execute(
            select(User).where(func.lower(User.nickname) == nickname.lower()).limit(1)
        ).scalar_one_or_none()
        return exists is not None

    def create(self, *, provider: str, sub: str, email: str, nickname: str) -> MobileUserRecord:
        user = create_oauth_user(self._db, provider=provider, sub=sub, email=email, nickname=nickname)
        now = datetime.now(timezone.utc)
        user.policy_agreed_at = now
        user.last_login_at = now
        self._db.flush()
        return _to_record(user)
