"""모바일 카카오 로그인 — 에러는 기존 관례대로 한국어 HTTPException.detail +
머신 판별용 X-Error-Code 헤더로 응답한다(플러터가 헤더로 분기)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from apps.auth.adapter.inbound.api.schemas.mobile_auth_schema import (
    MobileAuthTokensResponseSchema,
    MobileConsentCompleteRequestSchema,
    MobileKakaoLoginRequestSchema,
    MobileKakaoLoginResponseSchema,
    MobileRefreshRequestSchema,
)
from apps.auth.adapter.outbound.mappers.mobile_auth_mapper import (
    login_result_to_response,
    tokens_to_response,
)
from apps.auth.app.dtos.mobile_auth_dto import (
    MobileConsentCompleteCommand,
    MobileKakaoLoginCommand,
    MobileLogoutCommand,
    MobileRefreshCommand,
)
from apps.auth.app.ports.input.mobile_auth_use_case import (
    MobileConsentCompleteUseCase,
    MobileKakaoLoginUseCase,
    MobileLogoutUseCase,
    MobileRefreshUseCase,
)
from apps.auth.mobile_auth_provider import (
    get_mobile_consent_complete_use_case,
    get_mobile_kakao_login_use_case,
    get_mobile_logout_use_case,
    get_mobile_refresh_use_case,
)
from apps.auth.domain.exception.mobile_auth_exceptions import (
    ConsentRequiredTermsNotAgreedError,
    ConsentTokenInvalidError,
    ExpiredIdTokenError,
    IdpUnavailableError,
    InvalidAudienceError,
    InvalidIdTokenError,
    InvalidNonceError,
    MobileAuthError,
    NicknameRequiredError,
    NicknameTakenError,
    PlatformMismatchError,
    SessionUserNotFoundError,
    TokenReuseDetectedError,
)
from core.dependencies import get_current_user
from core.security import TokenPayload

mobile_auth_router = APIRouter(prefix="/auth/mobile", tags=["auth-mobile"])

_ERROR_MAP: dict[type[MobileAuthError], tuple[int, str, str]] = {
    InvalidIdTokenError: (401, "INVALID_ID_TOKEN", "유효하지 않은 로그인 토큰입니다."),
    ExpiredIdTokenError: (401, "EXPIRED_ID_TOKEN", "로그인 토큰이 만료되었습니다."),
    InvalidAudienceError: (401, "INVALID_AUDIENCE", "잘못된 앱에서 발급된 토큰입니다."),
    InvalidNonceError: (401, "INVALID_NONCE", "잘못되었거나 재사용된 로그인 요청입니다."),
    IdpUnavailableError: (503, "IDP_UNAVAILABLE", "카카오 로그인 서비스에 연결할 수 없습니다."),
    ConsentRequiredTermsNotAgreedError: (422, "TERMS_NOT_AGREED", "이용약관 및 개인정보처리방침에 동의해야 합니다."),
    NicknameRequiredError: (422, "NICKNAME_REQUIRED", "닉네임을 입력해 주세요."),
    NicknameTakenError: (409, "NICKNAME_TAKEN", "이미 사용 중인 닉네임입니다."),
    ConsentTokenInvalidError: (400, "CONSENT_TOKEN_INVALID", "만료되었거나 잘못된 요청입니다. 다시 로그인해 주세요."),
    TokenReuseDetectedError: (401, "TOKEN_REUSE_DETECTED", "세션이 만료되었습니다. 다시 로그인해 주세요."),
    SessionUserNotFoundError: (401, "SESSION_USER_NOT_FOUND", "사용자를 찾을 수 없습니다."),
    PlatformMismatchError: (401, "PLATFORM_MISMATCH", "세션이 유효하지 않습니다. 다시 로그인해 주세요."),
}


def _raise_mapped(error: MobileAuthError) -> None:
    status_code, code, message = _ERROR_MAP[type(error)]
    raise HTTPException(status_code=status_code, detail=message, headers={"X-Error-Code": code}) from error


@mobile_auth_router.post("/kakao/login", summary="카카오 id_token으로 모바일 로그인")
async def kakao_login(
    body: MobileKakaoLoginRequestSchema,
    use_case: MobileKakaoLoginUseCase = Depends(get_mobile_kakao_login_use_case),
) -> MobileKakaoLoginResponseSchema:
    try:
        result = await use_case.login(
            MobileKakaoLoginCommand(id_token=body.id_token, nonce=body.nonce, device_id=body.device_id)
        )
    except MobileAuthError as e:
        _raise_mapped(e)
    return login_result_to_response(result)


@mobile_auth_router.post("/consent/complete", summary="신규가입 약관동의 완료 후 로그인")
async def consent_complete(
    body: MobileConsentCompleteRequestSchema,
    use_case: MobileConsentCompleteUseCase = Depends(get_mobile_consent_complete_use_case),
) -> MobileAuthTokensResponseSchema:
    try:
        tokens = await use_case.complete(
            MobileConsentCompleteCommand(
                consent_token=body.consent_token,
                nickname=body.nickname,
                agree_terms=body.agree_terms,
                device_id=body.device_id,
            )
        )
    except MobileAuthError as e:
        _raise_mapped(e)
    return tokens_to_response(tokens)


@mobile_auth_router.post("/refresh", summary="모바일 세션 리프레시")
async def refresh(
    body: MobileRefreshRequestSchema,
    use_case: MobileRefreshUseCase = Depends(get_mobile_refresh_use_case),
) -> MobileAuthTokensResponseSchema:
    try:
        tokens = await use_case.refresh(MobileRefreshCommand(refresh_token=body.refresh_token))
    except MobileAuthError as e:
        _raise_mapped(e)
    return tokens_to_response(tokens)


@mobile_auth_router.post("/logout", status_code=204, summary="모바일 로그아웃")
async def logout(
    current_user: TokenPayload = Depends(get_current_user),
    use_case: MobileLogoutUseCase = Depends(get_mobile_logout_use_case),
) -> None:
    try:
        await use_case.logout(
            MobileLogoutCommand(sub=current_user.sub, jti=current_user.jti, platform=current_user.platform)
        )
    except MobileAuthError as e:
        _raise_mapped(e)
