from __future__ import annotations

from functools import lru_cache

from core.matrix.secret_manager import secret_manager
from ontology.adapter.outbound.repositories.sommelier_graph_repository import SommelierRepository
from ontology.app.use_cases.sommelier_graph_interactor import SommelierInteractor


@lru_cache(maxsize=1)
def _repo() -> SommelierRepository:
    return SommelierRepository(
        uri=secret_manager.get_secret("NEO4J_URI", "bolt://neo4j:7687"),
        user=secret_manager.get_secret("NEO4J_USER", "neo4j"),
        password=secret_manager.get_secret("NEO4J_PASSWORD", "changeme"),
    )


def get_sommelier_use_case() -> SommelierInteractor:
    return SommelierInteractor(repo=_repo())
