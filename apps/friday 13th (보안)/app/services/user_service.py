import logging

from sqlalchemy.orm import Session

from apps.auth.user_model import User
from apps.secom.app.repositories.user_repository import UserRepository
from apps.secom.app.schemas.login_schema import LoginSchema
from apps.secom.app.schemas.user_schema import UserSchema

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session):
        self._repository = UserRepository(db)

    def save_user(self, user: UserSchema) -> User:
        logger.info(
            "[secom.service] save_user 진입 — layer=service payload=%s",
            user.to_log_dict(),
        )
        saved = self._repository.save_user(user)
        logger.info(
            "[secom.service] save_user 완료 — DB 저장됨 id=%s username=%s email=%s "
            "nickname=%s role=%s",
            saved.id,
            saved.username,
            saved.email,
            saved.nickname,
            saved.role.value,
        )
        return saved

    def login_user(self, credentials: LoginSchema) -> User | None:
        logger.info(
            "[secom.service] login_user 진입 — layer=service payload=%s",
            credentials.to_log_dict(),
        )
        user = self._repository.login_user(credentials)
        if user is None:
            logger.info(
                "[secom.service] login_user 완료 — repository 반환 없음 (인증 실패 또는 미등록)"
            )
        else:
            logger.info(
                "[secom.service] login_user 완료 — repository 반환 id=%s username=%s role=%s",
                user.id,
                user.username,
                user.role.value,
            )
        return user
