from __future__ import annotations

from typing import Any

from kiwipiepy import Kiwi
from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery, JackTrainerResponse
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.output.passenger_jack_trainer_repository import JackTrainerRepository


class JackTrainerInteractor(JackTrainerUseCase):
    
    def __init__(self, repository: JackTrainerRepository):
        self.repository = repository
        self.kiwi = Kiwi()
        
    async def analyze_message_intent(self, user_message: str) -> dict:
        tokens = self.kiwi.tokenize(user_message)

        keywords = [t.form for t in tokens if t.tag in ("NNG", "NNP", "SL", "SN")]

        forms = {t.form for t in tokens}
        if forms & {"몇", "수", "명수", "총", "얼마", "인원"}:
            intent = "count"
        elif forms & {"생존", "살아남", "살았", "구조"}:
            intent = "survival"
        elif forms & {"사망", "죽었", "죽다", "사망자"}:
            intent = "death"
        elif forms & {"평균", "나이", "연령"}:
            intent = "statistics"
        elif forms & {"성별", "여성", "남성", "여자", "남자"}:
            intent = "gender"
        elif forms & {"등석", "클래스", "pclass"}:
            intent = "class"
        else:
            intent = "unknown"

        return {"keywords": keywords, "intent": intent}

    async def introduce_myself(self, schema: JackTrainerSchema) -> JackTrainerResponse:
        '''잭 트레이너의 자기소개 인터렉트'''
        query = JackTrainerQuery(
            id = schema.id,
            name = schema.name
        )
        return await self.repository.introduce_myself(JackTrainerQuery(
            id = schema.id,
            name = schema.name
        ))
        