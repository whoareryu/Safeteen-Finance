from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from apps.auth.adapter.outbound.kakao.kakao_id_token_verifier import KakaoIdTokenVerifier
from apps.auth.adapter.outbound.persistence.mobile_user_repository import SqlAlchemyMobileUserRepository
from apps.auth.adapter.outbound.redis.mobile_kakao_token_store import MobileKakaoTokenStore
from apps.auth.adapter.outbound.redis.mobile_nonce_store import RedisNonceStore
from apps.auth.adapter.outbound.redis.mobile_pending_signup_store import MobilePendingSignupStore
from apps.auth.app.ports.input.mobile_auth_use_case import (
    MobileConsentCompleteUseCase,
    MobileKakaoLoginUseCase,
    MobileLogoutUseCase,
    MobileRefreshUseCase,
)
from apps.auth.app.ports.output.kakao_id_token_verifier_port import IdTokenVerifierPort
from apps.auth.app.ports.output.mobile_nonce_store_port import NonceStorePort
from apps.auth.app.ports.output.mobile_pending_signup_port import PendingSignupPort
from apps.auth.app.ports.output.mobile_token_store_port import MobileTokenStorePort
from apps.auth.app.ports.output.mobile_user_repository_port import MobileUserRepositoryPort
from apps.auth.app.use_cases.mobile_consent_complete_interactor import MobileConsentCompleteInteractor
from apps.auth.app.use_cases.mobile_kakao_login_interactor import MobileKakaoLoginInteractor
from apps.auth.app.use_cases.mobile_logout_interactor import MobileLogoutInteractor
from apps.auth.app.use_cases.mobile_refresh_interactor import MobileRefreshInteractor
from apps.database import get_sync_db
from core.matrix.secret_manager import secret_manager

_AUD = secret_manager.get_secret("SERVICE_AUD", "whoareryu-api")


@lru_cache(maxsize=1)
def _kakao_jwks_client() -> PyJWKClient:
    jwks_url = secret_manager.get_secret("KAKAO_JWKS_URL", "https://kauth.kakao.com/.well-known/jwks.json")
    return PyJWKClient(jwks_url)


def get_kakao_id_token_verifier() -> IdTokenVerifierPort:
    return KakaoIdTokenVerifier(
        jwks_client=_kakao_jwks_client(),
        issuer=secret_manager.get_secret("KAKAO_ISSUER", "https://kauth.kakao.com"),
        audience=secret_manager.get_secret("KAKAO_NATIVE_APP_KEY"),
    )


def get_mobile_nonce_store() -> NonceStorePort:
    return RedisNonceStore()


def get_mobile_pending_signup_store() -> PendingSignupPort:
    return MobilePendingSignupStore()


def get_mobile_token_store() -> MobileTokenStorePort:
    return MobileKakaoTokenStore(aud=_AUD)


def get_mobile_user_repository(db: Session = Depends(get_sync_db)) -> MobileUserRepositoryPort:
    return SqlAlchemyMobileUserRepository(db=db)


def get_mobile_kakao_login_use_case(
    verifier: IdTokenVerifierPort = Depends(get_kakao_id_token_verifier),
    nonce_store: NonceStorePort = Depends(get_mobile_nonce_store),
    user_repository: MobileUserRepositoryPort = Depends(get_mobile_user_repository),
    pending_signup: PendingSignupPort = Depends(get_mobile_pending_signup_store),
    token_store: MobileTokenStorePort = Depends(get_mobile_token_store),
) -> MobileKakaoLoginUseCase:
    return MobileKakaoLoginInteractor(
        verifier=verifier,
        nonce_store=nonce_store,
        user_repository=user_repository,
        pending_signup=pending_signup,
        token_store=token_store,
    )


def get_mobile_consent_complete_use_case(
    pending_signup: PendingSignupPort = Depends(get_mobile_pending_signup_store),
    user_repository: MobileUserRepositoryPort = Depends(get_mobile_user_repository),
    token_store: MobileTokenStorePort = Depends(get_mobile_token_store),
) -> MobileConsentCompleteUseCase:
    return MobileConsentCompleteInteractor(
        pending_signup=pending_signup, user_repository=user_repository, token_store=token_store
    )


def get_mobile_refresh_use_case(
    token_store: MobileTokenStorePort = Depends(get_mobile_token_store),
    user_repository: MobileUserRepositoryPort = Depends(get_mobile_user_repository),
) -> MobileRefreshUseCase:
    return MobileRefreshInteractor(token_store=token_store, user_repository=user_repository)


def get_mobile_logout_use_case(
    token_store: MobileTokenStorePort = Depends(get_mobile_token_store),
) -> MobileLogoutUseCase:
    return MobileLogoutInteractor(token_store=token_store)
