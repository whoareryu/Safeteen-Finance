from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.infra.database_manager import get_db
from community.adapter.outbound.repositories.discord_repository import DiscordRepository
from community.app.ports.input.discord_use_case import DiscordUseCase
from community.app.ports.output.discord_port import DiscordPort
from community.app.use_cases.discord_interactor import DiscordInteractor


def get_discord_repository(db: AsyncSession = Depends(get_db)) -> DiscordPort:
    return DiscordRepository(session=db)


def get_discord_use_case(
    repository: DiscordPort = Depends(get_discord_repository),
) -> DiscordUseCase:
    return DiscordInteractor(repository=repository)
