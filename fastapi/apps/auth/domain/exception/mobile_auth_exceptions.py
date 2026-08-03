"""모바일 카카오 로그인 도메인 예외 — fastapi/HTTP 의존 없음.

라우터(adapter/inbound/api/v1/mobile_auth_router.py)가 이 예외들을 HTTP 상태코드 +
X-Error-Code 헤더로 매핑한다.
"""
from __future__ import annotations


class MobileAuthError(Exception):
    """모든 모바일 인증 예외의 베이스."""


class InvalidIdTokenError(MobileAuthError):
    pass


class ExpiredIdTokenError(MobileAuthError):
    pass


class InvalidAudienceError(MobileAuthError):
    pass


class InvalidNonceError(MobileAuthError):
    pass


class PlatformMismatchError(MobileAuthError):
    pass


class TokenReuseDetectedError(MobileAuthError):
    pass


class IdpUnavailableError(MobileAuthError):
    pass


class ConsentRequiredTermsNotAgreedError(MobileAuthError):
    pass


class NicknameRequiredError(MobileAuthError):
    pass


class NicknameTakenError(MobileAuthError):
    pass


class ConsentTokenInvalidError(MobileAuthError):
    pass


class SessionUserNotFoundError(MobileAuthError):
    pass
