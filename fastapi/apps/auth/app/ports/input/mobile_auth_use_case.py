from __future__ import annotations

from abc import ABC, abstractmethod

from apps.auth.app.dtos.mobile_auth_dto import (
    MobileAuthTokens,
    MobileConsentCompleteCommand,
    MobileKakaoLoginCommand,
    MobileLoginResult,
    MobileLogoutCommand,
    MobileRefreshCommand,
)


class MobileKakaoLoginUseCase(ABC):
    @abstractmethod
    async def login(self, command: MobileKakaoLoginCommand) -> MobileLoginResult:
        pass


class MobileConsentCompleteUseCase(ABC):
    @abstractmethod
    async def complete(self, command: MobileConsentCompleteCommand) -> MobileAuthTokens:
        pass


class MobileRefreshUseCase(ABC):
    @abstractmethod
    async def refresh(self, command: MobileRefreshCommand) -> MobileAuthTokens:
        pass


class MobileLogoutUseCase(ABC):
    @abstractmethod
    async def logout(self, command: MobileLogoutCommand) -> None:
        pass
