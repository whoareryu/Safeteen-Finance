from __future__ import annotations

from functools import lru_cache

from core.matrix.secret_manager import secret_manager
from ontology.adapter.outbound.repositories.lens_search_repository import LensRepository
from ontology.app.use_cases.lens_search_interactor import LensInteractor


@lru_cache(maxsize=1)
def _repo() -> LensRepository:
    return LensRepository(
        host=secret_manager.get_secret("QDRANT_HOST", "qdrant"),
        port=int(secret_manager.get_secret("QDRANT_PORT", "6333")),
    )


def get_lens_use_case() -> LensInteractor:
    return LensInteractor(repo=_repo())
