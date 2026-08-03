"""RS256 JWT 발급·검증 — auth-gateway-harness.md 2.2.

발급부(create_access_token/create_refresh_token)는 auth 컨테이너 전용이며
JWT_PRIVATE_KEY가 있어야 호출 가능하다. 검증부(verify_token)는 모든 컨테이너가
공용으로 쓰며 JWT_PUBLIC_KEY만 있으면 된다. 두 키 모두 모듈 로드 시점이 아니라
함수 호출 시점에 환경변수에서 읽는다 — 백엔드 컨테이너는 JWT_PRIVATE_KEY가 없어도
이 모듈을 import할 수 있어야 하기 때문이다(발급 함수를 실제로 호출하지 않는 한
에러가 나면 안 된다).
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import time
import uuid
from dataclasses import dataclass
from functools import lru_cache

import bcrypt
import jwt
from cryptography.hazmat.primitives import serialization
from redis.asyncio import Redis

from core.matrix.secret_manager import secret_manager

_ALGORITHM = "RS256"
# 프론트엔드에 자동 refresh 인터셉터가 아직 없어서(추후 과제), 액세스 토큰이 만료되면
# 곧바로 재로그인이 필요해진다. 문서가 예로 든 10분은 그 상태에서 너무 짧아 기본값을
# 늘렸다 — 필요하면 ACCESS_TOKEN_TTL_MIN 환경변수로 조정.
ACCESS_TOKEN_TTL_MIN_DEFAULT = int(secret_manager.get_secret("ACCESS_TOKEN_TTL_MIN", "120"))
REFRESH_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30  # 30일

_REFRESH_KEY_PREFIX = "refresh:"
_REFRESH_FAMILY_KEY_PREFIX = "refresh_family:"
_BLACKLIST_KEY_PREFIX = "jwt_blacklist:"

COOKIE_KWARGS = dict(
    domain=secret_manager.get_secret("COOKIE_DOMAIN", None),
    secure=True,
    httponly=True,
    samesite="lax",
)


@dataclass(frozen=True)
class TokenPayload:

    sub: str
    roles: list[str]
    aud: str
    exp: int
    iat: int
    jti: str
    platform: str = "web"


def _private_key() -> str:
    return os.environ["JWT_PRIVATE_KEY"]


def _public_key() -> str:
    return os.environ["JWT_PUBLIC_KEY"]


def key_id() -> str:
    """공개키에서 결정론적으로 kid를 만든다 — 같은 키를 쓰는 한 재시작해도 같다.

    (해시 계산 자체가 가벼워서 캐싱하지 않는다 — 캐싱하면 테스트에서 키를 바꿔
    끼울 때 stale한 kid가 남는 문제가 생긴다.)
    """
    digest = hashlib.sha256(_public_key().encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")[:16]


def public_jwk() -> dict:
    """JWKS(/.well-known/jwks.json) 응답용 — 공개키를 JWK(RFC 7517) 형식으로 변환."""
    public_key = serialization.load_pem_public_key(_public_key().encode())
    numbers = public_key.public_numbers()

    def _b64url_uint(value: int) -> str:
        length = (value.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(value.to_bytes(length, "big")).decode().rstrip("=")

    return {
        "kty": "RSA",
        "use": "sig",
        "alg": _ALGORITHM,
        "kid": key_id(),
        "n": _b64url_uint(numbers.n),
        "e": _b64url_uint(numbers.e),
    }


def create_access_token(
    sub: str,
    roles: list[str],
    aud: str,
    expires_min: int = ACCESS_TOKEN_TTL_MIN_DEFAULT,
    platform: str = "web",
) -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "roles": roles,
        "aud": aud,
        "iat": now,
        "exp": now + expires_min * 60,
        "jti": uuid.uuid4().hex,
        "platform": platform,
    }
    return jwt.encode(
        payload, _private_key(), algorithm=_ALGORITHM, headers={"kid": key_id()}
    )


def verify_token(token: str, aud: str) -> TokenPayload:
    """서명·만료·audience를 검증한다. 실패 시 jwt.PyJWTError 하위 예외를 그대로 raise."""
    payload = jwt.decode(token, _public_key(), algorithms=[_ALGORITHM], audience=aud)
    return TokenPayload(
        sub=payload["sub"],
        roles=payload.get("roles", []),
        aud=payload["aud"],
        exp=payload["exp"],
        iat=payload["iat"],
        jti=payload["jti"],
        platform=payload.get("platform", "web"),
    )


def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()


def verify_password(raw: str, hashed: str) -> bool:
    return bcrypt.checkpw(raw.encode(), hashed.encode())


# ── 리프레시 토큰 (Redis, 로테이션 방식) ─────────────────────────────────────
# 토큰 자체는 opaque(무작위 문자열)로 발급한다 — 클라이언트가 파싱할 필요가 없고,
# 서버 쪽 조회 없이는 무효화할 수 없는 JWT 리프레시 토큰보다 즉시 폐기가 쉽다.
# family_id로 "이 사용자의 현재 유효한 리프레시 체인"을 추적한다. 로테이션 시
# 이전 토큰은 바로 지우지 않고 status="used"로만 표시해 재사용 시도를 구분할 수
# 있게 하고, 재사용이 감지되면(이미 used인 토큰이 다시 제시됨) family 전체를
# 폐기해 해당 사용자의 모든 세션을 강제 로그아웃시킨다.


@lru_cache(maxsize=1)
def _redis_client() -> Redis:
    return Redis.from_url(secret_manager.get_secret("REDIS_URL", "redis://redis:6379/0"))


async def create_refresh_token(
    sub: str, *, namespace: str = "", extra: dict | None = None, ttl_seconds: int = REFRESH_TOKEN_TTL_SECONDS
) -> str:
    """새 리프레시 토큰 체인을 시작한다 (로그인 시 호출).

    namespace는 키 프리픽스 앞에 그대로 붙는다(기본값 ""이면 기존 웹 키와 동일) —
    모바일처럼 별도 세션 네임스페이스가 필요한 호출자가 서로 다른 값을 준다.
    extra는 저장되는 JSON에 그대로 병합된다(device_id 등 부가 정보용).
    """
    token = secrets.token_urlsafe(32)
    family_id = uuid.uuid4().hex
    client = _redis_client()
    data = {"sub": sub, "family_id": family_id, "status": "active"}
    if extra:
        data.update(extra)
    await client.set(
        f"{namespace}{_REFRESH_KEY_PREFIX}{token}",
        json.dumps(data),
        ex=ttl_seconds,
    )
    await client.set(
        f"{namespace}{_REFRESH_FAMILY_KEY_PREFIX}{sub}", family_id, ex=ttl_seconds
    )
    return token


async def rotate_refresh_token(
    token: str, *, namespace: str = "", ttl_seconds: int = REFRESH_TOKEN_TTL_SECONDS
) -> tuple[str, str] | None:
    """리프레시 토큰을 검증하고 로테이션한다.

    반환값: 성공 시 (sub, 새 리프레시 토큰). 실패(모르는 토큰) 또는 재사용
    감지(이미 used인 토큰 재제시) 시 None — 재사용 감지 시 해당 sub의 리프레시
    체인 전체를 폐기해 강제 재로그인시킨다.
    """
    client = _redis_client()
    raw = await client.get(f"{namespace}{_REFRESH_KEY_PREFIX}{token}")
    if raw is None:
        return None

    data = json.loads(raw)
    sub, family_id, status = data["sub"], data["family_id"], data["status"]
    current_family = await client.get(f"{namespace}{_REFRESH_FAMILY_KEY_PREFIX}{sub}")

    if status != "active" or current_family is None or current_family.decode() != family_id:
        await client.delete(f"{namespace}{_REFRESH_FAMILY_KEY_PREFIX}{sub}")
        return None

    data["status"] = "used"
    await client.set(
        f"{namespace}{_REFRESH_KEY_PREFIX}{token}", json.dumps(data), ex=ttl_seconds
    )

    new_token = secrets.token_urlsafe(32)
    new_data = {"sub": sub, "family_id": family_id, "status": "active"}
    extra_keys = set(data) - {"sub", "family_id", "status"}
    for key in extra_keys:
        new_data[key] = data[key]
    await client.set(
        f"{namespace}{_REFRESH_KEY_PREFIX}{new_token}", json.dumps(new_data), ex=ttl_seconds
    )
    return sub, new_token


async def revoke_refresh_family(sub: str, *, namespace: str = "") -> None:
    """로그아웃 등으로 해당 사용자의 리프레시 체인 전체를 폐기한다."""
    await _redis_client().delete(f"{namespace}{_REFRESH_FAMILY_KEY_PREFIX}{sub}")


# ── 액세스 토큰 블랙리스트 (즉시 차단용) ─────────────────────────────────────
# access token은 만료 전까지 서명만으로 유효하다고 판단하므로, 계정 정지처럼
# 즉시 무효화가 필요한 경우를 위해 jti 블랙리스트를 둔다.


async def blacklist_token(jti: str, ttl_seconds: int, *, namespace: str = "") -> None:
    await _redis_client().set(f"{namespace}{_BLACKLIST_KEY_PREFIX}{jti}", "1", ex=ttl_seconds)


async def is_token_blacklisted(jti: str, *, namespace: str = "") -> bool:
    return await _redis_client().exists(f"{namespace}{_BLACKLIST_KEY_PREFIX}{jti}") == 1
