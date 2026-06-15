from __future__ import annotations

import logging
from typing import Any
from fastapi import Depends


from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import SmithCaptainSchema, ChatSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse, SmithChatCommand, SmithChatResponse
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.output.crew_smith_captain_repository import SmithCaptainRepository
from titanic.dependencies.passenger_jack_trainer_provider import get_jack_trainer_use_case
from titanic.dependencies.passenger_rose_model_provider import get_rose_model_use_case

logger = logging.getLogger(__name__)

class SmithCaptainInteractor(SmithCaptainUseCase):

    def __init__(self, repository: SmithCaptainRepository):
        self.repository = repository

    async def chat(self, schema: ChatSchema,
                    jack: JackTrainerUseCase = Depends(get_jack_trainer_use_case),
                    rose: RoseModelUseCase = Depends(get_rose_model_use_case)
                    ) -> SmithChatResponse:
        logger.info("[Smith Chat] message: %s", schema.message)
        
        return "1309명 입니다."

    async def introduce_myself(self, schema: SmithCaptainSchema) -> SmithCaptainResponse:
        return await self.repository.introduce_myself(SmithCaptainQuery(
            id=schema.id,
            name=schema.name
        ))




