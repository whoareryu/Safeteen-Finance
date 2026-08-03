"""오프라인 검증 — 실제 kauth.kakao.com에 네트워크 요청을 보내지 않는다.
PyJWKClient를 로컬 RSA 키페어로 만든 가짜 JWKS로 대체한다."""
from __future__ import annotations

import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from apps.auth.adapter.outbound.kakao.kakao_id_token_verifier import KakaoIdTokenVerifier
from apps.auth.domain.exception.mobile_auth_exceptions import (
    ExpiredIdTokenError,
    InvalidAudienceError,
    InvalidIdTokenError,
    InvalidNonceError,
)

_ISSUER = "https://kauth.kakao.com"
_AUD = "test-native-app-key"


class _FakeSigningKey:
    def __init__(self, key) -> None:
        self.key = key


class _FakeJwksClient:
    def __init__(self, key) -> None:
        self._key = key

    def get_signing_key_from_jwt(self, token: str) -> _FakeSigningKey:
        return _FakeSigningKey(self._key)


@pytest.fixture(scope="module")
def keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


def _make_token(private_key, *, aud=_AUD, iss=_ISSUER, exp_delta=600, nonce="nonce-1", sub="12345"):
    now = int(time.time())
    payload = {
        "iss": iss,
        "aud": aud,
        "sub": sub,
        "iat": now,
        "exp": now + exp_delta,
        "nonce": nonce,
        "email": "user@example.com",
        "nickname": "새싹러",
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def _verifier(public_key) -> KakaoIdTokenVerifier:
    return KakaoIdTokenVerifier(jwks_client=_FakeJwksClient(public_key), issuer=_ISSUER, audience=_AUD)


def test_valid_token_returns_identity(keypair):
    private_key, public_key = keypair
    token = _make_token(private_key)

    identity = _verifier(public_key).verify(token, nonce="nonce-1")

    assert identity.sub == "12345"
    assert identity.email == "user@example.com"
    assert identity.nickname == "새싹러"


def test_wrong_audience_raises(keypair):
    private_key, public_key = keypair
    token = _make_token(private_key, aud="some-other-app")

    with pytest.raises(InvalidAudienceError):
        _verifier(public_key).verify(token, nonce="nonce-1")


def test_wrong_issuer_raises(keypair):
    private_key, public_key = keypair
    token = _make_token(private_key, iss="https://evil.example.com")

    with pytest.raises(InvalidIdTokenError):
        _verifier(public_key).verify(token, nonce="nonce-1")


def test_expired_token_raises(keypair):
    private_key, public_key = keypair
    token = _make_token(private_key, exp_delta=-600)

    with pytest.raises(ExpiredIdTokenError):
        _verifier(public_key).verify(token, nonce="nonce-1")


def test_tampered_signature_raises(keypair):
    _, public_key = keypair
    other_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = _make_token(other_private_key)  # 다른 키로 서명

    with pytest.raises(InvalidIdTokenError):
        _verifier(public_key).verify(token, nonce="nonce-1")


def test_nonce_mismatch_raises(keypair):
    private_key, public_key = keypair
    token = _make_token(private_key, nonce="nonce-1")

    with pytest.raises(InvalidNonceError):
        _verifier(public_key).verify(token, nonce="nonce-2")
