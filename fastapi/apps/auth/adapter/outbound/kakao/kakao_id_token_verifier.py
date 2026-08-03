"""카카오 OIDC id_token 검증 — JWKS 기반 로컬 서명 검증만으로 완결한다.

access_token으로 /v2/user/me를 호출하는 기존 웹 플로우(apps/auth/services.py)와
달리 카카오 서버에 신원 확인을 왕복하지 않는다 — id_token 자체가 카카오가 서명한
신원 증명이라, 서명·클레임 검증만으로 충분하다.
"""
from __future__ import annotations

import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientError

from apps.auth.app.ports.output.kakao_id_token_verifier_port import IdTokenVerifierPort
from apps.auth.domain.exception.mobile_auth_exceptions import (
    ExpiredIdTokenError,
    IdpUnavailableError,
    InvalidAudienceError,
    InvalidIdTokenError,
    InvalidNonceError,
)
from apps.auth.domain.model.mobile_kakao_identity import KakaoIdentity

_ALGORITHM = "RS256"
_LEEWAY_SECONDS = 60


class KakaoIdTokenVerifier(IdTokenVerifierPort):

    def __init__(self, jwks_client: PyJWKClient, issuer: str, audience: str) -> None:
        self._jwks_client = jwks_client
        self._issuer = issuer
        self._audience = audience

    def verify(self, id_token: str, *, nonce: str) -> KakaoIdentity:
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(id_token)
        except PyJWKClientError as e:
            raise IdpUnavailableError() from e

        try:
            payload = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=[_ALGORITHM],
                issuer=self._issuer,
                audience=self._audience,
                leeway=_LEEWAY_SECONDS,
            )
        except jwt.ExpiredSignatureError as e:
            raise ExpiredIdTokenError() from e
        except jwt.InvalidAudienceError as e:
            raise InvalidAudienceError() from e
        except jwt.PyJWTError as e:
            raise InvalidIdTokenError() from e

        if payload.get("nonce") != nonce:
            raise InvalidNonceError()

        sub = payload.get("sub")
        if not sub:
            raise InvalidIdTokenError()

        return KakaoIdentity(sub=str(sub), email=payload.get("email"), nickname=payload.get("nickname"))
