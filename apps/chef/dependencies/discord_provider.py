from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.gird_oracle_database_manager import get_db
from chef.adapter.outbound.repositories.discord_repository import DiscordRepository
from chef.app.ports.input.discord_use_case import DiscordUseCase
from chef.app.ports.output.discord_port import DiscordPort
from chef.app.use_cases.discord_interactor import DiscordInteractor


def get_discord_repository(db: AsyncSession = Depends(get_db)) -> DiscordPort:
    return DiscordRepository(session=db)


def get_discord_use_case(
    repository: DiscordPort = Depends(get_discord_repository),
) -> DiscordUseCase:
    return DiscordInteractor(repository=repository)
