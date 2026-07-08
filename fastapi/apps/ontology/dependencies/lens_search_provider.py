from __future__ import annotations

import os
from functools import lru_cache

from ontology.adapter.outbound.repositories.lens_search_repository import LensRepository
from ontology.app.use_cases.lens_search_interactor import LensInteractor


@lru_cache(maxsize=1)
def _repo() -> LensRepository:
    return LensRepository(
        host=os.getenv("QDRANT_HOST", "qdrant"),
        port=int(os.getenv("QDRANT_PORT", "6333")),
    )


def get_lens_use_case() -> LensInteractor:
    return LensInteractor(repo=_repo())
