from __future__ import annotations

from apps.auth.app.dtos.mobile_auth_dto import MobileAuthTokens, MobileRefreshCommand
from apps.auth.app.ports.input.mobile_auth_use_case import MobileRefreshUseCase
from apps.auth.app.ports.output.mobile_token_store_port import MobileTokenStorePort
from apps.auth.app.ports.output.mobile_user_repository_port import MobileUserRepositoryPort
from apps.auth.domain.exception.mobile_auth_exceptions import (
    SessionUserNotFoundError,
    TokenReuseDetectedError,
)


class MobileRefreshInteractor(MobileRefreshUseCase):

    def __init__(self, token_store: MobileTokenStorePort, user_repository: MobileUserRepositoryPort) -> None:
        self._token_store = token_store
        self._user_repository = user_repository

    async def refresh(self, command: MobileRefreshCommand) -> MobileAuthTokens:
        result = await self._token_store.rotate_refresh_token(command.refresh_token)
        if result is None:
            raise TokenReuseDetectedError()

        sub, new_refresh_token = result
        user = self._user_repository.find_by_id(int(sub))
        if user is None:
            raise SessionUserNotFoundError()

        access_token, expires_in = await self._token_store.create_access_token(
            sub=sub, roles=[user.role]
        )
        return MobileAuthTokens(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="Bearer",
            expires_in=expires_in,
        )
