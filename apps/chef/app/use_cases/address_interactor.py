from __future__ import annotations

from chef.app.dtos.address_dto import (
    AddressCreateCommand,
    AddressDetailResult,
    AddressQuery,
    AddressResponse,
    AddressUploadResult,
    ContactUploadDto,
)
from chef.app.ports.input.address_use_case import AddressUseCase
from chef.app.ports.output.address_port import AddressPort


class AddressInteractor(AddressUseCase):
    def __init__(self, repository: AddressPort) -> None:
        self._repository = repository

    async def introduce_myself(self, query: AddressQuery) -> AddressResponse:
        return AddressResponse(id=query.id, name=query.name)

    async def add_contact(self, cmd: AddressCreateCommand) -> AddressDetailResult:
        return await self._repository.add_contact(cmd)

    async def list_contacts(self) -> list[AddressDetailResult]:
        return await self._repository.list_contacts()

    async def upload_contacts(self, rows: list[ContactUploadDto]) -> AddressUploadResult:
        return await self._repository.upload_contacts(rows)
