from __future__ import annotations
from abc import ABC, abstractmethod

from chef.adapter.inbound.api.schemas.address_schema import AddressUploadResultSchema, ContactUploadSchema
from chef.app.dtos.address_dto import AddressCreateCommand, AddressDetailResult, AddressQuery, AddressResponse


class AddressPort(ABC):

    @abstractmethod
    async def introduce_myself(self, query: AddressQuery) -> AddressResponse:
        pass

    @abstractmethod
    async def add_contact(self, cmd: AddressCreateCommand) -> AddressDetailResult:
        pass

    @abstractmethod
    async def list_contacts(self) -> list[AddressDetailResult]:
        pass

    @abstractmethod
    async def upload_contacts(self, rows: list[ContactUploadSchema]) -> AddressUploadResultSchema:
        pass
