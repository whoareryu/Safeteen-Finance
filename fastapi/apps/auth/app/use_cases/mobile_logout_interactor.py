from __future__ import annotations

from apps.auth.app.dtos.mobile_auth_dto import MobileLogoutCommand
from apps.auth.app.ports.input.mobile_auth_use_case import MobileLogoutUseCase
from apps.auth.app.ports.output.mobile_token_store_port import MobileTokenStorePort
from apps.auth.domain.exception.mobile_auth_exceptions import PlatformMismatchError


class MobileLogoutInteractor(MobileLogoutUseCase):

    def __init__(self, token_store: MobileTokenStorePort) -> None:
        self._token_store = token_store

    async def logout(self, command: MobileLogoutCommand) -> None:
        if command.platform != "mobile":
            raise PlatformMismatchError()

        await self._token_store.revoke_all(command.sub)
        await self._token_store.blacklist_access_token(command.jti)
