from __future__ import annotations

import os
from functools import lru_cache

from ontology.adapter.outbound.repositories.sommelier_graph_repository import SommelierRepository
from ontology.app.use_cases.sommelier_graph_interactor import SommelierInteractor


@lru_cache(maxsize=1)
def _repo() -> SommelierRepository:
    return SommelierRepository(
        uri=os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "changeme"),
    )


def get_sommelier_use_case() -> SommelierInteractor:
    return SommelierInteractor(repo=_repo())
