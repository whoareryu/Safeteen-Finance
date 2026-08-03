from __future__ import annotations

import pytest

from apps.auth.app.dtos.mobile_auth_dto import MobileRefreshCommand, MobileUserRecord
from apps.auth.app.ports.output.mobile_token_store_port import MobileTokenStorePort
from apps.auth.app.ports.output.mobile_user_repository_port import MobileUserRepositoryPort
from apps.auth.app.use_cases.mobile_refresh_interactor import MobileRefreshInteractor
from apps.auth.domain.exception.mobile_auth_exceptions import (
    SessionUserNotFoundError,
    TokenReuseDetectedError,
)


class _FakeTokenStore(MobileTokenStorePort):
    def __init__(self, rotate_result: tuple[str, str] | None) -> None:
        self._rotate_result = rotate_result

    async def create_access_token(self, *, sub, roles) -> tuple[str, int]:
        return f"access-{sub}", 7200

    async def create_refresh_token(self, *, sub, device_id) -> str:
        raise NotImplementedError

    async def rotate_refresh_token(self, refresh_token):
        return self._rotate_result

    async def revoke_all(self, sub):
        raise NotImplementedError

    async def blacklist_access_token(self, jti):
        raise NotImplementedError


class _FakeUserRepository(MobileUserRepositoryPort):
    def __init__(self, user: MobileUserRecord | None) -> None:
        self._user = user

    def find_existing(self, *, provider, sub, email):
        raise NotImplementedError

    def find_by_id(self, user_id):
        return self._user

    def nickname_exists(self, nickname):
        raise NotImplementedError

    def create(self, *, provider, sub, email, nickname):
        raise NotImplementedError


async def test_successful_rotation_issues_new_tokens():
    interactor = MobileRefreshInteractor(
        token_store=_FakeTokenStore(rotate_result=("7", "new-refresh")),
        user_repository=_FakeUserRepository(user=MobileUserRecord(id=7, role="user")),
    )

    tokens = await interactor.refresh(MobileRefreshCommand(refresh_token="old-refresh"))

    assert tokens.access_token == "access-7"
    assert tokens.refresh_token == "new-refresh"


async def test_reuse_or_unknown_token_raises_reuse_detected():
    interactor = MobileRefreshInteractor(
        token_store=_FakeTokenStore(rotate_result=None),
        user_repository=_FakeUserRepository(user=None),
    )

    with pytest.raises(TokenReuseDetectedError):
        await interactor.refresh(MobileRefreshCommand(refresh_token="reused"))


async def test_user_deleted_after_token_issued_raises_session_user_not_found():
    interactor = MobileRefreshInteractor(
        token_store=_FakeTokenStore(rotate_result=("7", "new-refresh")),
        user_repository=_FakeUserRepository(user=None),
    )

    with pytest.raises(SessionUserNotFoundError):
        await interactor.refresh(MobileRefreshCommand(refresh_token="old-refresh"))
