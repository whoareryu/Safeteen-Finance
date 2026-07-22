from __future__ import annotations

import os

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

os.environ.setdefault("REDIS_URL", "redis://localhost:16379/0")
os.environ.setdefault("BACKEND_PUBLIC_URL", "https://auth.whoareryu.cloud")
os.environ.setdefault("NAVER_CLIENT_ID", "test-naver-client-id")
os.environ.setdefault("KAKAO_REST_API_KEY", "test-kakao-client-id")
os.environ.setdefault("OWNER_EMAIL", "owner@example.com")
os.environ.setdefault("OWNER_SESSION_SECRET", "test-owner-secret")

from apps.auth import services  # noqa: E402
from apps.auth.router import jwks  # noqa: E402
from core import security  # noqa: E402


def _generate_keypair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


@pytest.fixture(scope="module")
def keypair() -> tuple[str, str]:
    return _generate_keypair()


@pytest.fixture(autouse=True)
def _set_keys(monkeypatch, keypair) -> None:
    private_pem, public_pem = keypair
    monkeypatch.setenv("JWT_PRIVATE_KEY", private_pem)
    monkeypatch.setenv("JWT_PUBLIC_KEY", public_pem)


@pytest.fixture(autouse=True)
async def _fresh_redis_client():
    security._redis_client.cache_clear()
    yield
    await security._redis_client().aclose()
    security._redis_client.cache_clear()


def test_jwks_returns_public_key_only() -> None:
    result = jwks()

    assert "keys" in result
    assert len(result["keys"]) == 1
    key = result["keys"][0]
    assert key["kty"] == "RSA"
    assert key["alg"] == "RS256"
    assert "kid" in key
    assert "n" in key and "e" in key
    # 개인키 자료가 응답에 절대 섞이면 안 된다.
    assert "d" not in key


def test_naver_login_redirect_sets_state_cookie() -> None:
    response = services.naver_login_redirect()

    assert response.status_code in (302, 307)
    assert "nid.naver.com" in response.headers["location"]
    assert "wr_oauth_state_naver" in response.headers.get("set-cookie", "")


def test_kakao_login_redirect_sets_state_cookie() -> None:
    response = services.kakao_login_redirect()

    assert response.status_code in (302, 307)
    assert "kauth.kakao.com" in response.headers["location"]
    assert "wr_oauth_state_kakao" in response.headers.get("set-cookie", "")


async def test_naver_callback_rejects_missing_state_cookie() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await services.naver_callback(
            code="somecode", state="somestate", error=None, state_cookie=None, db=None
        )

    assert exc_info.value.status_code == 401


async def test_naver_callback_rejects_state_mismatch() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await services.naver_callback(
            code="somecode", state="state-a", error=None, state_cookie="state-b", db=None
        )

    assert exc_info.value.status_code == 401


async def test_refresh_session_without_cookie_raises_401() -> None:
    from fastapi import Response

    with pytest.raises(HTTPException) as exc_info:
        await services.refresh_session(None, Response(), db=None)

    assert exc_info.value.status_code == 401


async def test_refresh_session_with_unknown_token_raises_401_and_clears_cookies() -> None:
    from fastapi import Response

    response = Response()
    with pytest.raises(HTTPException) as exc_info:
        await services.refresh_session("never-issued", response, db=None)

    assert exc_info.value.status_code == 401
    set_cookie_headers = response.headers.getlist("set-cookie")
    assert any("wr_session=" in h for h in set_cookie_headers)
    assert any("wr_refresh=" in h for h in set_cookie_headers)
