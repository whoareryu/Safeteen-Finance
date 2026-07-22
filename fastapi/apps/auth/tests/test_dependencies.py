from __future__ import annotations

import os

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

os.environ.setdefault("REDIS_URL", "redis://localhost:16379/0")

from apps.auth.user_role import UserRole  # noqa: E402
from core import security  # noqa: E402
from core.dependencies import RoleChecker, get_current_user  # noqa: E402

_AUD = "whoareryu-api"


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
    # test_security.py와 동일한 이유 — 테스트마다 새 이벤트 루프가 생기므로
    # 캐시된 Redis 클라이언트를 매번 새로 만든다.
    security._redis_client.cache_clear()
    yield
    await security._redis_client().aclose()
    security._redis_client.cache_clear()


async def test_get_current_user_from_cookie() -> None:
    token = security.create_access_token(sub="7", roles=[UserRole.admin.value], aud=_AUD)

    payload = await get_current_user(wr_session=token, authorization=None)

    assert payload.sub == "7"
    assert payload.roles == ["admin"]


async def test_get_current_user_from_bearer_header() -> None:
    token = security.create_access_token(sub="8", roles=[UserRole.user.value], aud=_AUD)

    payload = await get_current_user(wr_session=None, authorization=f"Bearer {token}")

    assert payload.sub == "8"


async def test_get_current_user_missing_token_raises_401() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(wr_session=None, authorization=None)

    assert exc_info.value.status_code == 401


async def test_get_current_user_invalid_token_raises_401() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(wr_session="not-a-real-token", authorization=None)

    assert exc_info.value.status_code == 401


async def test_get_current_user_blacklisted_jti_raises_401() -> None:
    token = security.create_access_token(sub="9", roles=[UserRole.user.value], aud=_AUD)
    payload = security.verify_token(token, aud=_AUD)
    await security.blacklist_token(payload.jti, ttl_seconds=60)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(wr_session=token, authorization=None)

    assert exc_info.value.status_code == 401


async def test_role_checker_allows_matching_role() -> None:
    token = security.create_access_token(sub="10", roles=[UserRole.admin.value], aud=_AUD)
    user = await get_current_user(wr_session=token, authorization=None)

    checker = RoleChecker(UserRole.admin)
    result = checker(user=user)

    assert result.sub == "10"


async def test_role_checker_rejects_non_matching_role() -> None:
    token = security.create_access_token(sub="11", roles=[UserRole.user.value], aud=_AUD)
    user = await get_current_user(wr_session=token, authorization=None)

    checker = RoleChecker(UserRole.admin)
    with pytest.raises(HTTPException) as exc_info:
        checker(user=user)

    assert exc_info.value.status_code == 403
