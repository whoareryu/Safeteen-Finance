from __future__ import annotations

from apps.auth.adapter.inbound.api.schemas.mobile_auth_schema import (
    MobileAuthTokensResponseSchema,
    MobileKakaoLoginResponseSchema,
)
from apps.auth.app.dtos.mobile_auth_dto import MobileAuthTokens, MobileLoginResult


def login_result_to_response(result: MobileLoginResult) -> MobileKakaoLoginResponseSchema:
    tokens = result.tokens
    return MobileKakaoLoginResponseSchema(
        status=result.status,
        access_token=tokens.access_token if tokens else None,
        refresh_token=tokens.refresh_token if tokens else None,
        token_type=tokens.token_type if tokens else None,
        expires_in=tokens.expires_in if tokens else None,
        is_new_user=result.is_new_user,
        consent_token=result.consent_token,
        suggested_nickname=result.suggested_nickname,
    )


def tokens_to_response(tokens: MobileAuthTokens) -> MobileAuthTokensResponseSchema:
    return MobileAuthTokensResponseSchema(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )
