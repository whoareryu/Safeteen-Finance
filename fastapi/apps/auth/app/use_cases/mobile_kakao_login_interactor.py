from __future__ import annotations

from apps.auth.app.dtos.mobile_auth_dto import (
    MobileAuthTokens,
    MobileKakaoLoginCommand,
    MobileLoginResult,
)
from apps.auth.app.ports.input.mobile_auth_use_case import MobileKakaoLoginUseCase
from apps.auth.app.ports.output.kakao_id_token_verifier_port import IdTokenVerifierPort
from apps.auth.app.ports.output.mobile_nonce_store_port import NonceStorePort
from apps.auth.app.ports.output.mobile_pending_signup_port import PendingSignupPort
from apps.auth.app.ports.output.mobile_token_store_port import MobileTokenStorePort
from apps.auth.app.ports.output.mobile_user_repository_port import MobileUserRepositoryPort
from apps.auth.domain.exception.mobile_auth_exceptions import InvalidNonceError

_PROVIDER = "KAKAO"


class MobileKakaoLoginInteractor(MobileKakaoLoginUseCase):

    def __init__(
        self,
        verifier: IdTokenVerifierPort,
        nonce_store: NonceStorePort,
        user_repository: MobileUserRepositoryPort,
        pending_signup: PendingSignupPort,
        token_store: MobileTokenStorePort,
    ) -> None:
        self._verifier = verifier
        self._nonce_store = nonce_store
        self._user_repository = user_repository
        self._pending_signup = pending_signup
        self._token_store = token_store

    async def login(self, command: MobileKakaoLoginCommand) -> MobileLoginResult:
        identity = self._verifier.verify(command.id_token, nonce=command.nonce)

        if not await self._nonce_store.consume_once(command.nonce):
            raise InvalidNonceError()

        email = identity.email or f"kakao_{identity.sub}@kakao.local"
        user = self._user_repository.find_existing(provider=_PROVIDER, sub=identity.sub, email=email)

        if user is not None:
            tokens = await self._issue_tokens(sub=str(user.id), roles=[user.role], device_id=command.device_id)
            return MobileLoginResult(status="logged_in", tokens=tokens, is_new_user=False)

        consent_token = await self._pending_signup.create(
            provider=_PROVIDER, sub=identity.sub, email=email, name=identity.nickname or "사용자"
        )
        return MobileLoginResult(
            status="consent_required",
            consent_token=consent_token,
            suggested_nickname=identity.nickname or "사용자",
        )

    async def _issue_tokens(self, *, sub: str, roles: list[str], device_id: str) -> MobileAuthTokens:
        access_token, expires_in = await self._token_store.create_access_token(sub=sub, roles=roles)
        refresh_token = await self._token_store.create_refresh_token(sub=sub, device_id=device_id)
        return MobileAuthTokens(
            access_token=access_token, refresh_token=refresh_token, token_type="Bearer", expires_in=expires_in
        )
