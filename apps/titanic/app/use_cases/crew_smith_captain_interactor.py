from __future__ import annotations

from typing import Any
from fastapi import Depends


from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import SmithCaptainSchema, ChatSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse, SmithChatCommand, SmithChatResponse
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.output.crew_smith_captain_repository import SmithCaptainRepository
from titanic.dependencies.passenger_jack_trainer_provider import get_jack_trainer
from titanic.dependencies.passenger_rose_model_provider import get_rose_model


class SmithCaptainInteractor(SmithCaptainUseCase):

    def __init__(self, repository: SmithCaptainRepository):
        self.repository = repository

    async def chat(self, schema: ChatSchema,
                    jack: JackTrainerUseCase = Depends(get_jack_trainer),
                    rose: RoseModelUseCase = Depends(get_rose_model)
                    ) -> SmithChatResponse:
        
        
        return await self.repository.chat(SmithChatCommand(message=schema.message))

    async def introduce_myself(self, schema: SmithCaptainSchema) -> SmithCaptainResponse:
        return await self.repository.introduce_myself(SmithCaptainQuery(
            id=schema.id,
            name=schema.name
        ))

    
        