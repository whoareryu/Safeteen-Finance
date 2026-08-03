from __future__ import annotations

import pytest

from apps.auth.app.dtos.mobile_auth_dto import MobileLogoutCommand
from apps.auth.app.ports.output.mobile_token_store_port import MobileTokenStorePort
from apps.auth.app.use_cases.mobile_logout_interactor import MobileLogoutInteractor
from apps.auth.domain.exception.mobile_auth_exceptions import PlatformMismatchError


class _FakeTokenStore(MobileTokenStorePort):
    def __init__(self) -> None:
        self.revoked_for: list[str] = []
        self.blacklisted_jti: list[str] = []

    async def create_access_token(self, *, sub, roles):
        raise NotImplementedError

    async def create_refresh_token(self, *, sub, device_id):
        raise NotImplementedError

    async def rotate_refresh_token(self, refresh_token):
        raise NotImplementedError

    async def revoke_all(self, sub):
        self.revoked_for.append(sub)

    async def blacklist_access_token(self, jti):
        self.blacklisted_jti.append(jti)


async def test_mobile_logout_revokes_session_and_blacklists_jti():
    token_store = _FakeTokenStore()
    interactor = MobileLogoutInteractor(token_store=token_store)

    await interactor.logout(MobileLogoutCommand(sub="7", jti="jti-1", platform="mobile"))

    assert token_store.revoked_for == ["7"]
    assert token_store.blacklisted_jti == ["jti-1"]


async def test_web_platform_token_raises_platform_mismatch():
    token_store = _FakeTokenStore()
    interactor = MobileLogoutInteractor(token_store=token_store)

    with pytest.raises(PlatformMismatchError):
        await interactor.logout(MobileLogoutCommand(sub="7", jti="jti-1", platform="web"))

    assert token_store.revoked_for == []
    assert token_store.blacklisted_jti == []
