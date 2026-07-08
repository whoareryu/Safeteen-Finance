from __future__ import annotations

from abc import ABC, abstractmethod

from chef.app.dtos.address_dto import (
    AddressCreateCommand,
    AddressDetailResult,
    AddressQuery,
    AddressResponse,
    AddressUploadResult,
    ContactUploadDto,
)


class AddressUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, query: AddressQuery) -> AddressResponse: ...

    @abstractmethod
    async def add_contact(self, cmd: AddressCreateCommand) -> AddressDetailResult: ...

    @abstractmethod
    async def list_contacts(self) -> list[AddressDetailResult]: ...

    @abstractmethod
    async def upload_contacts(self, rows: list[ContactUploadDto]) -> AddressUploadResult: ...
