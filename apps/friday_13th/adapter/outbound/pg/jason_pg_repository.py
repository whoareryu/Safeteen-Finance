from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import func, select

from apps.database import DATABASE_INIT_ERROR, async_session_maker
from apps.friday_13th.app.ports.input.login_use_case import LoginCredentials, LoginUserResult
from apps.friday_13th.app.ports.output.user_repository import UserRepositoryPort
from apps.friday_13th.auth.password import verify_password
from apps.friday_13th.auth.user_model import User

logger = logging.getLogger(__name__)


class UserPGRepositoryAdapter(UserRepositoryPort):
    """UserRepositoryPort 구현 — users 테이블 로그인 (DB 세션은 outbound 에서만 연다)."""

    async def login_user(self, credentials: LoginCredentials) -> LoginUserResult | None:
        if DATABASE_INIT_ERROR or async_session_maker is None:
            raise RuntimeError(
                DATABASE_INIT_ERROR or "데이터베이스를 초기화할 수 없습니다."
            )

        logger.info(
            "[UserPGRepositoryAdapter] ports/output → outbound/pg → DB | username=%s",
            credentials.username,
        )
        name = credentials.username.strip().lower()

        async with async_session_maker() as db:
            user = (
                await db.execute(
                    select(User).where(func.lower(User.username) == name).limit(1)
                )
            ).scalar_one_or_none()

            if user is None or not verify_password(
                credentials.password, user.password_hash
            ):
                logger.info(
                    "[UserPGRepositoryAdapter] 로그인 실패 — username=%s",
                    credentials.username,
                )
                return None

            user.last_login_at = datetime.now(timezone.utc)
            try:
                await db.commit()
                await db.refresh(user)
            except Exception:
                await db.rollback()
                logger.exception("last_login_at 저장 실패")
                raise

        logger.info(
            "[UserPGRepositoryAdapter] DB 로그인 성공 | id=%s username=%s",
            user.id,
            user.username,
        )
        return LoginUserResult(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            role=user.role.value,
        )
