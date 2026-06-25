from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.gird_oracle_database_manager import get_db
from star_craft.adapter.outbound.repositories.kerrigan_topology_repository import KerriganTopologyRepository
from star_craft.app.ports.input.kerrigan_topology_use_case import KerriganTopologyUseCase
from star_craft.app.ports.output.kerrigan_topology_port import KerriganTopologyPort
from star_craft.app.use_cases.kerrigan_topology_interactor import KerriganTopologyInteractor

"""
KerriganTopology 의존성 조립소 (DIP 팩토리).
라우터는 KerriganTopologyUseCase(포트)만 알고, 구현체는 여기서 결정한다.
"""


def get_kerrigan_topology_repository(
    db: AsyncSession = Depends(get_db),
) -> KerriganTopologyPort:
    return KerriganTopologyRepository(session=db)


def get_kerrigan_topology_use_case(
    repository: KerriganTopologyPort = Depends(get_kerrigan_topology_repository),
) -> KerriganTopologyUseCase:
    return KerriganTopologyInteractor(repository=repository)
