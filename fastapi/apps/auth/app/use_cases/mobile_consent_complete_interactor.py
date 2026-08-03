from __future__ import annotations

from apps.auth.app.dtos.mobile_auth_dto import MobileAuthTokens, MobileConsentCompleteCommand
from apps.auth.app.ports.input.mobile_auth_use_case import MobileConsentCompleteUseCase
from apps.auth.app.ports.output.mobile_pending_signup_port import PendingSignupPort
from apps.auth.app.ports.output.mobile_token_store_port import MobileTokenStorePort
from apps.auth.app.ports.output.mobile_user_repository_port import MobileUserRepositoryPort
from apps.auth.domain.exception.mobile_auth_exceptions import (
    ConsentRequiredTermsNotAgreedError,
    ConsentTokenInvalidError,
    NicknameRequiredError,
    NicknameTakenError,
)


class MobileConsentCompleteInteractor(MobileConsentCompleteUseCase):

    def __init__(
        self,
        pending_signup: PendingSignupPort,
        user_repository: MobileUserRepositoryPort,
        token_store: MobileTokenStorePort,
    ) -> None:
        self._pending_signup = pending_signup
        self._user_repository = user_repository
        self._token_store = token_store

    async def complete(self, command: MobileConsentCompleteCommand) -> MobileAuthTokens:
        if not command.agree_terms:
            raise ConsentRequiredTermsNotAgreedError()

        nickname = command.nickname.strip()
        if not nickname:
            raise NicknameRequiredError()

        pending = await self._pending_signup.pop(command.consent_token)
        if pending is None:
            raise ConsentTokenInvalidError()

        if self._user_repository.nickname_exists(nickname):
            raise NicknameTakenError()

        user = self._user_repository.create(
            provider=pending.provider, sub=pending.sub, email=pending.email, nickname=nickname
        )

        access_token, expires_in = await self._token_store.create_access_token(
            sub=str(user.id), roles=[user.role]
        )
        refresh_token = await self._token_store.create_refresh_token(
            sub=str(user.id), device_id=command.device_id
        )
        return MobileAuthTokens(
            access_token=access_token, refresh_token=refresh_token, token_type="Bearer", expires_in=expires_in
        )
