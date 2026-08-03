from __future__ import annotations

import pytest

from apps.auth.app.dtos.mobile_auth_dto import (
    MobileConsentCompleteCommand,
    MobileUserRecord,
    PendingSignup,
)
from apps.auth.app.ports.output.mobile_pending_signup_port import PendingSignupPort
from apps.auth.app.ports.output.mobile_token_store_port import MobileTokenStorePort
from apps.auth.app.ports.output.mobile_user_repository_port import MobileUserRepositoryPort
from apps.auth.app.use_cases.mobile_consent_complete_interactor import MobileConsentCompleteInteractor
from apps.auth.domain.exception.mobile_auth_exceptions import (
    ConsentRequiredTermsNotAgreedError,
    ConsentTokenInvalidError,
    NicknameRequiredError,
    NicknameTakenError,
)

_PENDING = PendingSignup(provider="KAKAO", sub="12345", email="user@example.com", name="새싹러")


class _FakePendingSignup(PendingSignupPort):
    def __init__(self, pending: PendingSignup | None = _PENDING) -> None:
        self._pending = pending

    async def create(self, *, provider, sub, email, name) -> str:
        raise NotImplementedError

    async def pop(self, consent_token):
        return self._pending


class _FakeUserRepository(MobileUserRepositoryPort):
    def __init__(self, nickname_taken: bool = False) -> None:
        self._nickname_taken = nickname_taken
        self.created_with: dict | None = None

    def find_existing(self, *, provider, sub, email):
        raise NotImplementedError

    def find_by_id(self, user_id):
        raise NotImplementedError

    def nickname_exists(self, nickname) -> bool:
        return self._nickname_taken

    def create(self, *, provider, sub, email, nickname) -> MobileUserRecord:
        self.created_with = {"provider": provider, "sub": sub, "email": email, "nickname": nickname}
        return MobileUserRecord(id=7, role="user")


class _FakeTokenStore(MobileTokenStorePort):
    async def create_access_token(self, *, sub, roles) -> tuple[str, int]:
        return f"access-{sub}", 7200

    async def create_refresh_token(self, *, sub, device_id) -> str:
        return f"refresh-{sub}-{device_id}"

    async def rotate_refresh_token(self, refresh_token):
        raise NotImplementedError

    async def revoke_all(self, sub):
        raise NotImplementedError

    async def blacklist_access_token(self, jti):
        raise NotImplementedError


def _make_interactor(*, nickname_taken=False, pending=_PENDING):
    user_repo = _FakeUserRepository(nickname_taken=nickname_taken)
    interactor = MobileConsentCompleteInteractor(
        pending_signup=_FakePendingSignup(pending=pending),
        user_repository=user_repo,
        token_store=_FakeTokenStore(),
    )
    return interactor, user_repo


async def test_complete_creates_user_and_issues_tokens():
    interactor, user_repo = _make_interactor()

    tokens = await interactor.complete(
        MobileConsentCompleteCommand(
            consent_token="tok", nickname="새싹러123", agree_terms=True, device_id="d"
        )
    )

    assert tokens.access_token == "access-7"
    assert user_repo.created_with == {
        "provider": "KAKAO",
        "sub": "12345",
        "email": "user@example.com",
        "nickname": "새싹러123",
    }


async def test_terms_not_agreed_raises():
    interactor, _ = _make_interactor()

    with pytest.raises(ConsentRequiredTermsNotAgreedError):
        await interactor.complete(
            MobileConsentCompleteCommand(
                consent_token="tok", nickname="새싹러", agree_terms=False, device_id="d"
            )
        )


async def test_blank_nickname_raises():
    interactor, _ = _make_interactor()

    with pytest.raises(NicknameRequiredError):
        await interactor.complete(
            MobileConsentCompleteCommand(consent_token="tok", nickname="   ", agree_terms=True, device_id="d")
        )


async def test_expired_consent_token_raises():
    interactor, _ = _make_interactor(pending=None)

    with pytest.raises(ConsentTokenInvalidError):
        await interactor.complete(
            MobileConsentCompleteCommand(consent_token="tok", nickname="새싹러", agree_terms=True, device_id="d")
        )


async def test_nickname_taken_raises():
    interactor, _ = _make_interactor(nickname_taken=True)

    with pytest.raises(NicknameTakenError):
        await interactor.complete(
            MobileConsentCompleteCommand(consent_token="tok", nickname="새싹러", agree_terms=True, device_id="d")
        )
