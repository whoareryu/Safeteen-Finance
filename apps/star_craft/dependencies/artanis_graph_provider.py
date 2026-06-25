from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.gird_oracle_database_manager import get_db
from star_craft.adapter.outbound.repositories.artanis_graph_repository import ArtanisGraphRepository
from star_craft.app.ports.input.artanis_graph_use_case import ArtanisGraphUseCase
from star_craft.app.ports.output.artanis_graph_port import ArtanisGraphPort
from star_craft.app.use_cases.artanis_graph_interactor import ArtanisGraphInteractor

"""
ArtanisGraph 의존성 조립소 (DIP 팩토리).
"""


def get_artanis_graph_repository(
    db: AsyncSession = Depends(get_db),
) -> ArtanisGraphPort:
    return ArtanisGraphRepository(session=db)


def get_artanis_graph_use_case(
    repository: ArtanisGraphPort = Depends(get_artanis_graph_repository),
) -> ArtanisGraphUseCase:
    return ArtanisGraphInteractor(repository=repository)
