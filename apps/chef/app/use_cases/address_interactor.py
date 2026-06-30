from __future__ import annotations

from chef.adapter.inbound.api.schemas.address_schema import AddressSchema, AddressUploadResultSchema, ContactUploadSchema
from chef.app.dtos.address_dto import AddressCreateCommand, AddressDetailResult, AddressQuery, AddressResponse
from chef.app.ports.input.address_use_case import AddressUseCase
from chef.app.ports.output.address_port import AddressPort


class AddressInteractor(AddressUseCase):

    def __init__(self, repository: AddressPort) -> None:
        self.repository = repository

    async def introduce_myself(self, query: AddressQuery) -> AddressResponse:
        schema = AddressSchema(id=3, name="Chef Address Book")
        return AddressResponse(id=schema.id, name=schema.name)

    async def add_contact(self, cmd: AddressCreateCommand) -> AddressDetailResult:
        return await self.repository.add_contact(cmd)

    async def list_contacts(self) -> list[AddressDetailResult]:
        return await self.repository.list_contacts()

    async def upload_contacts(self, rows: list[ContactUploadSchema]) -> AddressUploadResultSchema:
        return await self.repository.upload_contacts(rows)
