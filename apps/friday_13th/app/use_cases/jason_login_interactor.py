from __future__ import annotations

import logging

from apps.friday_13th.app.ports.input.login_use_case import (
    LoginCredentials,
    LoginUseCase,
    LoginUserResult,
)
from apps.friday_13th.app.ports.output.user_repository import UserRepositoryPort

logger = logging.getLogger(__name__)


class LoginInteractor(LoginUseCase):
    """입력 포트(LoginUseCase) 구현 — 출력 포트만 의존."""

    def __init__(self, repository: UserRepositoryPort) -> None:
        self._repository = repository

    async def login(self, credentials: LoginCredentials) -> LoginUserResult:
        logger.info(
            "[LoginInteractor] ports/input → use_cases | username=%s",
            credentials.username,
        )
        user = await self._repository.login_user(credentials)
        if user is None:
            raise ValueError("아이디 또는 비밀번호가 올바르지 않습니다.")
        logger.info(
            "[LoginInteractor] use_cases → ports/output | id=%s username=%s",
            user.id,
            user.username,
        )
        return user
