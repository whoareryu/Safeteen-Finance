from __future__ import annotations

import pytest

from apps.auth.app.dtos.mobile_auth_dto import (
    MobileAuthTokens,
    MobileKakaoLoginCommand,
    MobileUserRecord,
    PendingSignup,
)
from apps.auth.app.ports.output.kakao_id_token_verifier_port import IdTokenVerifierPort
from apps.auth.app.ports.output.mobile_nonce_store_port import NonceStorePort
from apps.auth.app.ports.output.mobile_pending_signup_port import PendingSignupPort
from apps.auth.app.ports.output.mobile_token_store_port import MobileTokenStorePort
from apps.auth.app.ports.output.mobile_user_repository_port import MobileUserRepositoryPort
from apps.auth.app.use_cases.mobile_kakao_login_interactor import MobileKakaoLoginInteractor
from apps.auth.domain.exception.mobile_auth_exceptions import (
    ExpiredIdTokenError,
    InvalidNonceError,
)
from apps.auth.domain.model.mobile_kakao_identity import KakaoIdentity


class _FakeVerifier(IdTokenVerifierPort):
    def __init__(self, identity: KakaoIdentity | None = None, error: Exception | None = None) -> None:
        self._identity = identity
        self._error = error

    def verify(self, id_token: str, *, nonce: str) -> KakaoIdentity:
        if self._error:
            raise self._error
        assert self._identity is not None
        return self._identity


class _FakeNonceStore(NonceStorePort):
    def __init__(self, consumable: bool = True) -> None:
        self._consumable = consumable

    async def consume_once(self, nonce: str) -> bool:
        return self._consumable


class _FakeUserRepository(MobileUserRepositoryPort):
    def __init__(self, existing: MobileUserRecord | None = None) -> None:
        self.existing = existing
        self.create_calls = 0

    def find_existing(self, *, provider, sub, email):
        return self.existing

    def find_by_id(self, user_id):
        raise NotImplementedError

    def nickname_exists(self, nickname):
        raise NotImplementedError

    def create(self, *, provider, sub, email, nickname):
        raise NotImplementedError


class _FakePendingSignup(PendingSignupPort):
    def __init__(self) -> None:
        self.created_with: dict | None = None

    async def create(self, *, provider, sub, email, name) -> str:
        self.created_with = {"provider": provider, "sub": sub, "email": email, "name": name}
        return "consent-token-123"

    async def pop(self, consent_token):
        raise NotImplementedError


class _FakeTokenStore(MobileTokenStorePort):
    def __init__(self) -> None:
        self.issued_for: list[str] = []

    async def create_access_token(self, *, sub, roles) -> tuple[str, int]:
        self.issued_for.append(sub)
        return f"access-{sub}", 7200

    async def create_refresh_token(self, *, sub, device_id) -> str:
        return f"refresh-{sub}-{device_id}"

    async def rotate_refresh_token(self, refresh_token):
        raise NotImplementedError

    async def revoke_all(self, sub):
        raise NotImplementedError

    async def blacklist_access_token(self, jti):
        raise NotImplementedError


_IDENTITY = KakaoIdentity(sub="12345", email="user@example.com", nickname="새싹러")


def _make_interactor(
    *,
    identity: KakaoIdentity | None = _IDENTITY,
    verifier_error: Exception | None = None,
    nonce_consumable: bool = True,
    existing_user: MobileUserRecord | None = None,
) -> tuple[MobileKakaoLoginInteractor, _FakeUserRepository, _FakePendingSignup, _FakeTokenStore]:
    user_repo = _FakeUserRepository(existing=existing_user)
    pending = _FakePendingSignup()
    token_store = _FakeTokenStore()
    interactor = MobileKakaoLoginInteractor(
        verifier=_FakeVerifier(identity=identity, error=verifier_error),
        nonce_store=_FakeNonceStore(consumable=nonce_consumable),
        user_repository=user_repo,
        pending_signup=pending,
        token_store=token_store,
    )
    return interactor, user_repo, pending, token_store


async def test_existing_user_logs_in_directly():
    interactor, _, pending, token_store = _make_interactor(
        existing_user=MobileUserRecord(id=7, role="user")
    )

    result = await interactor.login(MobileKakaoLoginCommand(id_token="t", nonce="n", device_id="d"))

    assert result.status == "logged_in"
    assert result.is_new_user is False
    assert isinstance(result.tokens, MobileAuthTokens)
    assert token_store.issued_for == ["7"]
    assert pending.created_with is None


async def test_new_user_gets_consent_required():
    interactor, _, pending, token_store = _make_interactor(existing_user=None)

    result = await interactor.login(MobileKakaoLoginCommand(id_token="t", nonce="n", device_id="d"))

    assert result.status == "consent_required"
    assert result.tokens is None
    assert result.consent_token == "consent-token-123"
    assert result.suggested_nickname == "새싹러"
    assert pending.created_with == {
        "provider": "KAKAO",
        "sub": "12345",
        "email": "user@example.com",
        "name": "새싹러",
    }
    assert token_store.issued_for == []


async def test_verifier_error_propagates():
    interactor, *_ = _make_interactor(verifier_error=ExpiredIdTokenError())

    with pytest.raises(ExpiredIdTokenError):
        await interactor.login(MobileKakaoLoginCommand(id_token="t", nonce="n", device_id="d"))


async def test_nonce_reuse_raises_invalid_nonce():
    interactor, *_ = _make_interactor(nonce_consumable=False)

    with pytest.raises(InvalidNonceError):
        await interactor.login(MobileKakaoLoginCommand(id_token="t", nonce="n", device_id="d"))


async def test_missing_email_falls_back_to_kakao_local():
    identity = KakaoIdentity(sub="999", email=None, nickname=None)
    interactor, _, pending, _ = _make_interactor(identity=identity, existing_user=None)

    result = await interactor.login(MobileKakaoLoginCommand(id_token="t", nonce="n", device_id="d"))

    assert result.status == "consent_required"
    assert pending.created_with["email"] == "kakao_999@kakao.local"
    assert pending.created_with["name"] == "사용자"
