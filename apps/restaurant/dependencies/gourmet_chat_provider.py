from functools import lru_cache

from restaurant.adapter.outbound.pg.gourmet_chat_pg_repository import GourmetChatPgRepository
from restaurant.app.ports.input.gourmet_chat_use_case import GourmetChatUseCase
from restaurant.app.ports.output.gourmet_chat_repository import GourmetChatRepository
from restaurant.app.use_cases.gourmet_chat_interactor import GourmetChatInteractor


@lru_cache
def get_gourmet_chat_use_case() -> GourmetChatUseCase:
    repository: GourmetChatRepository = GourmetChatPgRepository()
    return GourmetChatInteractor(repository=repository)
