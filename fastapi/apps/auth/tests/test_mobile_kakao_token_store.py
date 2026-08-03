"""통합 테스트 — 실제 Redis 필요 (REDIS_URL, 기본 redis://localhost:16379/0).
auth:mobile:* 키가 웹의 refresh:*/refresh_family:* 프리픽스와 섞이지 않는지 확인한다."""
from __future__ import annotations

import os

os.environ.setdefault("REDIS_URL", "redis://localhost:16379/0")
os.environ.setdefault("JWT_PRIVATE_KEY", "unused-in-this-file")
os.environ.setdefault("JWT_PUBLIC_KEY", "unused-in-this-file")

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from apps.auth.adapter.outbound.redis.mobile_kakao_token_store import MobileKakaoTokenStore  # noqa: E402
from core import security  # noqa: E402

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


@pytest.fixture(autouse=True)
def _set_keys(monkeypatch):
    private_pem, public_pem = _generate_keypair()
    monkeypatch.setenv("JWT_PRIVATE_KEY", private_pem)
    monkeypatch.setenv("JWT_PUBLIC_KEY", public_pem)


@pytest.fixture(autouse=True)
async def _fresh_redis_client():
    security._redis_client.cache_clear()
    yield
    await security._redis_client().aclose()
    security._redis_client.cache_clear()


async def test_mobile_refresh_key_is_namespaced_and_isolated_from_web():
    store = MobileKakaoTokenStore(aud=_AUD)

    mobile_refresh = await store.create_refresh_token(sub="7", device_id="device-1")
    web_refresh = await security.create_refresh_token(sub="7")  # namespace="" (웹, 기본 동작)

    client = security._redis_client()
    assert await client.exists(f"auth:mobile:refresh:{mobile_refresh}") == 1
    assert await client.exists(f"refresh:{web_refresh}") == 1
    # 서로 다른 네임스페이스 — 모바일 토큰으로 웹 키 조회 시 아무것도 안 나옴
    assert await client.exists(f"refresh:{mobile_refresh}") == 0
    assert await client.exists(f"auth:mobile:refresh:{web_refresh}") == 0


async def test_mobile_rotate_and_reuse_detection():
    store = MobileKakaoTokenStore(aud=_AUD)
    token = await store.create_refresh_token(sub="42", device_id="device-1")

    result = await store.rotate_refresh_token(token)
    assert result is not None
    sub, rotated = result
    assert sub == "42"

    reuse_result = await store.rotate_refresh_token(token)
    assert reuse_result is None
    # family 전체 폐기 — 방금 정상 로테이션됐던 토큰도 무효화됨
    assert await store.rotate_refresh_token(rotated) is None


async def test_access_token_created_with_mobile_platform_claim():
    store = MobileKakaoTokenStore(aud=_AUD)

    token, expires_in = await store.create_access_token(sub="7", roles=["user"])
    payload = security.verify_token(token, aud=_AUD)

    assert payload.platform == "mobile"
    assert expires_in == security.ACCESS_TOKEN_TTL_MIN_DEFAULT * 60


async def test_blacklist_is_mobile_namespaced():
    store = MobileKakaoTokenStore(aud=_AUD)

    await store.blacklist_access_token("jti-mobile-test")

    assert await security.is_token_blacklisted("jti-mobile-test", namespace="auth:mobile:") is True
    assert await security.is_token_blacklisted("jti-mobile-test") is False
