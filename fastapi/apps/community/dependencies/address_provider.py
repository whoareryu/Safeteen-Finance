from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.infra.database_manager import get_db
from community.adapter.outbound.repositories.address_repository import AddressRepository
from community.app.ports.input.address_use_case import AddressUseCase
from community.app.ports.output.address_port import AddressPort
from community.app.use_cases.address_interactor import AddressInteractor


def get_address_repository(db: AsyncSession = Depends(get_db)) -> AddressPort:
    return AddressRepository(session=db)


def get_address_use_case(
    repository: AddressPort = Depends(get_address_repository),
) -> AddressUseCase:
    return AddressInteractor(repository=repository)
