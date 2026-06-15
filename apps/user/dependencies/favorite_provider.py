from functools import lru_cache

from user.adapter.outbound.pg.favorite_pg_repository import FavoritePgRepository
from user.app.ports.input.favorite_use_case import FavoriteUseCase
from user.app.ports.output.favorite_repository import FavoriteRepository
from user.app.use_cases.favorite_interactor import FavoriteInteractor


@lru_cache
def get_favorite_use_case() -> FavoriteUseCase:
    repository: FavoriteRepository = FavoritePgRepository()
    return FavoriteInteractor(repository=repository)
