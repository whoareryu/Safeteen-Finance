from __future__ import annotations

from abc import ABC, abstractmethod

from community.app.dtos.address_dto import (
    AddressCreateCommand,
    AddressDetailResult,
    AddressUploadResult,
    ContactUploadDto,
)


class AddressPort(ABC):
    @abstractmethod
    async def add_contact(self, cmd: AddressCreateCommand) -> AddressDetailResult: ...

    @abstractmethod
    async def list_contacts(self) -> list[AddressDetailResult]: ...

    @abstractmethod
    async def upload_contacts(self, rows: list[ContactUploadDto]) -> AddressUploadResult: ...
