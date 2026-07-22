from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

os.environ.setdefault("REDIS_URL", "redis://localhost:16379/0")

from core import security  # noqa: E402  (REDIS_URL must be set before import)


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
    # pytest-asyncio는 테스트 함수마다 새 이벤트 루프를 쓰는데, security._redis_client는
    # @lru_cache로 클라이언트를 프로세스 전역에 캐싱한다 — 이전 테스트의(이미 닫힌)
    # 이벤트 루프에 묶인 커넥션을 재사용하려다 "Event loop is closed"가 난다. 매
    # 테스트마다 캐시를 비워 현재 루프에 새로 연결하게 한다.
    security._redis_client.cache_clear()
    yield
    await security._redis_client().aclose()
    security._redis_client.cache_clear()


_AUD = "whoareryu-api"


def test_issue_and_verify_roundtrip() -> None:
    token = security.create_access_token(sub="42", roles=["admin"], aud=_AUD)
    payload = security.verify_token(token, aud=_AUD)

    assert payload.sub == "42"
    assert payload.roles == ["admin"]
    assert payload.aud == _AUD
    assert payload.jti


def test_verify_rejects_wrong_audience() -> None:
    token = security.create_access_token(sub="42", roles=["user"], aud=_AUD)

    with pytest.raises(jwt.InvalidAudienceError):
        security.verify_token(token, aud="some-other-service")


def test_verify_rejects_expired_token() -> None:
    token = security.create_access_token(sub="42", roles=["user"], aud=_AUD, expires_min=-1)

    with pytest.raises(jwt.ExpiredSignatureError):
        security.verify_token(token, aud=_AUD)


def test_verify_rejects_tampered_signature() -> None:
    token = security.create_access_token(sub="42", roles=["user"], aud=_AUD)
    tampered = token[:-4] + ("aaaa" if token[-4:] != "aaaa" else "bbbb")

    with pytest.raises(jwt.PyJWTError):
        security.verify_token(tampered, aud=_AUD)


def test_verify_rejects_alg_none_forged_token() -> None:
    now = int(time.time())
    forged = jwt.encode(
        {"sub": "42", "roles": ["admin"], "aud": _AUD, "iat": now, "exp": now + 600, "jti": "x"},
        key="",
        algorithm="none",
    )

    with pytest.raises(jwt.PyJWTError):
        security.verify_token(forged, aud=_AUD)


def test_verify_rejects_hs256_forced_token(keypair) -> None:
    # RS256/HS256 알고리즘 혼동 공격: 공개키를 HMAC 대칭키로 오용해 서명한 토큰을
    # verify_token의 algorithms=["RS256"] 하드코딩이 거부하는지 확인한다.
    # PyJWT의 jwt.encode()는 PEM 형식 키를 HMAC secret으로 쓰는 걸 자체 방어하므로,
    # 그 방어를 우회하는 공격자를 흉내 내 header.payload.signature를 직접 조립한다.
    _, public_pem = keypair
    now = int(time.time())
    header = base64.urlsafe_b64encode(
        json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
    ).rstrip(b"=")
    payload = base64.urlsafe_b64encode(
        json.dumps(
            {"sub": "42", "roles": ["admin"], "aud": _AUD, "iat": now, "exp": now + 600, "jti": "x"}
        ).encode()
    ).rstrip(b"=")
    signing_input = header + b"." + payload
    signature = base64.urlsafe_b64encode(
        hmac.new(public_pem.encode(), signing_input, hashlib.sha256).digest()
    ).rstrip(b"=")
    forged = (signing_input + b"." + signature).decode()

    with pytest.raises(jwt.PyJWTError):
        security.verify_token(forged, aud=_AUD)


async def test_refresh_token_rotation_returns_new_token() -> None:
    token = await security.create_refresh_token(sub="42")

    result = await security.rotate_refresh_token(token)

    assert result is not None
    sub, new_token = result
    assert sub == "42"
    assert new_token != token


async def test_refresh_token_reuse_revokes_entire_family() -> None:
    token = await security.create_refresh_token(sub="99")

    first_result = await security.rotate_refresh_token(token)
    assert first_result is not None
    _, rotated_token = first_result

    # 이미 사용된(로테이션된) 토큰을 다시 제시 — 재사용 공격 시나리오.
    reuse_result = await security.rotate_refresh_token(token)
    assert reuse_result is None

    # family 전체가 폐기됐으므로, 정상적으로 로테이션됐던 새 토큰도 더 이상 유효하지 않다.
    after_revoke = await security.rotate_refresh_token(rotated_token)
    assert after_revoke is None


async def test_rotate_refresh_token_rejects_unknown_token() -> None:
    result = await security.rotate_refresh_token("never-issued-token")

    assert result is None


async def test_blacklist_token_marks_jti_blacklisted() -> None:
    # 실제 Redis에 대고 도는 테스트라 매 실행마다 고유한 jti를 써야 한다 — 고정
    # 문자열을 쓰면 TTL이 끝나기 전에 같은 테스트를 다시 돌렸을 때 이전 실행의
    # 잔여 키 때문에 첫 assert가 깨진다.
    jti = uuid.uuid4().hex

    assert await security.is_token_blacklisted(jti) is False

    await security.blacklist_token(jti, ttl_seconds=60)

    assert await security.is_token_blacklisted(jti) is True


def test_password_hash_roundtrip() -> None:
    hashed = security.hash_password("hunter2")

    assert security.verify_password("hunter2", hashed) is True
    assert security.verify_password("wrong", hashed) is False
