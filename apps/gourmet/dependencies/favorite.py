from functools import lru_cache

from gourmet.adapter.outbound.pg.favorite_pg_repository import FavoritePgRepository
from gourmet.app.ports.input.favorite_use_case import FavoriteUseCase
from gourmet.app.ports.output.favorite_repository import FavoriteRepository
from gourmet.app.use_cases.favorite_interactor import FavoriteInteractor


@lru_cache
def get_favorite_use_case() -> FavoriteUseCase:
    repository: FavoriteRepository = FavoritePgRepository()
    return FavoriteInteractor(repository=repository)
