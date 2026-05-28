import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.auth.password import hash_password, verify_password
from apps.auth.user_model import User
from apps.auth.user_role import UserRole
from apps.secom.app.repositories.base_repository import BaseRepository
from apps.secom.app.schemas.login_schema import LoginSchema
from apps.secom.app.schemas.user_schema import UserSchema

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    @staticmethod
    def _parse_role(role: str) -> UserRole:
        value = role.strip().lower()
        try:
            return UserRole(value)
        except ValueError as e:
            raise ValueError(
                f"role은 admin, user, partner 중 하나여야 합니다. (입력: {role})"
            ) from e

    def save_user(self, user: UserSchema) -> User:
        payload = user.to_log_dict()
        logger.info(
            "[secom.repository] save_user 진입 — layer=repository payload=%s",
            payload,
        )

        entity = User(
            username=user.username.strip(),
            email=user.email.strip().lower(),
            nickname=user.nickname.strip(),
            password_hash=hash_password(user.password),
            role=self._parse_role(user.role),
        )

        saved = self._insert_now(entity)

        logger.info(
            "[secom.repository] save_user DB INSERT 완료 — id=%s username=%s email=%s "
            "nickname=%s role=%s",
            saved.id,
            saved.username,
            saved.email,
            saved.nickname,
            saved.role.value,
        )
        return saved

    def login_user(self, credentials: LoginSchema) -> User | None:
        payload = credentials.to_log_dict()
        logger.info(
            "[secom.repository] login_user 진입 — layer=repository payload=%s",
            payload,
        )

        name = credentials.username.strip().lower()
        user = self._db.execute(
            select(User).where(func.lower(User.username) == name).limit(1)
        ).scalar_one_or_none()

        if user is None:
            logger.info(
                "[secom.repository] login_user — users 에 username=%s 없음",
                credentials.username,
            )
            return None

        if not verify_password(credentials.password, user.password_hash):
            logger.info(
                "[secom.repository] login_user — username=%s 비밀번호 불일치",
                credentials.username,
            )
            return None

        logger.info(
            "[secom.repository] login_user 완료 — id=%s username=%s email=%s "
            "nickname=%s role=%s",
            user.id,
            user.username,
            user.email,
            user.nickname,
            user.role.value,
        )
        return user
